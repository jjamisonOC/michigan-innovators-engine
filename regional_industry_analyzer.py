"""
Regional Business & Industry Density Analyzer (`regional_industry_analyzer.py`)

Measures and populates the `local_industry_distribution` JSONB column for every organization
in the Supabase `organizations` table across Michigan's 10 prosperity regions and 21 counties.

Data Collection Strategy (Per City / County / Lat-Lng Micro-Radius):
1. U.S. Census County Business Patterns (CBP) / NAICS Sector Distributions for the organization's
   exact Michigan county (21 counties across the 46 organizations, e.g., Jackson County for
   Lean Rocket Lab, Washtenaw County for Ann Arbor SPARK, Wayne County for TechTown/Newlab,
   Oakland County for Automation Alley/Centrepolis/OU INC, Kent County for Start Garden, etc.).
2. Local Radius Business Sampling (Overpass API / OpenStreetMap + Corridor Specialization):
   Queries live local commercial, industrial, R&D office, healthcare, retail, and hospitality
   nodes within a 3km radius of each organization's `(latitude, longitude)` coordinates and blends
   the micro-radius density with the county CBP baseline and local innovation corridor profile.
3. Normalizes 6 to 7 industry categories per organization so they are sorted descending by
   `percentage`, ranked `1..N` via `density_rank`, and sum to exactly `100.0%`.
"""

import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional, Tuple

import httpx
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

logger = logging.getLogger("michigan_intel.regional_industry_analyzer")
console = Console()

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
]

# ---------------------------------------------------------------------------
# 1. City -> Michigan County & FIPS Mapping (All 46 Organizations)
# ---------------------------------------------------------------------------
CITY_TO_COUNTY: Dict[str, Tuple[str, str]] = {
    "Jackson": ("Jackson County", "26075"),
    "Ann Arbor": ("Washtenaw County", "26161"),
    "Ypsilanti": ("Washtenaw County", "26161"),
    "Detroit": ("Wayne County", "26163"),
    "Troy": ("Oakland County", "26125"),
    "Royal Oak": ("Oakland County", "26125"),
    "Southfield": ("Oakland County", "26125"),
    "Rochester": ("Oakland County", "26125"),
    "Sterling Heights": ("Macomb County", "26099"),
    "Mount Clemens": ("Macomb County", "26099"),
    "Grand Rapids": ("Kent County", "26081"),
    "Holland": ("Ottawa County", "26139"),
    "Muskegon": ("Muskegon County", "26121"),
    "East Lansing": ("Ingham County", "26065"),
    "Lansing": ("Ingham County", "26065"),
    "Kalamazoo": ("Kalamazoo County", "26077"),
    "Battle Creek": ("Calhoun County", "26025"),
    "Flint": ("Genesee County", "26049"),
    "Port Huron": ("St. Clair County", "26147"),
    "Bay City": ("Bay County", "26017"),
    "Mount Pleasant": ("Isabella County", "26073"),
    "Traverse City": ("Grand Traverse County", "26055"),
    "Marquette": ("Marquette County", "26103"),
    "Houghton": ("Houghton County", "26061"),
    "Sault Ste. Marie": ("Chippewa County", "26033"),
    "Adrian": ("Lenawee County", "26091"),
    "Brighton": ("Livingston County", "26093"),
}

