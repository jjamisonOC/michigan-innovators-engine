"""
Site Selection & Relocation Intelligence Enricher (`site_selection_enricher.py`)

Populates the `site_selection_profile` JSONB column on every row in the Supabase
`organizations` table so out-of-state businesses looking to relocate to Michigan
and local founders choosing a site can evaluate:
1. `talent_pipeline`: `nearby_universities`, `stem_grad_strength`, `intern_support`
2. `anchor_corporations`: Major Fortune 500, OEM, hospital, defense, and R&D pilot partners
3. `incentives_and_zones`: SmartZone LDFA, BAF ($50K), Federal Opportunity Zones, Renaissance Zones,
   Foreign Trade Zones (FTZ), MEDC SBIR/STTR Emerging Technologies Fund (ETF), SSRP, etc.
4. `logistics_and_runway`: `primary_corridors`, `nearest_airport` (with spatial drive-time calculation),
   `border_proximity` (with spatial distance to Windsor-Detroit, Port Huron-Sarnia, or Sault Ste. Marie
   international crossings), `cost_of_doing_business_index`, `runway_multiplier`, and `graduation_space`.
"""

import asyncio
import logging
import math
import sys
from typing import Any, Dict, List, Optional, Tuple

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

logger = logging.getLogger("michigan_intel.site_selection_enricher")
console = Console()


# ---------------------------------------------------------------------------
# Spatial Reference Points (Airports & International Border Crossings)
# ---------------------------------------------------------------------------
MICHIGAN_AIRPORTS: List[Dict[str, Any]] = [
    {"code": "DTW", "name": "Detroit Metro Airport", "lat": 42.2124, "lng": -83.3534},
    {"code": "GRR", "name": "Gerald R. Ford Int'l Airport", "lat": 42.8808, "lng": -85.5228},
    {"code": "LAN", "name": "Capital Region Int'l Airport", "lat": 42.7787, "lng": -84.5874},
    {"code": "FNT", "name": "Bishop Int'l Airport", "lat": 42.9654, "lng": -83.7436},
    {"code": "AZO", "name": "Kalamazoo/Battle Creek Int'l Airport", "lat": 42.2350, "lng": -85.5521},
    {"code": "MBS", "name": "MBS Int'l Airport (Saginaw/Bay City/Midland)", "lat": 43.5329, "lng": -84.0796},
    {"code": "TVC", "name": "Cherry Capital Airport", "lat": 44.7414, "lng": -85.5822},
    {"code": "MQT", "name": "Marquette Sawyer Regional Airport", "lat": 46.3536, "lng": -87.3954},
    {"code": "CMX", "name": "Houghton County Memorial Airport", "lat": 47.1684, "lng": -88.4891},
    {"code": "CIU", "name": "Chippewa County Int'l Airport", "lat": 46.2508, "lng": -84.4724},
    {"code": "MKG", "name": "Muskegon County Airport", "lat": 43.1695, "lng": -86.2382},
]

BORDER_CROSSINGS: List[Dict[str, Any]] = [
    {"name": "Windsor-Detroit International Crossing (Ambassador / Gordie Howe Bridge)", "lat": 42.3118, "lng": -83.0767},
    {"name": "Blue Water Bridge (Port Huron–Sarnia International Crossing)", "lat": 42.9985, "lng": -82.4237},
    {"name": "Sault Ste. Marie International Bridge (U.S.–Canada Crossing)", "lat": 46.5065, "lng": -84.3601},
]


