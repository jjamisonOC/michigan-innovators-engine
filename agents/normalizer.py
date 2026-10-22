"""
Agent 4: Taxonomy Normalizer & QA Agent (`agents/normalizer.py`)
Standardizes all extracted tags, enums, and geographical fields across parallel agents
before syncing into Supabase so frontend directory filters remain clean and canonical.
"""

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger("michigan_intel.normalizer")

VALID_ORG_TYPES = {
    "State SmartZone",
    "University Incubator",
    "Private Accelerator",
    "Local/Regional Hub",
    "Coworking/Makerspace",
    "Non-Profit Support",
}

VALID_OWNERSHIP_TYPES = {
    "Public",
    "Private",
    "Public-Private Partnership",
    "University",
}

VALID_EVENT_TYPES = {
    "Seminar",
    "Pitch Competition",
    "Workshop",
    "Networking",
    "Cohort Deadline",
}

# Canonical Equipment Taxonomy Mapping
EQUIPMENT_SYNONYM_MAP: Dict[str, List[str]] = {
    "3D Printing & Additive Manufacturing": [
        "3-d printer", "3d printer", "3d printing", "sla printing", "fdm",
        "sls", "additive mfg", "additive manufacturing", "stratasys", "formlabs",
        "markforged", "rapid prototyping printer", "metal 3d printing",
    ],
    "Wet Labs & BSL-1/BSL-2 Suites": [
        "wet lab", "wet labs", "bsl-1", "bsl-2", "bsl1", "bsl2", "biosafety",
        "cell culture", "fume hood", "biotech lab", "chemical hood", "autoclave",
        "life science lab", "molecular biology lab",
    ],
    "CNC Machining & Metal Fabrication": [
        "cnc", "cnc machine", "cnc machining", "5-axis", "lathe", "milling machine",
        "waterjet", "laser cutter", "plasma cutter", "haas", "sheet metal",
        "welding", "machine shop", "metal shop",
    ],
    "Cleanroom & Microelectronics Facility": [
        "cleanroom", "clean room", "iso class", "semiconductor", "wafer",
        "photolithography", "nanofabrication", "microfluidics", "optics lab",
    ],
    "Electronics & IoT Prototyping Lab": [
        "electronics lab", "pcb", "oscilloscope", "soldering", "smt", "pick and place",
        "iot lab", "embedded systems", "rf testing", "spectrum analyzer", "hardware lab",
    ],
    "Autonomous & Mobility Testing Track": [
        "autonomous track", "drone testing", "uav", "cav", "connected vehicle",
        "ev battery testing", "dynamometer", "dyno", "vehicle bay", "mobility testbed",
        "garage bay", "automotive bay", "charging test", "airspace",
    ],
    "Commercial Kitchen & Food Processing": [
        "commercial kitchen", "test kitchen", "food grade", "commissary",
        "cold storage", "packaging line", "licensed kitchen", "culinary incubator",
    ],
    "Media Studio & Podcasting Suite": [
        "podcast studio", "video studio", "green screen", "recording studio",
        "media lab", "av equipment", "photography studio",
    ],
    "High-Performance Computing & AI Cluster": [
        "gpu cluster", "hpc", "high performance computing", "ai server",
        "vr/ar lab", "simulation lab", "digital twin lab",
    ],
}