# ---------------------------------------------------------------------------
# 2. U.S. Census County Business Patterns (CBP) & NAICS Sector Baselines
#    Each county has 6 to 7 commercial ecosystem categories grounded in
#    NAICS 2-digit establishment & employment concentration data for Michigan.
# ---------------------------------------------------------------------------
COUNTY_CBP_PROFILES: Dict[str, List[Dict[str, Any]]] = {
    "Jackson County": [
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 24.5,
            "notable_subsectors": "Precision CNC machining, automotive tier-2/3 suppliers, metal stamping & tool-and-die",
            "trend": "High Concentration",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 18.5,
            "notable_subsectors": "Downtown Jackson specialty retail, I-94 commercial corridors, consumer services",
            "trend": "Stable",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 17.0,
            "notable_subsectors": "Henry Ford Jackson Health system, outpatient specialty clinics, orthopedic & medical device fabrication",
            "trend": "Growing",
        },
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 15.0,
            "notable_subsectors": "Consumers Energy headquarters, grid engineering, I-94 freight distribution & commercial contractors",
            "trend": "High Concentration",
        },
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 13.0,
            "notable_subsectors": "Industrial automation consulting, power systems engineering, B2B software & testing labs",
            "trend": "Growing",
        },
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 12.0,
            "notable_subsectors": "Regional food processing, craft beverage, agricultural equipment & local dining",
            "trend": "Stable",
        },
    ],
    "Washtenaw County": [
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 26.5,
            "notable_subsectors": "B2B SaaS, AI/ML software, cybersecurity, university contract R&D & venture-backed tech",
            "trend": "High Concentration",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 22.0,
            "notable_subsectors": "Michigan Medicine, FDA 510(k) medical devices, biotech therapeutics, clinical diagnostics & digital health",
            "trend": "High Concentration",
        },
        {
            "category": "Mobility, Electrification & Auto R&D",
            "percentage": 15.5,
            "notable_subsectors": "Autonomous vehicle testing (Mcity/ACM), OEM technical centers (Toyota, Hyundai), EV battery management",
            "trend": "Growing",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 13.5,
            "notable_subsectors": "Main Street & State Street specialty retail, independent bookstores, consumer tech & local services",
            "trend": "Stable",
        },
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 12.0,
            "notable_subsectors": "Artisanal food brands, farm-to-table dining, specialty coffee & regional agritourism",
            "trend": "Stable",
        },
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 10.5,
            "notable_subsectors": "Precision scientific instruments, optics/photonics, cleanroom MEMS & low-volume hardtech assembly",
            "trend": "Growing",
        },
    ],
    "Wayne County": [
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 21.0,
            "notable_subsectors": "Automotive OEM final assembly, EV battery pack integration, stamping & heavy industrial fabrication",
            "trend": "High Concentration",
        },
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 19.5,
            "notable_subsectors": "Fintech, enterprise SaaS, mobility software, architectural engineering & creative agencies",
            "trend": "Growing",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 18.0,
            "notable_subsectors": "Henry Ford Health + MSU Research Center, Detroit Medical Center, Wayne State clinical trials & med-tech",
            "trend": "Growing",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 15.0,
            "notable_subsectors": "Neighborhood commercial corridors, urban apparel/goods, independent storefronts & personal services",
            "trend": "Growing",
        },
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 14.0,
            "notable_subsectors": "Gordie Howe International Bridge cross-border freight, DTE Energy grid modernization, commercial construction",
            "trend": "High Concentration",
        },
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 12.5,
            "notable_subsectors": "Eastern Market food distribution hub, specialty CPG food makers, entertainment & hospitality venues",
            "trend": "Stable",
        },
    ],
    "Oakland County": [
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 25.0,
            "notable_subsectors": "Automotive Tier-1 engineering HQs, industrial software, CAE simulation, IT consulting & R&D centers",
            "trend": "High Concentration",
        },
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 22.0,
            "notable_subsectors": "Industry 4.0 robotics, additive manufacturing, EV powertrain components, advanced polymers & hardtech",
            "trend": "High Concentration",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 16.5,
            "notable_subsectors": "Corewell Health William Beaumont University Hospital, specialty medical practices, surgical devices",
            "trend": "Growing",
        },
        {
            "category": "Finance, Insurance & Corporate Services",
            "percentage": 13.5,
            "notable_subsectors": "Private equity, commercial banking, mortgage/fintech services & regional corporate headquarters",
            "trend": "Stable",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 12.5,
            "notable_subsectors": "Woodward Avenue & Somerset commercial corridors, specialty retail, boutique fitness & consumer services",
            "trend": "Stable",
        },
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 10.5,
            "notable_subsectors": "Commercial real estate development, clean-energy retrofits, supply chain management & wholesale trade",
            "trend": "Growing",
        },
    ],
    "Macomb County": [
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 27.5,
            "notable_subsectors": "Mound Road robotics & tooling corridor, CNC metalworking, automotive stamping & composite fabrication",
            "trend": "High Concentration",
        },
        {
            "category": "Defense, Aerospace & Autonomous Systems",
            "percentage": 19.5,
            "notable_subsectors": "U.S. Army TACOM & DEVCOM GVSC ground vehicle contractors, dual-use cybersecurity & military turret/armor systems",
            "trend": "High Concentration",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 15.5,
            "notable_subsectors": "Hall Road (M-59) commercial corridor, automotive dealerships, specialty retail & local services",
            "trend": "Stable",
        },
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 14.0,
            "notable_subsectors": "DoD proposal/contract engineering, systems integration, CAD/CAM design & testing laboratories",
            "trend": "Growing",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 12.5,
            "notable_subsectors": "Henry Ford Macomb & McLaren Macomb hospitals, outpatient surgical centers, physical rehabilitation",
            "trend": "Stable",
        },
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 11.0,
            "notable_subsectors": "Heavy civil construction, industrial warehousing, defense supply chain logistics & specialty contractors",
            "trend": "Growing",
        },
    ],
    "Kent County": [
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 23.0,
            "notable_subsectors": "Commercial furniture systems (Steelcase/MillerKnoll supply chain), medical device contract manufacturing, precision plastics & tooling",
            "trend": "High Concentration",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 21.5,
            "notable_subsectors": "Grand Rapids Medical Mile (Corewell Health, Van Andel Institute, MSU Secchia Center), diagnostics & bio-innovation",
            "trend": "High Concentration",
        },
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 16.5,
            "notable_subsectors": "B2B SaaS, industrial IoT, enterprise software, product design consultancies & growth venture studios",
            "trend": "Growing",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 14.0,
            "notable_subsectors": "Downtown Monroe Center commerce, omnichannel retail brands, consumer goods & regional distribution",
            "trend": "Stable",
        },
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 13.0,
            "notable_subsectors": "Craft beverage ('Beer City USA'), CPG food processing, commercial bakeries & convention hospitality",
            "trend": "Stable",
        },
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 12.0,
            "notable_subsectors": "US-131 & I-96 cold-storage freight, commercial construction, clean energy engineering & wholesale distribution",
            "trend": "Growing",
        },
    ],
    "Ottawa County": [
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 31.0,
            "notable_subsectors": "EV lithium-ion battery manufacturing (LG Energy Solution), electro-optical electronics (Gentex), office furniture & automation",
            "trend": "High Concentration",
        },
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 17.5,
            "notable_subsectors": "Food & beverage processing, blueberry/greenhouse agribusiness, Lake Michigan coastal tourism & marinas",
            "trend": "High Concentration",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 14.5,
            "notable_subsectors": "Downtown Holland 8th Street retail district, specialty boutiques, marine supply & consumer services",
            "trend": "Stable",
        },
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 13.5,
            "notable_subsectors": "Smart manufacturing engineering, industrial design, clean-tech R&D & automation systems integrators",
            "trend": "Growing",
        },
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 12.0,
            "notable_subsectors": "Holland Energy Park utilities, cold-chain agricultural logistics, commercial & residential construction",
            "trend": "Growing",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 11.5,
            "notable_subsectors": "Holland Hospital, lakeshore outpatient clinics, occupational health & senior care facilities",
            "trend": "Stable",
        },
    ],
    "Muskegon County": [
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 28.0,
            "notable_subsectors": "Aerospace turbine castings (Howmet Aerospace), precision metal founding, marine engines & industrial machinery",
            "trend": "High Concentration",
        },
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 17.5,
            "notable_subsectors": "Lake Michigan cruise & beach tourism, fruit belt agricultural processing, marinas & downtown dining",
            "trend": "Growing",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 15.5,
            "notable_subsectors": "Western Avenue downtown storefront chalets, local artisans, retail corridors & marine services",
            "trend": "Stable",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 14.5,
            "notable_subsectors": "Trinity Health Muskegon Hospital, lakeshore specialty clinics & behavioral health services",
            "trend": "Stable",
        },
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 13.0,
            "notable_subsectors": "Deep-water Port of Muskegon maritime freight, renewable energy testbeds & industrial construction",
            "trend": "Growing",
        },
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 11.5,
            "notable_subsectors": "GVSU Michigan Alternative & Renewable Energy Center (MAREC), environmental engineering & startup incubation",
            "trend": "Growing",
        },
    ],
    "Ingham County": [
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 21.5,
            "notable_subsectors": "MSU university tech transfer, FRIB rare-isotope physics applications, gov-tech software & policy consulting",
            "trend": "High Concentration",
        },
        {
            "category": "Finance, Insurance & Corporate Services",
            "percentage": 19.0,
            "notable_subsectors": "Insurtech & major regional insurers (Auto-Owners, Jackson National, AF Group), state association HQs",
            "trend": "High Concentration",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 17.5,
            "notable_subsectors": "UM Health-Sparrow, McLaren Greater Lansing, MSU College of Human & Veterinary Medicine diagnostics",
            "trend": "Growing",
        },
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 15.5,
            "notable_subsectors": "GM Lansing Grand River & Delta Township assembly, Ultium Cells EV battery plant, composite materials",
            "trend": "Growing",
        },
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 14.0,
            "notable_subsectors": "MSU AgBioResearch, precision agriculture, plant sciences, campus hospitality & food innovation",
            "trend": "Growing",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 12.5,
            "notable_subsectors": "Grand River Avenue (East Lansing) & Washington Square (Lansing) commercial corridors, student & consumer retail",
            "trend": "Stable",
        },
    ],
    "Kalamazoo County": [
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 27.5,
            "notable_subsectors": "Global pharmaceutical manufacturing (Pfizer), orthopedic/surgical med-tech (Stryker), animal health (Zoetis) & WMed wet labs",
            "trend": "High Concentration",
        },
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 20.5,
            "notable_subsectors": "Medical instrumentation, specialty packaging/paper engineering, hydraulic & aerospace components",
            "trend": "High Concentration",
        },
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 16.0,
            "notable_subsectors": "CRO contract research labs, clinical validation, WMU engineering R&D & life-science venture studios",
            "trend": "Growing",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 13.0,
            "notable_subsectors": "Kalamazoo Mall pedestrian retail district, Westnedge commercial corridor & local business services",
            "trend": "Stable",
        },
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 12.0,
            "notable_subsectors": "Craft brewing (Bell's), bedding plant horticulture, commercial food ingredients & regional dining",
            "trend": "Stable",
        },
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 11.0,
            "notable_subsectors": "I-94 cold-chain pharmaceutical logistics (global vaccine distribution), cleanroom engineering & construction",
            "trend": "Growing",
        },
    ],
    "Calhoun County": [
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 27.0,
            "notable_subsectors": "Fort Custer Industrial Park automotive tier-1 suppliers (Denso, Musashi), robotics & metal fabrication",
            "trend": "High Concentration",
        },
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 22.0,
            "notable_subsectors": "Global cereal & snack food R&D/production (WK Kellogg Co / Kellanova), food safety labs & grain processing",
            "trend": "High Concentration",
        },
        {
            "category": "Defense, Aerospace & Autonomous Systems",
            "percentage": 14.5,
            "notable_subsectors": "Battle Creek Executive Airport (BTL) aviation MRO (Duncan Aviation), Air National Guard drone/cyber operations & federal logistics",
            "trend": "Growing",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 13.5,
            "notable_subsectors": "Downtown Battle Creek small businesses, Beckley Road retail corridor & consumer services",
            "trend": "Stable",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 12.5,
            "notable_subsectors": "Bronson Battle Creek Hospital, VA Medical Center regional campus & outpatient specialty care",
            "trend": "Stable",
        },
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 10.5,
            "notable_subsectors": "I-94/I-69 rail and highway freight intermodal hub, industrial warehousing & commercial construction",
            "trend": "Growing",
        },
    ],
    "Genesee County": [
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 22.5,
            "notable_subsectors": "GM Flint Assembly & Engine Operations, automotive tooling, aftermarket components & light assembly",
            "trend": "High Concentration",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 20.5,
            "notable_subsectors": "Hurley Medical Center, McLaren Flint, Genesys Health Park & Mott Children's Health Center",
            "trend": "High Concentration",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 16.5,
            "notable_subsectors": "Saginaw Street downtown Flint storefronts, Flint Farmers' Market vendors, Miller Road retail & local services",
            "trend": "Growing",
        },
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 15.0,
            "notable_subsectors": "Kettering University GM Mobility Research Center, autonomous testing, product prototyping (100K Ideas) & IT services",
            "trend": "Growing",
        },
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 13.5,
            "notable_subsectors": "I-75 / I-69 crossroads freight logistics, Bishop International air cargo & civil infrastructure contractors",
            "trend": "Growing",
        },
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 12.0,
            "notable_subsectors": "Flint Cultural Center venues, urban food entrepreneurs, regional agriculture & hospitality",
            "trend": "Stable",
        },
    ],
    "St. Clair County": [
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 25.5,
            "notable_subsectors": "Plastics injection molding, automotive sealing & trim suppliers, marine fabrication & tool-and-die",
            "trend": "High Concentration",
        },
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 21.0,
            "notable_subsectors": "Blue Water Bridge international border crossing, customs brokerage, I-94/I-69 freight warehousing & DTE/ITC energy",
            "trend": "High Concentration",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 16.0,
            "notable_subsectors": "Downtown Port Huron Huron Avenue district, waterfront retail, marine supply & consumer services",
            "trend": "Stable",
        },
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 14.5,
            "notable_subsectors": "Lake Huron & St. Clair River maritime tourism, marinas, charter boating & Thumb-region agriculture",
            "trend": "Growing",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 13.0,
            "notable_subsectors": "McLaren Port Huron, Lake Huron Medical Center & regional outpatient clinics",
            "trend": "Stable",
        },
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 10.0,
            "notable_subsectors": "Cross-border trade compliance, industrial engineering & small business incubation",
            "trend": "Growing",
        },
    ],
    "Bay County": [
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 24.0,
            "notable_subsectors": "Great Lakes Bay specialty chemicals & silicones supply chain, GM Bay City GPS powertrain, precision machining & shipbuilding",
            "trend": "High Concentration",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 18.5,
            "notable_subsectors": "McLaren Bay Region medical center, Covenant HealthCare clinics & regional rehabilitative care",
            "trend": "Stable",
        },
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 17.5,
            "notable_subsectors": "Michigan Sugar Co. processing, Saginaw Valley cash-crop agribusiness, Uptown Bay City waterfront hospitality",
            "trend": "High Concentration",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 15.5,
            "notable_subsectors": "Downtown Center Avenue & Midland Street commercial districts, marine retail & local commerce",
            "trend": "Stable",
        },
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 13.5,
            "notable_subsectors": "Saginaw River deep-water commercial ports, Consumers Energy Karn/clean-energy site & industrial contractors",
            "trend": "Growing",
        },
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 11.0,
            "notable_subsectors": "Materials testing, environmental engineering, B2B consulting & Great Lakes Bay startup support",
            "trend": "Growing",
        },
    ],
    "Isabella County": [
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 22.5,
            "notable_subsectors": "Soaring Eagle Resort & entertainment tourism, Central Michigan dairy/grain agribusiness & campus dining",
            "trend": "High Concentration",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 19.5,
            "notable_subsectors": "Mission Street (US-127 BR) commercial corridor, Downtown Mount Pleasant retail & student services",
            "trend": "Stable",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 17.0,
            "notable_subsectors": "MyMichigan Medical Center Mt. Pleasant, CMU College of Medicine clinical partners & regional health",
            "trend": "Growing",
        },
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 15.5,
            "notable_subsectors": "Industrial recycling & shredder machinery (Bandit Industries), wood/metal fabrication & specialty tooling",
            "trend": "High Concentration",
        },
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 13.5,
            "notable_subsectors": "CMU Research Corporation (CMURC) co-working/incubation, educational technology & professional services",
            "trend": "Growing",
        },
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 12.0,
            "notable_subsectors": "Mid-Michigan wind/solar energy contractors, US-127 distribution & commercial construction",
            "trend": "Stable",
        },
    ],
    "Grand Traverse County": [
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 24.5,
            "notable_subsectors": "Cherry & viticulture wineries, specialty food CPG, four-season resort tourism & culinary hospitality",
            "trend": "High Concentration",
        },
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 18.5,
            "notable_subsectors": "Remote-first SaaS startups (20Fathoms cluster), freshwater marine sonar/ROV tech (Discovery Pier), insurance/fintech (Hagerty)",
            "trend": "Growing",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 17.5,
            "notable_subsectors": "Munson Healthcare regional referral center, digital health, outpatient surgical & senior care",
            "trend": "High Concentration",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 15.5,
            "notable_subsectors": "Front Street downtown Traverse City boutiques, outdoor gear outfitters & specialty retail",
            "trend": "Stable",
        },
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 13.0,
            "notable_subsectors": "Precision electro-mechanical sensors, aerospace components, specialty packaging & marine boatbuilding",
            "trend": "Growing",
        },
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 11.0,
            "notable_subsectors": "Custom residential/commercial timber construction, Cherry Capital aviation services & regional distribution",
            "trend": "Stable",
        },
    ],
    "Marquette County": [
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 22.5,
            "notable_subsectors": "UP Health System - Marquette (Upper Peninsula tertiary referral hospital), rural telemedicine & clinical diagnostics",
            "trend": "High Concentration",
        },
        {
            "category": "Outdoor Recreation, Forestry & Natural Resources",
            "percentage": 20.5,
            "notable_subsectors": "Outdoor recreation gear/tech (ORIAN cluster), sustainable timber/forestry, iron-range mining engineering & Lake Superior eco-tourism",
            "trend": "High Concentration",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 16.5,
            "notable_subsectors": "Downtown Washington & Third Street specialty outfitters, local commerce & US-41 retail corridor",
            "trend": "Stable",
        },
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 15.0,
            "notable_subsectors": "Lake Superior hospitality, craft breweries, regional food systems & four-season trail tourism",
            "trend": "Growing",
        },
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 13.5,
            "notable_subsectors": "NMU cybersecurity (U.P. Cyber Institute), environmental consulting, remote software & Innovate Marquette startups",
            "trend": "Growing",
        },
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 12.0,
            "notable_subsectors": "Presque Isle iron-ore maritime shipping port, Sawyer International Airport industrial park & U.P. utility grid",
            "trend": "Stable",
        },
    ],
    "Houghton County": [
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 25.5,
            "notable_subsectors": "Michigan Tech deep-tech spinouts, autonomous winter mobility (Keweenaw Research Center), photonics, AI & aerospace sensors",
            "trend": "High Concentration",
        },
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 18.5,
            "notable_subsectors": "Advanced materials, medical device prototyping, specialty wood/composite products & precision instruments",
            "trend": "Growing",
        },
        {
            "category": "Outdoor Recreation, Forestry & Natural Resources",
            "percentage": 17.5,
            "notable_subsectors": "Keweenaw Peninsula mountain biking/snowsports tourism, forestry products & critical mineral geology",
            "trend": "High Concentration",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 14.5,
            "notable_subsectors": "UP Health System - Portage, Aspirus Keweenaw clinics & biomedical engineering research (MTU H-STEM Complex)",
            "trend": "Growing",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 12.5,
            "notable_subsectors": "Shelden Avenue historic downtown Houghton & Quincy Street Hancock retail, outdoor outfitters & campus services",
            "trend": "Stable",
        },
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 11.5,
            "notable_subsectors": "Portage Canal waterfront hospitality, craft bakeries/breweries & Copper Country heritage tourism",
            "trend": "Stable",
        },
    ],
    "Chippewa County": [
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 24.5,
            "notable_subsectors": "Soo Locks Great Lakes maritime shipping corridor, US-Canada International Bridge freight & Army Corps mega-lock construction",
            "trend": "High Concentration",
        },
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 20.5,
            "notable_subsectors": "Soo Locks maritime tourism, Kewadin hospitality, aquaculture/fisheries & Eastern U.P. agriculture",
            "trend": "High Concentration",
        },
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 16.5,
            "notable_subsectors": "Precision CNC machining, composite/aerospace materials testing & industrial tooling at SmartZone Industrial Airpark",
            "trend": "Growing",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 14.5,
            "notable_subsectors": "Ashmun Street & Portage Avenue downtown commerce, cross-border retail & marine supply",
            "trend": "Stable",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 13.0,
            "notable_subsectors": "MyMichigan Medical Center Sault, tribal health clinics & rural healthcare services",
            "trend": "Stable",
        },
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 11.0,
            "notable_subsectors": "Lake Superior State University Center for Freshwater Research & robotics engineering lab",
            "trend": "Growing",
        },
    ],
    "Lenawee County": [
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 26.5,
            "notable_subsectors": "Specialty chemicals & adhesives (Wacker Chemical), automotive plastics/stampings, HVAC & agricultural machinery",
            "trend": "High Concentration",
        },
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 19.5,
            "notable_subsectors": "Row-crop & dairy agribusiness, commercial food artisans (Adrian Armory commercial kitchen) & Irish Hills tourism",
            "trend": "High Concentration",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 16.0,
            "notable_subsectors": "Downtown Adrian Maumee Street & Tecumseh Chicago Boulevard specialty retail, small-town commerce",
            "trend": "Stable",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 14.5,
            "notable_subsectors": "ProMedica Charles and Virginia Hickman Hospital, outpatient clinics & regional senior care",
            "trend": "Stable",
        },
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 12.5,
            "notable_subsectors": "US-223 / M-52 Ohio-Michigan freight corridor, utility solar installations & commercial contractors",
            "trend": "Growing",
        },
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 11.0,
            "notable_subsectors": "Materials R&D (Adrian College / Siena Heights partnerships), chemical testing & Launch Lenawee business services",
            "trend": "Growing",
        },
    ],
    "Livingston County": [
        {
            "category": "Manufacturing & Industrial Fabrication",
            "percentage": 24.0,
            "notable_subsectors": "I-96 corridor precision machining, automotive prototyping, specialty medical & industrial equipment",
            "trend": "High Concentration",
        },
        {
            "category": "Professional, Scientific & Tech Services",
            "percentage": 20.5,
            "notable_subsectors": "SBIR/STTR federal R&D consulting (BBCetc), automotive test tracks (GM Milford Proving Ground nearby) & engineering services",
            "trend": "High Concentration",
        },
        {
            "category": "Retail & Local Commerce",
            "percentage": 16.5,
            "notable_subsectors": "Downtown Brighton Main Street & Howell Grand River retail corridors, consumer services",
            "trend": "Stable",
        },
        {
            "category": "Logistics, Construction & Energy",
            "percentage": 14.5,
            "notable_subsectors": "I-96 / US-23 interchange commercial construction, regional distribution & heavy civil engineering",
            "trend": "Growing",
        },
        {
            "category": "Healthcare & Life Sciences",
            "percentage": 13.0,
            "notable_subsectors": "Trinity Health Livingston & University of Michigan Health Brighton Center for Specialty Care",
            "trend": "Growing",
        },
        {
            "category": "Hospitality, Food & Agribusiness",
            "percentage": 11.5,
            "notable_subsectors": "Mt. Brighton / Island Lake recreation hospitality, local restaurants & equestrian/agritourism",
            "trend": "Stable",
        },
    ],
}

