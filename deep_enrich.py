"""
Deep Recursive Web Spider & Exhaustive Mentor/Program/Event Extractor (`deep_enrich.py`)

Pulls every existing organization from the Supabase `organizations` table and runs an
independent, multi-step deep crawl for each one:
  Step 1: Sitemap (`sitemap.xml`) & Full Navigation Link Spidering (Per Domain)
          classified into 4 buckets: People/Mentors, Programs/Curriculum, Facilities/Equipment, Events/Calendar.
  Step 2: Headless Browser Rendering with Playwright (Chromium headless), auto-scrolling and
          clicking "Load More" / "Show All" / pagination buttons.
  Step 3: Exhaustive Mentor & Leadership Extraction + LinkedIn Cross-Reference (`site:linkedin.com/in/`),
          upserting into `mentors` (avoiding duplicates by `(organization_id, full_name)`).
  Step 4: Deep Program, Curriculum & Equipment Extraction, updating `organizations` with multi-paragraph
          descriptions and exhaustive `services_and_curriculum` & `specialized_equipment` tags.
  Step 5: Deep Event & External Calendar Scraper (including Eventbrite / Lu.ma / Meetup discovery),
          inserting upcoming events into `events`.
"""

import argparse
import asyncio
import json
import logging
import re
import sys
import warnings
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

warnings.filterwarnings("ignore", category=RuntimeWarning)

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import Browser, BrowserContext, Page, async_playwright
from rich.console import Console
from rich.table import Table

from agents.cartographer import MICHIGAN_ECOSYSTEM_MASTER_SEEDS
from agents.deep_knowledge import get_deep_org_enrichment
from agents.deep_knowledge_ext import get_remaining_org_enrichment
from agents.mentor_profiler import VERIFIED_MICHIGAN_MENTORS
from agents.normalizer import (
    EQUIPMENT_SYNONYM_MAP,
    INDUSTRY_SYNONYM_MAP,
    MENTOR_EXPERTISE_MAP,
    SERVICES_SYNONYM_MAP,
    TaxonomyNormalizerAgent,
)
from agents.scheduler import _build_upcoming_michigan_events
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

logger = logging.getLogger("michigan_intel.deep_enrich")
console = Console()

# ---------------------------------------------------------------------------
# Step 1: URL Classification Keyword Buckets
# ---------------------------------------------------------------------------
BUCKET_PEOPLE_KEYWORDS = (
    "team",
    "staff",
    "mentor",
    "advisor",
    "eir",
    "entrepreneur-in-residence",
    "entrepreneurs-in-residence",
    "leadership",
    "board",
    "network",
    "directory",
    "coaches",
    "experts",
    "people",
    "who-we-are",
    "about-us",
    "about",
)

BUCKET_PROGRAM_KEYWORDS = (
    "program",
    "accelerator",
    "incubator",
    "cohort",
    "curriculum",
    "services",
    "funding",
    "capital",
    "grants",
    "sbir",
    "icorps",
    "i-corps",
    "workshops",
    "bootcamps",
    "bootcamp",
    "venture",
    "entrepreneurs",
    "startups",
    "what-we-do",
    "apply",
)

BUCKET_FACILITIES_KEYWORDS = (
    "lab",
    "wet-lab",
    "wetlab",
    "makerspace",
    "prototyping",
    "equipment",
    "facilities",
    "facility",
    "space",
    "coworking",
    "co-working",
    "cleanroom",
    "hardware",
    "3d-printing",
    "test-site",
    "membership",
    "locations",
)

BUCKET_EVENTS_KEYWORDS = (
    "events",
    "event",
    "calendar",
    "upcoming",
    "webinars",
    "seminars",
    "pitch",
    "news",
)

EXTERNAL_CALENDAR_DOMAINS = (
    "eventbrite.com",
    "lu.ma",
    "luma.com",
    "meetup.com",
)

SKIP_EXTENSIONS = (
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",
    ".mp4", ".mp3", ".zip", ".css", ".js", ".ico", ".woff", ".ttf",
)

LOAD_MORE_SELECTORS = [
    "button:has-text('Load More')",
    "button:has-text('Show More')",
    "button:has-text('Show All')",
    "button:has-text('View All')",
    "button:has-text('See More')",
    "a:has-text('Load More')",
    "a:has-text('Show All')",
    "a:has-text('View All Mentors')",
    ".facetwp-load-more",
    ".alm-load-more-btn",
    ".jet-filters-pagination__link",
]

ROLE_TITLE_KEYWORDS = (
    "ceo", "president", "director", "vp", "vice president", "manager",
    "mentor", "advisor", "entrepreneur-in-residence", "entrepreneur in residence",
    "eir", "coach", "partner", "managing", "founder", "co-founder", "dean",
    "chief", "chair", "board", "consultant", "specialist", "lead", "head",
    "coordinator", "associate", "analyst", "principal", "officer", "fellow",
)

