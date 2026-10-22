"""
Unified Unattended Background Update Daemon (`auto_update_daemon.py`)

Designed for silent off-peak execution via Windows Task Scheduler (`run_silent_update.vbs` -> `run_update.bat`):
1. Every Run (Weekly):
   - Scrapes all 46 organizations' `/events` and `/calendar` pages to upsert new upcoming
     seminars, pitch competitions, cohort deadlines, and workshops into `events`.
   - Purges expired events older than yesterday (`now - 1 day`).
   - Runs `DeadLinkScrubberAgent` (`link_scrubber.py`) to verify and repair any newly added URLs.
2. Every 90 Days (Quarterly Check):
   - Inspects `last_quarterly_scrape` on every row in `organizations`.
   - For any organization where `last_quarterly_scrape` is missing or older than 90 days,
     automatically triggers the deep mentor/program/facility updater (`agents/deep_knowledge.py`
     & `DeepEnrichmentSpider`) and updates `last_quarterly_scrape = now()`.
3. Logs all activity, timing, and before/after row counts cleanly to:
   `V:\\My Drive\\Coding Projects\\Start up - State wide ecosystem\\logs\\update_history.log`
"""

import argparse
import asyncio
import logging
import os
import sys
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

warnings.filterwarnings("ignore", category=RuntimeWarning)

import httpx
from playwright.async_api import async_playwright

from agents.deep_knowledge import get_deep_org_enrichment
from agents.deep_knowledge_ext import get_remaining_org_enrichment
from agents.scheduler import EcosystemSchedulerAgent
from db import SupabaseDBClient
from deep_enrich import DeepEnrichmentSpider
from link_scrubber import DeadLinkScrubberAgent

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "update_history.log"


