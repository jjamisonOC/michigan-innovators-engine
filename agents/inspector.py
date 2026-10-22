"""
Agent 2: Deep-Dive Site Inspector (`agents/inspector.py`)
Spawns independent, asynchronous worker instances (one per organization URL)
to crawl `/about`, `/programs`, `/facilities`, `/equipment`, `/labs`, `/resources`, and `/apply`
pages and extract structured intelligence on industry specialties, differentiated lab/prototyping
equipment, and curriculum/services.
"""

import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from .normalizer import (
    EQUIPMENT_SYNONYM_MAP,
    INDUSTRY_SYNONYM_MAP,
    SERVICES_SYNONYM_MAP,
    TaxonomyNormalizerAgent,
)

logger = logging.getLogger("michigan_intel.inspector")

TARGET_SUBPATHS = [
    "",
    "/about",
    "/programs",
    "/facilities",
    "/equipment",
    "/labs",
    "/resources",
    "/apply",
]

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


class DeepDiveInspectorAgent:
    """
    Agent 2: Parallel asynchronous website inspector that crawls each Michigan
    startup hub's subpages and extracts physical equipment, industry specialties,
    and curriculum offerings.
    """

    def __init__(
        self,
        max_concurrency: int = 10,
        timeout_seconds: float = 12.0,
        user_agent: str = "Mozilla/5.0 (compatible; MichiganEcosystemBot/1.0)",
    ):
        self.max_concurrency = max_concurrency
        self.timeout_seconds = timeout_seconds
        self.user_agent = user_agent

    async def _fetch_page_text(self, client: httpx.AsyncClient, url: str) -> str:
        try:
            resp = await client.get(url, timeout=self.timeout_seconds)
            if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", ""):
                soup = BeautifulSoup(resp.text, "lxml")
                for tag in soup(["script", "style", "noscript", "svg"]):
                    tag.decompose()
                return soup.get_text(separator=" ", strip=True)
        except Exception as exc:
            logger.debug("Subpage fetch skipped for %s: %s", url, exc)
        return ""

    @staticmethod
    def _scan_text_for_taxonomy(text: str, synonym_map: Dict[str, List[str]]) -> List[str]:
        lower_text = text.lower()
        found = []
        for canonical, keywords in synonym_map.items():
            for kw in keywords:
                if kw in lower_text:
                    found.append(canonical)
                    break
        return found

    async def inspect_organization(
        self,
        client: httpx.AsyncClient,
        org: Dict[str, Any],
        semaphore: asyncio.Semaphore,
    ) -> Dict[str, Any]:
        """Worker coroutine that inspects a single organization across target subpaths."""
        async with semaphore:
            base_url = (org.get("url") or "").rstrip("/")
            updated = dict(org)

            if not base_url:
                return TaxonomyNormalizerAgent.normalize_organization(updated)

            # Crawl base URL and key subpaths concurrently (bounded per site)
            urls_to_crawl = [urljoin(base_url + "/", path.lstrip("/")) for path in TARGET_SUBPATHS[:5]]
            pages_text = await asyncio.gather(
                *[self._fetch_page_text(client, u) for u in urls_to_crawl]
            )
            combined_corpus = " ".join([t for t in pages_text if t])

            if combined_corpus:
                discovered_equipment = self._scan_text_for_taxonomy(
                    combined_corpus, EQUIPMENT_SYNONYM_MAP
                )
                discovered_industries = self._scan_text_for_taxonomy(
                    combined_corpus, INDUSTRY_SYNONYM_MAP
                )
                discovered_services = self._scan_text_for_taxonomy(
                    combined_corpus, SERVICES_SYNONYM_MAP
                )

                updated["specialized_equipment"] = list(
                    set(updated.get("specialized_equipment", [])) | set(discovered_equipment)
                )
                updated["industry_specialties"] = list(
                    set(updated.get("industry_specialties", [])) | set(discovered_industries)
                )
                updated["services_and_curriculum"] = list(
                    set(updated.get("services_and_curriculum", [])) | set(discovered_services)
                )

                # Extract contact email if missing
                if not updated.get("contact_email"):
                    emails = EMAIL_REGEX.findall(combined_corpus)
                    valid_emails = [
                        e for e in emails
                        if not any(x in e.lower() for x in ("example.com", "sentry", "wix", ".png", ".jpg"))
                    ]
                    if valid_emails:
                        updated["contact_email"] = valid_emails[0]

            updated["last_quarterly_scrape"] = datetime.now(timezone.utc).isoformat()
            return TaxonomyNormalizerAgent.normalize_organization(updated)

    async def run(self, organizations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Spawns parallel worker coroutines across all organizations."""
        semaphore = asyncio.Semaphore(self.max_concurrency)
        async with httpx.AsyncClient(
            follow_redirects=True,
            headers={"User-Agent": self.user_agent},
            timeout=self.timeout_seconds,
            verify=False,
        ) as client:
            tasks = [
                self.inspect_organization(client, org, semaphore)
                for org in organizations
            ]
            results = await asyncio.gather(*tasks)

        logger.info("Agent 2 (Deep-Dive Inspector) completed inspection of %d organizations.", len(results))
        return list(results)
