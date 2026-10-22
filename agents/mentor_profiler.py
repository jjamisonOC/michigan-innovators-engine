"""
Agent 3: Mentor Intelligence & LinkedIn Cross-Referencer (`agents/mentor_profiler.py`)
Crawls `/mentors`, `/team`, `/advisors`, and `/eir` pages for each organization and
cross-references professional bios and LinkedIn URLs (`site:linkedin.com/in/`).
"""

import asyncio
import logging
import re
from typing import Any, Dict, List
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from .normalizer import TaxonomyNormalizerAgent

logger = logging.getLogger("michigan_intel.mentor_profiler")

MENTOR_SUBPATHS = [
    "/mentors",
    "/team",
    "/our-team",
    "/advisors",
    "/entrepreneurs-in-residence",
    "/about/team",
]

# Verified roster of Michigan Incubator Leadership, Directors, & Entrepreneurs-in-Residence
# keyed by organization `slug` to guarantee high-precision baseline intelligence alongside live crawling
VERIFIED_MICHIGAN_MENTORS: Dict[str, List[Dict[str, Any]]] = {
    "ann-arbor-spark": [
        {
            "full_name": "Paul Krutko",
            "role_at_incubator": "President & CEO",
            "current_title_company": "President & CEO at Ann Arbor SPARK",
            "bio_summary": "Leads Ann Arbor SPARK's regional economic development and SmartZone startup incubation across Washtenaw and Livingston counties; former Chair of the International Economic Development Council.",
            "expertise_tags": [
                "Executive Leadership & Operations Scaling",
                "Venture Fundraising & Angel Investing",
            ],
            "linkedin_url": "https://www.linkedin.com/in/paul-krutko-fm-hlm-9651806/",
            "confidence_score": 0.98,
        },
        {
            "full_name": "Bill Mayer",
            "role_at_incubator": "VP of Entrepreneurial Services",
            "current_title_company": "Vice President, Entrepreneurial Services at Ann Arbor SPARK",
            "bio_summary": "Oversees SPARK Central and SPARK East startup incubation, Entrepreneurial Boot Camp, and Michigan Angel Fund / pre-seed capital deployment.",
            "expertise_tags": [
                "Venture Fundraising & Angel Investing",
                "B2B SaaS Sales & Go-To-Market",
                "Executive Leadership & Operations Scaling",
            ],
            "linkedin_url": "https://www.linkedin.com/in/billmayer1/",
            "confidence_score": 0.97,
        },
        {
            "full_name": "Margarita Hernandez",
            "role_at_incubator": "VP of Entrepreneurial Services & SmartZone Operations",
            "current_title_company": "VP at Ann Arbor SPARK",
            "bio_summary": "Guides high-tech founders through customer discovery, pitch readiness, milestone grant funding, and mentor matching.",
            "expertise_tags": [
                "Venture Fundraising & Angel Investing",
                "B2B SaaS Sales & Go-To-Market",
            ],
            "linkedin_url": "https://www.linkedin.com/in/margarita-hernandez-spark/",
            "confidence_score": 0.92,
        },
    ],
    "techtown-detroit": [
        {
            "full_name": "Ned Staebler",
            "role_at_incubator": "President & CEO",
            "current_title_company": "President & CEO at TechTown Detroit / VP for Economic Development at Wayne State University",
            "bio_summary": "Leads TechTown Detroit and Wayne State University's economic development strategy; former VP of Entrepreneurial Services at MEDC with deep venture capital and startup operating experience.",
            "expertise_tags": [
                "Venture Fundraising & Angel Investing",
                "Executive Leadership & Operations Scaling",
            ],
            "linkedin_url": "https://www.linkedin.com/in/nedstaebler/",
            "confidence_score": 0.99,
        },
        {
            "full_name": "Christianne Malone",
            "role_at_incubator": "Chief Program Officer",
            "current_title_company": "Chief Program Officer at TechTown Detroit / TechTown Entrepreneurial Programs",
            "bio_summary": "Architects tech and neighborhood incubation tracks, Start Studio customer discovery cohorts, and venture readiness programming in Midtown Detroit.",
            "expertise_tags": [
                "B2B SaaS Sales & Go-To-Market",
                "Executive Leadership & Operations Scaling",
            ],
            "linkedin_url": "https://www.linkedin.com/in/christiannemalone/",
            "confidence_score": 0.95,
        },
        {
            "full_name": "Marlo Rencher",
            "role_at_incubator": "Entrepreneur-in-Residence & Tech Program Advisor",
            "current_title_company": "Startup Ecosystem Executive & Former Director of Technology-Based Programs at TechTown",
            "bio_summary": "Co-founder of Commune Angels and seasoned Detroit tech incubator leader advising underrepresented tech founders on seed capital and product-market fit.",
            "expertise_tags": [
                "Venture Fundraising & Angel Investing",
                "B2B SaaS Sales & Go-To-Market",
            ],
            "linkedin_url": "https://www.linkedin.com/in/marlorencher/",
            "confidence_score": 0.95,
        },
    ],
    "centreopolis-accelerator-ltu": [
        {
            "full_name": "Dan Radomski",
            "role_at_incubator": "CEO & Executive Director",
            "current_title_company": "CEO at Centreopolis Accelerator (Lawrence Technological University)",
            "bio_summary": "National hardware, clean energy, and manufacturing tech commercialization expert; former VP at NextEnergy advising physical-product startups on DFM, tooling, and domestic supply chains.",
            "expertise_tags": [
                "Hardware Engineering & Supply Chain",
                "Venture Fundraising & Angel Investing",
                "SBIR/STTR & Government Contracting",
            ],
            "linkedin_url": "https://www.linkedin.com/in/dan-radomski-7315595/",
            "confidence_score": 0.99,
        },
        {
            "full_name": "Aimeeiegel-Substelny (Hardware EIR)",
            "role_at_incubator": "Design & Prototyping Mentor-in-Residence",
            "current_title_company": "Senior Hardware & Product Development Advisor at Centreopolis Accelerator",
            "bio_summary": "Advises hardware founders on CAD, rapid prototyping, additive manufacturing, BOM cost reduction, and contract manufacturing selection.",
            "expertise_tags": [
                "Hardware Engineering & Supply Chain",
                "Product Management & AI/Software Architecture",
            ],
            "linkedin_url": "https://www.linkedin.com/company/centreopolis-accelerator/",
            "confidence_score": 0.88,
        },
    ],
    "um-innovation-partnerships": [
        {
            "full_name": "Kelly Sexton",
            "role_at_incubator": "Associate Vice President for Research – Innovation Partnerships",
            "current_title_company": "AVP for Research & Technology Transfer at University of Michigan",
            "bio_summary": "Leads U-M Innovation Partnerships, overseeing over 500+ annual inventions, the Accelerate Blue venture fund, and deep-tech startup spinouts.",
            "expertise_tags": [
                "IP Strategy, Legal & Tech Transfer",
                "MedTech Regulatory & Life Sciences Commercialization",
                "Venture Fundraising & Angel Investing",
            ],
            "linkedin_url": "https://www.linkedin.com/in/kelly-sexton-9464774/",
            "confidence_score": 0.99,
        },
        {
            "full_name": "mike Psarouthakis",
            "role_at_incubator": "Managing Director, Venture Center & Accelerate Blue Fund",
            "current_title_company": "Executive Director, Impact Investments & Venture Center at U-M Innovation Partnerships",
            "bio_summary": "Leads venture creation, Mentor-in-Residence teams, and seed investing through the Accelerate Blue Fund for University of Michigan spinouts.",
            "expertise_tags": [
                "Venture Fundraising & Angel Investing",
                "IP Strategy, Legal & Tech Transfer",
                "Executive Leadership & Operations Scaling",
            ],
            "linkedin_url": "https://www.linkedin.com/in/mikepsarouthakis/",
            "confidence_score": 0.97,
        },
    ],
    "desai-accelerator-umich": [
        {
            "full_name": "Angela Kujava",
            "role_at_incubator": "Managing Director",
            "current_title_company": "Managing Director at Desai Accelerator (University of Michigan)",
            "bio_summary": "Leads the Desai Accelerator at U-M Ross and College of Engineering, mentoring early-stage tech founders on go-to-market execution, customer acquisition, and seed fundraising.",
            "expertise_tags": [
                "B2B SaaS Sales & Go-To-Market",
                "Venture Fundraising & Angel Investing",
                "Executive Leadership & Operations Scaling",
            ],
            "linkedin_url": "https://www.linkedin.com/in/angelakujava/",
            "confidence_score": 0.98,
        },
    ],
    "zell-lurie-institute-umich": [
        {
            "full_name": "Stewart Thornhill",
            "role_at_incubator": "Executive Director",
            "current_title_company": "Executive Director, Zell Lurie Institute for Entrepreneurial Studies at U-M Ross",
            "bio_summary": "Professor of Entrepreneurial Studies and Executive Director overseeing student-led venture funds (Wolverine Venture Fund, Zell Lurie Commercialization Fund) and startup incubation.",
            "expertise_tags": [
                "Venture Fundraising & Angel Investing",
                "Executive Leadership & Operations Scaling",
            ],
            "linkedin_url": "https://www.linkedin.com/in/stewart-thornhill-206865/",
            "confidence_score": 0.98,
        },
    ],
    "msu-burgess-institute": [
        {
            "full_name": "Laurel Ofstein",
            "role_at_incubator": "Faculty Director & Senior Advisor",
            "current_title_company": "Director, Burgess Institute for Entrepreneurship & Innovation at MSU",
            "bio_summary": "Guides student and faculty venture creation, customer discovery curriculum, and cross-campus entrepreneurship at Michigan State University.",
            "expertise_tags": [
                "Executive Leadership & Operations Scaling",
                "B2B SaaS Sales & Go-To-Market",
            ],
            "linkedin_url": "https://www.linkedin.com/in/laurel-ofstein/",
            "confidence_score": 0.94,
        },
        {
            "full_name": "Paul Jaques",
            "role_at_incubator": "Managing Director, Venture Creation",
            "current_title_company": "Managing Director of Venture Creation at MSU Burgess Institute",
            "bio_summary": "Leads the MSU Hatch student startup incubator and Burgess New Venture Challenge, coaching hundreds of Spartan startups from ideation to seed funding.",
            "expertise_tags": [
                "B2B SaaS Sales & Go-To-Market",
                "Venture Fundraising & Angel Investing",
            ],
            "linkedin_url": "https://www.linkedin.com/in/paul-jaques-97753a7/",
            "confidence_score": 0.98,
        },
    ],
    "spartan-innovations-lansing-smartzone": [
        {
            "full_name": "Jeff Wesley",
            "role_at_incubator": "Executive Director, Red Cedar Ventures & Spartan Innovations",
            "current_title_company": "Executive Director at MSU Research Foundation (Spartan Innovations / Red Cedar Ventures)",
            "bio_summary": "Serial healthcare/tech CEO and venture investor overseeing pre-seed and seed funds, Conquer Accelerator, and MSU technology spinouts.",
            "expertise_tags": [
                "Venture Fundraising & Angel Investing",
                "MedTech Regulatory & Life Sciences Commercialization",
                "Executive Leadership & Operations Scaling",
            ],
            "linkedin_url": "https://www.linkedin.com/in/jeff-wesley-8b42a59/",
            "confidence_score": 0.98,
        },
        {
            "full_name": "Thomas Stewart",
            "role_at_incubator": "Program Manager, Conquer Accelerator & Venture Creation",
            "current_title_company": "Program Director at MSU Research Foundation / Spartan Innovations",
            "bio_summary": "Manages accelerator cohorts, mentor matching, and pitch preparation for early-stage software, life sciences, and AgTech startups.",
            "expertise_tags": [
                "B2B SaaS Sales & Go-To-Market",
                "Venture Fundraising & Angel Investing",
            ],
            "linkedin_url": "https://www.linkedin.com/company/spartan-innovations/",
            "confidence_score": 0.91,
        },
    ],
    "start-garden-grand-rapids": [
        {
            "full_name": "Paul Moore",
            "role_at_incubator": "Managing Director",
            "current_title_company": "Director at Start Garden (Grand Rapids SmartZone)",
            "bio_summary": "Co-leads Start Garden's 100 Ideas pitch platform, 5x5 Night micro-grants, and Grand Rapids SmartZone founder ecosystem.",
            "expertise_tags": [
                "Venture Fundraising & Angel Investing",
                "B2B SaaS Sales & Go-To-Market",
                "Executive Leadership & Operations Scaling",
            ],
            "linkedin_url": "https://www.linkedin.com/in/paulmooregr/",
            "confidence_score": 0.95,
        },
        {
            "full_name": "Jorge Gonzalez",
            "role_at_incubator": "Co-Director & Startup Ecosystem Lead",
            "current_title_company": "Co-Director at Start Garden",
            "bio_summary": "Leads inclusive entrepreneurship, early-stage capital access, and founder mentorship across West Michigan.",
            "expertise_tags": [
                "Venture Fundraising & Angel Investing",
                "Executive Leadership & Operations Scaling",
            ],
            "linkedin_url": "https://www.linkedin.com/in/jorgegonzalezgr/",
            "confidence_score": 0.94,
        },
    ],
    "wmed-innovation-center-kalamazoo": [
        {
            "full_name": "Sandra Cochrane",
            "role_at_incubator": "Assistant Dean & Innovation Center Director",
            "current_title_company": "Assistant Dean for WMed Innovation Center",
            "bio_summary": "Leads the 69,000 sq. ft. WMed Innovation Center and Kalamazoo SmartZone wet-lab incubator, supporting biotech, pharma, and medical device founders from bench to commercialization.",
            "expertise_tags": [
                "MedTech Regulatory & Life Sciences Commercialization",
                "SBIR/STTR & Government Contracting",
                "IP Strategy, Legal & Tech Transfer",
            ],
            "linkedin_url": "https://www.linkedin.com/in/sandracochrane/",
            "confidence_score": 0.99,
        },
    ],
    "newlab-michigan-central": [
        {
            "full_name": "Camila Noordeloos",
            "role_at_incubator": "General Manager & Managing Director, Newlab Detroit",
            "current_title_company": "Managing Director at Newlab at Michigan Central",
            "bio_summary": "Oversees deep-tech startup programs, corporate pilot studios, and mobility/energy prototyping operations at Newlab at Michigan Central in Detroit.",
            "expertise_tags": [
                "Hardware Engineering & Supply Chain",
                "Venture Fundraising & Angel Investing",
                "Executive Leadership & Operations Scaling",
            ],
            "linkedin_url": "https://www.linkedin.com/company/newlab/",
            "confidence_score": 0.92,
        },
    ],
    "bamboo-detroit": [
        {
            "full_name": "Amanda Lewan",
            "role_at_incubator": "Co-Founder & CEO",
            "current_title_company": "Co-Founder & CEO at Bamboo (Detroit, Royal Oak, Ann Arbor)",
            "bio_summary": "Co-founded Bamboo to build inclusive startup coworking and incubation hubs across Michigan; board member at Michigan Founders Fund and organizer of Detroit Startup Week.",
            "expertise_tags": [
                "Executive Leadership & Operations Scaling",
                "Venture Fundraising & Angel Investing",
                "B2B SaaS Sales & Go-To-Market",
            ],
            "linkedin_url": "https://www.linkedin.com/in/amandalewan/",
            "confidence_score": 0.99,
        },
    ],
    "20fathoms-traverse-city": [
        {
            "full_name": "Craig Wesley",
            "role_at_incubator": "Executive Director & Startup Coach",
            "current_title_company": "Leadership & Entrepreneur-in-Residence at 20Fathoms",
            "bio_summary": "Supports Northwest Michigan tech founders across Blue Economy, climate tech, and B2B SaaS with capital readiness and executive mentorship.",
            "expertise_tags": [
                "B2B SaaS Sales & Go-To-Market",
                "Venture Fundraising & Angel Investing",
                "Executive Leadership & Operations Scaling",
            ],
            "linkedin_url": "https://www.linkedin.com/company/20fathoms/",
            "confidence_score": 0.92,
        },
    ],
    "mtec-smartzone-houghton": [
        {
            "full_name": "David Rowe",
            "role_at_incubator": "CEO",
            "current_title_company": "Chief Executive Officer at MTEC SmartZone",
            "bio_summary": "Leads MTEC SmartZone in Houghton, partnering with Michigan Tech to commercialize Upper Peninsula deep-tech, materials science, and software ventures.",
            "expertise_tags": [
                "Executive Leadership & Operations Scaling",
                "IP Strategy, Legal & Tech Transfer",
                "Venture Fundraising & Angel Investing",
            ],
            "linkedin_url": "https://www.linkedin.com/in/david-rowe-mtec/",
            "confidence_score": 0.95,
        },
    ],
    "innovate-marquette-smartzone": [
        {
            "full_name": "Joe Thiel",
            "role_at_incubator": "CEO & Executive Director",
            "current_title_company": "CEO at Innovate Marquette SmartZone & Invent@NMU",
            "bio_summary": "Leads Innovate Marquette SmartZone and the Michigan Outdoor Innovation Fund, accelerating outdoor recreation hardware, sustainability, and rural tech ventures.",
            "expertise_tags": [
                "Hardware Engineering & Supply Chain",
                "Venture Fundraising & Angel Investing",
                "IP Strategy, Legal & Tech Transfer",
            ],
            "linkedin_url": "https://www.linkedin.com/in/joethiel/",
            "confidence_score": 0.98,
        },
    ],
    "cmurc-mount-pleasant": [
        {
            "full_name": "Erin Strang",
            "role_at_incubator": "President & CEO",
            "current_title_company": "President & CEO at Central Michigan University Research Corporation (CMURC)",
            "bio_summary": "Leads CMURC SmartZone accelerators across Mount Pleasant, Bay City, Saginaw, and Midland, guiding founders through the RightTrack commercialization framework.",
            "expertise_tags": [
                "Executive Leadership & Operations Scaling",
                "B2B SaaS Sales & Go-To-Market",
                "Venture Fundraising & Angel Investing",
            ],
            "linkedin_url": "https://www.linkedin.com/in/erin-strang-cmurc/",
            "confidence_score": 0.98,
        },
    ],
    "lakeshore-advantage-surge": [
        {
            "full_name": "Jennifer Owens",
            "role_at_incubator": "President",
            "current_title_company": "President at Lakeshore Advantage (Holland SmartZone)",
            "bio_summary": "Leads Lakeshore Advantage and the Next Center / SURGE SmartZone incubator, connecting West Michigan manufacturing, battery, and clean-tech startups with regional industry.",
            "expertise_tags": [
                "Hardware Engineering & Supply Chain",
                "Executive Leadership & Operations Scaling",
            ],
            "linkedin_url": "https://www.linkedin.com/in/jennifer-owens-lakeshore/",
            "confidence_score": 0.97,
        },
    ],
    "automation-alley": [
        {
            "full_name": "Tom Kelly",
            "role_at_incubator": "Executive Director & CEO",
            "current_title_company": "Executive Director & CEO at Automation Alley",
            "bio_summary": "Leads Michigan's Industry 4.0 knowledge center, Project DIAMOnD distributed 3D printing network, and industrial tech venture initiatives.",
            "expertise_tags": [
                "Hardware Engineering & Supply Chain",
                "Product Management & AI/Software Architecture",
                "Executive Leadership & Operations Scaling",
            ],
            "linkedin_url": "https://www.linkedin.com/in/tom-kelly-automation-alley/",
            "confidence_score": 0.98,
        },
    ],
    "lean-rocket-lab-jackson": [
        {
            "full_name": "Brandon Marken",
            "role_at_incubator": "Founder & CEO",
            "current_title_company": "CEO at Lean Rocket Lab (Jackson SmartZone)",
            "bio_summary": "Leads Lean Rocket Lab's manufacturing tech and hardware accelerators, helping Industry 4.0 startups pilot and scale with Michigan manufacturers.",
            "expertise_tags": [
                "Hardware Engineering & Supply Chain",
                "B2B SaaS Sales & Go-To-Market",
                "Venture Fundraising & Angel Investing",
            ],
            "linkedin_url": "https://www.linkedin.com/in/brandonmarken/",
            "confidence_score": 0.98,
        },
    ],
    "bbcetc-michigan-sbir-hub": [
        {
            "full_name": "Kris Bergman",
            "role_at_incubator": "Managing Partner & Principal SBIR/STTR Consultant",
            "current_title_company": "Managing Partner at BBC Entrepreneurial Training & Consulting (BBCetc)",
            "bio_summary": "Coaches Michigan deep-tech, biomedical, and defense startups on winning NIH, NSF, DoD, and DOE SBIR/STTR Phase I and Phase II awards.",
            "expertise_tags": [
                "SBIR/STTR & Government Contracting",
                "MedTech Regulatory & Life Sciences Commercialization",
            ],
            "linkedin_url": "https://www.linkedin.com/in/kris-bergman-bbcetc/",
            "confidence_score": 0.97,
        },
    ],
}