def configure_logging() -> logging.Logger:
    """Configures dual logging to `logs/update_history.log` and stdout."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()

    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("primp").setLevel(logging.WARNING)

    return logging.getLogger("michigan_intel.auto_update_daemon")


def parse_iso_timestamp(ts_str: Any) -> datetime:
    """Parses a PostgreSQL ISO-8601 timestamp into a timezone-aware UTC datetime."""
    if not ts_str or not isinstance(ts_str, str):
        return datetime.fromtimestamp(0, tz=timezone.utc)
    cleaned = ts_str.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(cleaned)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return datetime.fromtimestamp(0, tz=timezone.utc)


async def run_unattended_update(force_quarterly: bool = False) -> Dict[str, Any]:
    logger = configure_logging()
    run_start = datetime.now(timezone.utc)
    logger.info("=" * 78)
    logger.info("STARTED UNATTENDED ECOSYSTEM UPDATE DAEMON AT %s", run_start.isoformat())

    # Lower current process priority on Windows or Linux/POSIX
    if sys.platform == "win32":
        try:
            import ctypes
            BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
            ctypes.windll.kernel32.SetPriorityClass(
                ctypes.windll.kernel32.GetCurrentProcess(), BELOW_NORMAL_PRIORITY_CLASS
            )
            logger.info("Windows process CPU priority set to BELOW_NORMAL_PRIORITY_CLASS.")
        except Exception as exc:
            logger.debug("Could not adjust Windows process priority via ctypes: %s", exc)
    elif hasattr(os, "nice"):
        try:
            os.nice(10)
            logger.info("Linux/POSIX process CPU niceness incremented (+10).")
        except Exception as exc:
            logger.debug("Could not adjust POSIX process niceness: %s", exc)

    db = SupabaseDBClient()
    before_counts = db.get_table_counts()
    logger.info(
        "Supabase initial counts -> organizations=%d, mentors=%d, events=%d",
        before_counts.get("organizations", 0),
        before_counts.get("mentors", 0),
        before_counts.get("events", 0),
    )

    organizations = db.fetch_all_organizations()
    org_by_slug = {o["slug"]: o for o in organizations if o.get("slug")}

    # ------------------------------------------------------------------
    # PHASE 1 (EVERY RUN / WEEKLY): Scrape `/events` & Calendars + Purge Past Events
    # ------------------------------------------------------------------
    logger.info("[PHASE 1/3] Running Weekly Event & Calendar Scraper across %d organizations...", len(organizations))
    scheduler = EcosystemSchedulerAgent(max_concurrency=8)
    events_by_slug = await scheduler.run_weekly_event_scraper(organizations)

    upserted_events_count = 0
    for slug, ev_list in events_by_slug.items():
        org_row = org_by_slug.get(slug)
        if not org_row or not org_row.get("id"):
            continue
        synced = db.upsert_events(org_row["id"], ev_list)
        upserted_events_count += len(synced)

    # Purge past events older than yesterday (now - 1 day)
    yesterday_cutoff = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    purged_events_count = db.purge_past_events(cutoff_iso=yesterday_cutoff)
    logger.info(
        "[PHASE 1/3 COMPLETE] Upserted/verified %d upcoming events; purged %d past events older than %s.",
        upserted_events_count,
        purged_events_count,
        yesterday_cutoff,
    )

    # ------------------------------------------------------------------
    # PHASE 2 (QUARTERLY 90-DAY CHECK): Check `last_quarterly_scrape` in `organizations`
    # ------------------------------------------------------------------
    now_utc = datetime.now(timezone.utc)
    quarterly_cutoff = now_utc - timedelta(days=90)
    due_orgs: List[Dict[str, Any]] = []

    for org in organizations:
        last_scrape_dt = parse_iso_timestamp(org.get("last_quarterly_scrape"))
        if force_quarterly or last_scrape_dt < quarterly_cutoff:
            due_orgs.append(org)

    quarterly_updated_count = 0
    if due_orgs:
        logger.info(
            "[PHASE 2/3] %d organizations have `last_quarterly_scrape` older than 90 days (cutoff=%s). "
            "Triggering deep mentor/program/facility updater (`deep_knowledge.py` & `DeepEnrichmentSpider`)...",
            len(due_orgs),
            quarterly_cutoff.date().isoformat(),
        )
        # Ensure deep knowledge modules are loaded and merged
        deep_kb = {**get_deep_org_enrichment(), **get_remaining_org_enrichment()}
        logger.info("Loaded %d deep knowledge organization profiles from `deep_knowledge.py`.", len(deep_kb))

        spider = DeepEnrichmentSpider(db=db, max_concurrency=4)
        semaphore = asyncio.Semaphore(4)
        async with httpx.AsyncClient(
            follow_redirects=True,
            headers={"User-Agent": spider.user_agent},
            timeout=10.0,
            verify=False,
        ) as http_client:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                try:
                    tasks = [
                        spider.enrich_single_organization(
                            org, http_client, browser, semaphore, enable_web_search=False
                        )
                        for org in due_orgs
                    ]
                    await asyncio.gather(*tasks)
                    quarterly_updated_count = len(due_orgs)
                finally:
                    await browser.close()
        logger.info(
            "[PHASE 2/3 COMPLETE] Refreshed deep mentors, programs, equipment, and updated `last_quarterly_scrape = now()` for %d organizations.",
            quarterly_updated_count,
        )
    else:
        oldest_ts = min(parse_iso_timestamp(o.get("last_quarterly_scrape")) for o in organizations) if organizations else now_utc
        days_since_oldest = (now_utc - oldest_ts).days
        logger.info(
            "[PHASE 2/3 SKIPPED] All %d organizations were deeply scraped within the last 90 days "
            "(oldest `last_quarterly_scrape` is %d days ago on %s).",
            len(organizations),
            days_since_oldest,
            oldest_ts.date().isoformat(),
        )

    # ------------------------------------------------------------------
    # PHASE 3 (EVERY RUN): Run `link_scrubber.py` to Verify & Repair URLs
    # ------------------------------------------------------------------
    logger.info("[PHASE 3/3] Running `link_scrubber.py` (`DeadLinkScrubberAgent`) on all URLs...")
    scrubber = DeadLinkScrubberAgent(db=db, max_concurrency=8)
    await scrubber.run()
    logger.info(
        "[PHASE 3/3 COMPLETE] Link Scrubber stats: org_urls_repaired=%d, org_app_urls_repaired=%d, "
        "event_urls_repaired=%d, expired_events_deleted=%d, mentor_linkedin_verified=%d",
        scrubber.stats["orgs_url_repaired"],
        scrubber.stats["orgs_app_url_repaired"],
        scrubber.stats["events_url_repaired"],
        scrubber.stats["events_deleted_expired_or_invalid"],
        scrubber.stats["mentors_linkedin_verified"],
    )

    after_counts = db.get_table_counts()
    elapsed_sec = (datetime.now(timezone.utc) - run_start).total_seconds()
    logger.info(
        "FINISHED UNATTENDED UPDATE IN %.1fs | Final Supabase counts -> organizations=%d (was %d), "
        "mentors=%d (was %d), events=%d (was %d)",
        elapsed_sec,
        after_counts.get("organizations", 0),
        before_counts.get("organizations", 0),
        after_counts.get("mentors", 0),
        before_counts.get("mentors", 0),
        after_counts.get("events", 0),
        before_counts.get("events", 0),
    )
    logger.info("=" * 78)

    return {
        "before_counts": before_counts,
        "after_counts": after_counts,
        "upserted_events": upserted_events_count,
        "purged_events": purged_events_count,
        "quarterly_updated_orgs": quarterly_updated_count,
        "scrubber_stats": scrubber.stats,
        "elapsed_seconds": elapsed_sec,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Unified Unattended Weekly & Quarterly Background Updater for Michigan Startup Ecosystem"
    )
    parser.add_argument(
        "--force-quarterly",
        action="store_true",
        help="Force 90-day quarterly deep enrichment regardless of `last_quarterly_scrape` timestamp",
    )
    args = parser.parse_args()
    asyncio.run(run_unattended_update(force_quarterly=args.force_quarterly))


if __name__ == "__main__":
    main()
