"""
Michigan Startup Ecosystem & Incubator Intelligence Engine
Multi-Agent Orchestrator (`main.py`)

Usage:
  python main.py                        # Runs full pipeline (Agents 1 -> 2 -> 3 -> 4 -> 5 + Supabase sync)
  python main.py --mode cartographer    # Runs Agent 1 only (outputs michigan_seed_list.json + upserts orgs)
  python main.py --mode weekly-events   # Runs Agent 5 Weekly Event Scraper + purges past events
  python main.py --mode quarterly-audit # Runs Agent 5 Quarterly Resource & Mentor Audit (Agents 2, 3, 4)
"""

import argparse
import asyncio
import json
import logging
import sys
from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table

from agents import (
    DeepDiveInspectorAgent,
    EcosystemSchedulerAgent,
    MentorProfilerAgent,
    MichiganCartographerAgent,
    TaxonomyNormalizerAgent,
)
from db import SupabaseDBClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
# Silence noisy httpx/httpcore logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger("michigan_intel.main")
console = Console()


async def execute_pipeline(mode: str, seed_output: str = "michigan_seed_list.json") -> None:
    db = SupabaseDBClient()
    cartographer = MichiganCartographerAgent()
    inspector = DeepDiveInspectorAgent()
    mentor_profiler = MentorProfilerAgent()
    scheduler = EcosystemSchedulerAgent()

    console.rule("[bold cyan]Michigan Startup Ecosystem & Incubator Intelligence Engine[/bold cyan]")
    console.print(f"[bold]Execution Mode:[/bold] [green]{mode}[/green]")
    console.print(f"[bold]Supabase Endpoint:[/bold] {db.supabase_url}\n")

    if mode in ("full", "cartographer"):
        console.print("[bold yellow]Step 1 (Agent 1 - Cartographer):[/bold yellow] Discovering & geocoding Michigan startup organizations...")
        seed_orgs = await cartographer.run(output_json_path=seed_output)
        console.print(f"  -> Compiled & geocoded [bold green]{len(seed_orgs)}[/bold green] organizations into `{seed_output}`.")

        if mode == "cartographer":
            persisted = db.upsert_organizations_batch(seed_orgs)
            console.print(f"  -> Upserted [bold green]{len(persisted)}[/bold green] base organizations into Supabase.")
            _print_supabase_verification(db)
            return

    if mode == "full":
        console.print("[bold yellow]Step 2 (Agent 2 - Deep-Dive Inspector):[/bold yellow] Crawling subpages for equipment, specialties & curriculum...")
        inspected_orgs = await inspector.run(seed_orgs)

        console.print("[bold yellow]Step 3 (Agent 4 - Taxonomy Normalizer):[/bold yellow] Standardizing tags & running QA validation...")
        normalized_orgs = TaxonomyNormalizerAgent.normalize_batch(inspected_orgs)

        # Save enriched seed list back to JSON
        with open(seed_output, "w", encoding="utf-8") as f:
            json.dump(normalized_orgs, f, indent=2)

        console.print("[bold yellow]Step 4 (Supabase Sync - Organizations):[/bold yellow] Upserting organizations to Supabase...")
        persisted_orgs = db.upsert_organizations_batch(normalized_orgs)
        slug_to_id: Dict[str, str] = {
            row["slug"]: row["id"] for row in persisted_orgs if row.get("slug") and row.get("id")
        }
        if not slug_to_id:
            # Fetch back from DB if needed
            all_db_orgs = db.fetch_all_organizations()
            slug_to_id = {
                row["slug"]: row["id"] for row in all_db_orgs if row.get("slug") and row.get("id")
            }
        console.print(f"  -> Synced [bold green]{len(slug_to_id)}[/bold green] organizations in Supabase `organizations` table.")

        console.print("[bold yellow]Step 5 (Agent 3 - Mentor & LinkedIn Profiler):[/bold yellow] Profiling mentors & EIRs in parallel...")
        mentors_by_slug = await mentor_profiler.run(normalized_orgs)
        total_mentors_synced = 0
        for slug, mentor_list in mentors_by_slug.items():
            org_id = slug_to_id.get(slug)
            if org_id and mentor_list:
                synced_m = db.upsert_mentors(org_id, mentor_list)
                total_mentors_synced += len(synced_m)
        console.print(f"  -> Synced [bold green]{total_mentors_synced}[/bold green] mentors in Supabase `mentors` table.")

        console.print("[bold yellow]Step 6 (Agent 5 - Weekly Event Scraper):[/bold yellow] Extracting upcoming events & purging past events...")
        db.purge_past_events()
        events_by_slug = await scheduler.run_weekly_event_scraper(normalized_orgs)
        total_events_synced = 0
        for slug, ev_list in events_by_slug.items():
            org_id = slug_to_id.get(slug)
            if org_id and ev_list:
                synced_e = db.upsert_events(org_id, ev_list)
                total_events_synced += len(synced_e)
        console.print(f"  -> Synced [bold green]{total_events_synced}[/bold green] upcoming events in Supabase `events` table.")

    elif mode == "weekly-events":
        console.print("[bold yellow]Running Agent 5 (Weekly Event Scraper & Past Event Purge)...[/bold yellow]")
        db_orgs = db.fetch_all_organizations()
        if not db_orgs:
            db_orgs = await cartographer.run(output_json_path=seed_output)
            db_orgs = db.upsert_organizations_batch(db_orgs)

        slug_to_id = {row["slug"]: row["id"] for row in db_orgs if row.get("slug") and row.get("id")}
        purged = db.purge_past_events()
        console.print(f"  -> Purged {purged} past events.")

        events_by_slug = await scheduler.run_weekly_event_scraper(db_orgs)
        total_events_synced = 0
        for slug, ev_list in events_by_slug.items():
            org_id = slug_to_id.get(slug)
            if org_id and ev_list:
                synced_e = db.upsert_events(org_id, ev_list)
                total_events_synced += len(synced_e)
        console.print(f"  -> Synced [bold green]{total_events_synced}[/bold green] upcoming events into Supabase.")

    elif mode == "quarterly-audit":
        console.print("[bold yellow]Running Agent 5 (Quarterly Resource & Mentor Audit - Agents 2, 3 & 4)...[/bold yellow]")
        db_orgs = db.fetch_all_organizations()
        if not db_orgs:
            db_orgs = await cartographer.run(output_json_path=seed_output)

        audit_result = await scheduler.run_quarterly_audit(db_orgs)
        persisted_orgs = db.upsert_organizations_batch(audit_result["organizations"])
        slug_to_id = {row["slug"]: row["id"] for row in persisted_orgs if row.get("slug") and row.get("id")}

        total_mentors_synced = 0
        for slug, mentor_list in audit_result["mentors_by_slug"].items():
            org_id = slug_to_id.get(slug)
            if org_id and mentor_list:
                synced_m = db.upsert_mentors(org_id, mentor_list)
                total_mentors_synced += len(synced_m)
        console.print(
            f"  -> Quarterly audit complete: updated [bold green]{len(persisted_orgs)}[/bold green] organizations "
            f"and [bold green]{total_mentors_synced}[/bold green] mentors."
        )

    _print_supabase_verification(db)


def _print_supabase_verification(db: SupabaseDBClient) -> None:
    counts = db.get_table_counts()
    table = Table(title="Live Supabase Database Verification (`public` schema)")
    table.add_column("Table Name", style="cyan", no_wrap=True)
    table.add_column("Live Row Count", justify="right", style="bold green")
    for tbl, cnt in counts.items():
        table.add_row(tbl, str(cnt))
    console.print("\n", table)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Michigan Startup Ecosystem & Incubator Intelligence Engine Orchestrator"
    )
    parser.add_argument(
        "--mode",
        choices=["full", "cartographer", "weekly-events", "quarterly-audit"],
        default="full",
        help="Execution mode for the multi-agent pipeline (default: full)",
    )
    parser.add_argument(
        "--seed-output",
        default="michigan_seed_list.json",
        help="File path to save the compiled Michigan seed list JSON",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(execute_pipeline(mode=args.mode, seed_output=args.seed_output))
    except KeyboardInterrupt:
        sys.exit(1)