# Canonical Industry Specialties Taxonomy Mapping
INDUSTRY_SYNONYM_MAP: Dict[str, List[str]] = {
    "Mobility, EV & Electrification": [
        "mobility", "ev", "electric vehicle", "automotive", "autotech",
        "connected vehicles", "electrification", "battery", "autonomous vehicles",
        "transportation", "next-gen mobility",
    ],
    "MedTech, Biotech & Life Sciences": [
        "medtech", "medical device", "biotech", "life sciences", "healthcare",
        "digital health", "pharma", "therapeutics", "diagnostics", "healthtech",
        "biomedical",
    ],
    "SaaS, AI & Enterprise Software": [
        "saas", "ai", "artificial intelligence", "machine learning", "software",
        "b2b saas", "cloud", "cybersecurity", "fintech", "data analytics", "it",
    ],
    "Advanced Manufacturing & Industry 4.0": [
        "advanced manufacturing", "industry 4.0", "robotics", "automation",
        "hardware", "industrial tech", "materials", "advanced materials",
        "smart manufacturing", "supply chain",
    ],
    "Defense, Aerospace & Dual-Use": [
        "defense", "aerospace", "dual-use", "dod", "military", "drones",
        "uav", "maritime defense", "national security", "space tech",
    ],
    "CleanTech, Energy & Blue Economy": [
        "cleantech", "clean energy", "renewable energy", "sustainability",
        "water tech", "blue economy", "maritime", "freshwater", "climate tech",
        "circular economy", "grid",
    ],
    "AgTech, Food & Forestry": [
        "agtech", "agriculture", "food", "foodtech", "cpg", "forestry",
        "natural resources", "beverage", "culinary",
    ],
    "Main Street, Creative & Small Business": [
        "small business", "main street", "retail", "creative", "design",
        "consumer products", "e-commerce", "social enterprise", "general",
    ],
}

# Canonical Services & Curriculum Taxonomy Mapping
SERVICES_SYNONYM_MAP: Dict[str, List[str]] = {
    "SBIR/STTR & Non-Dilutive Grant Writing": [
        "sbir", "sttr", "grant writing", "non-dilutive", "federal grants",
        "medc mtrc", "mtrac", "bbcetc", "proposal prep",
    ],
    "Customer Discovery & NSF I-Corps": [
        "customer discovery", "i-corps", "icorps", "lean startup", "business model canvas",
        "market validation", "product-market fit",
    ],
    "FDA Regulatory & Clinical Pathways": [
        "fda", "regulatory", "510(k)", "clinical trials", "hipaa",
        "quality systems", "iso 13485", "reimbursement",
    ],
    "IP, Patent & Tech Transfer Clinics": [
        "ip", "intellectual property", "patent", "licensing", "tech transfer",
        "technology commercialization", "legal clinic", "trademark",
    ],
    "Venture Fundraising & Pitch Coaching": [
        "pitch", "fundraising", "venture capital", "angel", "seed fund",
        "pre-seed", "investor readiness", "demo day", "term sheet", "capital access",
    ],
    "Financial Modeling & Accounting Readiness": [
        "financial modeling", "accounting", "bookkeeping", "cash flow",
        "unit economics", "valuation", "tax credits", "sbdc consulting",
    ],
    "Hardware DFM & Supply Chain Advisory": [
        "dfm", "design for manufacturability", "supply chain", "bom",
        "contract manufacturing", "tooling", "prototyping advisory", "hardware accelerator",
    ],
    "Executive Mentorship & EIR Program": [
        "eir", "entrepreneur in residence", "mentor-in-residence", "mentorship",
        "coaching", "advisory board", "c-suite", "talent matching",
    ],
}

# Canonical Mentor Expertise Taxonomy Mapping
MENTOR_EXPERTISE_MAP: Dict[str, List[str]] = {
    "B2B SaaS Sales & Go-To-Market": [
        "b2b sales", "saas sales", "go-to-market", "gtm", "enterprise sales",
        "growth marketing", "customer acquisition", "revenue operations",
    ],
    "Venture Fundraising & Angel Investing": [
        "venture capital", "fundraising", "angel investing", "seed funding",
        "m&a", "corporate finance", "investor relations", "cfo",
    ],
    "Hardware Engineering & Supply Chain": [
        "hardware", "supply chain", "manufacturing", "dfm", "mechanical engineering",
        "industrial design", "automotive engineering", "operations",
    ],
    "MedTech Regulatory & Life Sciences Commercialization": [
        "fda", "medtech", "biotech", "clinical", "life sciences", "healthcare",
        "medical device", "pharma", "diagnostics",
    ],
    "Product Management & AI/Software Architecture": [
        "product management", "cto", "software architecture", "ai", "machine learning",
        "cloud infrastructure", "cybersecurity", "ux",
    ],
    "IP Strategy, Legal & Tech Transfer": [
        "intellectual property", "patent", "licensing", "legal", "tech transfer",
        "corporate governance", "contracts",
    ],
    "SBIR/STTR & Government Contracting": [
        "sbir", "sttr", "dod", "defense contracting", "government grants",
        "non-dilutive funding", "public sector",
    ],
    "Executive Leadership & Operations Scaling": [
        "ceo", "executive coaching", "scaling", "hr", "talent", "strategy",
        "founder coaching", "general management",
    ],
}


