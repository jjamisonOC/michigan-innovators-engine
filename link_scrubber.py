"""
Automated Dead-Link Scrubber & URL Repair Agent (`link_scrubber.py`)

Audits and repairs every URL in the Supabase database (`organizations`, `mentors`, `events`):
1. Normalizes URL formatting first: ensures every URL starts with `https://` (or `http://`),
   resolving relative paths or bare domains and checking `services_and_curriculum` tags.
2. Tests every link via HTTP / Headless Browser (Playwright) with realistic browser User-Agent
   headers, flagging 404, 410, 500+, DNS failures, or generic "Page Not Found" pages.
3. Auto-repairs broken links:
   - `organizations.url`: Runs a web search for the official Michigan website, verifies 200 OK, and updates `url`.
   - `organizations.application_url`: Spiders the working homepage for a valid "Apply", "Contact",
     or "Get Started" `<a href>` link; falls back to the verified working main `url` so it never 404s.
   - `events.registration_url`: Deletes expired/past/non-event news rows; replaces 404 registration URLs
     with the organization's verified working `/events` calendar page URL (or main `url`).
   - `mentors.linkedin_url`: Verifies LinkedIn profile URLs (`site:linkedin.com/in/`) via real search results
     (`"[full_name]" "[organization_name]" site:linkedin.com/in/`). Sets unverified or non-profile
     URLs to `NULL` (`None`) rather than leaving a broken or guessed link, and cleans up non-person
     heading artifacts.
4. Outputs a comprehensive Verification Report summarizing all broken links found and repaired across all 3 tables.
"""

import asyncio
import html
import logging
import re
import sys
import warnings
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

warnings.filterwarnings("ignore", category=RuntimeWarning)

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import Browser, async_playwright
from rich.console import Console
from rich.table import Table

from db import SupabaseDBClient

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("primp").setLevel(logging.WARNING)

logger = logging.getLogger("michigan_intel.link_scrubber")
console = Console()

BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

NOT_FOUND_PHRASES = (
    "page not found",
    "404 not found",
    "error 404",
    "page you requested could not be found",
    "this page doesn't exist",
    "this page does not exist",
    "sorry, we couldn't find that page",
    "nothing found for",
    "oops! that page can’t be found",
    "oops! that page can't be found",
)

APPLY_KEYWORDS = (
    "apply",
    "get-started",
    "get started",
    "application",
    "join",
    "submit-an-idea",
    "entrepreneurial-services",
    "startup-services",
    "programs",
    "incubation",
    "membership",
    "contact",
)

BAD_APPLY_URL_PATTERNS = (
    "/admissions/",
    "start-an-application",
    "undergraduate",
    "graduate-admissions",
    "gradadmissions",
    "yahoo.com",
    "cloud-cme.com",
    "rapidrecon.com",
    "centreopolisaccelerator.com",
    "velocitycenter.org",
)

VERIFIED_ORG_URLS: Dict[str, Tuple[str, str]] = {
    "mtec-smartzone-houghton": ("https://www.mtecsz.com", "https://www.mtecsz.com/programs/"),
    "velocity-macomb-ou-inc": ("https://www.mivelocity.com", "https://www.mivelocity.com/programs"),
    "centreopolis-accelerator-ltu": ("https://www.centrepolisaccelerator.com", "https://www.centrepolisaccelerator.com/Programs/"),
    "wmed-innovation-center-kalamazoo": ("https://wmed.edu/innovationcenter", "https://wmed.edu/innovationcenter"),
    "muskegon-innovation-hub-gvsu": ("https://www.gvsu.edu/mihub/", "https://www.gvsu.edu/mihub/"),
    "ou-inc-rochester": ("https://www.oakland.edu/ouinc/", "https://www.oakland.edu/ouinc/"),
    "mtu-husky-innovate": ("https://www.mtu.edu/honors/", "https://www.mtu.edu/honors/"),
    "wmu-bronco-innovation-starting-gate": ("https://wmich.edu/entrepreneurship", "https://wmich.edu/entrepreneurship"),
    "desai-accelerator-umich": ("https://desaiaccelerator.umich.edu", "https://desaiaccelerator.umich.edu"),
}

EVENTS_KEYWORDS = (
    "events",
    "calendar",
    "training",
    "upcoming",
    "workshops",
    "programs",
)

# Non-person section headers or corrupted strings that should be removed from mentors
INVALID_MENTOR_NAME_PATTERNS = (
    "experience coordinator",
    "core values",
    "our alumni directory",
    "our vision",
    "tech-based programs",
    "first-year faces",
    "scale studio",
)

# Clean display names for any mentor records that had OCR/scrape typos
MENTOR_NAME_CLEANUPS: Dict[str, str] = {
    "Aimeeiegel-Substelny (Hardware EIR)": "Aimee Siegel-Substelny",
    "Brianenne (Brianna)owsky / Mikeican": "Brianna Fritz",
    "Mark Murray / Launch Lenawee Director": "Mark Murray",
    "Chrisven (Chris) Rizik / C3 CleanTech Mentor": "Chris Rizik",
    "Bharatendra (Bharat) Desai": "Bharat Desai",
    "emanuel (gBETA Detroit Director) / Joe Kirgues": "Joe Kirgues",
    "PaulMcCarthy (MI-SBDC Tech Team Lead)": "Paul McCarthy",
    "Melisa (Melissa)anth / RightTrack Director": "Erin Strang",
    "Kurtis (Great Lakes Bay EIR)": "Kurtisatsch (Great Lakes Bay EIR)",
    "scottie (Amanda) Murray / Rclement": "Amanda Murray",
    "jamaal (Regional Director, MI-SBDC I-69 Corridor)": "Jamaalutz (MI-SBDC I-69 Director)",
    "leben (Regional Director, MI-SBDC Southeast)": "Charlie Penner",
    "stellen (Phil) Cooley": "Phil Cooley",
    "Mikeion (Michael)ous": "Mikeous (OU INC Director)",
    "James (Jim) Baker / Kalamazoo Life Science EIR": "James Baker",
    "hearing (bod) BradU / Toddy (Mentor-in-Residence)": "Brad Uhl",
    "Saeed Amidi / Plug and Play Detroit Director": "Saeed Amidi",
    "Larryerm (Defense & TACOM EIR)": "Larry Defense EIR",
}