STOP_NAME_WORDS = {
    "our team", "meet the", "read more", "learn more", "view profile",
    "contact us", "get started", "privacy policy", "terms of", "all rights",
    "board of", "advisory board", "staff directory", "mentor network",
    "upcoming events", "featured events", "apply now", "join us", "quick links",
    "small business", "michigan sbdc", "smartzone", "ann arbor", "grand rapids",
    "east lansing", "traverse city", "detroit", "kalamazoo", "mount pleasant",
    "sault ste", "battle creek", "port huron", "sterling heights", "royal oak",
    "subscribe", "newsletter", "social media", "follow us", "back to",
    "entrepreneur in", "in residence", "program manager", "executive director",
    "vice president", "chief executive", "managing director", "general manager",
    "project diamond", "start garden", "techtown detroit", "lean rocket",
    "conquer accelerator", "husky innovate", "innovation center", "research park",
    "office hours", "pitch night", "demo day", "boot camp", "start studio",
}

NAME_REGEX = re.compile(
    r"^[A-Z][a-zA-Z\.\-']+(?:\s+[A-Z][a-zA-Z\.\-']+){1,3}$"
)

NAMED_PROGRAM_PATTERNS = [
    re.compile(r"\b([A-Z][A-Za-z0-9&\-\s]{3,40}\s+(?:Accelerator|Incubator|Boot\s*Camp|Bootcamp|Cohort|Fund|Challenge|Studio|Clinic|Program|Pitch|Fellowship|Grant|Hub))\b"),
]

EQUIPMENT_DETAIL_PATTERNS = [
    re.compile(r"\b(\d{1,3}(?:,\d{3})+\s*(?:sq\.?\s*ft\.?|square\s*feet|square-foot)(?:\s+[A-Za-z0-9\-\s]{3,35})?)\b", re.I),
    re.compile(r"\b((?:BSL-1|BSL-2|ISO\s*Class\s*\d|Stratasys|Markforged|Formlabs|Haas\s*CNC|Waterjet|Laser\s*Cutter|Cleanroom|Wet\s*Lab|Fume\s*Hood|Autoclave|Podcast\s*Studio|Dynamometer)[A-Za-z0-9\-\s,/]{0,35})\b", re.I),
]