class TaxonomyNormalizerAgent:
    """
    Agent 4: Normalizes raw extracted lists and metadata into canonical taxonomies
    and validates records against Supabase schema constraints.
    """

    @staticmethod
    def _normalize_tags(raw_tags: List[str], mapping: Dict[str, List[str]], keep_unmapped: bool = False) -> List[str]:
        normalized = set()
        for raw in raw_tags or []:
            if not raw or not isinstance(raw, str):
                continue
            clean_raw = raw.strip()
            lower_raw = clean_raw.lower()

            # Direct match against canonical keys
            matched = False
            for canonical, synonyms in mapping.items():
                if lower_raw == canonical.lower():
                    normalized.add(canonical)
                    matched = True
                    break
                for syn in synonyms:
                    if syn in lower_raw:
                        normalized.add(canonical)
                        matched = True
                        break
            if not matched and keep_unmapped and len(clean_raw) > 2:
                normalized.add(clean_raw)

        return sorted(normalized)

    @classmethod
    def normalize_equipment(cls, raw_tags: List[str]) -> List[str]:
        return cls._normalize_tags(raw_tags, EQUIPMENT_SYNONYM_MAP, keep_unmapped=False)

    @classmethod
    def normalize_industries(cls, raw_tags: List[str]) -> List[str]:
        result = cls._normalize_tags(raw_tags, INDUSTRY_SYNONYM_MAP, keep_unmapped=False)
        return result if result else ["Main Street, Creative & Small Business"]

    @classmethod
    def normalize_services(cls, raw_tags: List[str]) -> List[str]:
        result = cls._normalize_tags(raw_tags, SERVICES_SYNONYM_MAP, keep_unmapped=False)
        return result if result else ["Executive Mentorship & EIR Program"]

    @classmethod
    def normalize_mentor_expertise(cls, raw_tags: List[str]) -> List[str]:
        result = cls._normalize_tags(raw_tags, MENTOR_EXPERTISE_MAP, keep_unmapped=False)
        return result if result else ["Executive Leadership & Operations Scaling"]

    @staticmethod
    def normalize_org_type(org_type: str) -> str:
        if org_type in VALID_ORG_TYPES:
            return org_type
        lower = (org_type or "").lower()
        if "smartzone" in lower:
            return "State SmartZone"
        if "univ" in lower or "college" in lower or "tech transfer" in lower:
            return "University Incubator"
        if "accel" in lower or "venture" in lower:
            return "Private Accelerator"
        if "maker" in lower or "cowork" in lower or "fab" in lower:
            return "Coworking/Makerspace"
        if "sbdc" in lower or "non-profit" in lower or "nonprofit" in lower or "foundation" in lower:
            return "Non-Profit Support"
        return "Local/Regional Hub"

    @staticmethod
    def normalize_ownership(ownership: str, org_type: str = "") -> str:
        if ownership in VALID_OWNERSHIP_TYPES:
            return ownership
        lower = (ownership or "").lower()
        if "univ" in lower or org_type == "University Incubator":
            return "University"
        if "public-private" in lower or "ppp" in lower or org_type == "State SmartZone":
            return "Public-Private Partnership"
        if "private" in lower or org_type in ("Private Accelerator", "Coworking/Makerspace"):
            return "Private"
        if "public" in lower or "state" in lower:
            return "Public"
        return "Public-Private Partnership"

    @staticmethod
    def normalize_event_type(event_type: str, title: str = "") -> str:
        if event_type in VALID_EVENT_TYPES:
            return event_type
        combined = f"{event_type or ''} {title or ''}".lower()
        if "pitch" in combined or "demo day" in combined or "competition" in combined:
            return "Pitch Competition"
        if "deadline" in combined or "cohort" in combined or "application" in combined:
            return "Cohort Deadline"
        if "network" in combined or "mixer" in combined or "happy hour" in combined or "meetup" in combined:
            return "Networking"
        if "seminar" in combined or "lecture" in combined or "panel" in combined or "webinar" in combined:
            return "Seminar"
        return "Workshop"

    @staticmethod
    def slugify(name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        return slug

    @classmethod
    def normalize_organization(cls, org: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes a single organization dictionary and runs QA checks."""
        cleaned = dict(org)
        cleaned["name"] = (cleaned.get("name") or "").strip()
        cleaned["slug"] = cleaned.get("slug") or cls.slugify(cleaned["name"])
        cleaned["org_type"] = cls.normalize_org_type(cleaned.get("org_type", ""))
        cleaned["ownership"] = cls.normalize_ownership(
            cleaned.get("ownership", ""), cleaned["org_type"]
        )
        cleaned["industry_specialties"] = cls.normalize_industries(
            cleaned.get("industry_specialties", [])
        )
        cleaned["specialized_equipment"] = cls.normalize_equipment(
            cleaned.get("specialized_equipment", [])
        )
        cleaned["services_and_curriculum"] = cls.normalize_services(
            cleaned.get("services_and_curriculum", [])
        )

        # QA check on Michigan coordinates
        lat = cleaned.get("latitude")
        lon = cleaned.get("longitude")
        if lat is not None and lon is not None:
            try:
                lat_f = float(lat)
                lon_f = float(lon)
                if not (41.5 <= lat_f <= 48.5 and -90.6 <= lon_f <= -82.0):
                    logger.warning(
                        "Coordinates (%s, %s) for %s outside Michigan bounding box!",
                        lat_f,
                        lon_f,
                        cleaned["name"],
                    )
                cleaned["latitude"] = round(lat_f, 6)
                cleaned["longitude"] = round(lon_f, 6)
            except (TypeError, ValueError):
                cleaned["latitude"] = None
                cleaned["longitude"] = None

        return cleaned

    @classmethod
    def normalize_mentor(cls, mentor: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes a single mentor record and clamps confidence score."""
        cleaned = dict(mentor)
        cleaned["full_name"] = (cleaned.get("full_name") or "").strip()
        cleaned["expertise_tags"] = cls.normalize_mentor_expertise(
            cleaned.get("expertise_tags", [])
        )
        score = float(cleaned.get("confidence_score", 0.75))
        cleaned["confidence_score"] = round(max(0.0, min(1.0, score)), 2)
        return cleaned

    @classmethod
    def normalize_event(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes a single event record."""
        cleaned = dict(event)
        cleaned["title"] = (cleaned.get("title") or "").strip()
        cleaned["event_type"] = cls.normalize_event_type(
            cleaned.get("event_type", ""), cleaned["title"]
        )
        return cleaned

    @classmethod
    def normalize_batch(cls, organizations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicates by slug and normalizes an entire batch of organizations."""
        seen_slugs = set()
        normalized_list = []
        for org in organizations:
            norm_org = cls.normalize_organization(org)
            slug = norm_org["slug"]
            if slug in seen_slugs:
                logger.debug("Skipping duplicate organization slug: %s", slug)
                continue
            seen_slugs.add(slug)
            normalized_list.append(norm_org)
        logger.info("Normalized and QA-verified %d unique organizations.", len(normalized_list))
        return normalized_list