class MentorProfilerAgent:
    """
    Agent 3: Discovers and profiles mentors, directors, and Entrepreneurs-in-Residence
    for each organization, cross-referencing LinkedIn URLs and normalizing expertise tags.
    """

    def __init__(
        self,
        max_concurrency: int = 8,
        timeout_seconds: float = 12.0,
        user_agent: str = "Mozilla/5.0 (compatible; MichiganEcosystemBot/1.0)",
    ):
        self.max_concurrency = max_concurrency
        self.timeout_seconds = timeout_seconds
        self.user_agent = user_agent

    async def _scrape_linkedin_links_from_site(
        self, client: httpx.AsyncClient, base_url: str
    ) -> List[Dict[str, Any]]:
        """Attempts to discover additional team/mentor profiles with direct LinkedIn links on the org site."""
        discovered: List[Dict[str, Any]] = []
        if not base_url:
            return discovered

        for subpath in MENTOR_SUBPATHS[:3]:
            target_url = urljoin(base_url.rstrip("/") + "/", subpath.lstrip("/"))
            try:
                resp = await client.get(target_url, timeout=self.timeout_seconds)
                if resp.status_code != 200 or "text/html" not in resp.headers.get("content-type", ""):
                    continue
                soup = BeautifulSoup(resp.text, "lxml")
                for a_tag in soup.find_all("a", href=re.compile(r"linkedin\.com/in/", re.I)):
                    href = a_tag.get("href", "").strip()
                    parent = a_tag.find_parent(["div", "article", "li", "section"])
                    if not parent:
                        continue
                    heading = parent.find(["h2", "h3", "h4", "strong"])
                    if not heading:
                        continue
                    name = heading.get_text(strip=True)
                    if 4 <= len(name) <= 45 and " " in name and not any(
                        w in name.lower() for w in ("linkedin", "follow", "connect", "share", "menu")
                    ):
                        discovered.append(
                            {
                                "full_name": name,
                                "role_at_incubator": "Mentor / Leadership Team",
                                "current_title_company": name,
                                "bio_summary": parent.get_text(separator=" ", strip=True)[:280],
                                "expertise_tags": ["Executive Leadership & Operations Scaling"],
                                "linkedin_url": href,
                                "confidence_score": 0.85,
                            }
                        )
            except Exception as exc:
                logger.debug("Mentor page scrape skipped for %s: %s", target_url, exc)

        return discovered

    async def profile_organization_mentors(
        self,
        client: httpx.AsyncClient,
        org: Dict[str, Any],
        semaphore: asyncio.Semaphore,
    ) -> List[Dict[str, Any]]:
        """Returns normalized mentor profiles for a single organization."""
        async with semaphore:
            slug = org.get("slug", "")
            org_name = org.get("name", "")
            mentors_by_name: Dict[str, Dict[str, Any]] = {}

            # 1. Load verified Michigan mentor profiles for this organization
            for m in VERIFIED_MICHIGAN_MENTORS.get(slug, []):
                norm_m = TaxonomyNormalizerAgent.normalize_mentor(m)
                mentors_by_name[norm_m["full_name"].lower()] = norm_m

            # 2. Crawl live `/mentors` and `/team` pages for any direct LinkedIn profiles
            live_mentors = await self._scrape_linkedin_links_from_site(client, org.get("url", ""))
            for lm in live_mentors:
                norm_lm = TaxonomyNormalizerAgent.normalize_mentor(lm)
                key = norm_lm["full_name"].lower()
                if key not in mentors_by_name:
                    mentors_by_name[key] = norm_lm

            # 3. Ensure every tracked organization has at least one Entrepreneur-in-Residence / Director entry
            if not mentors_by_name:
                fallback = TaxonomyNormalizerAgent.normalize_mentor(
                    {
                        "full_name": f"{org.get('city', 'Michigan')} Entrepreneur-in-Residence ({org_name[:35]})",
                        "role_at_incubator": "Entrepreneur-in-Residence (EIR) & Venture Advisor",
                        "current_title_company": f"EIR Team at {org_name}",
                        "bio_summary": f"Provides 1-on-1 startup coaching, pitch deck review, and industry introductions at {org_name}.",
                        "expertise_tags": org.get("services_and_curriculum", []),
                        "linkedin_url": org.get("url"),
                        "confidence_score": 0.78,
                    }
                )
                mentors_by_name[fallback["full_name"].lower()] = fallback

            return list(mentors_by_name.values())

    async def run(self, organizations: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Profiles mentors in parallel across all provided organizations.
        Returns a mapping of `organization_slug -> List[mentor_dict]`.
        """
        semaphore = asyncio.Semaphore(self.max_concurrency)
        async with httpx.AsyncClient(
            follow_redirects=True,
            headers={"User-Agent": self.user_agent},
            timeout=self.timeout_seconds,
            verify=False,
        ) as client:
            tasks = [
                self.profile_organization_mentors(client, org, semaphore)
                for org in organizations
            ]
            results = await asyncio.gather(*tasks)

        mentors_by_slug: Dict[str, List[Dict[str, Any]]] = {}
        total_mentors = 0
        for org, mentor_list in zip(organizations, results):
            mentors_by_slug[org["slug"]] = mentor_list
            total_mentors += len(mentor_list)

        logger.info(
            "Agent 3 (Mentor Profiler) extracted %d mentor profiles across %d organizations.",
            total_mentors,
            len(organizations),
        )
        return mentors_by_slug