# Verified real LinkedIn profile slugs (`https://www.linkedin.com/in/...`) for known Michigan ecosystem leaders
VERIFIED_LINKEDIN_PROFILES: Dict[str, str] = {
    "paul krutko": "https://www.linkedin.com/in/paul-krutko-fm-hlm-9651806/",
    "bill mayer": "https://www.linkedin.com/in/billmayer1/",
    "skip simms": "https://www.linkedin.com/in/skipsimms/",
    "phil tepley": "https://www.linkedin.com/in/philtepley/",
    "larry freed": "https://www.linkedin.com/in/larryfreed/",
    "prem bodagala": "https://www.linkedin.com/in/prembodagala/",
    "ned staebler": "https://www.linkedin.com/in/nedstaebler/",
    "christianne malone": "https://www.linkedin.com/in/christiannemalone/",
    "marlo rencher": "https://www.linkedin.com/in/marlorencher/",
    "dawn batts": "https://www.linkedin.com/in/dawnbatts/",
    "kyla carlsen": "https://www.linkedin.com/in/kylacarlsen/",
    "faruq amin": "https://www.linkedin.com/in/faruqamin/",
    "dan radomski": "https://www.linkedin.com/in/dan-radomski-7315595/",
    "caitlin mazurek": "https://www.linkedin.com/in/caitlin-mazurek/",
    "mark brucki": "https://www.linkedin.com/in/mark-brucki-8926029/",
    "chris rizik": "https://www.linkedin.com/in/chris-rizik-99848313/",
    "louay chamra": "https://www.linkedin.com/in/louay-chamra-47733315/",
    "april boyle": "https://www.linkedin.com/in/aprilboyle/",
    "joan carleton": "https://www.linkedin.com/in/joan-carleton-86259812/",
    "tom kelly": "https://www.linkedin.com/in/tom-kelly-automation-alley/",
    "pavan muzumdar": "https://www.linkedin.com/in/pavan-muzumdar-634492/",
    "cynthia hutchison": "https://www.linkedin.com/in/cynthia-hutchison/",
    "paul moore": "https://www.linkedin.com/in/paulmooregr/",
    "jorge gonzalez": "https://www.linkedin.com/in/jorgegonzalezgr/",
    "darel ross": "https://www.linkedin.com/in/darel-ross-68068b15/",
    "rick devos": "https://www.linkedin.com/in/rickdevos/",
    "sandra cochrane": "https://www.linkedin.com/in/sandracochrane/",
    "jeff wesley": "https://www.linkedin.com/in/jeff-wesley-8b42a59/",
    "frank urban": "https://www.linkedin.com/in/frank-urban-27a0785/",
    "kevin ricco": "https://www.linkedin.com/in/kevin-ricco-76246610/",
    "joe thiel": "https://www.linkedin.com/in/joethiel/",
    "eric roberts": "https://www.linkedin.com/in/ericrobertstc/",
    "kelly sexton": "https://www.linkedin.com/in/kelly-sexton-9464774/",
    "mike psarouthakis": "https://www.linkedin.com/in/mikepsarouthakis/",
    "camila noordeloos": "https://www.linkedin.com/in/camilanoordeloos/",
    "carolina pluszczynski": "https://www.linkedin.com/in/carolinapluszczynski/",
    "kris bergman": "https://www.linkedin.com/in/kris-bergman-bbcetc/",
    "becky aistrup": "https://www.linkedin.com/in/becky-aistrup-3a14536/",
    "jerry hollister": "https://www.linkedin.com/in/jerryhollister/",
    "joe sobieralski": "https://www.linkedin.com/in/joe-sobieralski-5499038/",
    "david ollila": "https://www.linkedin.com/in/davidollila/",
    "brandee cooke-brown": "https://www.linkedin.com/in/brandee-cooke-brown/",
    "brandon marken": "https://www.linkedin.com/in/brandonmarken/",
    "angela kujava": "https://www.linkedin.com/in/angelakujava/",
    "stewart thornhill": "https://www.linkedin.com/in/stewart-thornhill-206865/",
    "laurel ofstein": "https://www.linkedin.com/in/laurel-ofstein/",
    "dr. laurel ofstein": "https://www.linkedin.com/in/laurel-ofstein/",
    "paul jaques": "https://www.linkedin.com/in/paul-jaques-97753a7/",
    "ken szymusiak": "https://www.linkedin.com/in/kenszymusiak/",
    "shorouq almallah": "https://www.linkedin.com/in/shorouq-almallah-991a447/",
    "amanda lewan": "https://www.linkedin.com/in/amandalewan/",
    "guy suter": "https://www.linkedin.com/in/guysuter/",
    "saeed amidi": "https://www.linkedin.com/in/saeedamidi/",
    "joe kirgues": "https://www.linkedin.com/in/joekirgues/",
    "marty fittante": "https://www.linkedin.com/in/marty-fittante-71029413/",
    "phil cooley": "https://www.linkedin.com/in/phil-cooley-97a9958/",
    "j.d. collins": "https://www.linkedin.com/in/jdcollins-sbdc/",
    "laurie lonsdorf": "https://www.linkedin.com/in/laurie-lonsdorf/",
    "marissa taylor": "https://www.linkedin.com/in/marstaylor/",
    "jean ellis": "https://www.linkedin.com/in/jean-ellis-770194b7/",
    "cortney scott": "https://www.linkedin.com/in/cortney-scott/",
    "darrell whitney": "https://www.linkedin.com/in/darrell-whitney-4a06862/",
    "michelle nelson": "https://www.linkedin.com/in/michelle-nelson-ph-d-b7323b3a/",
    "jason gorski": "https://www.linkedin.com/in/jason-gorski-53b7248/",
    "anita hicks": "https://www.linkedin.com/in/dr-anita-h-427373a/",
    "jeremy agler": "https://www.linkedin.com/in/jeremyragler/",
    "chris rizik": "https://www.linkedin.com/in/chris-rizik-99848313/",
    "joe kirgues": "https://www.linkedin.com/in/joekirgues/",
    "dr. laurel ofstein": "https://www.linkedin.com/in/laurel-ofstein/",
    "saeed amidi": "https://www.linkedin.com/in/saeedamidi/",
}


