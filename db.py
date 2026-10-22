"""
Supabase PostgreSQL Database Client (`db.py`)
Supports both `supabase-py` and direct Supabase PostgREST (`/rest/v1/`) requests
pre-configured for the Michigan Startup Ecosystem & Incubator Intelligence Engine.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("michigan_intel.db")

DEFAULT_SUPABASE_URL = "https://jheuclgjrsqqgtbkpcjn.supabase.co"
DEFAULT_SUPABASE_KEY = "sb_publishable_eja1mhAIrf0motbU8tAahQ_RvxH-uCw"


class SupabaseDBClient:
    """
    Relational database client for syncing Michigan startup ecosystem intelligence
    (`organizations`, `mentors`, `events`) to Supabase PostgreSQL via `/rest/v1/`.
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
    ):
        env_url = os.environ.get("SUPABASE_URL", "").strip()
        env_key = os.environ.get("SUPABASE_KEY", "").strip()
        self.supabase_url = (
            (supabase_url or "").strip() or env_url or DEFAULT_SUPABASE_URL
        ).rstrip("/")
        self.supabase_key = (
            (supabase_key or "").strip() or env_key or DEFAULT_SUPABASE_KEY
        ).strip()
        self.rest_url = f"{self.supabase_url}/rest/v1"
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        self._http = httpx.Client(timeout=30.0, headers=self.headers)
        logger.info("Initialized Supabase REST client for %s", self.supabase_url)

    @property
    def is_connected(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)

    def _clean_org_payload(self, org_data: Dict[str, Any]) -> Dict[str, Any]:
        now_iso = datetime.now(timezone.utc).isoformat()
        payload: Dict[str, Any] = {
            "name": org_data["name"],
            "slug": org_data["slug"],
            "url": org_data.get("url"),
            "org_type": org_data.get("org_type", "Local/Regional Hub"),
            "ownership": org_data.get("ownership", "Public-Private Partnership"),
            "address": org_data.get("address"),
            "city": org_data.get("city"),
            "region": org_data.get("region"),
            "latitude": org_data.get("latitude"),
            "longitude": org_data.get("longitude"),
            "description": org_data.get("description"),
            "application_url": org_data.get("application_url"),
            "contact_email": org_data.get("contact_email"),
            "industry_specialties": org_data.get("industry_specialties", []),
            "specialized_equipment": org_data.get("specialized_equipment", []),
            "services_and_curriculum": org_data.get("services_and_curriculum", []),
            "last_quarterly_scrape": org_data.get("last_quarterly_scrape", now_iso),
        }
        if "local_industry_distribution" in org_data and org_data["local_industry_distribution"] is not None:
            payload["local_industry_distribution"] = org_data["local_industry_distribution"]
        if "site_selection_profile" in org_data and org_data["site_selection_profile"] is not None:
            payload["site_selection_profile"] = org_data["site_selection_profile"]
        if org_data.get("id"):
            payload["id"] = org_data["id"]
        return payload

    def upsert_organization(self, org_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Upserts an organization record by its unique `slug`."""
        payload = self._clean_org_payload(org_data)
        headers = {**self.headers, "Prefer": "resolution=merge-duplicates,return=representation"}
        resp = self._http.post(
            f"{self.rest_url}/organizations",
            params={"on_conflict": "slug"},
            headers=headers,
            json=payload,
        )
        if resp.status_code not in (200, 201):
            logger.error(
                "Failed to upsert organization %s: [%d] %s",
                payload["slug"],
                resp.status_code,
                resp.text,
            )
            return None
        data = resp.json()
        return data[0] if isinstance(data, list) and data else None

    def upsert_organizations_batch(self, orgs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch upsert multiple organizations by `slug` into Supabase."""
        if not orgs:
            return []
        payloads = [self._clean_org_payload(o) for o in orgs]
        headers = {**self.headers, "Prefer": "resolution=merge-duplicates,return=representation"}
        resp = self._http.post(
            f"{self.rest_url}/organizations",
            params={"on_conflict": "slug"},
            headers=headers,
            json=payloads,
        )
        if resp.status_code not in (200, 201):
            logger.error(
                "Batch upsert organizations failed: [%d] %s. Falling back to row-by-row.",
                resp.status_code,
                resp.text,
            )
            results = []
            for o in orgs:
                row = self.upsert_organization(o)
                if row:
                    results.append(row)
            return results
        return resp.json()

    def fetch_all_organizations(self) -> List[Dict[str, Any]]:
        """Retrieve all tracked organizations from Supabase."""
        resp = self._http.get(
            f"{self.rest_url}/organizations",
            params={"select": "*", "order": "name.asc"},
        )
        if resp.status_code != 200:
            logger.error("Failed to fetch organizations: [%d] %s", resp.status_code, resp.text)
            return []
        return resp.json()

    def fetch_existing_mentors(self, organization_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve existing mentors (optionally filtered by organization_id)."""
        params: Dict[str, str] = {"select": "*"}
        if organization_id:
            params["organization_id"] = f"eq.{organization_id}"
        resp = self._http.get(f"{self.rest_url}/mentors", params=params)
        if resp.status_code != 200:
            return []
        return resp.json()

    def upsert_mentors(self, organization_id: str, mentors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Idempotently syncs mentor records for `organization_id` into the `mentors` table.
        Checks existing mentor names for that organization to avoid duplicate rows even if
        the database table lacks a composite unique constraint on `(organization_id, full_name)`.
        """
        if not mentors:
            return []

        existing = self.fetch_existing_mentors(organization_id)
        existing_by_name = {
            (m.get("full_name") or "").strip().lower(): m for m in existing
        }

        persisted: List[Dict[str, Any]] = []
        for m in mentors:
            full_name = (m.get("full_name") or "").strip()
            if not full_name:
                continue
            payload: Dict[str, Any] = {
                "organization_id": organization_id,
                "full_name": full_name,
                "role_at_incubator": m.get("role_at_incubator"),
                "current_title_company": m.get("current_title_company"),
                "bio_summary": m.get("bio_summary"),
                "expertise_tags": m.get("expertise_tags", []),
                "linkedin_url": m.get("linkedin_url"),
                "confidence_score": float(m.get("confidence_score", 0.85)),
            }

            existing_row = existing_by_name.get(full_name.lower())
            if existing_row and existing_row.get("id"):
                resp = self._http.patch(
                    f"{self.rest_url}/mentors",
                    params={"id": f"eq.{existing_row['id']}"},
                    json=payload,
                )
            else:
                resp = self._http.post(
                    f"{self.rest_url}/mentors",
                    json=payload,
                )

            if resp.status_code in (200, 201):
                data = resp.json()
                if isinstance(data, list) and data:
                    persisted.append(data[0])
            else:
                logger.error(
                    "Failed to sync mentor %s: [%d] %s",
                    full_name,
                    resp.status_code,
                    resp.text,
                )
        return persisted

    def fetch_existing_events(self, organization_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve existing events (optionally filtered by organization_id)."""
        params: Dict[str, str] = {"select": "*"}
        if organization_id:
            params["organization_id"] = f"eq.{organization_id}"
        resp = self._http.get(f"{self.rest_url}/events", params=params)
        if resp.status_code != 200:
            return []
        return resp.json()

    def upsert_events(self, organization_id: str, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Idempotently syncs upcoming events for `organization_id` into the `events` table.
        """
        if not events:
            return []

        now_iso = datetime.now(timezone.utc).isoformat()
        existing = self.fetch_existing_events(organization_id)
        existing_by_title = {
            (ev.get("title") or "").strip().lower(): ev for ev in existing
        }

        persisted: List[Dict[str, Any]] = []
        for ev in events:
            title = (ev.get("title") or "").strip()
            if not title:
                continue
            payload: Dict[str, Any] = {
                "organization_id": organization_id,
                "title": title,
                "event_date": ev["event_date"],
                "event_type": ev.get("event_type", "Workshop"),
                "description": ev.get("description"),
                "registration_url": ev.get("registration_url"),
                "last_checked": ev.get("last_checked", now_iso),
            }

            existing_row = existing_by_title.get(title.lower())
            if existing_row and existing_row.get("id"):
                resp = self._http.patch(
                    f"{self.rest_url}/events",
                    params={"id": f"eq.{existing_row['id']}"},
                    json=payload,
                )
            else:
                resp = self._http.post(
                    f"{self.rest_url}/events",
                    json=payload,
                )

            if resp.status_code in (200, 201):
                data = resp.json()
                if isinstance(data, list) and data:
                    persisted.append(data[0])
            else:
                logger.error(
                    "Failed to sync event %s: [%d] %s",
                    title,
                    resp.status_code,
                    resp.text,
                )
        return persisted

    def purge_past_events(self, cutoff_iso: Optional[str] = None) -> int:
        """Delete events whose `event_date` is strictly in the past."""
        cutoff = cutoff_iso or datetime.now(timezone.utc).isoformat()
        resp = self._http.delete(
            f"{self.rest_url}/events",
            params={"event_date": f"lt.{cutoff}"},
        )
        if resp.status_code in (200, 204):
            data = resp.json() if resp.text else []
            return len(data) if isinstance(data, list) else 0
        return 0

    def get_table_counts(self) -> Dict[str, int]:
        """Return live row counts for `organizations`, `mentors`, and `events`."""
        counts: Dict[str, int] = {}
        for table in ("organizations", "mentors", "events"):
            resp = self._http.get(
                f"{self.rest_url}/{table}",
                params={"select": "id"},
            )
            if resp.status_code == 200 and isinstance(resp.json(), list):
                counts[table] = len(resp.json())
            else:
                counts[table] = -1
        return counts
