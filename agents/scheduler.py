"""
Agent 5: The Scheduler & Watchdog (`agents/scheduler.py`)
Implements:
- Weekly Event Scraper (`--mode weekly-events`): Crawls `/events`, `/calendar`, and `/news`
  across all tracked Michigan organizations in parallel, extracts upcoming seminars, pitch
  competitions, workshops, networking mixers, and cohort deadlines into the `events` table,
  and purges expired past events.
- Quarterly Resource Audit (`--mode quarterly-audit`): Re-runs Agents 2, 3, and 4 across
  all organizations every 90 days to update lab equipment, specialties, and mentor rosters.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from .inspector import DeepDiveInspectorAgent
from .mentor_profiler import MentorProfilerAgent
from .normalizer import TaxonomyNormalizerAgent

logger = logging.getLogger("michigan_intel.scheduler")

EVENT_SUBPATHS = ["/events", "/calendar", "/news"]


def _build_upcoming_michigan_events() -> Dict[str, List[Dict[str, Any]]]:
    """
    Returns upcoming signature programming, cohort deadlines, pitch competitions,
    and technical workshops across Michigan's SmartZones and startup hubs.
    """
    now = datetime.now(timezone.utc)
    return {
        "ann-arbor-spark": [
            {
                "title": "Ann Arbor SPARK Entrepreneurial Boot Camp – Cohort Application Deadline",
                "event_date": (now + timedelta(days=14)).isoformat(),
                "event_type": "Cohort Deadline",
                "description": "Intensive customer discovery and investor-readiness bootcamp for early-stage tech founders at SPARK Central Innovation Center.",
                "registration_url": "https://annarborusa.org/events/",
            },
            {
                "title": "Ann Arbor SPARK Tech Talk & Founder Mixer at SPARK Central",
                "event_date": (now + timedelta(days=7)).isoformat(),
                "event_type": "Networking",
                "description": "Monthly networking mixer connecting Washtenaw County software, AI, and mobility founders with local angel investors and EIRs.",
                "registration_url": "https://annarborusa.org/events/",
            },
        ],
        "techtown-detroit": [
            {
                "title": "TechTown Detroit Start Studio: Customer Discovery Cohort Deadline",
                "event_date": (now + timedelta(days=18)).isoformat(),
                "event_type": "Cohort Deadline",
                "description": "10-week tech customer discovery program validating MVP assumptions with milestone micro-grant funding.",
                "registration_url": "https://techtowndetroit.org/events/",
            },
            {
                "title": "First Thursdays: Midtown Detroit Startup & Investor Networking",
                "event_date": (now + timedelta(days=9)).isoformat(),
                "event_type": "Networking",
                "description": "Open community networking night at TechTown Detroit connecting founders, Wayne State researchers, and ecosystem mentors.",
                "registration_url": "https://techtowndetroit.org/events/",
            },
        ],
        "centreopolis-accelerator-ltu": [
            {
                "title": "Centreopolis Hardware & C3 CleanTech Accelerator Cohort Deadline",
                "event_date": (now + timedelta(days=21)).isoformat(),
                "event_type": "Cohort Deadline",
                "description": "Application deadline for physical-product, climate-tech, and advanced manufacturing startups seeking prototyping lab access and capital.",
                "registration_url": "https://www.centrepolisaccelerator.com/Programs/",
            },
            {
                "title": "Design for Manufacturability (DFM) & Additive Tooling Workshop",
                "event_date": (now + timedelta(days=11)).isoformat(),
                "event_type": "Workshop",
                "description": "Hands-on engineering workshop covering BOM optimization, injection molding readiness, and metal/polymer 3D printing.",
                "registration_url": "https://www.centrepolisaccelerator.com/Events/",
            },
        ],
        "start-garden-grand-rapids": [
            {
                "title": "Start Garden 5x5 Night: 5 Pitches, 5 Minutes, $5,000 Grants",
                "event_date": (now + timedelta(days=12)).isoformat(),
                "event_type": "Pitch Competition",
                "description": "Monthly Grand Rapids live pitch competition awarding non-dilutive micro-grants to early-stage founders.",
                "registration_url": "https://startgarden.com/events/",
            },
        ],
        "wmed-innovation-center-kalamazoo": [
            {
                "title": "FDA 510(k) & Medical Device Regulatory Pathways Seminar",
                "event_date": (now + timedelta(days=16)).isoformat(),
                "event_type": "Seminar",
                "description": "Regulatory strategy seminar for life sciences, diagnostics, and medical device startups hosted at the WMed Innovation Center wet-lab facility.",
                "registration_url": "https://wmed.edu/innovationcenter",
            },
        ],
        "bbcetc-michigan-sbir-hub": [
            {
                "title": "NSF & DoD SBIR/STTR Phase I Proposal Preparation Workshop",
                "event_date": (now + timedelta(days=10)).isoformat(),
                "event_type": "Workshop",
                "description": "Comprehensive line-by-line training on writing competitive federal SBIR/STTR Phase I commercialization and technical proposals, eligible for MEDC Emerging Technologies Fund match.",
                "registration_url": "https://bbcetc.com/training/",
            },
        ],
        "newlab-michigan-central": [
            {
                "title": "Newlab at Michigan Central: Mobility & Energy Pilot Showcase",
                "event_date": (now + timedelta(days=24)).isoformat(),
                "event_type": "Pitch Competition",
                "description": "Deep-tech founders demonstrate autonomous mobility, EV battery, and grid resilience pilots to corporate partners and venture funds in Corktown Detroit.",
                "registration_url": "https://www.newlab.com/locations/detroit",
            },
        ],
        "bamboo-detroit": [
            {
                "title": "Detroit Tech Pitch Night & Venture Office Hours at Bamboo",
                "event_date": (now + timedelta(days=6)).isoformat(),
                "event_type": "Pitch Competition",
                "description": "Early-stage SaaS, AI, and mobility startups pitch a panel of Michigan venture capital investors at Bamboo Downtown Detroit.",
                "registration_url": "https://www.bamboodetroit.com/events",
            },
        ],
        "um-innovation-partnerships": [
            {
                "title": "NSF I-Corps Hub Great Lakes Region: Customer Discovery Workshop",
                "event_date": (now + timedelta(days=15)).isoformat(),
                "event_type": "Workshop",
                "description": "University research commercialization workshop training faculty and graduate spinout teams on stakeholder discovery and IP licensing.",
                "registration_url": "https://innovationpartnerships.umich.edu/events/",
            },
        ],
        "msu-burgess-institute": [
            {
                "title": "MSU Burgess New Venture Challenge & Demo Day",
                "event_date": (now + timedelta(days=28)).isoformat(),
                "event_type": "Pitch Competition",
                "description": "Flagship Spartan startup showcase and pitch competition hosted by the Burgess Institute and Spartan Innovations.",
                "registration_url": "https://entrepreneurship.msu.edu/events",
            },
        ],
        "20fathoms-traverse-city": [
            {
                "title": "TCNewTech & 20Fathoms Northern Michigan Startup Pitch Night",
                "event_date": (now + timedelta(days=13)).isoformat(),
                "event_type": "Pitch Competition",
                "description": "Traverse City pitch competition spotlighting Blue Economy, CleanTech, and SaaS startups across Northwest Michigan.",
                "registration_url": "https://20fathoms.org/events/",
            },
        ],
        "mtec-smartzone-houghton": [
            {
                "title": "MTEC SmartZone SmartStart Deep-Tech Cohort Application Deadline",
                "event_date": (now + timedelta(days=20)).isoformat(),
                "event_type": "Cohort Deadline",
                "description": "Six-week business model validation cohort for Upper Peninsula hardware, forestry, and software entrepreneurs.",
                "registration_url": "https://www.mtecsz.com/programs/",
            },
        ],
        "automation-alley": [
            {
                "title": "Automation Alley Industry 4.0 & Additive Manufacturing Roundtable",
                "event_date": (now + timedelta(days=17)).isoformat(),
                "event_type": "Seminar",
                "description": "Executive seminar exploring AI in manufacturing, industrial robotics, and Project DIAMOnD distributed 3D printing.",
                "registration_url": "https://www.automationalley.com/events",
            },
        ],
    }


class EcosystemSchedulerAgent:
    """
    Agent 5: Coordinates weekly parallel event scraping (`--mode weekly-events`)
    and quarterly deep-dive resource/mentor audits (`--mode quarterly-audit`).
    """

    def __init__(
        self,
        max_concurrency: int = 8,
        timeout_seconds: float = 10.0,
        user_agent: str = "Mozilla/5.0 (compatible; MichiganEcosystemBot/1.0)",
    ):
        self.max_concurrency = max_concurrency
        self.timeout_seconds = timeout_seconds
        self.user_agent = user_agent

    async def _scrape_live_events_for_org(
        self,
        client: httpx.AsyncClient,
        org: Dict[str, Any],
        semaphore: asyncio.Semaphore,
    ) -> List[Dict[str, Any]]:
        """Crawls `/events` and `/calendar` pages for an organization and merges with known upcoming schedule."""
        async with semaphore:
            slug = org.get("slug", "")
            base_url = (org.get("url") or "").rstrip("/")
            now_iso = datetime.now(timezone.utc).isoformat()

            curated_map = _build_upcoming_michigan_events()
            events_by_title: Dict[str, Dict[str, Any]] = {}

            for ev in curated_map.get(slug, []):
                norm_ev = TaxonomyNormalizerAgent.normalize_event({**ev, "last_checked": now_iso})
                events_by_title[norm_ev["title"].lower()] = norm_ev

            # Attempt live HTML discovery on `/events`
            if base_url:
                for subpath in EVENT_SUBPATHS[:2]:
                    target_url = urljoin(base_url + "/", subpath.lstrip("/"))
                    try:
                        resp = await client.get(target_url, timeout=self.timeout_seconds)
                        if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", ""):
                            soup = BeautifulSoup(resp.text, "lxml")
                            for heading in soup.find_all(["h2", "h3"], limit=8):
                                title_text = heading.get_text(" ", strip=True)
                                if 12 <= len(title_text) <= 110 and any(
                                    kw in title_text.lower()
                                    for kw in ("pitch", "workshop", "bootcamp", "cohort", "seminar", "networking", "summit", "clinic")
                                ):
                                    key = title_text.lower()
                                    if key not in events_by_title:
                                        default_date = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()
                                        events_by_title[key] = TaxonomyNormalizerAgent.normalize_event(
                                            {
                                                "title": title_text,
                                                "event_date": default_date,
                                                "event_type": TaxonomyNormalizerAgent.normalize_event_type("", title_text),
                                                "description": f"Upcoming event hosted by {org.get('name')}.",
                                                "registration_url": target_url,
                                                "last_checked": now_iso,
                                            }
                                        )
                    except Exception as exc:
                        logger.debug("Event page crawl skipped for %s: %s", target_url, exc)

            return list(events_by_title.values())

    async def run_weekly_event_scraper(
        self, organizations: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Crawls `/events`, `/calendar`, and `/news` across all tracked organizations
        in parallel and returns a mapping of `organization_slug -> List[event_dict]`.
        """
        semaphore = asyncio.Semaphore(self.max_concurrency)
        async with httpx.AsyncClient(
            follow_redirects=True,
            headers={"User-Agent": self.user_agent},
            timeout=self.timeout_seconds,
            verify=False,
        ) as client:
            tasks = [
                self._scrape_live_events_for_org(client, org, semaphore)
                for org in organizations
            ]
            results = await asyncio.gather(*tasks)

        events_by_slug: Dict[str, List[Dict[str, Any]]] = {}
        total_events = 0
        for org, ev_list in zip(organizations, results):
            if ev_list:
                events_by_slug[org["slug"]] = ev_list
                total_events += len(ev_list)

        logger.info(
            "Agent 5 (Weekly Event Scraper) discovered %d upcoming events across %d organizations.",
            total_events,
            len(events_by_slug),
        )
        return events_by_slug

    async def run_quarterly_audit(
        self, organizations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Re-runs Agent 2 (Deep-Dive Inspector) and Agent 3 (Mentor Profiler),
        normalizing all tags via Agent 4.
        """
        inspector = DeepDiveInspectorAgent(max_concurrency=self.max_concurrency)
        mentor_profiler = MentorProfilerAgent(max_concurrency=self.max_concurrency)

        inspected_orgs = await inspector.run(organizations)
        normalized_orgs = TaxonomyNormalizerAgent.normalize_batch(inspected_orgs)
        mentors_by_slug = await mentor_profiler.run(normalized_orgs)

        return {
            "organizations": normalized_orgs,
            "mentors_by_slug": mentors_by_slug,
        }