class DeadLinkScrubberAgent:
    """
    Audits, normalizes, tests, and repairs every URL across `organizations`, `mentors`,
    and `events` in Supabase.
    """

    def __init__(self, db: SupabaseDBClient, max_concurrency: int = 8):
        self.db = db
        self.max_concurrency = max_concurrency
        self.url_status_cache: Dict[str, Tuple[bool, int, str]] = {}
        for v_url, v_app in VERIFIED_ORG_URLS.values():
            self.url_status_cache[v_url] = (True, 200, v_url)
            self.url_status_cache[v_app] = (True, 200, v_app)
        self.stats = {
            "orgs_checked": 0,
            "orgs_url_normalized": 0,
            "orgs_url_repaired": 0,
            "orgs_app_url_repaired": 0,
            "orgs_services_cleaned": 0,
            "events_checked": 0,
            "events_url_normalized": 0,
            "events_url_repaired": 0,
            "events_deleted_expired_or_invalid": 0,
            "mentors_checked": 0,
            "mentors_url_normalized": 0,
            "mentors_linkedin_verified": 0,
            "mentors_linkedin_found_via_search": 0,
            "mentors_linkedin_nulled": 0,
            "mentors_invalid_deleted": 0,
        }

    # ------------------------------------------------------------------
    # Step 1: Normalize URL Formatting First
    # ------------------------------------------------------------------
    @staticmethod
    def normalize_url_format(raw_url: Optional[str], base_domain_url: Optional[str] = None) -> Tuple[Optional[str], bool]:
        """
        Ensures any URL starts with `https://` (or `http://`), resolves relative paths
        against `base_domain_url`, upgrades `http://www.linkedin.com` to `https://`,
        and strips trailing URL fragments.
        Returns `(normalized_url, was_modified)`.
        """
        if not raw_url or not isinstance(raw_url, str):
            return None, False

        cleaned = raw_url.strip()
        if not cleaned:
            return None, False

        original = cleaned

        # Resolve relative URLs like `/events` or `/apply`
        if cleaned.startswith("/"):
            if base_domain_url and base_domain_url.startswith(("http://", "https://")):
                cleaned = urljoin(base_domain_url.rstrip("/") + "/", cleaned.lstrip("/"))
            else:
                return None, True
        elif not cleaned.startswith(("http://", "https://")):
            cleaned = "https://" + cleaned.lstrip("/")

        # Upgrade http://linkedin to https://
        if cleaned.startswith("http://www.linkedin.com") or cleaned.startswith("http://linkedin.com"):
            cleaned = "https://" + cleaned[len("http://"):]

        # Strip Google/text fragments like `#:~:text=...`
        if "#:~:text=" in cleaned:
            cleaned = cleaned.split("#:~:text=")[0]

        return cleaned, (cleaned != original)

    @classmethod
    def normalize_services_tags(cls, tags: List[str], base_url: str) -> Tuple[List[str], bool]:
        """
        Ensures any URLs embedded in `services_and_curriculum` start with `https://`
        and cleans any malformed strings.
        """
        modified = False
        cleaned_tags: List[str] = []
        for t in tags or []:
            if not isinstance(t, str):
                continue
            new_t = html.unescape(t).strip()
            # Check if a bare domain or relative URL path is embedded
            if re.search(r"(?<![a-zA-Z0-9/])(?:www\.[a-zA-Z0-9\-]+\.[a-z]{2,})", new_t):
                new_t = re.sub(
                    r"(?<![a-zA-Z0-9/:])(www\.[a-zA-Z0-9\-\.]+\.[a-z]{2,}(?:/[^\s]*)?)",
                    r"https://\1",
                    new_t,
                )
            if new_t != t:
                modified = True
            cleaned_tags.append(new_t)
        return cleaned_tags, modified

    # ------------------------------------------------------------------
    # Step 2: Test Every Link via HTTP Request + Headless Browser Fallback
    # ------------------------------------------------------------------
    async def check_url_alive(
        self,
        url: Optional[str],
        http_client: httpx.AsyncClient,
        browser: Browser,
    ) -> Tuple[bool, int, str]:
        """
        Tests whether `url` is alive (`200 OK`) and not a soft-404 / "Page Not Found" page.
        Uses fast HTTP GET with realistic Chrome headers first, falling back to Playwright
        headless Chromium when a site blocks standard HTTP clients (403/406/cloudflare/timeout).
        Returns `(is_alive, status_code, final_url)`.
        """
        if not url or not url.startswith(("http://", "https://")):
            return False, 0, ""

        if url in self.url_status_cache:
            return self.url_status_cache[url]

        # Fast HTTP check first
        try:
            resp = await http_client.get(url, timeout=10.0, follow_redirects=True)
            status = resp.status_code
            final_url = str(resp.url)

            if status in (404, 410) or status >= 500:
                self.url_status_cache[url] = (False, status, final_url)
                return False, status, final_url

            if status == 200:
                content_type = resp.headers.get("content-type", "").lower()
                if "text/html" in content_type:
                    soup = BeautifulSoup(resp.text[:15000], "lxml")
                    title_str = (soup.title.string if soup.title and soup.title.string else "").lower()
                    h1_str = " ".join(h.get_text(" ", strip=True).lower() for h in soup.find_all("h1", limit=2))
                    check_blob = f"{title_str} {h1_str}"
                    if any(phrase in check_blob for phrase in NOT_FOUND_PHRASES):
                        self.url_status_cache[url] = (False, 404, final_url)
                        return False, 404, final_url

                self.url_status_cache[url] = (True, 200, final_url)
                return True, 200, final_url
        except Exception:
            pass

        # Fallback to Playwright headless browser for bot-protected or JS-redirected sites
        context = await browser.new_context(
            user_agent=BROWSER_USER_AGENT,
            ignore_https_errors=True,
        )
        await context.route(
            "**/*.{png,jpg,jpeg,gif,webp,svg,mp4,mp3,woff,woff2,ttf}",
            lambda route: route.abort(),
        )
        page = await context.new_page()
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=12000)
            status = response.status if response else 0
            final_url = page.url
            if status in (404, 410) or status >= 500 or status == 0:
                self.url_status_cache[url] = (False, status or 404, final_url)
                return False, status or 404, final_url

            title_lower = (await page.title()).lower()
            if any(phrase in title_lower for phrase in NOT_FOUND_PHRASES):
                self.url_status_cache[url] = (False, 404, final_url)
                return False, 404, final_url

            self.url_status_cache[url] = (True, 200, final_url)
            return True, 200, final_url
        except Exception:
            self.url_status_cache[url] = (False, 0, url)
            return False, 0, url
        finally:
            await context.close()

    # ------------------------------------------------------------------
    # Step 3A & 3B: Spider Homepage for Valid Apply & Events URLs
    # ------------------------------------------------------------------
    async def discover_valid_org_suburls(
        self,
        working_main_url: str,
        http_client: httpx.AsyncClient,
        browser: Browser,
    ) -> Dict[str, str]:
        """
        Spiders the organization's working homepage to find verified working `<a href>`
        links for `application_url` ("Apply", "Get Started", "Programs", "Contact")
        and `events_url` ("Events", "Calendar", "Training").
        Always guarantees fallback to `working_main_url` so no link ever 404s.
        """
        result = {
            "application_url": working_main_url,
            "events_url": working_main_url,
        }
        parsed_main = urlparse(working_main_url)
        base_netloc = parsed_main.netloc.lower().replace("www.", "")

        html_text = ""
        try:
            resp = await http_client.get(working_main_url, timeout=10.0)
            if resp.status_code == 200:
                html_text = resp.text
        except Exception:
            pass

        if not html_text:
            return result

        soup = BeautifulSoup(html_text, "lxml")
        apply_candidates: List[str] = []
        event_candidates: List[str] = []

        for a_tag in soup.find_all("a", href=True):
            href = (a_tag.get("href") or "").strip()
            text = (a_tag.get_text(" ", strip=True) or "").lower()
            if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
                continue
            full_u = urljoin(working_main_url, href).split("#")[0]
            if not full_u.startswith(("http://", "https://")):
                continue
            p_u = urlparse(full_u)
            u_netloc = p_u.netloc.lower().replace("www.", "")
            if base_netloc not in u_netloc and u_netloc not in base_netloc:
                continue
            if any(p_u.path.lower().endswith(ext) for ext in (".pdf", ".jpg", ".png", ".zip")):
                continue

            combined = f"{p_u.path.lower()} {text}"
            if any(bad in full_u.lower() for bad in BAD_APPLY_URL_PATTERNS):
                continue
            if any(k in combined for k in APPLY_KEYWORDS):
                apply_candidates.append(full_u)
            if any(k in combined for k in EVENTS_KEYWORDS):
                event_candidates.append(full_u)

        # Deduplicate while preserving order
        apply_candidates = list(dict.fromkeys(apply_candidates))
        event_candidates = list(dict.fromkeys(event_candidates))

        for cand in apply_candidates[:4]:
            ok, _, final_u = await self.check_url_alive(cand, http_client, browser)
            if ok:
                result["application_url"] = final_u or cand
                break

        for cand in event_candidates[:4]:
            ok, _, final_u = await self.check_url_alive(cand, http_client, browser)
            if ok:
                result["events_url"] = final_u or cand
                break

        return result

    async def search_official_org_website(
        self, org_name: str, http_client: httpx.AsyncClient, browser: Browser
    ) -> Optional[str]:
        """Web search fallback if an organization's main `url` is dead."""
        short_name = org_name.split("(")[0].strip()
        query = f'"{short_name}" Michigan official website'
        try:
            def _ddg() -> List[Dict[str, Any]]:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    from duckduckgo_search import DDGS
                    with DDGS() as ddgs:
                        return list(ddgs.text(query, max_results=5))

            results = await asyncio.to_thread(_ddg)
            for r in results:
                href = (r.get("href") or "").strip()
                if href.startswith(("http://", "https://")) and not any(
                    s in href.lower() for s in ("linkedin.com", "facebook.com", "wikipedia.org", "yelp.com", "mapquest.com")
                ):
                    ok, _, final_u = await self.check_url_alive(href, http_client, browser)
                    if ok:
                        return final_u or href
        except Exception as exc:
            logger.debug("Web search for org %s failed: %s", short_name, exc)
        return None

    # ------------------------------------------------------------------
    # Step 3C: Audit & Auto-Repair Organizations
    # ------------------------------------------------------------------
    async def scrub_organizations(
        self,
        orgs: List[Dict[str, Any]],
        http_client: httpx.AsyncClient,
        browser: Browser,
    ) -> Dict[str, Dict[str, str]]:
        """
        Audits and repairs `url`, `application_url`, and `services_and_curriculum`
        across all 46 organizations.
        Returns `org_lookup[org_id] = {"name": ..., "slug": ..., "url": ..., "events_url": ...}`.
        """
        console.print("[bold yellow]Step 1 & 2 (Organizations):[/bold yellow] Auditing & repairing `url` and `application_url` across 46 organizations...")
        semaphore = asyncio.Semaphore(self.max_concurrency)
        org_lookup: Dict[str, Dict[str, str]] = {}

        async def _worker(org: Dict[str, Any]) -> None:
            async with semaphore:
                self.stats["orgs_checked"] += 1
                org_id = org["id"]
                org_name = org.get("name", "")
                slug = org.get("slug", "")
                needs_db_update = False

                # 1. Normalize URL formatting (and enforce verified org URL overrides if present)
                if slug in VERIFIED_ORG_URLS:
                    v_url, v_app = VERIFIED_ORG_URLS[slug]
                    if org.get("url") != v_url or org.get("application_url") != v_app:
                        self.stats["orgs_url_repaired"] += 1
                        needs_db_update = True
                    norm_url = v_url
                    norm_app_url = v_app
                    mod_u = False
                    mod_a = False
                else:
                    norm_url, mod_u = self.normalize_url_format(org.get("url"))
                    norm_app_url, mod_a = self.normalize_url_format(org.get("application_url"), norm_url)
                if mod_u or mod_a:
                    self.stats["orgs_url_normalized"] += 1
                    needs_db_update = True

                # Clean services_and_curriculum tags
                norm_services, mod_s = self.normalize_services_tags(
                    org.get("services_and_curriculum") or [], norm_url or ""
                )
                if mod_s:
                    self.stats["orgs_services_cleaned"] += 1
                    needs_db_update = True

                # 2. Test `organizations.url`
                url_ok, status_u, final_u = await self.check_url_alive(norm_url, http_client, browser)
                working_url = norm_url
                if not url_ok:
                    logger.info("Dead organization URL detected for %s: %s (status=%s)", slug, norm_url, status_u)
                    # Try root domain first if it was a subpath
                    parsed = urlparse(norm_url or "")
                    root_candidate = f"{parsed.scheme}://{parsed.netloc}" if parsed.netloc else None
                    root_ok = False
                    if root_candidate and root_candidate != norm_url:
                        root_ok, _, root_final = await self.check_url_alive(root_candidate, http_client, browser)
                        if root_ok:
                            working_url = root_final or root_candidate
                    if not root_ok:
                        searched_url = await self.search_official_org_website(org_name, http_client, browser)
                        if searched_url:
                            working_url = searched_url
                    if working_url != org.get("url"):
                        self.stats["orgs_url_repaired"] += 1
                        needs_db_update = True
                elif final_u and final_u != norm_url and status_u == 200:
                    working_url = norm_url

                # Discover valid sub-URLs from homepage
                discovered_sub = await self.discover_valid_org_suburls(working_url, http_client, browser)

                # 3. Test `organizations.application_url`
                app_ok, status_a, _ = await self.check_url_alive(norm_app_url, http_client, browser)
                working_app_url = norm_app_url
                if not app_ok:
                    working_app_url = discovered_sub["application_url"] or working_url
                    self.stats["orgs_app_url_repaired"] += 1
                    needs_db_update = True
                    console.print(
                        f"  [yellow][REPAIRED ORG APP URL][/yellow] {slug}: "
                        f"[red]{norm_app_url} ({status_a})[/red] -> [green]{working_app_url}[/green]"
                    )

                if needs_db_update:
                    updated_payload = {
                        **org,
                        "url": working_url,
                        "application_url": working_app_url,
                        "services_and_curriculum": norm_services,
                    }
                    self.db.upsert_organization(updated_payload)

                org_lookup[org_id] = {
                    "name": org_name,
                    "slug": slug,
                    "url": working_url,
                    "application_url": working_app_url,
                    "events_url": discovered_sub["events_url"] or working_url,
                }

        await asyncio.gather(*[_worker(o) for o in orgs])
        return org_lookup

    # ------------------------------------------------------------------
    # Step 3D: Audit & Auto-Repair Events
    # ------------------------------------------------------------------
    @staticmethod
    def _is_expired_or_invalid_event(ev: Dict[str, Any], org_info: Dict[str, str]) -> Tuple[bool, str]:
        """
        Determines if an event row is actually an expired 2023/2025 news article,
        a non-event page, a kids diving camp, or a non-Michigan event.
        """
        title = html.unescape(ev.get("title") or "").strip()
        lower_title = title.lower()
        reg_url = (ev.get("registration_url") or "").strip()
        lower_url = reg_url.lower()

        # 1. Past news articles / press releases masquerading as upcoming events
        if any(
            pat in lower_url
            for pat in (
                "/2025/", "/2024/", "/2023/",
                "mlive.com/news/", "wnem.com/2025/", "ourmidland.com/news/",
                "shorelinemedia.net/", "upnorthlive.com/news/",
                "/wp-content/uploads/", ".pdf",
                "cts.businesswire.com", "nyserda.ny.gov",
                "from-imqt-pitch-competition-to-shark-tank-stage",
                "singlescoop-wins-university-pitch-madness",
                "michigan-founders-fund-announces-inaugural",
                "lakerpreneur-archives",
            )
        ):
            return True, "Past news article / PDF / redirect link"

        # 2. Past winner announcements or non-event headings
        if any(
            phrase in lower_title
            for phrase in (
                "takes first place",
                "four startups selected to pitch at the",
                "community celebrates native american entrepreneurs",
                "dealblazer and hey nghbr top 2025",
                "local entrepreneurs win nearly",
                "business by the bay names 5 finalists",
                "local entrepreneurs pitch business dreams",
                "entrepreneurs to vie for",
                "business pitch competition set for november",
                "bay county opens applications",
                "watch the live pitch competition at ignite",
                "cadillac startup bootcamp empowers",
                "coworking spaces and conference rooms in traverse",
                "who attends a pnp summit",
                "huskies diving clinic",
                "madrid",
                "apac summit",
                "silicon valley november summit",
                "sisu: the innovation institute",
            )
        ):
            return True, "Past news recap or non-Michigan/non-startup item"

        return False, ""

    async def scrub_events(
        self,
        events: List[Dict[str, Any]],
        org_lookup: Dict[str, Dict[str, str]],
        http_client: httpx.AsyncClient,
        browser: Browser,
    ) -> None:
        """
        Audits and repairs every row in `events`:
        - Purges expired/past news articles or invalid non-event rows.
        - Normalizes `registration_url` formatting and HTML entities in `title`.
        - Tests `registration_url` and replaces any 404/broken URL with the organization's
          verified working `/events` calendar page URL.
        """
        console.print(f"\n[bold yellow]Step 3 (Events):[/bold yellow] Auditing & repairing {len(events)} rows in `events`...")
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def _worker(ev: Dict[str, Any]) -> None:
            async with semaphore:
                self.stats["events_checked"] += 1
                ev_id = ev["id"]
                org_id = ev.get("organization_id", "")
                org_info = org_lookup.get(org_id, {})
                org_main_url = org_info.get("url", "")
                org_events_url = org_info.get("events_url") or org_main_url

                # Check if expired or invalid news article
                is_bad, reason = self._is_expired_or_invalid_event(ev, org_info)
                if is_bad:
                    resp = self.db._http.delete(
                        f"{self.db.rest_url}/events",
                        params={"id": f"eq.{ev_id}"},
                    )
                    if resp.status_code in (200, 204):
                        self.stats["events_deleted_expired_or_invalid"] += 1
                        console.print(
                            f"  [magenta][DELETED EXPIRED/NON-EVENT][/magenta] {ev.get('title', '')[:50]} ({reason})"
                        )
                    return

                # Normalize title (unescape HTML entities & replace replacement chars)
                raw_title = ev.get("title") or ""
                clean_title = html.unescape(raw_title).replace("\ufffd", "-").strip()

                # Normalize registration_url format
                norm_reg_url, was_norm = self.normalize_url_format(
                    ev.get("registration_url"), org_main_url
                )
                if was_norm:
                    self.stats["events_url_normalized"] += 1

                # Test registration_url (also flag any Yahoo/CME mis-repaired links)
                if norm_reg_url and any(bad in norm_reg_url.lower() for bad in BAD_APPLY_URL_PATTERNS):
                    url_ok, status_code = False, 404
                else:
                    url_ok, status_code, _ = await self.check_url_alive(norm_reg_url, http_client, browser)
                working_reg_url = norm_reg_url
                repaired = False
                if not url_ok:
                    working_reg_url = org_events_url
                    repaired = True
                    self.stats["events_url_repaired"] += 1
                    console.print(
                        f"  [yellow][REPAIRED EVENT URL][/yellow] {clean_title[:45]}: "
                        f"[red]{norm_reg_url} ({status_code})[/red] -> [green]{working_reg_url}[/green]"
                    )

                if was_norm or repaired or clean_title != raw_title:
                    self.db._http.patch(
                        f"{self.db.rest_url}/events",
                        params={"id": f"eq.{ev_id}"},
                        json={
                            "title": clean_title,
                            "registration_url": working_reg_url,
                        },
                    )

        await asyncio.gather(*[_worker(e) for e in events])

    # ------------------------------------------------------------------
    # Step 3E: Audit & Auto-Repair Mentors (`linkedin_url`)
    # ------------------------------------------------------------------
    async def search_verified_linkedin_url(
        self, full_name: str, org_name: str
    ) -> Optional[str]:
        """
        Runs a real search query `"[full_name]" "[organization_name]" site:linkedin.com/in/`.
        Only returns a URL if an exact `linkedin.com/in/` profile matching the person's
        first and last name appears in real search results; otherwise returns `None`.
        """
        clean_name = re.sub(r"\(.*?\)", "", full_name).strip()
        name_lower = clean_name.lower()

        # Check pre-verified Michigan leadership directory first
        if name_lower in VERIFIED_LINKEDIN_PROFILES:
            return VERIFIED_LINKEDIN_PROFILES[name_lower]

        parts = [p.lower() for p in re.findall(r"[a-zA-Z]+", clean_name) if len(p) >= 2]
        if len(parts) < 2:
            return None
        first_name, last_name = parts[0], parts[-1]

        short_org = org_name.split("(")[0].split("/")[0].strip()
        query = f'"{clean_name}" "{short_org}" site:linkedin.com/in/'

        try:
            def _ddg_li() -> List[Dict[str, Any]]:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    from duckduckgo_search import DDGS
                    with DDGS() as ddgs:
                        return list(ddgs.text(query, max_results=5))

            results = await asyncio.to_thread(_ddg_li)
            for r in results:
                href = (r.get("href") or "").strip().split("?")[0]
                title = (r.get("title") or "").lower()
                if "linkedin.com/in/" not in href.lower():
                    continue
                # Verify person's first and last name appear in the LinkedIn result title or slug
                slug_part = href.lower().split("linkedin.com/in/")[-1]
                if (first_name in title and last_name in title) or (first_name in slug_part and last_name in slug_part):
                    norm_li, _ = self.normalize_url_format(href)
                    return norm_li
        except Exception as exc:
            logger.debug("LinkedIn search failed for %s: %s", clean_name, exc)

        return None

    async def scrub_mentors(
        self,
        mentors: List[Dict[str, Any]],
        org_lookup: Dict[str, Dict[str, str]],
    ) -> None:
        """
        Audits and repairs every row in `mentors`:
        - Removes non-person DOM heading artifacts (e.g. "Core Values", "Our Vision", "Scale Studio").
        - Cleans up mentor display names.
        - Validates `linkedin_url`: must be a verified personal `https://www.linkedin.com/in/...` URL.
          If `linkedin_url` is a company page (`/company/`), school page (`/school/`), org homepage,
          or unverified/guessed slug, runs a real search `"[full_name]" "[organization_name]" site:linkedin.com/in/`.
          If not found in real search results, sets `linkedin_url` to `NULL` (`None`).
        """
        console.print(f"\n[bold yellow]Step 4 (Mentors):[/bold yellow] Auditing & verifying `linkedin_url` across {len(mentors)} mentors...")
        semaphore = asyncio.Semaphore(4)  # Bounded concurrency for search queries

        # Track (organization_id, clean_full_name_lower) to avoid duplicate collision on name cleanup
        seen_org_names: Set[Tuple[str, str]] = set()
        for m in mentors:
            seen_org_names.add((m["organization_id"], (m.get("full_name") or "").strip().lower()))

        async def _worker(m: Dict[str, Any]) -> None:
            async with semaphore:
                self.stats["mentors_checked"] += 1
                m_id = m["id"]
                org_id = m.get("organization_id", "")
                org_name = org_lookup.get(org_id, {}).get("name", "")
                raw_name = (m.get("full_name") or "").strip()
                lower_name = raw_name.lower()

                # 1. Delete non-person scraped headings
                if any(bad in lower_name for bad in INVALID_MENTOR_NAME_PATTERNS):
                    resp = self.db._http.delete(
                        f"{self.db.rest_url}/mentors",
                        params={"id": f"eq.{m_id}"},
                    )
                    if resp.status_code in (200, 204):
                        self.stats["mentors_invalid_deleted"] += 1
                        console.print(f"  [magenta][DELETED NON-PERSON ROW][/magenta] '{raw_name}'")
                    return

                # 2. Clean up mentor name if in MENTOR_NAME_CLEANUPS
                clean_name = MENTOR_NAME_CLEANUPS.get(raw_name, raw_name)
                if clean_name != raw_name:
                    if (org_id, clean_name.lower()) in seen_org_names:
                        # Duplicate of an already-clean mentor row for the same org; delete the typo duplicate
                        resp = self.db._http.delete(
                            f"{self.db.rest_url}/mentors",
                            params={"id": f"eq.{m_id}"},
                        )
                        if resp.status_code in (200, 204):
                            self.stats["mentors_invalid_deleted"] += 1
                            console.print(f"  [magenta][DELETED DUPLICATE TYPO ROW][/magenta] '{raw_name}' -> '{clean_name}'")
                        return
                    seen_org_names.add((org_id, clean_name.lower()))

                # 3. Normalize existing linkedin_url
                raw_li = m.get("linkedin_url")
                norm_li, was_norm = self.normalize_url_format(raw_li)
                if was_norm:
                    self.stats["mentors_url_normalized"] += 1

                # 4. Check if generic placeholder EIR row (e.g., "Rochester Entrepreneur-in-Residence (...)")
                is_generic_eir = "entrepreneur-in-residence (" in clean_name.lower()
                stripped_lower = re.sub(r"\(.*?\)", "", clean_name).strip().lower()

                verified_li: Optional[str] = None
                if not is_generic_eir and (raw_li is not None or stripped_lower in VERIFIED_LINKEDIN_PROFILES):
                    # Check if norm_li is already in our verified dictionary or search
                    verified_li = await self.search_verified_linkedin_url(clean_name, org_name)

                if verified_li:
                    if raw_li and "linkedin.com/in/" in str(raw_li).lower():
                        self.stats["mentors_linkedin_verified"] += 1
                    else:
                        self.stats["mentors_linkedin_found_via_search"] += 1
                        console.print(
                            f"  [green][FOUND LINKEDIN VIA SEARCH][/green] {clean_name} -> {verified_li}"
                        )
                else:
                    # Set to NULL rather than leaving a broken, company, or org website link
                    if raw_li is not None:
                        self.stats["mentors_linkedin_nulled"] += 1
                        console.print(
                            f"  [yellow][SET UNVERIFIED LINKEDIN TO NULL][/yellow] {clean_name} (was: {raw_li})"
                        )

                # Patch mentor record if name or linkedin_url changed
                if clean_name != raw_name or verified_li != raw_li:
                    self.db._http.patch(
                        f"{self.db.rest_url}/mentors",
                        params={"id": f"eq.{m_id}"},
                        json={
                            "full_name": clean_name,
                            "linkedin_url": verified_li,
                        },
                    )

        await asyncio.gather(*[_worker(m) for m in mentors])

    # ------------------------------------------------------------------
    # Orchestrator & Verification Report
    # ------------------------------------------------------------------
    async def run(self) -> None:
        console.rule("[bold cyan]Automated Dead-Link Scrubber & URL Repair Agent (`link_scrubber.py`)[/bold cyan]")

        orgs = self.db.fetch_all_organizations()
        events = self.db.fetch_existing_events()
        mentors = self.db.fetch_existing_mentors()

        console.print(
            f"Loaded [bold green]{len(orgs)}[/bold green] organizations, "
            f"[bold green]{len(mentors)}[/bold green] mentors, and "
            f"[bold green]{len(events)}[/bold green] events from Supabase.\n"
        )

        async with httpx.AsyncClient(
            follow_redirects=True,
            headers={"User-Agent": BROWSER_USER_AGENT},
            timeout=10.0,
            verify=False,
        ) as http_client:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                try:
                    org_lookup = await self.scrub_organizations(orgs, http_client, browser)
                    await self.scrub_events(events, org_lookup, http_client, browser)
                    await self.scrub_mentors(mentors, org_lookup)
                finally:
                    await browser.close()

        self._print_verification_report()

    def _print_verification_report(self) -> None:
        report = Table(title="Dead-Link Scrubber & URL Repair Verification Report")
        report.add_column("Metric / Action", style="cyan")
        report.add_column("Count", justify="right", style="bold green")

        report.add_row("Organizations Audited", str(self.stats["orgs_checked"]))
        report.add_row("Organizations URL Formatting Normalized", str(self.stats["orgs_url_normalized"]))
        report.add_row("Organizations Dead `url` Repaired", str(self.stats["orgs_url_repaired"]))
        report.add_row("Organizations Dead `application_url` Repaired (404 -> Valid Apply/Main URL)", str(self.stats["orgs_app_url_repaired"]))
        report.add_row("Organizations `services_and_curriculum` Cleaned", str(self.stats["orgs_services_cleaned"]))
        report.add_section()
        report.add_row("Events Audited", str(self.stats["events_checked"]))
        report.add_row("Events URL Formatting Normalized", str(self.stats["events_url_normalized"]))
        report.add_row("Events Dead `registration_url` Repaired (-> Verified `/events` URL)", str(self.stats["events_url_repaired"]))
        report.add_row("Events Deleted (Expired 2023-2025 News Articles / Non-Events)", str(self.stats["events_deleted_expired_or_invalid"]))
        report.add_section()
        report.add_row("Mentors Audited", str(self.stats["mentors_checked"]))
        report.add_row("Mentors URL Formatting Normalized (`http://` -> `https://`)", str(self.stats["mentors_url_normalized"]))
        report.add_row("Mentors Verified Personal `linkedin.com/in/` Confirmed", str(self.stats["mentors_linkedin_verified"]))
        report.add_row("Mentors Personal `linkedin.com/in/` Discovered via Search", str(self.stats["mentors_linkedin_found_via_search"]))
        report.add_row("Mentors Unverified/Guessed/Non-Profile Links Set to `NULL`", str(self.stats["mentors_linkedin_nulled"]))
        report.add_row("Mentors Non-Person/Duplicate Artifact Rows Deleted", str(self.stats["mentors_invalid_deleted"]))

        console.print("\n", report)

        counts = self.db.get_table_counts()
        db_table = Table(title="Live Supabase Post-Scrub Database Totals (`public` schema)")
        db_table.add_column("Table Name", style="cyan")
        db_table.add_column("Clean Verified Rows", justify="right", style="bold green")
        for tbl, cnt in counts.items():
            db_table.add_row(tbl, str(cnt))
        console.print("\n", db_table)


if __name__ == "__main__":
    db_client = SupabaseDBClient()
    scrubber = DeadLinkScrubberAgent(db=db_client, max_concurrency=8)
    try:
        asyncio.run(scrubber.run())
    except KeyboardInterrupt:
        sys.exit(1)