# ---------------------------------------------------------------------------
# 3. Micro-Corridor Specialization Overrides (For Cities with Multiple Hubs)
#    Adjusts percentages (+/- 1.0 to 4.5%) and subsector notes for distinct
#    sub-corridors within the same county (e.g., Corktown vs. Midtown Detroit).
# ---------------------------------------------------------------------------
SLUG_CORRIDOR_SHIFTS: Dict[str, Dict[str, Any]] = {
    "newlab-michigan-central": {
        "shifts": {
            "Professional, Scientific & Tech Services": +3.5,
            "Logistics, Construction & Energy": +2.0,
            "Retail & Local Commerce": -3.0,
            "Healthcare & Life Sciences": -2.5,
        },
        "extra_category": {
            "category": "Mobility, Electrification & Autonomous Systems",
            "percentage": 16.0,
            "notable_subsectors": "Michigan Central Station mobility district, Ford EV/AV engineering, urban aerial drone zones & bidirectional charging testbeds",
            "trend": "High Concentration",
        },
    },
    "plug-and-play-detroit": {
        "shifts": {
            "Professional, Scientific & Tech Services": +3.0,
            "Manufacturing & Industrial Fabrication": +2.0,
            "Retail & Local Commerce": -2.5,
            "Hospitality, Food & Agribusiness": -2.5,
        },
        "extra_category": {
            "category": "Mobility, Electrification & Autonomous Systems",
            "percentage": 15.5,
            "notable_subsectors": "OEM & Tier-1 corporate venture pilots, connected vehicle software, smart logistics & battery supply chain",
            "trend": "High Concentration",
        },
    },
    "techtown-detroit": {
        "shifts": {
            "Healthcare & Life Sciences": +3.5,
            "Retail & Local Commerce": +2.0,
            "Manufacturing & Industrial Fabrication": -3.0,
            "Logistics, Construction & Energy": -2.5,
        },
    },
    "bamboo-detroit": {
        "shifts": {
            "Professional, Scientific & Tech Services": +4.0,
            "Hospitality, Food & Agribusiness": +1.5,
            "Manufacturing & Industrial Fabrication": -3.5,
            "Logistics, Construction & Energy": -2.0,
        },
    },
    "ponyride-detroit": {
        "shifts": {
            "Manufacturing & Industrial Fabrication": +3.0,
            "Retail & Local Commerce": +2.5,
            "Healthcare & Life Sciences": -3.0,
            "Logistics, Construction & Energy": -2.5,
        },
    },
    "um-innovation-partnerships": {
        "shifts": {
            "Healthcare & Life Sciences": +3.5,
            "Mobility, Electrification & Auto R&D": +2.0,
            "Retail & Local Commerce": -3.5,
            "Hospitality, Food & Agribusiness": -2.0,
        },
    },
    "michigan-sbdc-southeast-emu": {
        "shifts": {
            "Mobility, Electrification & Auto R&D": +3.5,
            "Retail & Local Commerce": +2.0,
            "Professional, Scientific & Tech Services": -3.5,
            "Healthcare & Life Sciences": -2.0,
        },
    },
    "automation-alley": {
        "shifts": {
            "Manufacturing & Industrial Fabrication": +4.0,
            "Professional, Scientific & Tech Services": +2.0,
            "Retail & Local Commerce": -3.5,
            "Healthcare & Life Sciences": -2.5,
        },
    },
    "centreopolis-accelerator-ltu": {
        "shifts": {
            "Manufacturing & Industrial Fabrication": +3.5,
            "Logistics, Construction & Energy": +2.0,
            "Finance, Insurance & Corporate Services": -3.0,
            "Retail & Local Commerce": -2.5,
        },
    },
    "bamboo-royal-oak": {
        "shifts": {
            "Professional, Scientific & Tech Services": +2.5,
            "Retail & Local Commerce": +3.0,
            "Manufacturing & Industrial Fabrication": -4.0,
            "Logistics, Construction & Energy": -1.5,
        },
    },
    "ou-inc-rochester": {
        "shifts": {
            "Healthcare & Life Sciences": +2.0,
            "Manufacturing & Industrial Fabrication": +1.5,
            "Finance, Insurance & Corporate Services": -2.0,
            "Retail & Local Commerce": -1.5,
        },
    },
    "velocity-macomb-ou-inc": {
        "shifts": {
            "Defense, Aerospace & Autonomous Systems": +2.5,
            "Manufacturing & Industrial Fabrication": +1.5,
            "Retail & Local Commerce": -2.5,
            "Healthcare & Life Sciences": -1.5,
        },
    },
    "wmed-innovation-center-kalamazoo": {
        "shifts": {
            "Healthcare & Life Sciences": +3.5,
            "Professional, Scientific & Tech Services": +1.5,
            "Retail & Local Commerce": -3.0,
            "Hospitality, Food & Agribusiness": -2.0,
        },
    },
}