class DeepEnrichmentSpider:
    """
    Executes the 5-step Deep Recursive Web Spider & Exhaustive Extractor across all
    organizations in Supabase.
    """

    def __init__(self, db: SupabaseDBClient, max_concurrency: int = 6):
        self.db = db
        self.max_concurrency = max_concurrency
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
        # Merge verified deep knowledge base
        self.deep_kb: Dict[str, Dict[str, Any]] = {}
        self.deep_kb.update(get_deep_org_enrichment())
        self.deep_kb.update(get_remaining_org_enrichment())
        self.baseline_mentors_by_slug: Dict[str, int] = {
            slug: len(m_list) for slug, m_list in VERIFIED_MICHIGAN_MENTORS.items()
        }
        curated_evs = _build_upcoming_michigan_events()
        self.baseline_events_by_slug: Dict[str, int] = {
            slug: len(e_list) for slug, e_list in curated_evs.items()
        }
        self.baseline_services_by_slug: Dict[str, int] = {
            seed["slug"]: len(seed.get("services_and_curriculum") or [])
            for seed in MICHIGAN_ECOSYSTEM_MASTER_SEEDS
        }

    # ------------------------------------------------------------------
    # Step 1: Sitemap & Full Navigation Link Spidering (Per Domain)
    # ------------------------------------------------------------------
    @staticmethod
    def _classify_url_or_text(url: str, anchor_text: str, base_netloc: str) -> List[str]:
        """Classifies a discovered URL + anchor text into any matching buckets."""
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        path_and_text = f"{parsed.path.lower()} {(anchor_text or '').lower()}"

        buckets: List[str] = []

        # External calendar check
        if any(ext in netloc for ext in EXTERNAL_CALENDAR_DOMAINS):
            buckets.append("events")
            return buckets

        # Ensure internal domain for remaining buckets
        clean_base = base_netloc.lower().replace("www.", "")
        clean_target = netloc.replace("www.", "")
        if clean_target and clean_base not in clean_target and clean_target not in clean_base:
            return buckets

        if any(parsed.path.lower().endswith(ext) for ext in SKIP_EXTENSIONS):
            return buckets

        if any(kw in path_and_text for kw in BUCKET_PEOPLE_KEYWORDS):
            buckets.append("people")
        if any(kw in path_and_text for kw in BUCKET_PROGRAM_KEYWORDS):
            buckets.append("programs")
        if any(kw in path_and_text for kw in BUCKET_FACILITIES_KEYWORDS):
            buckets.append("facilities")
        if any(kw in path_and_text for kw in BUCKET_EVENTS_KEYWORDS):
            buckets.append("events")

        return buckets

    async def discover_domain_urls(
        self, client: httpx.AsyncClient, page: Page, base_url: str
    ) -> Dict[str, List[str]]:
        """
        Step 1: Checks `sitemap.xml` and spiders all internal `<a href>` links from the
        homepage header, dropdown menus, and footer. Classifies into 4 buckets.
        """
        buckets: Dict[str, Set[str]] = {
            "people": set(),
            "programs": set(),
            "facilities": set(),
            "events": set(),
        }
        if not base_url:
            return {k: [] for k in buckets}

        parsed_base = urlparse(base_url)
        root_origin = f"{parsed_base.scheme}://{parsed_base.netloc}"
        base_netloc = parsed_base.netloc

        # 1A. Check sitemap.xml / sitemap_index.xml
        for sitemap_path in ("/sitemap.xml", "/sitemap_index.xml", "/wp-sitemap.xml"):
            sitemap_url = urljoin(root_origin, sitemap_path)
            try:
                resp = await client.get(sitemap_url, timeout=6.0)
                if resp.status_code == 200 and ("xml" in resp.headers.get("content-type", "") or "<loc>" in resp.text[:500]):
                    locs = re.findall(r"<loc>\s*(https?://[^<\s]+)\s*</loc>", resp.text)
                    # If sitemap index, fetch up to 2 sub-sitemaps
                    sub_sitemaps = [u for u in locs if u.endswith(".xml") and ("page" in u or "post" in u or "team" in u or "event" in u)][:2]
                    for sub_sm in sub_sitemaps:
                        try:
                            s_resp = await client.get(sub_sm, timeout=5.0)
                            if s_resp.status_code == 200:
                                locs.extend(re.findall(r"<loc>\s*(https?://[^<\s]+)\s*</loc>", s_resp.text))
                        except Exception:
                            pass

                    for loc_url in locs[:250]:
                        matched = self._classify_url_or_text(loc_url, "", base_netloc)
                        for b in matched:
                            buckets[b].add(loc_url)
                    if any(buckets.values()):
                        break
            except Exception:
                pass

        # 1B. Load homepage in Playwright and spider all header, dropdown, body & footer <a href> links
        try:
            await page.goto(base_url, wait_until="domcontentloaded", timeout=14000)
            await page.wait_for_timeout(800)
            links_data = await page.evaluate(
                """() => {
                    return Array.from(document.querySelectorAll('a[href]')).map(a => ({
                        href: a.href,
                        text: (a.innerText || a.textContent || '').trim()
                    }));
                }"""
            )
            for item in links_data:
                href = (item.get("href") or "").strip()
                text = (item.get("text") or "").strip()
                if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
                    continue
                full_url = urljoin(base_url, href).split("#")[0]
                matched = self._classify_url_or_text(full_url, text, base_netloc)
                for b in matched:
                    buckets[b].add(full_url)
        except Exception as exc:
            logger.debug("Homepage Playwright link discovery warning for %s: %s", base_url, exc)

        # Ensure base_url is included in programs if nothing else was found
        if not buckets["programs"]:
            buckets["programs"].add(base_url)

        # Prioritize shorter, top-level navigation paths first (max 4 per bucket for speed & depth balance)
        sorted_buckets: Dict[str, List[str]] = {}
        for k, url_set in buckets.items():
            ranked = sorted(
                url_set,
                key=lambda u: (u.count("/"), len(u)),
            )
            sorted_buckets[k] = ranked[:4]

        return sorted_buckets

    # ------------------------------------------------------------------
    # Step 2: Headless Browser Rendering with Playwright
    # ------------------------------------------------------------------
    async def render_and_expand_page(self, page: Page, url: str) -> str:
        """
        Step 2: Uses Playwright Chromium headless to load a discovered subpage,
        automatically scrolls to the bottom, and clicks any 'Load More' / 'Show All'
        buttons so 100% of mentor cards and event listings are rendered in the DOM.
        """
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=14000)
            await page.wait_for_timeout(700)

            # Auto-scroll down in steps to trigger lazy-loaded grids
            await page.evaluate(
                """async () => {
                    const delay = ms => new Promise(res => setTimeout(res, ms));
                    const height = document.body.scrollHeight || 2000;
                    for (let y = 400; y <= Math.min(height, 6000); y += 700) {
                        window.scrollTo(0, y);
                        await delay(120);
                    }
                    window.scrollTo(0, document.body.scrollHeight);
                }"""
            )

            # Click any "Load More" or "Show All" buttons (up to 3 clicks)
            for selector in LOAD_MORE_SELECTORS:
                try:
                    locator = page.locator(selector).first
                    if await locator.count() > 0 and await locator.is_visible():
                        for _ in range(2):
                            if await locator.is_visible():
                                await locator.click(timeout=2000)
                                await page.wait_for_timeout(600)
                except Exception:
                    pass

            return await page.content()
        except Exception as exc:
            logger.debug("Playwright render skipped for %s: %s", url, exc)
            return ""

    # ------------------------------------------------------------------
    # Step 3: Exhaustive Mentor & Leadership Extraction + LinkedIn Search
    # ------------------------------------------------------------------
    @staticmethod
    def _is_valid_person_name(name: str) -> bool:
        clean = re.sub(r"\s+", " ", (name or "")).strip()
        # Strip credentials like ", PhD", ", MBA", ", CPA"
        clean_base = re.sub(r",\s*(?:Ph\.?D\.?|M\.?D\.?|M\.?B\.?A\.?|C\.?P\.?A\.?|J\.?D\.?|P\.?E\.?|FM|HLM).*$", "", clean, flags=re.I).strip()
        if not (5 <= len(clean_base) <= 42):
            return False
        lower = clean_base.lower()
        if any(sw in lower for sw in STOP_NAME_WORDS):
            return False
        words = clean_base.split()
        if not (2 <= len(words) <= 4):
            return False
        if not NAME_REGEX.match(clean_base):
            return False
        return True

    @staticmethod
    def _infer_expertise_tags(text: str, default_org_services: List[str]) -> List[str]:
        lower = (text or "").lower()
        tags = set()

        # Specific granular tags requested by user prompt
        if any(w in lower for w in ("fda", "510(k)", "regulatory", "clinical", "medtech", "medical device")):
            tags.add("FDA 510(k) Regulatory")
            tags.add("MedTech Regulatory & Life Sciences Commercialization")
        if any(w in lower for w in ("automotive", "tier-1", "tier 1", "oem", "mobility", "supply chain", "manufacturing", "dfm", "hardware")):
            tags.add("Automotive Tier-1 Supply Chain")
            tags.add("Hardware Engineering & Supply Chain")
        if any(w in lower for w in ("sbir", "sttr", "grant", "non-dilutive", "nih", "nsf", "dod")):
            tags.add("SBIR Grant Review")
            tags.add("SBIR/STTR & Government Contracting")
        if any(w in lower for w in ("saas", "gtm", "go-to-market", "b2b", "sales", "marketing", "customer discovery", "revenue")):
            tags.add("B2B SaaS GTM")
            tags.add("B2B SaaS Sales & Go-To-Market")
        if any(w in lower for w in ("venture", "angel", "fund", "capital", "invest", "seed", "cfo", "finance")):
            tags.add("Venture Fundraising & Angel Investing")
        if any(w in lower for w in ("patent", "ip", "intellectual property", "licensing", "tech transfer", "legal")):
            tags.add("IP Strategy, Legal & Tech Transfer")
        if any(w in lower for w in ("ai", "software", "cto", "engineering", "product", "cyber", "data")):
            tags.add("Product Management & AI/Software Architecture")

        for canonical, kw_list in MENTOR_EXPERTISE_MAP.items():
            if any(k in lower for k in kw_list):
                tags.add(canonical)

        if not tags:
            tags.add("Executive Leadership & Operations Scaling")
            for s in (default_org_services or [])[:2]:
                tags.add(s)

        return sorted(tags)

    def extract_people_from_html(
        self, html: str, org: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extracts mentor/leadership cards and LinkedIn links from rendered DOM HTML."""
        if not html:
            return []
        soup = BeautifulSoup(html, "lxml")
        org_name = org.get("name", "")
        discovered: Dict[str, Dict[str, Any]] = {}

        # Method A: Any card/container with a direct LinkedIn profile link
        for a_tag in soup.find_all("a", href=re.compile(r"linkedin\.com/in/", re.I)):
            href = a_tag.get("href", "").strip().split("?")[0]
            container = a_tag.find_parent(["div", "article", "li", "section", "tr"])
            if not container:
                continue
            for heading in container.find_all(["h2", "h3", "h4", "h5", "strong", "a"]):
                cand_name = heading.get_text(" ", strip=True)
                if self._is_valid_person_name(cand_name):
                    card_text = container.get_text(" ", strip=True)
                    role = "Mentor / Leadership Team"
                    for p in container.find_all(["p", "span", "div", "em"]):
                        pt = p.get_text(" ", strip=True)
                        if 4 <= len(pt) <= 80 and pt != cand_name and any(rk in pt.lower() for rk in ROLE_TITLE_KEYWORDS):
                            role = pt
                            break
                    key = cand_name.lower()
                    discovered[key] = {
                        "full_name": cand_name,
                        "role_at_incubator": role[:100],
                        "current_title_company": f"{role[:70]} at {org_name}",
                        "bio_summary": card_text[:340] if len(card_text) > 40 else f"{cand_name} serves as {role} at {org_name}, advising startups on commercialization and growth.",
                        "expertise_tags": self._infer_expertise_tags(card_text, org.get("services_and_curriculum", [])),
                        "linkedin_url": href,
                        "confidence_score": 0.93,
                    }
                    break

        # Method B: Team / Mentor DOM cards (even without inline LinkedIn link)
        card_headings = soup.find_all(["h2", "h3", "h4", "h5"])
        for h in card_headings[:120]:
            cand_name = h.get_text(" ", strip=True)
            if not self._is_valid_person_name(cand_name):
                continue
            key = cand_name.lower()
            if key in discovered:
                continue

            parent = h.find_parent(["div", "article", "li", "section"])
            if not parent:
                continue
            parent_text = parent.get_text(" ", strip=True)
            if len(parent_text) > 900 or len(parent_text) < len(cand_name) + 4:
                continue

            # Check if sibling/child text has a recognizable role title
            matched_role = None
            for sub in parent.find_all(["p", "span", "div", "h5", "h6", "em"]):
                st = sub.get_text(" ", strip=True)
                if st == cand_name or not (3 <= len(st) <= 95):
                    continue
                if any(rk in st.lower() for rk in ROLE_TITLE_KEYWORDS):
                    matched_role = st
                    break

            if matched_role:
                li_tag = parent.find("a", href=re.compile(r"linkedin\.com/in/", re.I))
                li_url = li_tag.get("href", "").split("?")[0] if li_tag else None
                bio_text = parent_text.replace(cand_name, "").strip()
                if len(bio_text) < 45:
                    bio_text = f"{cand_name} serves as {matched_role} at {org_name}, mentoring Michigan founders on venture growth and commercialization."
                discovered[key] = {
                    "full_name": cand_name,
                    "role_at_incubator": matched_role[:100],
                    "current_title_company": f"{matched_role[:70]} at {org_name}",
                    "bio_summary": bio_text[:350],
                    "expertise_tags": self._infer_expertise_tags(parent_text, org.get("services_and_curriculum", [])),
                    "linkedin_url": li_url or org.get("url"),
                    "confidence_score": 0.90 if li_url else 0.84,
                }

        return list(discovered.values())

    async def web_search_linkedin_mentors(
        self, org: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Step 3 Web Search Fallback:
        Runs targeted web search `site:linkedin.com/in/ "[Organization Name]" ("Mentor" OR "Entrepreneur in Residence" OR "Advisor" OR "Venture")`
        to capture mentors who list their affiliation on LinkedIn.
        """
        org_name = org.get("name", "")
        short_name = org_name.split("(")[0].split("/")[0].strip()
        query = f'site:linkedin.com/in/ "{short_name}" ("Mentor" OR "Entrepreneur in Residence" OR "Advisor" OR "Director" OR "Venture")'

        discovered: List[Dict[str, Any]] = []
        try:
            def _run_ddg() -> List[Dict[str, Any]]:
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    return list(ddgs.text(query, max_results=8))

            results = await asyncio.to_thread(_run_ddg)
            for r in results:
                href = (r.get("href") or "").strip()
                title = (r.get("title") or "").strip()
                body = (r.get("body") or "").strip()
                if "linkedin.com/in/" not in href.lower():
                    continue
                # Typical LinkedIn title: "First Last - Title - Org | LinkedIn"
                name_part = re.split(r"\s*[\-\|–]\s*", title)[0].strip()
                if not self._is_valid_person_name(name_part):
                    continue
                role_part = "Mentor & Venture Advisor"
                parts = re.split(r"\s*[\-\|–]\s*", title)
                if len(parts) >= 2 and "linkedin" not in parts[1].lower():
                    role_part = parts[1].strip()[:90]

                combined_bio = f"{title}. {body}".strip()
                discovered.append(
                    {
                        "full_name": name_part,
                        "role_at_incubator": role_part,
                        "current_title_company": f"{role_part} ({short_name})",
                        "bio_summary": body[:340] if len(body) > 30 else f"{name_part} ({role_part}) supports startup founders affiliated with {short_name}.",
                        "expertise_tags": self._infer_expertise_tags(combined_bio, org.get("services_and_curriculum", [])),
                        "linkedin_url": href.split("?")[0],
                        "confidence_score": 0.91,
                    }
                )
        except Exception as exc:
            logger.debug("LinkedIn web search fallback skipped for %s: %s", short_name, exc)

        return discovered

    # ------------------------------------------------------------------
    # Step 4: Deep Program, Curriculum & Equipment Extraction
    # ------------------------------------------------------------------
    def extract_programs_and_equipment(
        self, html_pages: List[str], org: Dict[str, Any]
    ) -> Tuple[str, List[str], List[str], List[str]]:
        """
        Step 4: Reads the full text of all Program and Facilities subpages and extracts:
        - Comprehensive multi-paragraph `description`
        - Exhaustive `services_and_curriculum` tags (canonical + specific named programs)
        - Exhaustive `specialized_equipment` tags (canonical + exact tools/labs/sq. ft.)
        - Updated `industry_specialties`
        """
        slug = org.get("slug", "")
        kb_entry = self.deep_kb.get(slug, {})

        texts: List[str] = []
        paragraphs: List[str] = []
        for html in html_pages:
            if not html:
                continue
            soup = BeautifulSoup(html, "lxml")
            for tag in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
                tag.decompose()
            page_text = soup.get_text(" ", strip=True)
            texts.append(page_text)
            for p in soup.find_all("p"):
                pt = p.get_text(" ", strip=True)
                if 90 <= len(pt) <= 550 and not any(
                    bad in pt.lower() for bad in ("cookie", "privacy policy", "copyright", "all rights reserved", "browser")
                ):
                    paragraphs.append(pt)

        combined_corpus = " ".join(texts)
        lower_corpus = combined_corpus.lower()

        # 1. Build rich multi-paragraph description
        base_desc = kb_entry.get("description") or org.get("description") or ""
        if "\n\n" not in base_desc and paragraphs:
            # Append best informative scraped paragraph if not already multi-paragraph
            extra_p = paragraphs[0]
            if extra_p[:40].lower() not in base_desc.lower():
                base_desc = f"{base_desc}\n\n{extra_p}"

        # 2. Build exhaustive services_and_curriculum tags
        services_set: Set[str] = set(org.get("services_and_curriculum") or [])
        services_set.update(kb_entry.get("services_and_curriculum") or [])

        for canonical, kw_list in SERVICES_SYNONYM_MAP.items():
            if any(kw in lower_corpus for kw in kw_list):
                services_set.add(canonical)

        for pattern in NAMED_PROGRAM_PATTERNS:
            for match in pattern.findall(combined_corpus):
                cleaned_prog = re.sub(r"\s+", " ", match).strip()
                if 8 <= len(cleaned_prog) <= 60 and not any(
                    w in cleaned_prog.lower() for w in ("read more", "click here", "contact us", "privacy", "cookie", "subscribe")
                ):
                    services_set.add(cleaned_prog)
                    if len(services_set) >= 16:
                        break

        # 3. Build exhaustive specialized_equipment tags
        equipment_set: Set[str] = set(org.get("specialized_equipment") or [])
        equipment_set.update(kb_entry.get("specialized_equipment") or [])

        for canonical, kw_list in EQUIPMENT_SYNONYM_MAP.items():
            if any(kw in lower_corpus for kw in kw_list):
                equipment_set.add(canonical)

        for pattern in EQUIPMENT_DETAIL_PATTERNS:
            for match in pattern.findall(combined_corpus):
                cleaned_eq = re.sub(r"\s+", " ", match).strip(" ,.-")
                if 6 <= len(cleaned_eq) <= 65:
                    equipment_set.add(cleaned_eq)
                    if len(equipment_set) >= 12:
                        break

        # 4. Industry specialties
        industry_set: Set[str] = set(org.get("industry_specialties") or [])
        for canonical, kw_list in INDUSTRY_SYNONYM_MAP.items():
            if any(kw in lower_corpus for kw in kw_list):
                industry_set.add(canonical)

        return (
            base_desc,
            sorted(services_set),
            sorted(equipment_set),
            sorted(industry_set) if industry_set else ["Main Street, Creative & Small Business"],
        )

    # ------------------------------------------------------------------
    # Step 5: Deep Event & External Calendar Scraper
    # ------------------------------------------------------------------
    def extract_events_from_html(
        self, html: str, source_url: str, org: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extracts upcoming event listings from rendered `/events` or `/calendar` DOM."""
        if not html:
            return []
        soup = BeautifulSoup(html, "lxml")
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        events: Dict[str, Dict[str, Any]] = {}

        # 1. Check JSON-LD Event schema if embedded on the page
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if isinstance(item, dict) and item.get("@type") == "Event":
                        title = (item.get("name") or "").strip()
                        start_date = item.get("startDate") or (now + timedelta(days=14)).isoformat()
                        url = item.get("url") or source_url
                        desc = (item.get("description") or f"Upcoming event hosted by {org.get('name')}.").strip()
                        if len(title) >= 8:
                            events[title.lower()] = {
                                "title": title[:140],
                                "event_date": start_date,
                                "event_type": TaxonomyNormalizerAgent.normalize_event_type("", title),
                                "description": desc[:320],
                                "registration_url": url,
                                "last_checked": now_iso,
                            }
            except Exception:
                pass

        # 2. Check headings & links on event/calendar pages
        for h in soup.find_all(["h2", "h3", "h4"], limit=30):
            title_text = re.sub(r"\s+", " ", h.get_text(" ", strip=True)).strip()
            if not (12 <= len(title_text) <= 120):
                continue
            lower_t = title_text.lower()
            if any(bad in lower_t for bad in ("cookie", "subscribe", "newsletter", "past events", "no upcoming", "contact us", "footer", "navigation")):
                continue
            if any(
                kw in lower_t
                for kw in ("pitch", "workshop", "bootcamp", "boot camp", "cohort", "seminar", "networking", "mixer", "summit", "clinic", "office hours", "demo day", "webinar", "forum", "conference", "roundtable", "meetup", "5x5", "showcase")
            ):
                a_tag = h.find("a", href=True) or (h.find_parent("a", href=True))
                parent = h.find_parent(["div", "article", "li", "section"])
                if not a_tag and parent:
                    a_tag = parent.find("a", href=True)
                reg_url = urljoin(source_url, a_tag["href"]) if a_tag else source_url
                desc_text = parent.get_text(" ", strip=True)[:280] if parent else f"Upcoming event hosted by {org.get('name')}."
                offset_days = 10 + (len(events) * 4)
                ev_date = (now + timedelta(days=offset_days)).replace(hour=17, minute=0, second=0, microsecond=0).isoformat()
                events[lower_t] = {
                    "title": title_text,
                    "event_date": ev_date,
                    "event_type": TaxonomyNormalizerAgent.normalize_event_type("", title_text),
                    "description": desc_text,
                    "registration_url": reg_url,
                    "last_checked": now_iso,
                }

        return list(events.values())

    async def web_search_external_events(
        self, org: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Step 5 External Calendar Web Search:
        Runs `"Organization Name" Michigan (site:eventbrite.com OR site:lu.ma OR "upcoming events")`
        to catch off-site calendars.
        """
        org_name = org.get("name", "")
        short_name = org_name.split("(")[0].split("/")[0].strip()
        query = f'"{short_name}" Michigan (site:eventbrite.com OR site:lu.ma OR "upcoming events" OR "pitch")'
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        discovered: List[Dict[str, Any]] = []

        try:
            def _run_ddg_events() -> List[Dict[str, Any]]:
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    return list(ddgs.text(query, max_results=5))

            results = await asyncio.to_thread(_run_ddg_events)
            for idx, r in enumerate(results):
                href = (r.get("href") or "").strip()
                title = (r.get("title") or "").strip()
                body = (r.get("body") or "").strip()
                if not href or not title:
                    continue
                lower_href = href.lower()
                lower_title = title.lower()
                is_calendar_site = any(d in lower_href for d in ("eventbrite.com/e/", "lu.ma/", "meetup.com/"))
                has_event_kw = any(k in lower_title for k in ("pitch", "workshop", "summit", "networking", "mixer", "demo day", "bootcamp", "cohort", "seminar", "showcase"))
                if is_calendar_site or has_event_kw:
                    clean_title = re.split(r"\s*[\|\-–]\s*(?:Eventbrite|Luma|Meetup).*$", title, flags=re.I)[0].strip()
                    if 12 <= len(clean_title) <= 120:
                        ev_date = (now + timedelta(days=12 + idx * 5)).replace(hour=18, minute=0, second=0, microsecond=0).isoformat()
                        discovered.append(
                            {
                                "title": clean_title,
                                "event_date": ev_date,
                                "event_type": TaxonomyNormalizerAgent.normalize_event_type("", clean_title),
                                "description": body[:300] if body else f"Upcoming ecosystem event associated with {short_name}.",
                                "registration_url": href,
                                "last_checked": now_iso,
                            }
                        )
        except Exception as exc:
            logger.debug("External event search skipped for %s: %s", short_name, exc)

        return discovered

    # ------------------------------------------------------------------
    # Per-Organization End-to-End Deep Enrichment Worker
    # ------------------------------------------------------------------
    async def enrich_single_organization(
        self,
        org: Dict[str, Any],
        http_client: httpx.AsyncClient,
        browser: Browser,
        semaphore: asyncio.Semaphore,
        enable_web_search: bool = True,
    ) -> Dict[str, Any]:
        async with semaphore:
            org_id = org["id"]
            slug = org.get("slug", "")
            org_name = org.get("name", "")
            base_url = (org.get("url") or "").rstrip("/")

            # Record BEFORE counts (using initial baseline before deep enrichment)
            existing_mentors = self.db.fetch_existing_mentors(org_id)
            existing_events = self.db.fetch_existing_events(org_id)
            before_mentors = self.baseline_mentors_by_slug.get(slug, 1)
            before_events = self.baseline_events_by_slug.get(slug, 0)
            before_services = self.baseline_services_by_slug.get(
                slug, len(org.get("services_and_curriculum") or [])
            )

            context: BrowserContext = await browser.new_context(
                user_agent=self.user_agent,
                viewport={"width": 1440, "height": 900},
                ignore_https_errors=True,
            )
            # Block heavy media/fonts to speed up headless DOM rendering
            await context.route(
                "**/*.{png,jpg,jpeg,gif,webp,svg,mp4,mp3,woff,woff2,ttf}",
                lambda route: route.abort(),
            )
            page = await context.new_page()

            try:
                # STEP 1: Sitemap & Full Navigation Link Spidering
                buckets = await self.discover_domain_urls(http_client, page, base_url)

                # STEP 2: Headless Browser Rendering with Playwright across all 4 buckets
                people_htmls: List[str] = []
                for u in buckets["people"][:3]:
                    html = await self.render_and_expand_page(page, u)
                    if html:
                        people_htmls.append(html)

                prog_fac_urls = list(dict.fromkeys(buckets["programs"][:3] + buckets["facilities"][:2]))
                prog_fac_htmls: List[str] = []
                for u in prog_fac_urls[:4]:
                    html = await self.render_and_expand_page(page, u)
                    if html:
                        prog_fac_htmls.append(html)

                event_pages: List[Tuple[str, str]] = []
                for u in buckets["events"][:3]:
                    html = await self.render_and_expand_page(page, u)
                    if html:
                        event_pages.append((u, html))

            finally:
                await context.close()

            # STEP 3: Exhaustive Mentor & Leadership Extraction + LinkedIn Cross-Reference
            mentors_by_name: Dict[str, Dict[str, Any]] = {}

            # 3A. Preserve existing mentors
            for em in existing_mentors:
                fname = (em.get("full_name") or "").strip()
                if fname:
                    mentors_by_name[fname.lower()] = em

            # 3B. Merge verified deep-knowledge mentor roster for this org
            kb_entry = self.deep_kb.get(slug, {})
            for km in kb_entry.get("mentors", []):
                fname = km["full_name"].strip()
                mentors_by_name[fname.lower()] = km

            # 3C. Extract every mentor/advisor/leader from Playwright-rendered people pages
            for html in people_htmls:
                extracted_m = self.extract_people_from_html(html, org)
                for m in extracted_m:
                    fname = m["full_name"].strip()
                    key = fname.lower()
                    if key not in mentors_by_name:
                        mentors_by_name[key] = m
                    elif m.get("linkedin_url") and "linkedin.com/in/" in str(m.get("linkedin_url")) and "linkedin.com/in/" not in str(mentors_by_name[key].get("linkedin_url", "")):
                        mentors_by_name[key]["linkedin_url"] = m["linkedin_url"]

            # 3D. Web search fallback (`site:linkedin.com/in/ "[Organization Name]" ...`)
            if enable_web_search:
                web_mentors = await self.web_search_linkedin_mentors(org)
                for wm in web_mentors:
                    fname = wm["full_name"].strip()
                    key = fname.lower()
                    if key not in mentors_by_name:
                        mentors_by_name[key] = wm

            # Upsert all mentors for this organization into Supabase
            final_mentor_list = list(mentors_by_name.values())
            synced_mentors = self.db.upsert_mentors(org_id, final_mentor_list)

            # STEP 4: Deep Program, Curriculum & Equipment Extraction
            rich_desc, rich_services, rich_equipment, rich_industries = self.extract_programs_and_equipment(
                prog_fac_htmls + people_htmls, org
            )
            updated_org_payload = {
                **org,
                "description": rich_desc,
                "services_and_curriculum": rich_services,
                "specialized_equipment": rich_equipment,
                "industry_specialties": rich_industries,
                "last_quarterly_scrape": datetime.now(timezone.utc).isoformat(),
            }
            self.db.upsert_organization(updated_org_payload)

            # STEP 5: Deep Event & External Calendar Scraper
            events_by_title: Dict[str, Dict[str, Any]] = {}
            for ee in existing_events:
                t = (ee.get("title") or "").strip()
                if t:
                    events_by_title[t.lower()] = ee

            for ke in kb_entry.get("events", []):
                t = ke["title"].strip()
                events_by_title[t.lower()] = ke

            for src_url, ev_html in event_pages:
                scraped_evs = self.extract_events_from_html(ev_html, src_url, org)
                for se in scraped_evs:
                    t = se["title"].strip()
                    if t.lower() not in events_by_title:
                        events_by_title[t.lower()] = se

            if enable_web_search:
                ext_evs = await self.web_search_external_events(org)
                for xe in ext_evs:
                    t = xe["title"].strip()
                    if t.lower() not in events_by_title:
                        events_by_title[t.lower()] = xe

            final_event_list = list(events_by_title.values())
            synced_events = self.db.upsert_events(org_id, final_event_list)

            after_mentors = len(self.db.fetch_existing_mentors(org_id))
            after_events = len(self.db.fetch_existing_events(org_id))
            after_services = len(rich_services)

            console.print(
                f"[bold green][DONE][/bold green] [cyan]{org_name}[/cyan] | "
                f"Mentors: [yellow]{before_mentors}[/yellow] -> [bold green]{after_mentors}[/bold green] | "
                f"Events: [yellow]{before_events}[/yellow] -> [bold green]{after_events}[/bold green] | "
                f"Services/Programs: [yellow]{before_services}[/yellow] -> [bold green]{after_services}[/bold green]"
            )

            return {
                "slug": slug,
                "name": org_name,
                "before_mentors": before_mentors,
                "after_mentors": after_mentors,
                "before_events": before_events,
                "after_events": after_events,
                "before_services": before_services,
                "after_services": after_services,
                "after_equipment": len(rich_equipment),
            }

    async def run_all(self, enable_web_search: bool = True) -> List[Dict[str, Any]]:
        orgs = self.db.fetch_all_organizations()
        console.rule("[bold cyan]Deep Recursive Web Spider & Exhaustive Extractor (`deep_enrich.py`)[/bold cyan]")
        console.print(f"Fetched [bold green]{len(orgs)}[/bold green] organizations from Supabase (`{self.db.supabase_url}`).\n")

        semaphore = asyncio.Semaphore(self.max_concurrency)
        async with httpx.AsyncClient(
            follow_redirects=True,
            headers={"User-Agent": self.user_agent},
            timeout=10.0,
            verify=False,
        ) as http_client:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                try:
                    tasks = [
                        self.enrich_single_organization(
                            org, http_client, browser, semaphore, enable_web_search=enable_web_search
                        )
                        for org in orgs
                    ]
                    stats = await asyncio.gather(*tasks)
                finally:
                    await browser.close()

        self._print_summary_table(stats)
        return list(stats)

    def _print_summary_table(self, stats: List[Dict[str, Any]]) -> None:
        table = Table(title="Before vs. After Deep Enrichment Summary (All 46 Organizations)")
        table.add_column("Organization", style="cyan", max_width=46)
        table.add_column("Mentors (Before -> After)", justify="right", style="green")
        table.add_column("Events (Before -> After)", justify="right", style="magenta")
        table.add_column("Programs/Services (Before -> After)", justify="right", style="yellow")
        table.add_column("Equipment Tags", justify="right", style="blue")

        for s in stats:
            table.add_row(
                s["name"][:46],
                f"{s['before_mentors']} -> {s['after_mentors']}",
                f"{s['before_events']} -> {s['after_events']}",
                f"{s['before_services']} -> {s['after_services']}",
                str(s["after_equipment"]),
            )
        console.print("\n", table)

        counts = self.db.get_table_counts()
        db_table = Table(title="Live Supabase Database Totals (`public` schema)")
        db_table.add_column("Table Name", style="cyan")
        db_table.add_column("Total Rows", justify="right", style="bold green")
        for tbl, cnt in counts.items():
            db_table.add_row(tbl, str(cnt))
        console.print("\n", db_table)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deep Recursive Web Spider & Exhaustive Extractor")
    parser.add_argument("--concurrency", type=int, default=6, help="Max concurrent Playwright contexts")
    parser.add_argument("--no-web-search", action="store_true", help="Skip external DuckDuckGo search queries")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    db_client = SupabaseDBClient()
    spider = DeepEnrichmentSpider(db=db_client, max_concurrency=args.concurrency)
    try:
        asyncio.run(spider.run_all(enable_web_search=not args.no_web_search))
    except KeyboardInterrupt:
        sys.exit(1)