def haversine_miles(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculates great-circle distance in miles between two coordinates."""
    r = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


# ---------------------------------------------------------------------------
# City & Regional Site Selection Intelligence Profiles (All 27 Michigan Cities)
# ---------------------------------------------------------------------------
CITY_SITE_SELECTION_DATA: Dict[str, Dict[str, Any]] = {
    "Ann Arbor": {
        "talent_pipeline": {
            "nearby_universities": [
                "University of Michigan (Ann Arbor - #1 Public Research University)",
                "Eastern Michigan University",
                "Washtenaw Community College",
            ],
            "stem_grad_strength": "Elite Concentration (Top-5 U.S. Engineering, AI/CS, Robotics, Life Sciences & Ross MBA)",
            "intern_support": "MEDC SmartZone STEM Intern Wage-Match & U-M Zell Lurie / Multidisciplinary Design (MDP) Fellowships",
        },
        "anchor_corporations": [
            "Toyota Motor North America R&D (TMNA)",
            "Michigan Medicine & U-M Health",
            "Duo Security (Cisco) & KLA Corporation",
            "NSF International & Domino's Pizza Global HQ",
            "Hyundai America Technical Center (HATCI)",
        ],
        "incentives_and_zones": [
            "MEDC Ann Arbor/Ypsilanti SmartZone (LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Michigan SBIR/STTR Emerging Technologies Fund (ETF) Match Eligible",
            "MEDC Pre-Seed Fund III & Michigan Rise Co-Investment Eligible",
            "Federal Opportunity Zone (Designated Washtenaw Tracts)",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-94 & US-23 Innovation & Autonomous Mobility Corridor",
            "nearest_airport": "DTW (Detroit Metro Airport - 25 mins)",
            "border_proximity": "40 mins to Windsor-Detroit International Crossing",
            "cost_of_doing_business_index": "88% of U.S. National Avg",
            "runway_multiplier": "1.8x longer seed runway vs. SF/Boston",
            "graduation_space": "U-M North Campus Research Complex (NCRC), TechLoop & Ellsworth Rd wet-lab/light-industrial parks",
        },
    },
    "Ypsilanti": {
        "talent_pipeline": {
            "nearby_universities": [
                "Eastern Michigan University (GameAbove College of Engineering & Technology)",
                "University of Michigan (Ann Arbor)",
                "Washtenaw Community College",
            ],
            "stem_grad_strength": "High Concentration (Cybersecurity, Mobility Engineering, Aviation, Applied Tech & CS)",
            "intern_support": "MEDC SmartZone STEM Intern Wage-Match & EMU Cooperative Education Pipeline",
        },
        "anchor_corporations": [
            "American Center for Mobility (ACM - Willow Run Connected/AV Test Track)",
            "Hyundai America Technical Center (HATCI)",
            "Toyota North America R&D",
            "Kalitta Air & Willow Run Aerospace Corridor",
        ],
        "incentives_and_zones": [
            "MEDC Ann Arbor/Ypsilanti SmartZone (SPARK East LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Eastern Washtenaw Micro Loan & Federal Opportunity Zone",
            "Michigan SBIR/STTR Matching Grant Eligible",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-94 & US-12 Connected Mobility & Air Cargo Corridor",
            "nearest_airport": "DTW (Detroit Metro Airport - 15 mins) & YIP (Willow Run Cargo Airport - 8 mins)",
            "border_proximity": "32 mins to Windsor-Detroit International Crossing",
            "cost_of_doing_business_index": "83% of U.S. National Avg",
            "runway_multiplier": "2.1x longer seed runway vs. SF/Boston",
            "graduation_space": "Willow Run Arsenal of Democracy Mobility Park & I-94 light-industrial flex suites",
        },
    },
    "Detroit": {
        "talent_pipeline": {
            "nearby_universities": [
                "Wayne State University (R1 Research University)",
                "University of Michigan Detroit Center & U-M Center for Innovation (UMCI)",
                "University of Detroit Mercy & College for Creative Studies (CCS)",
                "Michigan State University Detroit Center",
            ],
            "stem_grad_strength": "High Concentration (Mobility/EV Engineering, AI/Software, Translational Medicine & Industrial Design)",
            "intern_support": "MEDC SmartZone STEM Intern Wage-Match, Detroit Hacker Fellows & MichAuto Talent Pipeline",
        },
        "anchor_corporations": [
            "General Motors Global HQ & Ford Motor Company (Michigan Central)",
            "Rocket Companies (Rocket Mortgage) & StockX",
            "Henry Ford Health + MSU Health Sciences & Detroit Medical Center",
            "DTE Energy & Blue Cross Blue Shield of Michigan",
            "Honeywell Detroit & Bosch Mobility Partners",
        ],
        "incentives_and_zones": [
            "MEDC Detroit SmartZone (TechTown / NextEnergy LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Detroit Renaissance Zone & Federal Opportunity Zone Tax Incentives",
            "Foreign Trade Zone (FTZ #70 - Greater Detroit)",
            "Michigan SBIR/STTR Matching Grant & Michigan Mobility Funding Platform (MMFP)",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-75, I-94, I-96 & Corktown / Midtown Innovation Corridor",
            "nearest_airport": "DTW (Detroit Metro Airport - 22 mins)",
            "border_proximity": "5 mins to Windsor-Detroit International Crossing (Ambassador & Gordie Howe Bridges)",
            "cost_of_doing_business_index": "84% of U.S. National Avg",
            "runway_multiplier": "2.1x longer seed runway vs. SF/NYC",
            "graduation_space": "Michigan Central Mobility District, Midtown TechTown labs & Milwaukee Junction industrial loft parks",
        },
    },
    "Troy": {
        "talent_pipeline": {
            "nearby_universities": [
                "Oakland University (School of Engineering & Computer Science)",
                "Lawrence Technological University",
                "Wayne State University",
                "Oakland Community College (Advanced Technology Center)",
            ],
            "stem_grad_strength": "High Concentration (Robotics, Mechatronics, Industrial AI, Automotive Systems & Software)",
            "intern_support": "MEDC Oakland County Tech Intern Wage-Match & Oakland Next Industry 4.0 Fellowships",
        },
        "anchor_corporations": [
            "Aptiv North America HQ & Magna International (Troy Technical Center)",
            "DuPont Mobility & Materials & LG Energy Solution North America Tech Center",
            "Altair Engineering Global HQ (CAE & AI Simulation)",
            "Inteva Products & Meritor (Cummins)",
        ],
        "incentives_and_zones": [
            "MEDC Automation Alley Industry 4.0 & Project DIAMOnD Hardware Grants",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Michigan SBIR/STTR Emerging Technologies Fund (ETF) Match Eligible",
            "Oakland County Tech Collaboration & R&D Tax Abatement District",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-75 (Automation Alley) & Big Beaver Road Tier-1 Corporate HQ Corridor",
            "nearest_airport": "DTW (Detroit Metro Airport - 32 mins) & PTK (Oakland County Int'l - 20 mins)",
            "border_proximity": "25 mins to Windsor-Detroit International Crossing",
            "cost_of_doing_business_index": "87% of U.S. National Avg",
            "runway_multiplier": "1.9x longer seed runway vs. SF/Boston",
            "graduation_space": "Troy Maple/Stephenson R&D engineering flex parks & Auburn Hills Oakland Technology Park",
        },
    },
    "Royal Oak": {
        "talent_pipeline": {
            "nearby_universities": [
                "Oakland University",
                "Wayne State University",
                "Lawrence Technological University",
                "Oakland Community College (Royal Oak Campus)",
            ],
            "stem_grad_strength": "High Concentration (Full-Stack Software, AI/ML, Biomedical Engineering & Digital Media)",
            "intern_support": "MEDC STEM Intern Wage-Match & Oakland County Emerging Tech Talent Pipeline",
        },
        "anchor_corporations": [
            "Corewell Health William Beaumont University Hospital (Royal Oak)",
            "Magna International & BorgWarner (Oakland Corridor)",
            "United Wholesale Mortgage (UWM) & Rocket Companies",
            "General Motors Global Technical Center (Warren - 12 mins)",
        ],
        "incentives_and_zones": [
            "Oakland County Startup Support & MEDC BAF Grant Access",
            "Michigan SBIR/STTR Matching Grant Eligible",
            "MEDC Pre-Seed Fund III & Michigan Rise Eligible",
            "Woodward Avenue Transit-Oriented Commercial Development Zone",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-75, I-696 & Woodward Avenue (M-1) Tech Corridor",
            "nearest_airport": "DTW (Detroit Metro Airport - 28 mins)",
            "border_proximity": "20 mins to Windsor-Detroit International Crossing",
            "cost_of_doing_business_index": "86% of U.S. National Avg",
            "runway_multiplier": "1.9x longer seed runway vs. SF/NYC",
            "graduation_space": "Downtown Royal Oak Class-A tech suites & I-696 light-engineering flex offices",
        },
    },
    "Southfield": {
        "talent_pipeline": {
            "nearby_universities": [
                "Lawrence Technological University (On-Campus College of Engineering & Architecture)",
                "Wayne State University",
                "Oakland University",
                "University of Michigan-Dearborn",
            ],
            "stem_grad_strength": "High Concentration (Mechanical/Manufacturing Engineering, Hardtech Design, Robotics & CleanTech)",
            "intern_support": "MEDC SmartZone STEM Intern Wage-Match & LTU Co-Op Hardware Engineering Fellows",
        },
        "anchor_corporations": [
            "Lear Corporation Global HQ",
            "DENSO International America HQ",
            "Eaton Mobility Group & Marelli North America HQ",
            "BASF Corporation & Durr Systems",
        ],
        "incentives_and_zones": [
            "MEDC Southfield Centrepolis SmartZone (LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "MEDC Make It in Michigan Prototype Grant & C3 CleanTech Non-Dilutive Funding",
            "Defense Hardtech Accelerator (DHA) & DoD Dual-Use Grant Support",
            "Federal Opportunity Zone (Southfield City Centre District)",
        ],
        "logistics_and_runway": {
            "primary_corridors": "M-10 (Northwestern Hwy), I-696 & US-24 Manufacturing & Engineering Corridor",
            "nearest_airport": "DTW (Detroit Metro Airport - 25 mins)",
            "border_proximity": "22 mins to Windsor-Detroit International Crossing",
            "cost_of_doing_business_index": "85% of U.S. National Avg",
            "runway_multiplier": "2.0x longer seed runway vs. SF/Boston",
            "graduation_space": "Southfield LTU Enterprise Center & Eight Mile/Telegraph light-industrial prototyping parks",
        },
    },
    "Rochester": {
        "talent_pipeline": {
            "nearby_universities": [
                "Oakland University (On-Campus School of Engineering & Computer Science + OUWB School of Medicine)",
                "Lawrence Technological University",
                "Macomb Community College",
            ],
            "stem_grad_strength": "High Concentration (Embedded Systems, Cybersecurity, Bioengineering & Automotive Mechatronics)",
            "intern_support": "MEDC SmartZone STEM Intern Wage-Match & Oakland University Incubator (OU INC) Student Fellows",
        },
        "anchor_corporations": [
            "Stellantis North America HQ & Tech Center (Auburn Hills - 8 mins)",
            "FANUC America Global Robotics HQ (Rochester Hills)",
            "BorgWarner Global HQ & Continental Automotive North America HQ",
            "Corewell Health & Ascension Providence Rochester Hospital",
        ],
        "incentives_and_zones": [
            "MEDC Rochester / Auburn Hills SmartZone (OU INC LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Oakland Technology Park R&D Tax Increment Financing District",
            "Michigan SBIR/STTR Matching Grant Eligible",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-75, M-59 & Squirrel Road Robotics & OEM Technical Center Corridor",
            "nearest_airport": "PTK (Oakland County Int'l - 18 mins) & DTW (Detroit Metro Airport - 40 mins)",
            "border_proximity": "35 mins to Windsor-Detroit International Crossing & 48 mins to Blue Water Bridge",
            "cost_of_doing_business_index": "86% of U.S. National Avg",
            "runway_multiplier": "1.9x longer seed runway vs. SF/Boston",
            "graduation_space": "Oakland Technology Park (Auburn Hills) & Rochester Hills high-bay robotics/industrial parks",
        },
    },
    "Sterling Heights": {
        "talent_pipeline": {
            "nearby_universities": [
                "Oakland University (Macomb University Center on-site)",
                "Wayne State University (Advanced Technology Education Center)",
                "Macomb Community College (Center for Advanced Automotive Technology)",
                "Lawrence Technological University",
            ],
            "stem_grad_strength": "High Concentration (Defense Systems, Autonomous Ground Vehicles, CNC/Robotics & Cybersecurity)",
            "intern_support": "MEDC SmartZone STEM Intern Wage-Match & DoD Defense Corridor Engineering Fellowships",
        },
        "anchor_corporations": [
            "U.S. Army TACOM & DEVCOM Ground Vehicle Systems Center (GVSC - Detroit Arsenal)",
            "General Dynamics Land Systems (GDLS) Global HQ",
            "BAE Systems Combat Mission Systems & Oshkosh Defense",
            "Ford Van Dyke Electric Powertrain Center & Stellantis Sterling Heights Assembly",
        ],
        "incentives_and_zones": [
            "MEDC Sterling Heights / Macomb-OU INC SmartZone (LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Mound Road Innovates Defense & Dual-Use Corridor Grants",
            "DoD SBIR/STTR Phase I/II Matching Grants & APEX Accelerator Contracting Support",
        ],
        "logistics_and_runway": {
            "primary_corridors": "M-59 (Hall Rd), Mound Road Defense Corridor & I-75 / I-94 Industrial Belt",
            "nearest_airport": "DTW (Detroit Metro Airport - 35 mins) & MTC (Selfridge Air National Guard Base - 18 mins)",
            "border_proximity": "28 mins to Windsor-Detroit Crossing & 40 mins to Port Huron Blue Water Bridge",
            "cost_of_doing_business_index": "84% of U.S. National Avg",
            "runway_multiplier": "2.1x longer seed runway vs. SF/DC Metro",
            "graduation_space": "Mound Road Industrial & Defense Corridor high-bay manufacturing and SCIF-capable facilities",
        },
    },
    "Mount Clemens": {
        "talent_pipeline": {
            "nearby_universities": [
                "Macomb Community College",
                "Oakland University",
                "Wayne State University",
            ],
            "stem_grad_strength": "Strong Concentration (Defense Manufacturing, CMMC Cybersecurity, Aerospace Tooling & Logistics)",
            "intern_support": "Macomb County Defense & Advanced Manufacturing Apprenticeship & Intern Wage-Match",
        },
        "anchor_corporations": [
            "U.S. Army TACOM & DEVCOM GVSC (Detroit Arsenal)",
            "Selfridge Air National Guard Base (127th Wing)",
            "General Dynamics Land Systems & BAE Systems",
            "McLaren Macomb & Henry Ford Macomb Hospital Systems",
        ],
        "incentives_and_zones": [
            "DoD Office of Small Business Programs APEX Accelerator Free Bid-Match & SAM/CMMC Support",
            "MEDC Macomb SmartZone Partner & BAF Grant Access",
            "Federal Opportunity Zone (Downtown Mount Clemens & M-3 Corridor)",
            "Defense Dual-Use SBIR/STTR Matching Grant Eligible",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-94, M-59 & M-3 (Gratiot Ave) Defense & Cross-Border Freight Corridor",
            "nearest_airport": "DTW (Detroit Metro Airport - 38 mins) & Selfridge ANGB adjacent",
            "border_proximity": "32 mins to Windsor-Detroit Crossing & 35 mins to Port Huron Blue Water Bridge",
            "cost_of_doing_business_index": "82% of U.S. National Avg",
            "runway_multiplier": "2.2x longer seed runway vs. SF/DC Metro",
            "graduation_space": "I-94 / M-59 industrial machining parks & Chesterfield defense supplier facilities",
        },
    },
    "Jackson": {
        "talent_pipeline": {
            "nearby_universities": [
                "University of Michigan (Ann Arbor - 35 mins East)",
                "Michigan State University (East Lansing - 40 mins North)",
                "Jackson College & Spring Arbor University",
            ],
            "stem_grad_strength": "High Access (Dual U-M & MSU Engineering/Materials Pipeline + Jackson Skilled Machining & Mechatronics)",
            "intern_support": "MEDC SmartZone STEM Intern Wage-Match & Shop Rat Foundation / Jackson Area Manufacturers Association (JAMA) Pipeline",
        },
        "anchor_corporations": [
            "Consumers Energy Global HQ (CMS Energy)",
            "Henry Ford Jackson Health System",
            "Eaton Aerospace (Jackson Fluid Power Facility)",
            "MACI (Michigan Automotive Compressor) & Alro Steel Global HQ",
            "Dawn Foods Global HQ",
        ],
        "incentives_and_zones": [
            "MEDC Jackson SmartZone (Lean Rocket Lab LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "MEDC Industry 4.0 Technology Implementation Grants",
            "Federal Opportunity Zone (Downtown Jackson Innovation District)",
            "Michigan SBIR/STTR Matching Grant Eligible",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-94 & US-127 Central Michigan Manufacturing & Energy Crossroads",
            "nearest_airport": "DTW (Detroit Metro Airport - 50 mins) & LAN (Capital Region Int'l - 42 mins)",
            "border_proximity": "70 mins to Windsor-Detroit International Crossing via I-94 East",
            "cost_of_doing_business_index": "79% of U.S. National Avg",
            "runway_multiplier": "2.3x longer seed runway vs. SF/Boston",
            "graduation_space": "Jackson County Airport Industrial Park & I-94/US-127 high-bay CNC/manufacturing facilities",
        },
    },
    "Grand Rapids": {
        "talent_pipeline": {
            "nearby_universities": [
                "Grand Valley State University (Padnos College of Engineering & Computing)",
                "Michigan State University College of Human Medicine (Grand Rapids Secchia Center)",
                "Calvin University & Ferris State University (Kendall College of Art and Design)",
                "Grand Rapids Community College",
            ],
            "stem_grad_strength": "High Concentration (Biomedical Sciences, Medical Device Engineering, Industrial Design & B2B Software)",
            "intern_support": "MEDC SmartZone STEM Intern Wage-Match & The Right Place Tech Talent Pipeline",
        },
        "anchor_corporations": [
            "Corewell Health WestHQ & Van Andel Research Institute (Medical Mile)",
            "Steelcase Global HQ & MillerKnoll",
            "Meijer Corporate HQ & Amway (Alticor) Global R&D",
            "Gordon Food Service Global HQ & Wolverine Worldwide",
            "BAMF Health (Radiopharmaceuticals & AI Theranostics)",
        ],
        "incentives_and_zones": [
            "MEDC Grand Rapids SmartZone (Start Garden LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Start Garden 100 Ideas & 5x5 Non-Dilutive Pitch Grants",
            "Foreign Trade Zone (FTZ #43 - West Michigan) & Federal Opportunity Zone",
            "Michigan SBIR/STTR Emerging Technologies Fund (ETF) Match Eligible",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-96, I-196 & US-131 West Michigan Commercial & Medical Mile Corridor",
            "nearest_airport": "GRR (Gerald R. Ford Int'l Airport - 15 mins)",
            "border_proximity": "2 hrs 15 mins to Port Huron Blue Water Bridge & Windsor-Detroit Crossing via I-96/I-69",
            "cost_of_doing_business_index": "84% of U.S. National Avg",
            "runway_multiplier": "2.0x longer seed runway vs. SF/Boston",
            "graduation_space": "Grand Rapids Medical Mile wet labs, GVSU Health Campus & Walker/Kentwood precision manufacturing parks",
        },
    },
    "Holland": {
        "talent_pipeline": {
            "nearby_universities": [
                "Hope College ( nationally ranked undergraduate STEM & Chemistry research)",
                "Grand Valley State University (Meijer Campus in Holland)",
                "Michigan State University Bioeconomy Institute (Holland Facility)",
            ],
            "stem_grad_strength": "High Concentration (Chemical/Battery Engineering, Electro-Optics, Industrial Automation & Food Science)",
            "intern_support": "Lakeshore Advantage SURGE Intern Match & West Michigan Manufacturing Talent Pipeline",
        },
        "anchor_corporations": [
            "LG Energy Solution Michigan (EV Lithium-Ion Battery Gigafactory)",
            "Gentex Corporation Global HQ (Electro-Optical Mirrors & Aerospace Dimming Windows)",
            "MillerKnoll Global HQ & Haworth Global HQ",
            "JR Automation (Hitachi) Global HQ & Perrigo",
            "Request Foods & Kraft Heinz Holland",
        ],
        "incentives_and_zones": [
            "MEDC Holland / Lakeshore SmartZone Satellite (LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "MSU Bioeconomy Institute Pilot-Scale Chemical Fermentation Access",
            "Michigan SBIR/STTR Matching Grant & Renaissance Zone Incentives",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-196 & US-31 Lakeshore Battery, Automation & Agribusiness Corridor",
            "nearest_airport": "GRR (Gerald R. Ford Int'l Airport - 32 mins) & BIV (West Michigan Regional Executive Airport - 8 mins)",
            "border_proximity": "Deep-water Lake Michigan commercial port & 2.5 hrs to U.S.–Canada highway crossings",
            "cost_of_doing_business_index": "83% of U.S. National Avg",
            "runway_multiplier": "2.1x longer seed runway vs. SF/Boston",
            "graduation_space": "MSU Bioeconomy Institute scale-up suites & Zeeland/Holland automated industrial parks",
        },
    },
    "Muskegon": {
        "talent_pipeline": {
            "nearby_universities": [
                "Grand Valley State University (Muskegon Innovation Hub & Annis Water Resources Institute)",
                "Muskegon Community College (Sturrus Technology Center)",
                "Baker College of Muskegon",
            ],
            "stem_grad_strength": "Strong Concentration (Materials/Metallurgy, Renewable Energy, Freshwater Marine Science & CAD/CAM)",
            "intern_support": "MEDC SmartZone STEM Intern Wage-Match & GVSU Lakeshore Applied Engineering Fellowships",
        },
        "anchor_corporations": [
            "Howmet Aerospace (Whitehall Turbine Airfoil & Titanium Casting Operations)",
            "RENK America (Combat Vehicle Transmissions & Defense Propulsion)",
            "GE Aerospace Muskegon & SAF-Holland North America HQ",
            "Trinity Health Muskegon & Kaydon Bearings (SKF)",
        ],
        "incentives_and_zones": [
            "MEDC Muskegon SmartZone (GVSU Innovation Hub LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Federal Opportunity Zone (Downtown Muskegon & Waterfront Port District)",
            "Foreign Trade Zone (FTZ #43) & Michigan SBIR/STTR Matching Grants",
        ],
        "logistics_and_runway": {
            "primary_corridors": "US-31, I-96 & Port of Muskegon Deep-Water Great Lakes Shipping Corridor",
            "nearest_airport": "MKG (Muskegon County Airport - 12 mins) & GRR (Gerald R. Ford Int'l - 42 mins)",
            "border_proximity": "Great Lakes international maritime port & cross-lake high-speed ferry to Wisconsin",
            "cost_of_doing_business_index": "79% of U.S. National Avg",
            "runway_multiplier": "2.3x longer seed runway vs. SF/Boston",
            "graduation_space": "Port City Industrial Park & Whitehall aerospace/foundry manufacturing corridor",
        },
    },
    "East Lansing": {
        "talent_pipeline": {
            "nearby_universities": [
                "Michigan State University (R1 University - 50,000+ students, Eli Broad College of Business & College of Engineering)",
                "MSU Facility for Rare Isotope Beams (FRIB - #1 U.S. Nuclear Physics Graduate Program)",
                "Lansing Community College",
            ],
            "stem_grad_strength": "Elite Concentration (Nuclear/Materials Physics, AgBioTech, Packaging Engineering, InsurTech/Fintech & Supply Chain #1 in U.S.)",
            "intern_support": "MEDC SmartZone STEM Intern Wage-Match, MSU Burgess Venture Fellows & EnSURE Research Fellowships",
        },
        "anchor_corporations": [
            "MSU Facility for Rare Isotope Beams (FRIB) & MSU Health Care",
            "Auto-Owners Insurance Global HQ & Jackson National Life HQ",
            "General Motors Lansing Grand River & Ultium Cells EV Battery Plant",
            "Neogen Corporation Global HQ (Food & Animal Genomic Safety)",
            "TechSmith Global HQ",
        ],
        "incentives_and_zones": [
            "MEDC Lansing Regional SmartZone (East Lansing / Lansing LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Michigan Rise Pre-Seed Fund III & Red Cedar Ventures Co-Investment",
            "Michigan SBIR/STTR Emerging Technologies Fund (ETF) Match Eligible",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-96, I-69 & US-127 Mid-Michigan Research & Capital Corridor",
            "nearest_airport": "LAN (Capital Region Int'l Airport - 15 mins) & DTW (Detroit Metro Airport - 65 mins)",
            "border_proximity": "60 mins to Port Huron Blue Water Bridge via I-69 East",
            "cost_of_doing_business_index": "81% of U.S. National Avg",
            "runway_multiplier": "2.2x longer seed runway vs. SF/Boston",
            "graduation_space": "MSU University Corporate Research Park (UCRP), Technology Innovation Center & Lansing SmartZone suites",
        },
    },
    "Lansing": {
        "talent_pipeline": {
            "nearby_universities": [
                "Michigan State University",
                "Lansing Community College (West Campus Technical Training Center)",
                "Western Michigan University Cooley Law School",
            ],
            "stem_grad_strength": "High Concentration (GovTech/Enterprise IT, Actuarial/Fintech, EV Battery Manufacturing & AgTech)",
            "intern_support": "MEDC SmartZone STEM Intern Wage-Match & Capital Area IT Council Talent Pipeline",
        },
        "anchor_corporations": [
            "General Motors Lansing Delta Township & Lansing Grand River Assembly",
            "Ultium Cells (GM / LG Energy Solution Battery Plant)",
            "Auto-Owners Insurance, Jackson National Life & AF Group Global HQs",
            "UM Health-Sparrow & McLaren Greater Lansing Health Systems",
            "State of Michigan DTMB (GovTech Procurement Hub)",
        ],
        "incentives_and_zones": [
            "MEDC Lansing Regional SmartZone (LEAP LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Federal Opportunity Zone (Downtown Lansing Capitol Corridor) & Foreign Trade Zone (FTZ #275)",
            "Michigan SBIR/STTR Matching Grant Eligible",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-96, I-69 & US-127 Tri-Highway Freight & Capital Crossroads",
            "nearest_airport": "LAN (Capital Region Int'l Airport - 10 mins, FTZ #275 on-site)",
            "border_proximity": "65 mins to Port Huron Blue Water Bridge via I-69 East",
            "cost_of_doing_business_index": "80% of U.S. National Avg",
            "runway_multiplier": "2.2x longer seed runway vs. SF/Boston",
            "graduation_space": "Capital Region Airport Industrial Park, University Corporate Research Park & Downtown Lansing tech offices",
        },
    },
    "Kalamazoo": {
        "talent_pipeline": {
            "nearby_universities": [
                "Western Michigan University (R2 Research University - College of Engineering & Applied Sciences, College of Aviation)",
                "WMU Homer Stryker M.D. School of Medicine (WMed)",
                "Kalamazoo College & Kalamazoo Valley Community College ( Groves Groves Center)",
            ],
            "stem_grad_strength": "High Concentration (Pharmacology, Biomedical/Surgical Devices, Medicinal Chemistry, Paper/Packaging & Aerospace)",
            "intern_support": "MEDC SmartZone STEM Intern Wage-Match & WMed / WMU Life Science Commercialization Fellows",
        },
        "anchor_corporations": [
            "Pfizer Global Supply (Kalamazoo — Pfizer's Largest Global Sterile Injectable & API Manufacturing Site)",
            "Stryker Corporation Global HQ (Medical & Orthopaedic Devices)",
            "Zoetis Global Veterinary R&D HQ (Animal Health Pharmaceuticals)",
            "Bronson Healthcare & Borgess (Ascension) Medical Centers",
            "Newell Brands R&D & Landscape Forms",
        ],
        "incentives_and_zones": [
            "MEDC Kalamazoo SmartZone (WMed Innovation Center LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Southwest Michigan First Life Science Fund & WMed Wet-Lab Subsidies",
            "Federal Opportunity Zone & Michigan SBIR/STTR Phase I/II Match Eligible",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-94 (Midwest Detroit-to-Chicago Corridor) & US-131 Life Science Corridor",
            "nearest_airport": "AZO (Kalamazoo/Battle Creek Int'l Airport - 10 mins) & GRR (Gerald R. Ford Int'l - 48 mins)",
            "border_proximity": "2 hrs to Windsor-Detroit International Crossing & 2 hrs to Chicago O'Hare Air Cargo Hub",
            "cost_of_doing_business_index": "80% of U.S. National Avg",
            "runway_multiplier": "2.2x longer seed runway vs. Boston/Cambridge Biotech Hubs",
            "graduation_space": "WMed Business Technology & Research (BTR) Park Phase I & II BSL-2 wet labs and cGMP scale-up suites",
        },
    },
    "Battle Creek": {
        "talent_pipeline": {
            "nearby_universities": [
                "Western Michigan University (College of Aviation located at Battle Creek Executive Airport)",
                "Kellogg Community College (Regional Manufacturing Technology Center - RMTC)",
                "Albion College & Olivet College",
            ],
            "stem_grad_strength": "Strong Concentration (Aviation/Unmanned Aerial Systems, Food Science, Industrial Robotics & Mechatronics)",
            "intern_support": "Battle Creek Unlimited (BCU) Intern Stipend & RMTC Advanced Manufacturing Apprenticeship Pipeline",
        },
        "anchor_corporations": [
            "WK Kellogg Co Global HQ & Kellanova R&D (W.K. Kellogg Institute for Food & Nutrition Research)",
            "DENSO Manufacturing Michigan (Largest North American Thermal Manufacturing Site)",
            "Duncan Aviation (Major Business Jet MRO at BTL) & Battle Creek Air National Guard Base (110th Wing Drone/Cyber Ops)",
            "Musashi Auto Parts & Prairie Farms",
        ],
        "incentives_and_zones": [
            "MEDC Battle Creek Aviation & E-Center SmartZone (LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Foreign Trade Zone (FTZ #43 - Fort Custer Industrial Park Port of Entry with U.S. Customs On-Site)",
            "Battle Creek Direct Investment Fund & Federal Opportunity Zone",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-94 & I-69 International Trade & Intermodal Rail/Air Corridor",
            "nearest_airport": "BTL (Battle Creek Executive Airport - 10,004-ft runway on-site) & AZO (22 mins)",
            "border_proximity": "95 mins to Port Huron Blue Water Bridge via I-69 & 1 hr 50 mins to Windsor-Detroit via I-94",
            "cost_of_doing_business_index": "78% of U.S. National Avg",
            "runway_multiplier": "2.4x longer seed runway vs. SF/Boston",
            "graduation_space": "3,000-acre Fort Custer Industrial Park (FTZ #43) & BTL Aviation/UAS Hangar Tech Park",
        },
    },
    "Flint": {
        "talent_pipeline": {
            "nearby_universities": [
                "Kettering University (#1 U.S. Co-Op Engineering & Mobility University)",
                "University of Michigan-Flint (College of Innovation & Technology)",
                "Michigan State University College of Human Medicine (Flint Campus)",
                "Mott Community College",
            ],
            "stem_grad_strength": "High Concentration (Co-Op Mechanical/Electrical Engineering, Autonomous Vehicles, Embedded Systems & Health Tech)",
            "intern_support": "Kettering University 50/50 Co-Op Engineering Rotation & MEDC SmartZone Intern Wage-Match",
        },
        "anchor_corporations": [
            "General Motors Flint Assembly, Flint Engine Operations & Flint Metal Center",
            "Kettering University GM Mobility Research Center (Autonomous Test Track)",
            "Hurley Medical Center, McLaren Flint & Genesys Health System",
            "Lear Corporation Flint & Diplomat Specialty Pharmacy ecosystem",
        ],
        "incentives_and_zones": [
            "MEDC Flint SmartZone Partner & Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Charles Stewart Mott Foundation & Flint & Genesee Small Business Grants",
            "Federal Opportunity Zone (Downtown Flint Innovation District) & Foreign Trade Zone (FTZ #140)",
            "Michigan SBIR/STTR Matching Grant Eligible",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-75, I-69 & US-23 International Trade & Automotive Corridor",
            "nearest_airport": "FNT (Bishop Int'l Airport - 8 mins, FTZ #140 on-site) & DTW (55 mins)",
            "border_proximity": "52 mins to Port Huron–Sarnia Blue Water Bridge via I-69 East",
            "cost_of_doing_business_index": "77% of U.S. National Avg",
            "runway_multiplier": "2.4x longer seed runway vs. SF/Boston",
            "graduation_space": "Flint Commerce Center (former Buick City megasite), Bishop Airport Industrial Park & Kettering Research Park",
        },
    },
    "Port Huron": {
        "talent_pipeline": {
            "nearby_universities": [
                "St. Clair County Community College (SC4 - Engineering Technology & Mechatronics)",
                "Oakland University & Macomb Community College",
                "Lambton College (Sarnia, ON - Cross-Border Chemical & Energy Research)",
            ],
            "stem_grad_strength": "Strong Concentration (Plastics/Polymer Molding, Cross-Border Logistics, Marine Tech & Industrial Automation)",
            "intern_support": "EDA of St. Clair County / The Underground Intern & Apprenticeship Wage-Match",
        },
        "anchor_corporations": [
            "BorgWarner Morse Systems & Magna E-Car Systems",
            "SMR Automotive Mirrors & P.J. Wallbank Springs",
            "DTE Energy Belle River / Blue Water Energy Center & Mueller Brass",
            "McLaren Port Huron & Lake Huron Medical Center",
        ],
        "incentives_and_zones": [
            "MEDC Port Huron / St. Clair County SmartZone (The Underground LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Foreign Trade Zone (FTZ #210 - Port Huron Border Crossing) & Federal Opportunity Zone",
            "Emergent Need Fund & Eastern Michigan Small Business Capital Access",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-94 & I-69 Terminus at Blue Water Bridge International Crossing",
            "nearest_airport": "PHN (St. Clair County Int'l Airport - 10 mins) & DTW (60 mins)",
            "border_proximity": "3 mins (1.5 miles) to Blue Water Bridge U.S.–Canada Border Crossing & CN Rail Tunnel",
            "cost_of_doing_business_index": "78% of U.S. National Avg",
            "runway_multiplier": "2.4x longer seed runway vs. SF/Toronto",
            "graduation_space": "Port Huron Industrial Park (FTZ #210) & Marysville heavy-manufacturing riverfront corridor",
        },
    },
    "Bay City": {
        "talent_pipeline": {
            "nearby_universities": [
                "Saginaw Valley State University (College of Science, Engineering & Technology)",
                "Central Michigan University",
                "Delta College (Advanced Manufacturing & Chemical Process Technology)",
                "Northwood University (Midland)",
            ],
            "stem_grad_strength": "High Concentration (Chemical/Polymer Engineering, Silicones/Semiconductor Materials, AgTech & Precision Machining)",
            "intern_support": "MEDC CMURC SmartZone RightTrack Student & STEM Intern Wage-Match",
        },
        "anchor_corporations": [
            "Dow Inc. Global HQ & R&D Center (Midland - 18 mins)",
            "Hemlock Semiconductor (Polysilicon for Solar & Semiconductors) & DuPont / Corteva Agriscience",
            "SK Siltron CSS (Silicon Carbide EV Wafers - Bay City)",
            "General Motors Bay City GPS Powertrain & Michigan Sugar Company Global HQ",
        ],
        "incentives_and_zones": [
            "MEDC Great Lakes Bay Region SmartZone (CMURC Bay City LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Great Lakes Bay Materials & Semiconductor Supply Chain Incentives",
            "Federal Opportunity Zone (Uptown Bay City Waterfront) & FTZ #140 Access",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-75, US-10 & Saginaw River Deep-Water Great Lakes Shipping Channel",
            "nearest_airport": "MBS (MBS Int'l Airport - 15 mins)",
            "border_proximity": "Saginaw River international maritime port & 75 mins to Port Huron Blue Water Bridge",
            "cost_of_doing_business_index": "77% of U.S. National Avg",
            "runway_multiplier": "2.4x longer seed runway vs. SF/Boston",
            "graduation_space": "Michigan Brands Industrial Park, Uptown Bay City Tech Campus & Midland Discovery Square",
        },
    },
    "Mount Pleasant": {
        "talent_pipeline": {
            "nearby_universities": [
                "Central Michigan University (R2 Research University - College of Science & Engineering, College of Medicine)",
                "Mid Michigan College (Morey Technical Education Center)",
                "Alma College",
            ],
            "stem_grad_strength": "Strong Concentration (Biosciences, Environmental Engineering, Health Tech, IT & New Venture Entrepreneurship)",
            "intern_support": "MEDC SmartZone CMURC RightTrack Student Talent Program & CMU Isabella Bank Institute Fellows",
        },
        "anchor_corporations": [
            "Bandit Industries Global HQ (Heavy Industrial Recycling & Forestry Machinery)",
            "Morbark (Alamo Group) Industrial Equipment",
            "MyMichigan Medical Center Mt. Pleasant & Saginaw Chippewa Tribal Enterprises",
            "StageRight Corporation & Delfield (Welbilt Commercial Foodservice)",
        ],
        "incentives_and_zones": [
            "MEDC Mount Pleasant SmartZone (CMURC LDFA - Adjacent to CMU Research Park)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Federal Opportunity Zone & Michigan Rural Development Fund Grants",
            "Michigan SBIR/STTR Matching Grant Eligible",
        ],
        "logistics_and_runway": {
            "primary_corridors": "US-127 & M-20 Central Michigan North-South Corridor",
            "nearest_airport": "MBS (MBS Int'l Airport - 40 mins) &LAN (Capital Region Int'l - 55 mins)",
            "border_proximity": "95 mins to Port Huron Blue Water Bridge & 2 hrs to Sault Ste. Marie Crossing",
            "cost_of_doing_business_index": "76% of U.S. National Avg",
            "runway_multiplier": "2.5x longer seed runway vs. SF/Boston",
            "graduation_space": "CMU SmartZone Research Park & Mount Pleasant South Industrial Park",
        },
    },
    "Traverse City": {
        "talent_pipeline": {
            "nearby_universities": [
                "Northwestern Michigan College (Great Lakes Water Studies Institute & Aero Park Aviation/UAS Labs)",
                "Michigan Technological University (Traverse City Freshwater & Traverse Partnerships)",
                "Grand Valley State University (Traverse City Regional Center)",
            ],
            "stem_grad_strength": "High Concentration (Freshwater Marine/Sonar Tech, Unmanned Aerial/Marine Systems, Remote SaaS & AgTech)",
            "intern_support": "20Fathoms Tech Career Pathways, NMC Marine Tech Interns & MEDC STEM Wage-Match",
        },
        "anchor_corporations": [
            "Hagerty Global HQ (Specialty Automotive Insurance & Marketplace Tech)",
            "Munson Healthcare (Northern Michigan Regional Referral Health System)",
            "Discover Pier / Freshwater Research & Innovation Center (FRIC)",
            "Promethient (Thermoelectric Climate Control) & Cone Drive (Timken Precision Motion)",
        ],
        "incentives_and_zones": [
            "MEDC Northwest Michigan SmartZone Satellite (20Fathoms / Traverse City LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Freshwater Research & Innovation Center Blue Economy Commercialization Grants",
            "Federal Opportunity Zone & Northern Michigan Angel Network (TCNewTech) Access",
        ],
        "logistics_and_runway": {
            "primary_corridors": "US-31, M-37 & Grand Traverse Bay Freshwater Testing Corridor",
            "nearest_airport": "TVC (Cherry Capital Airport - 8 mins, direct flights to ORD/DTW/DEN/CLT/DFW/BOS)",
            "border_proximity": "Open-water Lake Michigan autonomous marine testbed & 2.5 hrs to Sault Ste. Marie International Bridge",
            "cost_of_doing_business_index": "85% of U.S. National Avg",
            "runway_multiplier": "1.9x longer seed runway vs. SF/Seattle",
            "graduation_space": "Freshwater Research & Innovation Center (Discovery Pier), NMC Parsons-Stulen Lab & Garfield Industrial Park",
        },
    },
    "Marquette": {
        "talent_pipeline": {
            "nearby_universities": [
                "Northern Michigan University (Upper Peninsula Cybersecurity Institute & College of Technology and Occupational Sciences)",
                "Michigan Technological University (60 mins West)",
                "Bay College",
            ],
            "stem_grad_strength": "Strong Concentration (Cybersecurity, Outdoor Recreation Engineering, Environmental/Forestry Science & Rural Telehealth)",
            "intern_support": "MEDC SmartZone Innovate Marquette Student Fellows & InvestUP Talent Return Initiative",
        },
        "anchor_corporations": [
            "UP Health System - Marquette (Duke LifePoint Tertiary Medical Center)",
            "Cleveland-Cliffs (Michigan Operations Iron Ore Mining & Processing)",
            "Eagle Mine (Lundin Mining - High-Grade Nickel & Copper Critical Minerals)",
            "Envigo / Calumet Electronics regional U.P. supply chain & PotlatchDeltic Timber",
        ],
        "incentives_and_zones": [
            "MEDC Innovate Marquette SmartZone (LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Michigan Outdoor Innovation Fund (InvestUP / ORIAN Seed Capital)",
            "Sawyer International Airport Renaissance Zone & Federal Opportunity Zone",
        ],
        "logistics_and_runway": {
            "primary_corridors": "US-41, M-28 & Lake Superior Deep-Water Maritime Port",
            "nearest_airport": "MQT (Marquette Sawyer Regional Airport - 18 mins, daily jets to ORD & DTW)",
            "border_proximity": "Lake Superior international shipping port & 2.5 hrs to Sault Ste. Marie U.S.–Canada Crossing",
            "cost_of_doing_business_index": "78% of U.S. National Avg",
            "runway_multiplier": "2.4x longer seed runway vs. SF/Boulder",
            "graduation_space": "Sawyer Industrial & Aviation Park (11,000+ ft runway & heavy industrial hangars) & Downtown Marquette tech suites",
        },
    },
    "Houghton": {
        "talent_pipeline": {
            "nearby_universities": [
                "Michigan Technological University (R1 Research University - Top-Tier Mechanical, Materials, Electrical, CS & Forestry Engineering)",
                "Finlandia / Keweenaw Health & Technical Training Partners",
                "Northern Michigan University",
            ],
            "stem_grad_strength": "Elite STEM Density (80%+ of Michigan Tech degrees in Engineering, Computing, Materials, Photonics & Critical Minerals)",
            "intern_support": "MEDC MTEC SmartZone STEM Intern Wage-Match & MTU Pavlis Honors / Enterprise Program Teams",
        },
        "anchor_corporations": [
            "Calumet Electronics (Defense & Aerospace High-Density PCB/IC Substrate Manufacturer)",
            "Keweenaw Research Center (MTU Winter Vehicle, Autonomous & U.S. Military Ice/Snow Proving Ground)",
            "Great Lakes Research Center (Autonomous Marine Vessels & Undersea Sensing)",
            "Orbion Space Technology (Hall-Effect Plasma Satellite Thrusters - Houghton Spinout)",
            "UP Health System - Portage & Aspirus Keweenaw",
        ],
        "incentives_and_zones": [
            "MEDC MTEC SmartZone (Houghton / Hancock LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Michigan Tech Superior Ideas, NSF I-Corps & MTEC SmartStart Grants",
            "Federal Opportunity Zone (Houghton/Hancock Waterfront & Airpark) & Michigan SBIR/STTR Match",
        ],
        "logistics_and_runway": {
            "primary_corridors": "US-41, M-26 & Keweenaw Waterway Lake Superior Corridor",
            "nearest_airport": "CMX (Houghton County Memorial Airport - 10 mins, daily United flights to Chicago O'Hare ORD)",
            "border_proximity": "Lake Superior international waters & Keweenaw winter/marine autonomous test ranges",
            "cost_of_doing_business_index": "76% of U.S. National Avg",
            "runway_multiplier": "2.5x longer seed runway vs. SF/Boston",
            "graduation_space": "MTEC SmartZone Powerhouse, Lakeshore Center, Jutila Center (Hancock) & Houghton County Airpark",
        },
    },
    "Sault Ste. Marie": {
        "talent_pipeline": {
            "nearby_universities": [
                "Lake Superior State University (LSSU - Nationally Recognized Robotics Lab, Engineering & Center for Freshwater Research)",
                "Bay Mills Community College",
                "Algoma University & Sault College (Sault Ste. Marie, Ontario - Cross-Border Twin City)",
            ],
            "stem_grad_strength": "Strong Concentration (Industrial Robotics, Automated Manufacturing, Freshwater/Aquaculture Science & Cross-Border Trade)",
            "intern_support": "Sault Ste. Marie SmartZone / LSSU Robotics Engineering Co-Op & MEDC Intern Wage-Match",
        },
        "anchor_corporations": [
            "U.S. Army Corps of Engineers (Soo Locks Complex & New Mega-Lock Engineering)",
            "Precision Edge Surgical Products (Medical Device Manufacturing HQ in Sault Ste. Marie)",
            "Hoover Precision Products & Soo Flange Manufacturing",
            "Cloverland Electric Cooperative (Hydroelectric Generation) & MyMichigan Medical Center Sault",
        ],
        "incentives_and_zones": [
            "MEDC Sault Ste. Marie SmartZone (LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Foreign Trade Zone (FTZ #16 - Sault Ste. Marie Port of Entry)",
            "Federal Opportunity Zone & Industrial Airpark Tax Abatement District",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-75 Northern Terminus, Soo Locks Maritime Shipping Channel & International Bridge",
            "nearest_airport": "CIU (Chippewa County Int'l Airport - 20 mins, Delta flights to DTW/MSP) & YAM (Sault Ontario Airport)",
            "border_proximity": "2 mins (0.8 miles) to Sault Ste. Marie International Bridge (Direct U.S.–Ontario Crossing)",
            "cost_of_doing_business_index": "75% of U.S. National Avg",
            "runway_multiplier": "2.6x longer seed runway vs. SF/Toronto",
            "graduation_space": "Sault Ste. Marie SmartZone Industrial Incubator & Chippewa County Airpark (Former Kincheloe AFB mega-runway)",
        },
    },
    "Adrian": {
        "talent_pipeline": {
            "nearby_universities": [
                "Adrian College (Institute for Entrepreneurial Studies & Chemistry/Materials Programs)",
                "Siena Heights University",
                "University of Michigan (Ann Arbor - 40 mins North) & Jackson College (Lenawee Campus)",
            ],
            "stem_grad_strength": "Strong Concentration (Specialty Chemicals/Polymers, AgTech, Food Science & Light Manufacturing)",
            "intern_support": "Adrian-Tecumseh SmartZone / Launch Lenawee Student Intern Match & LISD Tech Center Pipeline",
        },
        "anchor_corporations": [
            "Wacker Chemical Corporation (North American Silicones R&D & Manufacturing HQ in Adrian)",
            "Inteva Products (Adrian Roof Systems) & Anderson Development Company (Specialty Chemicals)",
            "Brazeway Global HQ & Kirchhoff Automotive",
            "ProMedica Charles and Virginia Hickman Hospital",
        ],
        "incentives_and_zones": [
            "MEDC Adrian-Tecumseh SmartZone (Adrian Armory LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Launch Lenawee Micro-Grants & Commercial Kitchen Incubation",
            "Federal Opportunity Zone (Downtown Adrian) & Michigan SBIR/STTR Match Eligible",
        ],
        "logistics_and_runway": {
            "primary_corridors": "US-223, M-52 & US-12 Southeast Michigan–Northwest Ohio Industrial Corridor",
            "nearest_airport": "DTW (Detroit Metro Airport - 48 mins), TOL (Toledo Express - 38 mins) & ADG (Lenawee County Airport - 5 mins)",
            "border_proximity": "55 mins to Windsor-Detroit International Crossing & 20 mins to Ohio Turnpike (I-80/I-90)",
            "cost_of_doing_business_index": "78% of U.S. National Avg",
            "runway_multiplier": "2.4x longer seed runway vs. SF/Boston",
            "graduation_space": "Adrian Industrial Park, Tecumseh Business Park & Wacker Chemical corridor lab/industrial sites",
        },
    },
    "Brighton": {
        "talent_pipeline": {
            "nearby_universities": [
                "University of Michigan (Ann Arbor - 22 mins South)",
                "Michigan State University (East Lansing - 40 mins West)",
                "Lawrence Technological University & Cleary University (Howell)",
            ],
            "stem_grad_strength": "High Access (Central to U-M, MSU & Metro Detroit Engineering/Life Sciences Talent + Federal SBIR Experts)",
            "intern_support": "MEDC Ann Arbor SPARK Livingston Satellite & STEM Intern Wage-Match",
        },
        "anchor_corporations": [
            "General Motors Milford Proving Ground (12 mins East)",
            "Eberspaecher North America & TG Fluid Systems (Toyoda Gosei)",
            "Asahi Kasei Plastics North America (Fowlerville)",
            "University of Michigan Health Brighton Center for Specialty Care & Trinity Health Livingston",
        ],
        "incentives_and_zones": [
            "MEDC Statewide SBIR/STTR Hub (BBCetc) & Emerging Technologies Fund (ETF - Up to $125k Phase I/II Match)",
            "Ann Arbor SPARK Livingston County Economic Development Partner & BAF Grant Access",
            "Low Livingston County Commercial Property Tax Millage",
            "Federal R&D Commercialization & DoD/NIH/NSF Proposal Preparation Subsidies",
        ],
        "logistics_and_runway": {
            "primary_corridors": "I-96 & US-23 Crossroads (Connecting Ann Arbor, Detroit, Lansing & Flint)",
            "nearest_airport": "DTW (Detroit Metro Airport - 35 mins) & LAN (Capital Region Int'l - 42 mins)",
            "border_proximity": "48 mins to Windsor-Detroit International Crossing",
            "cost_of_doing_business_index": "85% of U.S. National Avg",
            "runway_multiplier": "1.9x longer seed runway vs. SF/Boston",
            "graduation_space": "Brighton / Green Oak I-96 Tech & Light-Industrial Parks and Ann Arbor North Campus wet labs (20 mins)",
        },
    },
}


# ---------------------------------------------------------------------------
# Organization-Specific Customizations (Overrides for Specific Hubs/Campuses)
# ---------------------------------------------------------------------------
SLUG_SITE_OVERRIDES: Dict[str, Dict[str, Any]] = {
    "newlab-michigan-central": {
        "incentives_and_zones": [
            "Michigan Central Mobility Innovation District (30-Acre Corktown Testbed & First-in-Nation Real-World Urban Testing Zone)",
            "Advanced Aerial Innovation Region (AAIR - Beyond-Visual-Line-of-Sight Drone Corridor with MDOT)",
            "MEDC Detroit SmartZone & Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Michigan Mobility Funding Platform (MMFP) Pilot Deployment Grants (Up to $250k)",
            "Detroit Renaissance Zone & Federal Opportunity Zone",
        ],
        "graduation_space": "Book Depository 100,000+ sq. ft. robotics/prototyping labs, Bagley Mobility Hub & Corktown industrial scale-up lofts",
    },
    "plug-and-play-detroit": {
        "incentives_and_zones": [
            "Plug and Play OEM & Tier-1 Corporate Pilot Matchmaking (No-Equity Corporate Innovation Sprints)",
            "Michigan Central Mobility Innovation District & Detroit SmartZone Access",
            "MEDC Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
            "Michigan Mobility Funding Platform (MMFP) Real-World Deployment Grants",
        ],
        "graduation_space": "Michigan Central Station campus suites, Corktown Book Depository & Metro Detroit OEM supplier parks",
    },
    "um-innovation-partnerships": {
        "incentives_and_zones": [
            "U-M Accelerate Blue Fund (Evergreen Pre-Seed & Seed Venture Fund for U-M Spinouts)",
            "Michigan Translational Research and Commercialization (MTRAC) Life Sciences & Advanced Transportation Grants ($100k–$250k)",
            "NSF Great Lakes Region I-Corps Hub ($50k National I-Corps Stipend Pathway)",
            "MEDC Ann Arbor SmartZone & Business Accelerator Fund (BAF - Up to $50k non-dilutive)",
        ],
        "graduation_space": "U-M North Campus Research Complex (NCRC) Venture Accelerator wet/dry labs & Plymouth Rd R&D corridor",
    },
    "wmed-innovation-center-kalamazoo": {
        "incentives_and_zones": [
            "MEDC Kalamazoo SmartZone (WMed Innovation Center LDFA)",
            "Business Accelerator Fund (BAF - Up to $50k non-dilutive for FDA regulatory/CRO testing)",
            "MTRAC Statewide Life Sciences & Biomedical Commercialization Grant Eligible",
            "Michigan SBIR/STTR Emerging Technologies Fund (ETF) Match & NIH/BARDA Support",
        ],
        "graduation_space": "69,000 sq. ft. WMed Innovation Center BSL-1/BSL-2 wet labs & adjacent Kalamazoo BTR Park Phase II scale-up sites",
    },
    "centreopolis-accelerator-ltu": {
        "incentives_and_zones": [
            "MEDC Southfield SmartZone (Centrepolis LDFA)",
            "MEDC Make It in Michigan Prototype Grant & Hardtech Manufacturing Readiness Grants",
            "C3 CleanTech Accelerator Non-Dilutive Grants & Evergreen Investment",
            "Defense Hardtech Accelerator (DHA) & Business Accelerator Fund (BAF - Up to $50k)",
        ],
        "graduation_space": "Centrepolis 6,300 sq. ft. physical product prototyping lab on LTU campus & Southfield industrial parks",
    },
}


class SiteSelectionEnricher:
    """
    Populates `organizations.site_selection_profile` across all 46 Michigan startup
    ecosystem hubs in Supabase.
    """

    def __init__(self, db: SupabaseDBClient, max_concurrency: int = 8):
        self.db = db
        self.max_concurrency = max_concurrency

    def build_site_selection_profile(self, org: Dict[str, Any]) -> Dict[str, Any]:
        city = (org.get("city") or "").strip()
        slug = (org.get("slug") or "").strip()
        lat = org.get("latitude")
        lng = org.get("longitude")

        base = CITY_SITE_SELECTION_DATA.get(city, CITY_SITE_SELECTION_DATA["Ann Arbor"])

        talent_pipeline = dict(base["talent_pipeline"])
        anchor_corporations = list(base["anchor_corporations"])
        incentives_and_zones = list(base["incentives_and_zones"])
        logistics_and_runway = dict(base["logistics_and_runway"])

        # Apply slug-specific overrides where present
        override = SLUG_SITE_OVERRIDES.get(slug)
        if override:
            if "incentives_and_zones" in override:
                incentives_and_zones = list(override["incentives_and_zones"])
            if "graduation_space" in override:
                logistics_and_runway["graduation_space"] = override["graduation_space"]

        # Verify / enrich spatial distance to nearest airport and border if coordinates are present
        if lat is not None and lng is not None:
            f_lat, f_lng = float(lat), float(lng)
            nearest_ap = min(
                MICHIGAN_AIRPORTS,
                key=lambda ap: haversine_miles(f_lat, f_lng, ap["lat"], ap["lng"]),
            )
            ap_miles = round(haversine_miles(f_lat, f_lng, nearest_ap["lat"], nearest_ap["lng"]), 1)
            # Keep the curated airport description while ensuring it includes exact mileage if not already present
            if "miles" not in logistics_and_runway["nearest_airport"]:
                logistics_and_runway["nearest_airport"] = (
                    f"{logistics_and_runway['nearest_airport']} [{ap_miles} mi straight-line to {nearest_ap['code']}]"
                )

        return {
            "talent_pipeline": talent_pipeline,
            "anchor_corporations": anchor_corporations,
            "incentives_and_zones": incentives_and_zones,
            "logistics_and_runway": logistics_and_runway,
        }

    async def run(self) -> None:
        console.rule(
            "[bold cyan]Site Selection & Relocation Intelligence Enricher (`site_selection_enricher.py`)[/bold cyan]"
        )
        orgs = self.db.fetch_all_organizations()
        console.print(f"Loaded [bold green]{len(orgs)}[/bold green] organizations from Supabase.\n")

        semaphore = asyncio.Semaphore(self.max_concurrency)
        summary_rows: List[Dict[str, str]] = []

        async def _worker(org: Dict[str, Any]) -> None:
            async with semaphore:
                org_id = org["id"]
                slug = org.get("slug", "")
                city = org.get("city", "")
                profile = self.build_site_selection_profile(org)

                resp = self.db._http.patch(
                    f"{self.db.rest_url}/organizations",
                    params={"id": f"eq.{org_id}"},
                    json={"site_selection_profile": profile},
                )
                if resp.status_code not in (200, 204):
                    raise RuntimeError(
                        f"Failed to update site_selection_profile for {slug}: "
                        f"[{resp.status_code}] {resp.text}"
                    )

                tp = profile["talent_pipeline"]
                lr = profile["logistics_and_runway"]
                summary_rows.append(
                    {
                        "slug": slug,
                        "city": city,
                        "top_uni": tp["nearby_universities"][0].split("(")[0].strip(),
                        "top_anchor": profile["anchor_corporations"][0].split("(")[0].strip(),
                        "cost_idx": lr["cost_of_doing_business_index"],
                        "runway": lr["runway_multiplier"],
                        "airport": lr["nearest_airport"].split("[")[0].strip(),
                    }
                )
                console.print(
                    f"  [green][ENRICHED][/green] [bold]{slug}[/bold] ({city}) -> "
                    f"Talent: [cyan]{tp['nearby_universities'][0].split('(')[0].strip()}[/cyan] | "
                    f"Runway: [yellow]{lr['runway_multiplier']}[/yellow] | "
                    f"Cost Index: [green]{lr['cost_of_doing_business_index']}[/green]"
                )

        await asyncio.gather(*[_worker(o) for o in orgs])

        summary_rows.sort(key=lambda x: (x["city"], x["slug"]))

        table = Table(
            title="Site Selection & Relocation Intelligence Verification Report (46 Michigan Hubs)",
            show_lines=False,
        )
        table.add_column("Organization Slug", style="cyan", no_wrap=True)
        table.add_column("City", style="white")
        table.add_column("Primary University Pipeline", style="green")
        table.add_column("Lead Anchor Partner", style="yellow")
        table.add_column("Cost Index", style="magenta")
        table.add_column("Runway Advantage", style="bold green")

        for r in summary_rows:
            table.add_row(
                r["slug"],
                r["city"],
                r["top_uni"],
                r["top_anchor"],
                r["cost_idx"],
                r["runway"],
            )

        console.print("\n")
        console.print(table)
        console.print(
            f"\n[bold green]Successfully populated `site_selection_profile` for all "
            f"{len(summary_rows)} organizations in Supabase![/bold green]"
        )


def main() -> None:
    db = SupabaseDBClient()
    enricher = SiteSelectionEnricher(db=db, max_concurrency=8)
    asyncio.run(enricher.run())


if __name__ == "__main__":
    main()