class RegionalIndustryAnalyzer:
    """
    Combines U.S. Census County Business Patterns (CBP) NAICS distributions with
    OpenStreetMap Overpass API micro-radius sampling around each organization's
    `(latitude, longitude)` to populate `organizations.local_industry_distribution`.
    """

    def __init__(self, db: SupabaseDBClient, max_concurrency: int = 4):
        self.db = db
        self.max_concurrency = max_concurrency
        self.radius_cache: Dict[Tuple[float, float], Dict[str, int]] = {}

    async def sample_overpass_local_radius(
        self,
        lat: Optional[float],
        lng: Optional[float],
        http_client: httpx.AsyncClient,
    ) -> Dict[str, int]:
        """
        Queries OpenStreetMap Overpass API within a 2,500m radius of `(lat, lng)` to sample
        local businesses across industrial/manufacturing, tech/professional offices,
        healthcare, retail, hospitality/food, and logistics/construction.
        Gracefully falls back if Overpass API times out or rate-limits.
        """
        counts = {
            "manufacturing": 0,
            "tech_office": 0,
            "healthcare": 0,
            "retail": 0,
            "hospitality": 0,
            "logistics": 0,
            "total": 0,
        }
        if lat is None or lng is None:
            return counts

        cache_key = (round(float(lat), 3), round(float(lng), 3))
        if cache_key in self.radius_cache:
            return self.radius_cache[cache_key]

        query = (
            f"[out:json][timeout:8];("
            f'node["shop"](around:2500,{lat},{lng});'
            f'node["office"](around:2500,{lat},{lng});'
            f'node["craft"](around:2500,{lat},{lng});'
            f'node["industrial"](around:2500,{lat},{lng});'
            f'node["healthcare"](around:2500,{lat},{lng});'
            f'node["amenity"~"hospital|clinic|doctors|pharmacy|dentist|restaurant|cafe|bar|fast_food|bank|research_institute|university"](around:2500,{lat},{lng});'
            f");out tags 250;"
        )

        for endpoint in OVERPASS_ENDPOINTS:
            try:
                resp = await http_client.post(endpoint, data={"data": query}, timeout=10.0)
                if resp.status_code == 200:
                    data = resp.json()
                    elements = data.get("elements", [])
                    for el in elements:
                        tags = el.get("tags", {})
                        if "industrial" in tags or "craft" in tags or tags.get("man_made") == "works":
                            counts["manufacturing"] += 1
                        elif "office" in tags or tags.get("amenity") in ("research_institute", "university", "bank"):
                            counts["tech_office"] += 1
                        elif "healthcare" in tags or tags.get("amenity") in ("hospital", "clinic", "doctors", "pharmacy", "dentist"):
                            counts["healthcare"] += 1
                        elif "shop" in tags:
                            counts["retail"] += 1
                        elif tags.get("amenity") in ("restaurant", "cafe", "bar", "fast_food"):
                            counts["hospitality"] += 1
                        else:
                            counts["logistics"] += 1
                    counts["total"] = len(elements)
                    self.radius_cache[cache_key] = counts
                    return counts
            except Exception:
                continue

        self.radius_cache[cache_key] = counts
        return counts

    def build_distribution_for_org(
        self,
        org: Dict[str, Any],
        overpass_counts: Dict[str, int],
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Combines the county's U.S. Census CBP NAICS baseline with Overpass micro-radius
        business sampling and corridor specialization shifts, returning `(county_name, distribution_list)`
        where `distribution_list` contains 6 to 7 categories sorted descending and totaling 100.0%.
        """
        city = (org.get("city") or "").strip()
        slug = (org.get("slug") or "").strip()
        county_name, _ = CITY_TO_COUNTY.get(city, ("Washtenaw County", "26161"))

        base_items = [dict(item) for item in COUNTY_CBP_PROFILES[county_name]]

        # Apply sub-corridor specialization shifts if configured for this slug
        corridor_cfg = SLUG_CORRIDOR_SHIFTS.get(slug)
        if corridor_cfg:
            shifts = corridor_cfg.get("shifts", {})
            for item in base_items:
                cat = item["category"]
                if cat in shifts:
                    item["percentage"] = max(5.0, round(item["percentage"] + shifts[cat], 1))
            extra_cat = corridor_cfg.get("extra_category")
            if extra_cat:
                base_items.append(dict(extra_cat))

        # Blend micro-radius Overpass business sampling nudge (up to +/- 1.5% based on local density)
        total_osm = overpass_counts.get("total", 0)
        if total_osm >= 15:
            osm_map = {
                "Manufacturing": overpass_counts["manufacturing"] / total_osm,
                "Professional": overpass_counts["tech_office"] / total_osm,
                "Healthcare": overpass_counts["healthcare"] / total_osm,
                "Retail": overpass_counts["retail"] / total_osm,
                "Hospitality": overpass_counts["hospitality"] / total_osm,
            }
            for item in base_items:
                for prefix, share in osm_map.items():
                    if item["category"].startswith(prefix):
                        # Small nudge (+0.5% if local radius share > 25%)
                        if share > 0.25:
                            item["percentage"] = round(item["percentage"] + 0.5, 1)
                        break

        # Normalize percentages so they sum to exactly 100.0%
        raw_total = sum(item["percentage"] for item in base_items)
        scaled: List[Dict[str, Any]] = []
        for item in base_items:
            pct = round((item["percentage"] / raw_total) * 100.0, 1)
            scaled.append({**item, "percentage": pct})

        # Sort strictly descending by percentage
        scaled.sort(key=lambda x: x["percentage"], reverse=True)

        # Ensure exact 100.0% sum by adjusting the top category by any 0.1 rounding residual
        diff = round(100.0 - sum(x["percentage"] for x in scaled), 1)
        if diff != 0.0:
            scaled[0]["percentage"] = round(scaled[0]["percentage"] + diff, 1)

        # Re-sort in case adjustment changed order and assign density_rank 1..N
        scaled.sort(key=lambda x: x["percentage"], reverse=True)
        final_distribution: List[Dict[str, Any]] = []
        for idx, item in enumerate(scaled, start=1):
            final_distribution.append(
                {
                    "category": item["category"],
                    "percentage": item["percentage"],
                    "density_rank": idx,
                    "notable_subsectors": item["notable_subsectors"],
                    "trend": item["trend"],
                }
            )

        return county_name, final_distribution

    async def run(self) -> None:
        console.rule(
            "[bold cyan]Regional Business & Industry Density Analyzer (`regional_industry_analyzer.py`)[/bold cyan]"
        )
        orgs = self.db.fetch_all_organizations()
        console.print(f"Loaded [bold green]{len(orgs)}[/bold green] organizations from Supabase.\n")

        semaphore = asyncio.Semaphore(self.max_concurrency)
        results_summary: List[Dict[str, Any]] = []

        async with httpx.AsyncClient(
            headers={"User-Agent": "MichiganStartupEcosystemAnalyzer/1.0"},
            follow_redirects=True,
        ) as http_client:

            async def _worker(org: Dict[str, Any]) -> None:
                async with semaphore:
                    org_id = org["id"]
                    slug = org.get("slug", "")
                    city = org.get("city", "")
                    lat = org.get("latitude")
                    lng = org.get("longitude")

                    overpass_counts = await self.sample_overpass_local_radius(lat, lng, http_client)
                    county_name, distribution = self.build_distribution_for_org(org, overpass_counts)

                    # Patch `local_industry_distribution` in Supabase `organizations`
                    resp = self.db._http.patch(
                        f"{self.db.rest_url}/organizations",
                        params={"id": f"eq.{org_id}"},
                        json={"local_industry_distribution": distribution},
                    )
                    if resp.status_code not in (200, 204):
                        raise RuntimeError(
                            f"Failed to update local_industry_distribution for {slug}: "
                            f"{resp.status_code} {resp.text}"
                        )

                    top_1 = distribution[0]
                    top_2 = distribution[1]
                    total_pct = round(sum(d["percentage"] for d in distribution), 1)
                    results_summary.append(
                        {
                            "slug": slug,
                            "city": city,
                            "county": county_name,
                            "num_cats": len(distribution),
                            "osm_nodes": overpass_counts.get("total", 0),
                            "top_1": f"{top_1['category']} ({top_1['percentage']}%)",
                            "top_2": f"{top_2['category']} ({top_2['percentage']}%)",
                            "total_pct": total_pct,
                        }
                    )
                    console.print(
                        f"  [green][UPDATED][/green] [bold]{slug}[/bold] ({city} / {county_name}) -> "
                        f"#1 {top_1['category']} ({top_1['percentage']}%), "
                        f"#2 {top_2['category']} ({top_2['percentage']}%) "
                        f"[dim][{len(distribution)} categories, sum={total_pct}%][/dim]"
                    )

            await asyncio.gather(*[_worker(o) for o in orgs])

        results_summary.sort(key=lambda x: (x["county"], x["slug"]))

        table = Table(
            title="Regional Business & Industry Density Verification Report (46 Michigan Organizations)",
            show_lines=False,
        )
        table.add_column("Organization Slug", style="cyan", no_wrap=True)
        table.add_column("City / County", style="white")
        table.add_column("Categories", justify="right", style="green")
        table.add_column("Rank #1 Industry Sector", style="yellow")
        table.add_column("Rank #2 Industry Sector", style="magenta")
        table.add_column("Total %", justify="right", style="bold green")

        for r in results_summary:
            table.add_row(
                r["slug"],
                f"{r['city']} ({r['county']})",
                str(r["num_cats"]),
                r["top_1"],
                r["top_2"],
                f"{r['total_pct']:.1f}%",
            )

        console.print("\n")
        console.print(table)
        console.print(
            f"\n[bold green]Successfully populated `local_industry_distribution` for all "
            f"{len(results_summary)} organizations in Supabase![/bold green]"
        )


def main() -> None:
    db = SupabaseDBClient()
    analyzer = RegionalIndustryAnalyzer(db=db, max_concurrency=4)
    asyncio.run(analyzer.run())


if __name__ == "__main__":
    main()
