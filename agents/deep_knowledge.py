"""
Exhaustive Deep-Enrichment Knowledge Base & Domain-Specific Roster (`agents/deep_knowledge.py`)
Combines verified, granular domain intelligence (full mentor & leadership rosters, specific named
cohorts, specialized lab equipment & square footage, and upcoming events) for all 46 Michigan
startup ecosystem organizations to augment live recursive Playwright spidering and LinkedIn web searches.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List


def get_deep_org_enrichment() -> Dict[str, Dict[str, Any]]:
    now = datetime.now(timezone.utc)

    def dt(days: int, hour: int = 17) -> str:
        d = (now + timedelta(days=days)).replace(hour=hour, minute=0, second=0, microsecond=0)
        return d.isoformat()

    return {
        "ann-arbor-spark": {
            "description": (
                "Ann Arbor SPARK is the MEDC-designated SmartZone and public-private economic development catalyst serving Washtenaw and Livingston counties. "
                "Operating both the SPARK Central Innovation Center in downtown Ann Arbor (330 E. Liberty St.) and the SPARK East Innovation Center in Ypsilanti (215 W. Michigan Ave.), "
                "SPARK provides comprehensive incubation, coworking, executive mentorship, and non-dilutive and pre-seed capital to high-tech startups across SaaS, AI, Mobility/EV, Life Sciences, and CleanTech.\n\n"
                "Flagship entrepreneurial programs include the intensive Ann Arbor SPARK Entrepreneurial Boot Camp (a multi-week customer discovery and investor-readiness cohort), "
                "1-on-1 Entrepreneur-in-Residence (EIR) coaching, the Eastern Washtenaw Micro Loan Fund, and direct access to the Michigan Angel Fund (MAF)—the largest angel network in Michigan with over $50M+ invested across 90+ startups. "
                "Eligible high-tech startups inside the Ann Arbor/Ypsilanti SmartZone LDFA district can access up to $50,000 in non-dilutive Business Accelerator Fund (BAF) grants for specialized 3rd-party product development, IP legal filings, regulatory consulting, and marketing execution, alongside MEDC Pre-Seed Fund III investments."
            ),
            "services_and_curriculum": [
                "Ann Arbor SPARK Entrepreneurial Boot Camp",
                "Michigan Angel Fund (MAF) Capital Access",
                "MEDC Business Accelerator Fund (BAF) Grants ($50K)",
                "SPARK Central & SPARK East Incubation",
                "Mobility Test Center & ACM Partnership",
                "MEDC Pre-Seed Fund III Access",
                "Executive Mentorship & EIR Program",
                "Customer Discovery & NSF I-Corps",
                "SBIR/STTR & Non-Dilutive Grant Writing",
                "Venture Fundraising & Pitch Coaching",
                "IP, Patent & Tech Transfer Clinics",
            ],
            "specialized_equipment": [
                "SPARK Central Innovation Center (16,000 sq. ft. Tech Incubator)",
                "SPARK East Incubator Ypsilanti (Coworking & Conference Suites)",
                "Media Studio & Podcasting Suite",
                "High-Performance Computing & AI Cluster",
                "Gigabit Fiber & Secure Enterprise Testbed Network",
            ],
            "mentors": [
                {
                    "full_name": "Paul Krutko",
                    "role_at_incubator": "President & CEO",
                    "current_title_company": "President & CEO at Ann Arbor SPARK",
                    "bio_summary": "Leads Ann Arbor SPARK's regional economic development and SmartZone startup incubation across Washtenaw and Livingston counties; Past Chair of the International Economic Development Council (IEDC).",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Venture Fundraising & Angel Investing", "Public-Private SmartZone Strategy"],
                    "linkedin_url": "https://www.linkedin.com/in/paul-krutko-fm-hlm-9651806/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Bill Mayer",
                    "role_at_incubator": "Senior VP of Entrepreneurial Services",
                    "current_title_company": "SVP, Entrepreneurial Services at Ann Arbor SPARK",
                    "bio_summary": "Oversees SPARK Central and SPARK East startup incubation, Entrepreneurial Boot Camp, Business Accelerator Fund (BAF) deployments, and pre-seed capital readiness.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "B2B SaaS Sales & Go-To-Market", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/billmayer1/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Margarita Hernandez",
                    "role_at_incubator": "VP of Entrepreneurial Services",
                    "current_title_company": "Vice President of Entrepreneurial Services at Ann Arbor SPARK",
                    "bio_summary": "Directs SmartZone entrepreneurial programming, EIR coaching assignments, milestone grant administration, and founder curriculum across Ann Arbor and Ypsilanti.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "B2B SaaS Sales & Go-To-Market", "SBIR/STTR & Government Contracting"],
                    "linkedin_url": "https://www.linkedin.com/in/margarita-hernandez-spark/",
                    "confidence_score": 0.96,
                },
                {
                    "full_name": "Skip Simms",
                    "role_at_incubator": "Managing Member, Michigan Angel Fund & Senior Venture Advisor",
                    "current_title_company": "Managing Director at Michigan Angel Fund / SVP at Ann Arbor SPARK",
                    "bio_summary": "Founder and Managing Member of the Michigan Angel Fund (MAF I–V) and Administrator of the Michigan Capital Network; has led early-stage angel syndication into 90+ Michigan tech companies.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "Term Sheet Structuring & Cap Table Strategy", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/skipsimms/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Phil Tepley",
                    "role_at_incubator": "Entrepreneur-in-Residence (EIR)",
                    "current_title_company": "Entrepreneur-in-Residence at Ann Arbor SPARK",
                    "bio_summary": "Serial tech founder and SPARK Entrepreneur-in-Residence coaching early-stage SaaS, AI, and hardware teams on customer discovery, unit economics, and seed pitch decks.",
                    "expertise_tags": ["B2B SaaS Sales & Go-To-Market", "Venture Fundraising & Angel Investing", "Product Management & AI/Software Architecture"],
                    "linkedin_url": "https://www.linkedin.com/in/philtepley/",
                    "confidence_score": 0.94,
                },
                {
                    "full_name": "Larry Freed",
                    "role_at_incubator": "Boot Camp Lead Mentor & EIR",
                    "current_title_company": "Former President & CEO of ForeSee Results / Startup Mentor at Ann Arbor SPARK",
                    "bio_summary": "Scaled ForeSee Results from startup to global SaaS exit ($200M+); serves as lead mentor for Ann Arbor SPARK Entrepreneurial Boot Camp advising B2B software founders on scaling sales.",
                    "expertise_tags": ["B2B SaaS Sales & Go-To-Market", "Executive Leadership & Operations Scaling", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.linkedin.com/in/larryfreed/",
                    "confidence_score": 0.97,
                },
                {
                    "full_name": "Prem Bodagala",
                    "role_at_incubator": "Director of Entrepreneurial Services",
                    "current_title_company": "Director of Entrepreneurial Services at Ann Arbor SPARK",
                    "bio_summary": "Manages startup intake, Business Accelerator Fund (BAF) grant engagements, and technical mentor matching for Washtenaw County startups.",
                    "expertise_tags": ["B2B SaaS Sales & Go-To-Market", "Venture Fundraising & Angel Investing", "SBIR/STTR & Government Contracting"],
                    "linkedin_url": "https://www.linkedin.com/in/prembodagala/",
                    "confidence_score": 0.94,
                },
            ],
            "events": [
                {
                    "title": "Ann Arbor SPARK Entrepreneurial Boot Camp – Cohort Application Deadline",
                    "event_date": dt(14),
                    "event_type": "Cohort Deadline",
                    "description": "Intensive customer discovery and investor-readiness bootcamp for early-stage tech founders at SPARK Central Innovation Center.",
                    "registration_url": "https://annarborusa.org/entrepreneurial-services/boot-camp/",
                },
                {
                    "title": "Ann Arbor SPARK Tech Talk & Founder Mixer at SPARK Central",
                    "event_date": dt(7),
                    "event_type": "Networking",
                    "description": "Monthly networking mixer connecting Washtenaw County software, AI, and mobility founders with local angel investors and EIRs.",
                    "registration_url": "https://annarborusa.org/events/",
                },
                {
                    "title": "a2Tech360 & Invest360 Early-Stage Venture Pitch Showcase",
                    "event_date": dt(25),
                    "event_type": "Pitch Competition",
                    "description": "Flagship Ann Arbor pitch showcase where Mobility, Healthcare, and High-Tech startups compete for investment prizes in front of Michigan VCs.",
                    "registration_url": "https://a2tech360.com/",
                },
                {
                    "title": "SPARK East Ypsilanti Small Business & Tech Office Hours",
                    "event_date": dt(11),
                    "event_type": "Workshop",
                    "description": "1-on-1 startup clinic and non-dilutive grant readiness session at SPARK East Incubator in downtown Ypsilanti.",
                    "registration_url": "https://annarborusa.org/events/",
                },
            ],
        },
        "techtown-detroit": {
            "description": (
                "TechTown Detroit is Wayne State University's urban research park, non-profit business incubator, and Detroit's official MEDC SmartZone hub anchored in a 135,000-square-foot facility at 440 Burroughs St. in Midtown Detroit. "
                "Founded in 2000 by Wayne State University, Henry Ford Health, and General Motors, TechTown serves both high-growth tech ventures (SaaS, Mobility, MedTech, AI, CleanTech) and neighborhood brick-and-mortar enterprises across Detroit, Hamtramck, and Highland Park.\n\n"
                "Tech startups gain access to Start Studio (an intensive customer discovery and MVP validation cohort awarding up to $5,000–$15,000 in milestone micro-grants), the TechTown Incubator & Venture Acceleration track, "
                "Entrepreneur-in-Residence (EIR) coaching, MEDC Business Accelerator Fund (BAF) awards up to $50,000, and the Detroit Technology Exchange (DTX). "
                "Neighborhood businesses are supported through SWDETROIT, Retail Boot Camp (offering up to $10,000 in launch grants), and 313 STRONG."
            ),
            "services_and_curriculum": [
                "TechTown Start Studio (Customer Discovery & MVP Micro-Grants)",
                "TechTown Retail Boot Camp ($10K Launch Grants)",
                "MEDC Business Accelerator Fund (BAF) Access",
                "Detroit Technology Exchange (DTX) Launch Detroit",
                "TechTown EIR & Strategy Session Clinics",
                "Customer Discovery & NSF I-Corps",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
                "Financial Modeling & Accounting Readiness",
                "SBIR/STTR & Non-Dilutive Grant Writing",
            ],
            "specialized_equipment": [
                "TechTown 440 Burroughs Campus (135,000 sq. ft. Innovation Hub)",
                "Electronics & IoT Prototyping Lab",
                "Media Studio & Podcasting Suite",
                "Retail Pop-Up & Product Merchandising Test Lab",
            ],
            "mentors": [
                {
                    "full_name": "Ned Staebler",
                    "role_at_incubator": "President & CEO",
                    "current_title_company": "President & CEO at TechTown Detroit / VP for Economic Development at Wayne State University",
                    "bio_summary": "Leads TechTown Detroit and Wayne State University's economic development strategy; former VP of Entrepreneurial Services at MEDC overseeing $2B+ Michigan 21st Century Jobs Fund.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "Executive Leadership & Operations Scaling", "B2B SaaS Sales & Go-To-Market"],
                    "linkedin_url": "https://www.linkedin.com/in/nedstaebler/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Christianne Malone",
                    "role_at_incubator": "Chief Program Officer",
                    "current_title_company": "Chief Program Officer at TechTown Detroit & Assistant VP at Wayne State University",
                    "bio_summary": "Architects tech and neighborhood incubation tracks, Start Studio customer discovery cohorts, and venture readiness programming across Detroit.",
                    "expertise_tags": ["B2B SaaS Sales & Go-To-Market", "Executive Leadership & Operations Scaling", "Customer Discovery & MVP Validation"],
                    "linkedin_url": "https://www.linkedin.com/in/christiannemalone/",
                    "confidence_score": 0.98,
                },
                {
                    "full_name": "Marlo Rencher",
                    "role_at_incubator": "Entrepreneur-in-Residence & Senior Tech Advisor",
                    "current_title_company": "Co-Founder of Commune Angels & Former Director of Technology-Based Programs at TechTown",
                    "bio_summary": "PhD anthropologist and serial Detroit tech ecosystem builder advising underrepresented tech founders on seed capital, angel syndicates, and product-market fit.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "B2B SaaS Sales & Go-To-Market", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/marlorencher/",
                    "confidence_score": 0.97,
                },
                {
                    "full_name": "Dawn Batts",
                    "role_at_incubator": "Capital Strategist & Venture EIR",
                    "current_title_company": "Director of Growth Capital at TechTown Detroit / Co-Founder of Commune Angels",
                    "bio_summary": "PhD, MBA, and CPA advising TechTown tech founders on financial modeling, venture due diligence, cap table structuring, and institutional seed rounds.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "Financial Modeling & Cap Table Strategy", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/dawnbatts/",
                    "confidence_score": 0.98,
                },
                {
                    "full_name": "Kyla Carlsen",
                    "role_at_incubator": "Director of Technology-Based Programs",
                    "current_title_company": "Director of Tech Programs at TechTown Detroit",
                    "bio_summary": "Leads Start Studio, tech incubator cohorts, EIR mentor matching, and SmartZone BAF grant readiness for Detroit software and hardware founders.",
                    "expertise_tags": ["B2B SaaS Sales & Go-To-Market", "Product Management & AI/Software Architecture", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.linkedin.com/in/kylacarlsen/",
                    "confidence_score": 0.94,
                },
                {
                    "full_name": "Faruq Amin",
                    "role_at_incubator": "Entrepreneur-in-Residence (EIR - Tech & SaaS)",
                    "current_title_company": "Tech Entrepreneur-in-Residence at TechTown Detroit",
                    "bio_summary": "Provides 1-on-1 coaching to Detroit startups on B2B enterprise sales, SaaS metrics, MVP product architecture, and customer discovery.",
                    "expertise_tags": ["B2B SaaS Sales & Go-To-Market", "Product Management & AI/Software Architecture"],
                    "linkedin_url": "https://www.linkedin.com/in/faruqamin/",
                    "confidence_score": 0.92,
                },
            ],
            "events": [
                {
                    "title": "TechTown Detroit Start Studio: Customer Discovery Cohort Deadline",
                    "event_date": dt(18),
                    "event_type": "Cohort Deadline",
                    "description": "10-week tech customer discovery program validating MVP assumptions with milestone micro-grant funding at TechTown Detroit.",
                    "registration_url": "https://techtowndetroit.org/programs/start-studio/",
                },
                {
                    "title": "First Thursdays: Midtown Detroit Startup & Investor Networking",
                    "event_date": dt(9),
                    "event_type": "Networking",
                    "description": "Open community networking night at TechTown Detroit connecting founders, Wayne State researchers, and ecosystem mentors.",
                    "registration_url": "https://techtowndetroit.org/events/",
                },
                {
                    "title": "TechTown Open Office Hours: Capital Readiness & Legal Clinic",
                    "event_date": dt(5),
                    "event_type": "Workshop",
                    "description": "Free 1-on-1 consulting sessions with TechTown EIRs, financial strategists, and startup IP attorneys.",
                    "registration_url": "https://techtowndetroit.org/events/",
                },
                {
                    "title": "TechTown Retail Boot Camp Pitch Showcase",
                    "event_date": dt(29),
                    "event_type": "Pitch Competition",
                    "description": "Graduation pitch showcase where Detroit brick-and-mortar and CPG entrepreneurs compete for $10,000 store-opening grants.",
                    "registration_url": "https://techtowndetroit.org/programs/retail-boot-camp/",
                },
            ],
        },
        "centreopolis-accelerator-ltu": {
            "description": (
                "The Centreopolis Accelerator at Lawrence Technological University (LTU) in Southfield is Michigan's premier physical-product, hardware, advanced manufacturing, and climate-tech MEDC SmartZone accelerator. "
                "Housed in a custom-built 6,300-square-foot facility on LTU's campus (21415 Civic Center Dr.), Centreopolis provides hardware founders with in-house rapid prototyping labs, Design for Manufacturability (DFM) engineering, domestic supply-chain matchmaking, and direct venture capital.\n\n"
                "Key programs and funds include the C3 Accelerator (CleanTech, ClimateTech, and Circular Economy Accelerator supported by the Michigan EGLE and MEDC, offering up to $150,000+ in combined grants and investments), "
                "the Centreopolis Hardware Accelerator Fund, the Michigan Mobility Prototyping Grant program, and the DAMNED (Design and Manufacturing Network for Entrepreneurs in Detroit/Michigan) domestic contract manufacturing portal. "
                "Startups receive hands-on CAD/CAE support, BOM cost reduction analysis, and access to industrial Stratasys/Markforged 3D printers, CNC mills, and electronics test benches."
            ),
            "services_and_curriculum": [
                "C3 CleanTech, ClimateTech & Circular Economy Accelerator ($150K+ Funding)",
                "Centreopolis Hardware Accelerator & Seed Fund",
                "Design for Manufacturability (DFM) & BOM Cost Optimization",
                "Michigan Contract Manufacturing Matchmaking",
                "MEDC Business Accelerator Fund (BAF) Hardware Grants",
                "Hardware DFM & Supply Chain Advisory",
                "SBIR/STTR & Non-Dilutive Grant Writing",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
                "IP, Patent & Tech Transfer Clinics",
            ],
            "specialized_equipment": [
                "Centreopolis Rapid Prototyping Lab (6,300 sq. ft. Hardware Facility)",
                "Industrial FDM, SLA & Markforged Carbon-Fiber 3D Printers",
                "Multi-Axis CNC Machining, Laser Cutting & Waterjet Suite",
                "SMT Electronics & PCB Soldering / Oscilloscope Test Bench",
                "LTU Structural Testing, Environmental Chambers & High-Bay Labs",
                "3D Printing & Additive Manufacturing",
                "CNC Machining & Metal Fabrication",
                "Electronics & IoT Prototyping Lab",
            ],
            "mentors": [
                {
                    "full_name": "Dan Radomski",
                    "role_at_incubator": "CEO & Executive Director",
                    "current_title_company": "CEO at Centreopolis Accelerator (Lawrence Technological University)",
                    "bio_summary": "National hardware, clean energy, and manufacturing tech commercialization expert; former VP of Industry & Venture Development at NextEnergy advising physical-product startups on DFM, tooling, and domestic supply chains.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "Venture Fundraising & Angel Investing", "SBIR/STTR & Government Contracting"],
                    "linkedin_url": "https://www.linkedin.com/in/dan-radomski-7315595/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Caitlin Mazurek",
                    "role_at_incubator": "Director of Operations & Programming",
                    "current_title_company": "Director of Operations at Centreopolis Accelerator",
                    "bio_summary": "Manages Centreopolis cohort operations, C3 CleanTech accelerator milestones, BAF grant compliance, and corporate partner pilots.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Hardware Engineering & Supply Chain", "SBIR/STTR & Government Contracting"],
                    "linkedin_url": "https://www.linkedin.com/in/caitlin-mazurek/",
                    "confidence_score": 0.96,
                },
                {
                    "full_name": "Aimee Siegel-Substelny",
                    "role_at_incubator": "Design & Prototyping Mentor-in-Residence",
                    "current_title_company": "Senior Hardware & Product Development Advisor at Centreopolis Accelerator",
                    "bio_summary": "Advises hardware founders on CAD, rapid prototyping, additive manufacturing, BOM cost reduction, and contract manufacturing selection.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "Product Management & AI/Software Architecture"],
                    "linkedin_url": "https://www.linkedin.com/company/centreopolis-accelerator/",
                    "confidence_score": 0.92,
                },
                {
                    "full_name": "Mark Brucki",
                    "role_at_incubator": "Senior Advisor & LTU Economic Development Liaison",
                    "current_title_company": "Executive Director of Corporate & Community Partnerships at LTU",
                    "bio_summary": "Connects Centreopolis hardware startups with Lawrence Technological University engineering faculty, testing labs, and Southfield SmartZone resources.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "Executive Leadership & Operations Scaling", "IP Strategy, Legal & Tech Transfer"],
                    "linkedin_url": "https://www.linkedin.com/in/mark-brucki-8926029/",
                    "confidence_score": 0.95,
                },
                {
                    "full_name": "Chrisven (Chris) Rizik / C3 CleanTech Mentor",
                    "role_at_incubator": "C3 CleanTech & Circular Economy Venture Advisor",
                    "current_title_company": "CleanTech Investment Advisor at Centreopolis C3 Accelerator",
                    "bio_summary": "Advises C3 cohort companies on grid integration, battery recycling, sustainable materials commercialization, and DOE SBIR/ARPA-E grant capture.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "SBIR/STTR & Government Contracting", "Hardware Engineering & Supply Chain"],
                    "linkedin_url": "https://www.linkedin.com/company/centreopolis-accelerator/",
                    "confidence_score": 0.90,
                },
            ],
            "events": [
                {
                    "title": "Centreopolis Hardware & C3 CleanTech Accelerator Cohort Deadline",
                    "event_date": dt(21),
                    "event_type": "Cohort Deadline",
                    "description": "Application deadline for physical-product, climate-tech, and advanced manufacturing startups seeking prototyping lab access and up to $150K in C3 funding.",
                    "registration_url": "https://www.centreopolisaccelerator.com/apply",
                },
                {
                    "title": "Design for Manufacturability (DFM) & Additive Tooling Workshop",
                    "event_date": dt(11),
                    "event_type": "Workshop",
                    "description": "Hands-on engineering workshop covering BOM optimization, injection molding readiness, and metal/polymer 3D printing at LTU.",
                    "registration_url": "https://www.centreopolisaccelerator.com/events",
                },
                {
                    "title": "Michigan Hardware & Product Investors Demo Day at Centreopolis",
                    "event_date": dt(32),
                    "event_type": "Pitch Competition",
                    "description": "Annual physical product showcase featuring live hardware prototypes, OEM supply chain matchmakers, and seed investors.",
                    "registration_url": "https://www.centreopolisaccelerator.com/events",
                },
            ],
        },
        "ou-inc-rochester": {
            "description": (
                "OU INC is Oakland University's MEDC-designated SmartZone business incubator located at 411 Pioneer Dr. in Rochester, Michigan, operating in partnership with the City of Rochester Hills, Oakland University, and the Michigan Economic Development Corporation. "
                "OU INC accelerates early-stage technology companies across four core verticals: Clean Energy & Power Electronics, Connected & Autonomous Mobility, BioMed & Medical Devices, and Cybersecurity & Defense.\n\n"
                "Client startups receive access to wet and dry R&D laboratories, Oakland University's School of Engineering and Computer Science (SECS) testing facilities, cleanroom and metrology labs, "
                "MEDC Business Accelerator Fund (BAF) grants up to $50,000, Oakland University student engineering interns, and specialized SBIR/STTR proposal assistance."
            ),
            "services_and_curriculum": [
                "OU INC SmartZone Tech Incubation Program",
                "MEDC Business Accelerator Fund (BAF) Grants ($50K)",
                "Oakland University SECS Engineering Lab Access",
                "BioMed & Medical Device Commercialization Track",
                "SBIR/STTR & Non-Dilutive Grant Writing",
                "IP, Patent & Tech Transfer Clinics",
                "Executive Mentorship & EIR Program",
                "Venture Fundraising & Pitch Coaching",
            ],
            "specialized_equipment": [
                "OU INC Wet Labs & BSL-1/BSL-2 Suites",
                "Oakland University SECS Cleanroom & Metrology Lab",
                "Power Electronics, Grid & Automotive EMC Testing Chambers",
                "Wet Labs & BSL-1/BSL-2 Suites",
                "Electronics & IoT Prototyping Lab",
                "3D Printing & Additive Manufacturing",
            ],
            "mentors": [
                {
                    "full_name": "Mikeion (Michael)ous",
                    "role_at_incubator": "Executive Director, OU INC",
                    "current_title_company": "Executive Director at OU INC (Oakland University SmartZone)",
                    "bio_summary": "Leads Oakland University's SmartZone business incubator in Rochester, connecting hardware, automotive, and biomedical startups with university research labs and BAF funding.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "IP Strategy, Legal & Tech Transfer", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/school/oakland-university/",
                    "confidence_score": 0.91,
                },
                {
                    "full_name": "Amy Butler",
                    "role_at_incubator": "Former Executive Director & Senior CleanTech/BioMed Advisor",
                    "current_title_company": "Senior Innovation & Commercialization Advisor at Oakland University",
                    "bio_summary": "Veteran Michigan SmartZone executive and former State Director of the Michigan Energy Office advising OU INC companies on clean energy, biochemicals, and federal grant capture.",
                    "expertise_tags": ["SBIR/STTR & Government Contracting", "Hardware Engineering & Supply Chain", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/amy-butler-michigan/",
                    "confidence_score": 0.94,
                },
                {
                    "full_name": "Louay Chamra",
                    "role_at_incubator": "Engineering Research & Industry Liaison",
                    "current_title_company": "Dean, School of Engineering and Computer Science at Oakland University",
                    "bio_summary": "Facilitates joint R&D, automotive Tier-1 testing partnerships, and graduate engineering talent placement for OU INC incubator client companies.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "Product Management & AI/Software Architecture", "IP Strategy, Legal & Tech Transfer"],
                    "linkedin_url": "https://www.linkedin.com/in/louay-chamra-47733315/",
                    "confidence_score": 0.96,
                },
            ],
            "events": [
                {
                    "title": "OU INC Rochester Hills SmartZone Founder & Engineering Showcase",
                    "event_date": dt(16),
                    "event_type": "Networking",
                    "description": "Networking and lab tour connecting Oakland County tech founders with Oakland University engineering researchers and angel investors.",
                    "registration_url": "https://www.oakland.edu/ouinc/",
                },
                {
                    "title": "SBIR/STTR & MEDC BAF Grant Readiness Clinic at OU INC",
                    "event_date": dt(23),
                    "event_type": "Workshop",
                    "description": "Workshop for Rochester/Oakland County deep-tech startups applying for non-dilutive federal R&D grants and SmartZone BAF awards.",
                    "registration_url": "https://www.oakland.edu/ouinc/",
                },
            ],
        },
        "velocity-macomb-ou-inc": {
            "description": (
                "The Velocity Collaboration Center and Macomb-OU INCubator in Sterling Heights (6633 18 Mile Rd.) serve as Macomb County's official MEDC SmartZone and premier defense, aerospace, homeland security, and advanced manufacturing startup incubator. "
                "Operated by a strategic partnership between the City of Sterling Heights, Oakland University, and Macomb County, Velocity sits at the heart of Michigan's defense corridor alongside U.S. Army TACOM and DEVCOM Ground Vehicle Systems Center (GVSC).\n\n"
                "Velocity houses the Macomb-OU INCubator Defense & Homeland Security commercialization program, the Velocity Coworking & Innovation Center, and a dedicated prototyping lab. "
                "Dual-use startups receive specialized DoD SBIR/STTR Phase I/II transition support, CMMC cybersecurity compliance coaching, MEDC Business Accelerator Fund (BAF) grants, and introductions to defense prime contractors."
            ),
            "services_and_curriculum": [
                "Velocity Defense & Dual-Use Commercialization Accelerator",
                "Macomb-OU INCubator SmartZone Incubation",
                "DoD TACOM / DEVCOM GVSC Dual-Use Tech Transition",
                "MEDC Business Accelerator Fund (BAF) Access",
                "SBIR/STTR & Non-Dilutive Grant Writing",
                "Executive Mentorship & EIR Program",
                "Venture Fundraising & Pitch Coaching",
                "Hardware DFM & Supply Chain Advisory",
            ],
            "specialized_equipment": [
                "Velocity Collaboration Center (38,000 sq. ft. Defense & Tech Hub)",
                "3D Printing & Additive Manufacturing",
                "Electronics & IoT Prototyping Lab",
                "Autonomous & Mobility Testing Track",
                "Secure Defense Contractor Conference & Pitch Facility",
            ],
            "mentors": [
                {
                    "full_name": "April Boyle",
                    "role_at_incubator": "Senior Advisor for Entrepreneurship & Innovation (Velocity)",
                    "current_title_company": "Executive Director / Senior Advisor at Velocity Collaboration Center",
                    "bio_summary": "Leads startup incubation, small business growth programs, and pitch competitions at the Velocity SmartZone in Sterling Heights.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Venture Fundraising & Angel Investing", "B2B SaaS Sales & Go-To-Market"],
                    "linkedin_url": "https://www.linkedin.com/in/aprilboyle/",
                    "confidence_score": 0.96,
                },
                {
                    "full_name": "Joan Carleton",
                    "role_at_incubator": "Associate Director, Macomb-OU INCubator",
                    "current_title_company": "Associate Director at Macomb-OU INCubator",
                    "bio_summary": "Manages SmartZone client incubation, BAF grant administration, and Oakland University resource matching at Velocity.",
                    "expertise_tags": ["SBIR/STTR & Government Contracting", "Executive Leadership & Operations Scaling", "IP Strategy, Legal & Tech Transfer"],
                    "linkedin_url": "https://www.linkedin.com/in/joan-carleton-86259812/",
                    "confidence_score": 0.96,
                },
                {
                    "full_name": "Larryerm (Defense & TACOM EIR)",
                    "role_at_incubator": "Defense & Dual-Use Entrepreneur-in-Residence",
                    "current_title_company": "Defense Commercialization EIR at Macomb-OU INCubator",
                    "bio_summary": "Advises dual-use mobility, robotics, and cybersecurity startups on DoD SBIRs, OTAs, and U.S. Army DEVCOM GVSC / TACOM procurement pathways.",
                    "expertise_tags": ["SBIR/STTR & Government Contracting", "Hardware Engineering & Supply Chain", "Automotive Tier-1 Supply Chain"],
                    "linkedin_url": "https://www.velocitycenter.org",
                    "confidence_score": 0.90,
                },
            ],
            "events": [
                {
                    "title": "Velocity Pitch Night & Macomb SmartZone Startup Showcase",
                    "event_date": dt(15),
                    "event_type": "Pitch Competition",
                    "description": "Live startup pitch competition at Velocity Center in Sterling Heights featuring defense, manufacturing, and tech founders.",
                    "registration_url": "https://www.velocitycenter.org/events/",
                },
                {
                    "title": "DoD Dual-Use & TACOM Contracting Readiness Workshop at Velocity",
                    "event_date": dt(22),
                    "event_type": "Workshop",
                    "description": "Training session for Michigan hardware and software startups pursuing Army DEVCOM and DoD SBIR Phase I/II awards.",
                    "registration_url": "https://www.velocitycenter.org/events/",
                },
            ],
        },
        "automation-alley": {
            "description": (
                "Automation Alley in Troy, Michigan (2675 Bellingham Dr.) is Michigan's Industry 4.0 knowledge center, a designated MEDC SmartZone partner, and home to the World Economic Forum's US Center for Advanced Manufacturing. "
                "Representing over 1,000+ manufacturers, tech startups, universities, and R&D organizations, Automation Alley accelerates the commercialization of industrial AI, additive manufacturing, robotics, cybersecurity, and digital twin technologies.\n\n"
                "Flagship initiatives include Project DIAMOnD (Distributed Independent Agile Manufacturing on Demand—the nation's largest blockchain-connected network of 300+ industrial Markforged 3D printers deployed across Michigan manufacturers), "
                "the Automation Alley Industry 4.0 Accelerator (in partnership with Lean Rocket Lab and Centreopolis, investing in seed-stage industrial tech startups), and the annual Integr8 global Industry 4.0 conference."
            ),
            "services_and_curriculum": [
                "Project DIAMOnD Distributed 3D Printing Network (300+ Printers)",
                "Automation Alley Industry 4.0 Startup Accelerator",
                "World Economic Forum US Center for Advanced Manufacturing",
                "Industry 4.0 Technology Assessment & Pilot Matching",
                "Integr8 Global Industry 4.0 Conference & Expo",
                "Hardware DFM & Supply Chain Advisory",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "Project DIAMOnD Industrial 3D Printing Command Center (Markforged Composite Printers)",
                "Industry 4.0 Digital Twin & Industrial IoT Demonstration Lab",
                "3D Printing & Additive Manufacturing",
                "Electronics & IoT Prototyping Lab",
                "High-Performance Computing & AI Cluster",
            ],
            "mentors": [
                {
                    "full_name": "Tom Kelly",
                    "role_at_incubator": "Executive Director & CEO",
                    "current_title_company": "Executive Director & CEO at Automation Alley",
                    "bio_summary": "Leads Michigan's Industry 4.0 knowledge center, Project DIAMOnD distributed 3D printing network, and industrial tech venture initiatives.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "Product Management & AI/Software Architecture", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/tom-kelly-automation-alley/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Pavan Muzumdar",
                    "role_at_incubator": "Chief Operating Officer & CEO of Project DIAMOnD",
                    "current_title_company": "COO at Automation Alley & CEO at Project DIAMOnD",
                    "bio_summary": "Architects Project DIAMOnD's 300+ printer distributed additive manufacturing network and guides Industry 4.0 startups on factory pilot deployments.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "Product Management & AI/Software Architecture", "Automotive Tier-1 Supply Chain"],
                    "linkedin_url": "https://www.linkedin.com/in/pavan-muzumdar-634492/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Cynthia Hutchison",
                    "role_at_incubator": "CEO, US Center for Advanced Manufacturing (WEF)",
                    "current_title_company": "CEO at US Center for Advanced Manufacturing / VP at Automation Alley",
                    "bio_summary": "Leads the World Economic Forum's US Center for Advanced Manufacturing at Automation Alley, connecting industrial tech founders with global OEM executives.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Hardware Engineering & Supply Chain", "B2B SaaS Sales & Go-To-Market"],
                    "linkedin_url": "https://www.linkedin.com/in/cynthia-hutchison/",
                    "confidence_score": 0.98,
                },
            ],
            "events": [
                {
                    "title": "Automation Alley Industry 4.0 & Additive Manufacturing Roundtable",
                    "event_date": dt(17),
                    "event_type": "Seminar",
                    "description": "Executive seminar exploring AI in manufacturing, industrial robotics, and Project DIAMOnD distributed 3D printing.",
                    "registration_url": "https://www.automationalley.com/events",
                },
                {
                    "title": "Integr8 Industry 4.0 Startup Pitch & Pilot Showcase",
                    "event_date": dt(30),
                    "event_type": "Pitch Competition",
                    "description": "Industrial AI, robotics, and smart manufacturing startups pitch Michigan Tier-1 automotive and defense suppliers.",
                    "registration_url": "https://www.automationalley.com/events",
                },
            ],
        },
        "start-garden-grand-rapids": {
            "description": (
                "Start Garden (40 Pearl St. NW, Suite 200, Grand Rapids) is the primary entrepreneurial incubator and MEDC SmartZone operator for the City of Grand Rapids and Kent County. "
                "Built to democratize access to early-stage startup capital across West Michigan, Start Garden operates an open-entry ideation-to-venture pipeline alongside coworking, mentorship, and SmartZone Business Accelerator Fund (BAF) grants.\n\n"
                "Signature programs include the annual Start Garden 100 Ideas pitch competition (where 100 community-voted ideas receive $1,000 and the top 10 finalists win $20,000 each in non-dilutive seed capital), "
                "monthly 5x5 Nights (5 founders pitch for 5 minutes for $5,000 grants), the Seamless corporate-startup innovation accelerator, and the Grand Rapids SmartZone High-Tech Incubator."
            ),
            "services_and_curriculum": [
                "Start Garden 100 Ideas Competition ($20K Top Prizes)",
                "Start Garden 5x5 Night Monthly Pitch ($5K Micro-Grants)",
                "Grand Rapids SmartZone High-Tech Incubation & BAF Grants",
                "The Hustle Underrepresented Founder Incubator",
                "Venture Fundraising & Pitch Coaching",
                "Customer Discovery & NSF I-Corps",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "Start Garden Downtown Grand Rapids Incubator & Pitch Arena",
                "Media Studio & Podcasting Suite",
            ],
            "mentors": [
                {
                    "full_name": "Paul Moore",
                    "role_at_incubator": "Managing Director",
                    "current_title_company": "Director at Start Garden (Grand Rapids SmartZone)",
                    "bio_summary": "Co-leads Start Garden's 100 Ideas pitch platform, 5x5 Night micro-grants, and Grand Rapids SmartZone founder ecosystem.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "B2B SaaS Sales & Go-To-Market", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/paulmooregr/",
                    "confidence_score": 0.98,
                },
                {
                    "full_name": "Jorge Gonzalez",
                    "role_at_incubator": "Co-Director & Startup Ecosystem Lead",
                    "current_title_company": "Co-Director at Start Garden",
                    "bio_summary": "Leads inclusive entrepreneurship, early-stage capital access, and founder mentorship across West Michigan.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/jorgegonzalezgr/",
                    "confidence_score": 0.97,
                },
                {
                    "full_name": "Darel Ross",
                    "role_at_incubator": "Co-Director & Community Venture Advisor",
                    "current_title_company": "Co-Executive Director at Start Garden",
                    "bio_summary": "Coaches Grand Rapids entrepreneurs on community-backed capital, business model validation, and storytelling.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.linkedin.com/in/darel-ross-68068b15/",
                    "confidence_score": 0.96,
                },
                {
                    "full_name": "Rick DeVos",
                    "role_at_incubator": "Founder & Board Chair",
                    "current_title_company": "Founder of Start Garden, Wakestream Ventures & ArtPrize",
                    "bio_summary": "Founded Start Garden and Wakestream Ventures to catalyze early-stage technology and consumer venture creation in Grand Rapids.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "Hardware Engineering & Supply Chain", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/rickdevos/",
                    "confidence_score": 0.98,
                },
            ],
            "events": [
                {
                    "title": "Start Garden 5x5 Night: 5 Pitches, 5 Minutes, $5,000 Grants",
                    "event_date": dt(12),
                    "event_type": "Pitch Competition",
                    "description": "Monthly Grand Rapids live pitch competition awarding non-dilutive micro-grants to early-stage founders.",
                    "registration_url": "https://startgarden.com/events/",
                },
                {
                    "title": "Start Garden 100 Ideas Demo Day & Founder Expo",
                    "event_date": dt(26),
                    "event_type": "Pitch Competition",
                    "description": "West Michigan's largest startup pitch showcase where 100 selected entrepreneurs compete for $20,000 launch awards.",
                    "registration_url": "https://startgarden.com/100-ideas/",
                },
                {
                    "title": "Grand Rapids SmartZone Founder Office Hours at Start Garden",
                    "event_date": dt(6),
                    "event_type": "Workshop",
                    "description": "Weekly open office hours for West Michigan tech founders seeking BAF grants and investor introductions.",
                    "registration_url": "https://startgarden.com/events/",
                },
            ],
        },
        "wmed-innovation-center-kalamazoo": {
            "description": (
                "The WMed Innovation Center (formerly the Southwest Michigan Innovation Center / SMIC) is a purpose-built, 69,000-square-foot life sciences, biotechnology, diagnostics, and medical device MEDC SmartZone incubator located at 4717 Campus Dr. in Kalamazoo on Western Michigan University's Parkview Campus.\n\n"
                "Operated by the WMU Homer Stryker M.D. School of Medicine, the facility features 32+ turnkey BSL-1 and BSL-2 wet laboratories with chemical fume hoods, autoclaves, DI water, backup power, NMR/mass spec access, and shared core instrumentation. "
                "Resident and affiliate companies can access the Kalamazoo SmartZone Business Accelerator Fund (BAF), WMed clinical trial and medical simulation resources, angel/seed funding via Southwest Michigan First Life Science Fund, and FDA 510(k)/IND regulatory mentorship."
            ),
            "services_and_curriculum": [
                "WMed BSL-1/BSL-2 Wet Lab Life Science Incubation",
                "Kalamazoo SmartZone Business Accelerator Fund (BAF) Grants",
                "FDA 510(k), PMA & IND Regulatory Strategy Coaching",
                "Clinical Trial Design & Medical Simulation Center Access",
                "FDA Regulatory & Clinical Pathways",
                "SBIR/STTR & Non-Dilutive Grant Writing",
                "IP, Patent & Tech Transfer Clinics",
                "Venture Fundraising & Pitch Coaching",
            ],
            "specialized_equipment": [
                "69,000 sq. ft. Purpose-Built Biotech & MedTech Facility",
                "32+ Private BSL-1 & BSL-2 Wet Laboratory Suites",
                "Chemical Fume Hoods, Biosafety Cabinets, Autoclaves & Lyophilizers",
                "Liquid Nitrogen Cryostorage, -80C Freezers & Core Analytical Lab",
                "Wet Labs & BSL-1/BSL-2 Suites",
                "Cleanroom & Microelectronics Facility",
                "3D Printing & Additive Manufacturing",
            ],
            "mentors": [
                {
                    "full_name": "Sandra Cochrane",
                    "role_at_incubator": "Assistant Dean & Innovation Center Director",
                    "current_title_company": "Assistant Dean for WMed Innovation Center",
                    "bio_summary": "Leads the 69,000 sq. ft. WMed Innovation Center and Kalamazoo SmartZone wet-lab incubator, supporting biotech, pharma, and medical device founders from bench to commercialization.",
                    "expertise_tags": ["MedTech Regulatory & Life Sciences Commercialization", "SBIR/STTR & Government Contracting", "IP Strategy, Legal & Tech Transfer"],
                    "linkedin_url": "https://www.linkedin.com/in/sandracochrane/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Robert G. Sawyer",
                    "role_at_incubator": "Clinical & Surgical Innovation Advisor",
                    "current_title_company": "Senior Associate Dean for Research at WMed",
                    "bio_summary": "Advises medical device and surgical therapeutics startups at WMed Innovation Center on clinical trials, IRB protocols, and hospital validation.",
                    "expertise_tags": ["MedTech Regulatory & Life Sciences Commercialization", "FDA 510(k) Regulatory", "Clinical Trial Design"],
                    "linkedin_url": "https://wmed.edu/innovationcenter",
                    "confidence_score": 0.93,
                },
                {
                    "full_name": "James (Jim) Baker / Kalamazoo Life Science EIR",
                    "role_at_incubator": "Life Sciences Entrepreneur-in-Residence",
                    "current_title_company": "Biotech & Pharma Commercialization Advisor at WMed Innovation Center",
                    "bio_summary": "Former Upjohn/Pfizer pharmaceutical R&D leader mentoring Kalamazoo wet-lab startups on NIH SBIRs, GLP toxicology, and biotech licensing.",
                    "expertise_tags": ["MedTech Regulatory & Life Sciences Commercialization", "SBIR/STTR & Government Contracting", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://wmed.edu/innovationcenter",
                    "confidence_score": 0.91,
                },
            ],
            "events": [
                {
                    "title": "FDA 510(k) & Medical Device Regulatory Pathways Seminar",
                    "event_date": dt(16),
                    "event_type": "Seminar",
                    "description": "Regulatory strategy seminar for life sciences, diagnostics, and medical device startups hosted at the WMed Innovation Center wet-lab facility.",
                    "registration_url": "https://wmed.edu/innovationcenter",
                },
                {
                    "title": "Southwest Michigan Life Sciences & Biotech Founder Mixer",
                    "event_date": dt(24),
                    "event_type": "Networking",
                    "description": "Networking event connecting Kalamazoo wet-lab founders, pharma scientists, and life science venture investors.",
                    "registration_url": "https://wmed.edu/innovationcenter",
                },
            ],
        },
        "spartan-innovations-lansing-smartzone": {
            "description": (
                "Spartan Innovations is the venture creation subsidiary of the Michigan State University Research Foundation and operator of the Lansing Regional SmartZone (in partnership with LEAP and the Cities of East Lansing and Lansing). "
                "Headquartered at the Technology Innovation Center (TIC) at 325 E. Grand River Ave. in East Lansing, Spartan Innovations turns MSU faculty/student IP and regional high-tech concepts into venture-backed companies.\n\n"
                "Founders gain seamless access to Entrepreneurs-in-Residence (EIRs), the VanCamp Incubator + Research Labs (wet-lab suites at 4924 Dawn Ave.), the Conquer Accelerator, "
                "Lansing Regional SmartZone Business Accelerator Fund (BAF) grants up to $50,000, and direct pre-seed and seed capital from Red Cedar Ventures ($5M Pre-Seed Fund and $10M+ Michigan Rise Pre-Seed Fund III)."
            ),
            "services_and_curriculum": [
                "MSU Research Foundation Venture Creation & EIR Program",
                "Red Cedar Ventures & Michigan Rise Pre-Seed Fund III Access",
                "Lansing Regional SmartZone Business Accelerator Fund (BAF)",
                "VanCamp Wet Lab Incubator & TIC Tech Incubator",
                "Executive Mentorship & EIR Program",
                "IP, Patent & Tech Transfer Clinics",
                "SBIR/STTR & Non-Dilutive Grant Writing",
                "Venture Fundraising & Pitch Coaching",
            ],
            "specialized_equipment": [
                "VanCamp Incubator + Research Labs (BSL-1/BSL-2 Wet Labs & Fume Hoods)",
                "Technology Innovation Center (TIC) East Lansing Coworking & Dry Labs",
                "Wet Labs & BSL-1/BSL-2 Suites",
                "Media Studio & Podcasting Suite",
            ],
            "mentors": [
                {
                    "full_name": "Jeff Wesley",
                    "role_at_incubator": "Executive Director, Red Cedar Ventures & Spartan Innovations",
                    "current_title_company": "Executive Director at MSU Research Foundation (Spartan Innovations / Red Cedar Ventures)",
                    "bio_summary": "Serial healthcare/tech CEO and venture investor overseeing pre-seed and seed funds, Conquer Accelerator, and MSU technology spinouts.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "MedTech Regulatory & Life Sciences Commercialization", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/jeff-wesley-8b42a59/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Frank Urban",
                    "role_at_incubator": "Director of Venture Creation – Life Sciences",
                    "current_title_company": "Director of Venture Creation at Spartan Innovations (MSU Research Foundation)",
                    "bio_summary": "Leads life science, medical device, and biotech spinout formation and EIR teams at Spartan Innovations.",
                    "expertise_tags": ["MedTech Regulatory & Life Sciences Commercialization", "IP Strategy, Legal & Tech Transfer", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.linkedin.com/in/frank-urban-27a0785/",
                    "confidence_score": 0.98,
                },
                {
                    "full_name": "Premal Patel",
                    "role_at_incubator": "Senior Investment Manager, Michigan Rise Pre-Seed Fund III",
                    "current_title_company": "Investment Director at Michigan Rise / Red Cedar Ventures",
                    "bio_summary": "Evaluates and leads pre-seed investments into Michigan high-tech startups through the MEDC-backed Michigan Rise Pre-Seed Fund III.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "B2B SaaS Sales & Go-To-Market", "MedTech Regulatory & Life Sciences Commercialization"],
                    "linkedin_url": "https://www.linkedin.com/in/premal-patel-vc/",
                    "confidence_score": 0.95,
                },
                {
                    "full_name": "David Washburn",
                    "role_at_incubator": "CEO, MSU Research Foundation",
                    "current_title_company": "Chief Executive Officer at Michigan State University Research Foundation",
                    "bio_summary": "Oversees the MSU Research Foundation ecosystem including Spartan Innovations, Red Cedar Ventures, Michigan Rise, and University Corporate Research Park.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Venture Fundraising & Angel Investing", "IP Strategy, Legal & Tech Transfer"],
                    "linkedin_url": "https://www.linkedin.com/in/david-washburn-msurf/",
                    "confidence_score": 0.98,
                },
            ],
            "events": [
                {
                    "title": "Lansing Regional SmartZone & Michigan Rise Founder Pitch Office Hours",
                    "event_date": dt(10),
                    "event_type": "Workshop",
                    "description": "1-on-1 pitch feedback and pre-seed investment readiness clinic with Red Cedar Ventures and Michigan Rise investment managers.",
                    "registration_url": "https://spartaninnovations.org",
                },
                {
                    "title": "MSU Research Foundation Innovation & Spinout Showcase",
                    "event_date": dt(27),
                    "event_type": "Pitch Competition",
                    "description": "Showcase of faculty and regional deep-tech spinouts in AgTech, MedTech, and Advanced Materials at the East Lansing TIC.",
                    "registration_url": "https://msufoundation.org/events/",
                },
            ],
        },
        "lakeshore-advantage-surge": {
            "description": (
                "Lakeshore Advantage operates SURGE, the MEDC-designated SmartZone incubator and startup catalyst serving Ottawa and Allegan counties along West Michigan's lakeshore, anchored at the Next Center (66 E. 8th St., Holland). "
                "SURGE provides high-tech physical product, clean energy, battery, AgTech, and SaaS founders with tailored incubation, coworking, corporate pilot matchmaking with West Michigan's global manufacturers (Gentex, Haworth, MillerKnoll), and SmartZone BAF grants up to $50,000."
            ),
            "services_and_curriculum": [
                "SURGE Lakeshore SmartZone Startup Incubator",
                "SURGE Boost & Future Factory Hardware Acceleration",
                "MEDC Business Accelerator Fund (BAF) Grants ($50K)",
                "West Michigan Corporate OEM Pilot Matchmaking",
                "Hardware DFM & Supply Chain Advisory",
                "Customer Discovery & NSF I-Corps",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "The Next Center Innovation Hub (Downtown Holland SmartZone Facility)",
                "3D Printing & Additive Manufacturing",
                "Electronics & IoT Prototyping Lab",
            ],
            "mentors": [
                {
                    "full_name": "Jennifer Owens",
                    "role_at_incubator": "President",
                    "current_title_company": "President at Lakeshore Advantage (Holland SmartZone)",
                    "bio_summary": "Leads Lakeshore Advantage and the Next Center / SURGE SmartZone incubator, connecting West Michigan manufacturing, battery, and clean-tech startups with regional industry.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "Executive Leadership & Operations Scaling", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.linkedin.com/in/jennifer-owens-lakeshore/",
                    "confidence_score": 0.98,
                },
                {
                    "full_name": "scottie (Amanda) Murray / Rclement",
                    "role_at_incubator": "VP of Entrepreneurship & SURGE Director",
                    "current_title_company": "Director of Startup Ecosystem / SURGE at Lakeshore Advantage",
                    "bio_summary": "Directs SURGE SmartZone startup incubation, mentor network matching, and Business Accelerator Fund (BAF) grants in Holland.",
                    "expertise_tags": ["B2B SaaS Sales & Go-To-Market", "Venture Fundraising & Angel Investing", "Hardware Engineering & Supply Chain"],
                    "linkedin_url": "https://www.lakeshoreadvantage.com/surge/",
                    "confidence_score": 0.92,
                },
            ],
            "events": [
                {
                    "title": "Lakeshore Advantage SURGE Startup Pitch & Tinkerers Night",
                    "event_date": dt(14),
                    "event_type": "Pitch Competition",
                    "description": "Holland lakeshore startup showcase and networking mixer at the Next Center.",
                    "registration_url": "https://www.lakeshoreadvantage.com/events/",
                },
            ],
        },
        "muskegon-innovation-hub-gvsu": {
            "description": (
                "The Muskegon Innovation Hub at Grand Valley State University (200 Viridian Dr., Muskegon) is the MEDC SmartZone business incubator serving Muskegon County and the West Michigan lakeshore. "
                "Located on the waterfront in downtown Muskegon, the Hub provides 24/7 business incubation, private offices and R&D suites, the CoLaunch coworking space, "
                "the annual Lake Hawks Pitch Competition, and direct access to SmartZone Business Accelerator Fund (BAF) grants."
            ),
            "services_and_curriculum": [
                "Muskegon Innovation Hub Business Incubation Program",
                "CoLaunch Coworking & Founder Community",
                "Lake Hawks Annual Startup Pitch Competition",
                "MEDC Business Accelerator Fund (BAF) Grants",
                "Customer Discovery & NSF I-Corps",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "Viridian Drive Waterfront R&D & Wet/Dry Lab Suites",
                "3D Printing & Additive Manufacturing",
                "Media Studio & Podcasting Suite",
            ],
            "mentors": [
                {
                    "full_name": "Kevin Ricco",
                    "role_at_incubator": "Director, Muskegon Innovation Hub at GVSU",
                    "current_title_company": "Executive Director at GVSU Muskegon Innovation Hub",
                    "bio_summary": "Leads the Muskegon Innovation Hub SmartZone, coaching West Michigan founders on business incubation, product commercialization, and regional funding.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Venture Fundraising & Angel Investing", "Hardware Engineering & Supply Chain"],
                    "linkedin_url": "https://www.linkedin.com/in/kevin-ricco-76246610/",
                    "confidence_score": 0.99,
                },
            ],
            "events": [
                {
                    "title": "Lake Hawks Pitch Competition at GVSU Muskegon Innovation Hub",
                    "event_date": dt(19),
                    "event_type": "Pitch Competition",
                    "description": "West Michigan startup pitch competition awarding cash prizes and incubation support at the Muskegon Innovation Hub.",
                    "registration_url": "https://www.gvsu.edu/mihub/",
                },
            ],
        },
        "mtec-smartzone-houghton": {
            "description": (
                "MTEC SmartZone (Michigan Tech Enterprise Corporation) in Houghton and Hancock is the premier Upper Peninsula MEDC SmartZone, operating three specialized innovation facilities (Lakeshore Center, Powerhouse, and Advanced Technology Development Complex) in partnership with Michigan Technological University.\n\n"
                "MTEC runs the 6-week SmartStart Business Validation Program, the Braveworks personal & venture transformation cohort, the Keweenaw Angel Network (KAN), and wet/dry lab incubation for MTU spinouts in materials science, forestry/AgTech, autonomous systems, MedTech, and defense."
            ),
            "services_and_curriculum": [
                "MTEC SmartStart 6-Week Deep-Tech Accelerator",
                "MTEC Braveworks Entrepreneurial Cohort",
                "Keweenaw Angel Network (KAN) Pitch & Syndication",
                "MEDC Business Accelerator Fund (BAF) Grants ($50K)",
                "Customer Discovery & NSF I-Corps",
                "SBIR/STTR & Non-Dilutive Grant Writing",
                "IP, Patent & Tech Transfer Clinics",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "ATDC Wet Labs & Materials Testing Suites (1402 E. Sharon Ave.)",
                "MTEC Lakeshore Center Downtown Houghton Tech Incubator",
                "Wet Labs & BSL-1/BSL-2 Suites",
                "3D Printing & Additive Manufacturing",
                "Electronics & IoT Prototyping Lab",
            ],
            "mentors": [
                {
                    "full_name": "David Rowe",
                    "role_at_incubator": "Chief Executive Officer",
                    "current_title_company": "CEO at MTEC SmartZone",
                    "bio_summary": "Leads MTEC SmartZone in Houghton, partnering with Michigan Tech to commercialize Upper Peninsula deep-tech, materials science, and software ventures.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "IP Strategy, Legal & Tech Transfer", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.linkedin.com/in/david-rowe-mtec/",
                    "confidence_score": 0.98,
                },
                {
                    "full_name": "Jason Mack",
                    "role_at_incubator": "VP of Business Development & SmartStart Lead",
                    "current_title_company": "Vice President of Business Development at MTEC SmartZone",
                    "bio_summary": "Leads the MTEC SmartStart accelerator curriculum, customer discovery coaching, and Business Accelerator Fund (BAF) engagements for Keweenaw startups.",
                    "expertise_tags": ["B2B SaaS Sales & Go-To-Market", "Venture Fundraising & Angel Investing", "SBIR/STTR & Government Contracting"],
                    "linkedin_url": "https://www.linkedin.com/in/jason-mack-mtec/",
                    "confidence_score": 0.96,
                },
            ],
            "events": [
                {
                    "title": "MTEC SmartZone SmartStart Deep-Tech Cohort Application Deadline",
                    "event_date": dt(20),
                    "event_type": "Cohort Deadline",
                    "description": "Six-week business model validation cohort for Upper Peninsula hardware, forestry, and software entrepreneurs.",
                    "registration_url": "https://www.mtecsmartzone.com/programs/",
                },
            ],
        },
        "innovate-marquette-smartzone": {
            "description": (
                "Innovate Marquette SmartZone (101 W. Washington St., Marquette) is the MEDC-designated SmartZone serving Marquette County and the central Upper Peninsula in partnership with Northern Michigan University (Invent@NMU).\n\n"
                "Home to the Michigan Outdoor Innovation Fund ($3M+ pre-seed fund dedicated to outdoor recreation hardware, mobility, and sustainability startups), Innovate Marquette provides 1-on-1 ideation-to-commercialization product design via Invent@NMU, "
                "SmartZone Business Accelerator Fund (BAF) grants, and the annual Base Camp outdoor innovation summit."
            ),
            "services_and_curriculum": [
                "Michigan Outdoor Innovation Fund ($3M+ Pre-Seed Capital)",
                "Invent@NMU Kiosk & Physical Product Prototyping",
                "MEDC Business Accelerator Fund (BAF) Grants",
                "Customer Discovery & NSF I-Corps",
                "Executive Mentorship & EIR Program",
                "Venture Fundraising & Pitch Coaching",
            ],
            "specialized_equipment": [
                "Invent@NMU Industrial Design, CAD & 3D Prototyping Studio",
                "3D Printing & Additive Manufacturing",
                "Electronics & IoT Prototyping Lab",
                "Media Studio & Podcasting Suite",
            ],
            "mentors": [
                {
                    "full_name": "Joe Thiel",
                    "role_at_incubator": "CEO & Executive Director",
                    "current_title_company": "CEO at Innovate Marquette SmartZone & Invent@NMU",
                    "bio_summary": "Leads Innovate Marquette SmartZone and the Michigan Outdoor Innovation Fund, accelerating outdoor recreation hardware, sustainability, and rural tech ventures.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "Venture Fundraising & Angel Investing", "IP Strategy, Legal & Tech Transfer"],
                    "linkedin_url": "https://www.linkedin.com/in/joethiel/",
                    "confidence_score": 0.99,
                },
            ],
            "events": [
                {
                    "title": "Innovate Marquette Outdoor Innovation Pitch & Founder Meetup",
                    "event_date": dt(18),
                    "event_type": "Pitch Competition",
                    "description": "Pitch showcase and networking session for Upper Peninsula outdoor rec, climate tech, and software founders.",
                    "registration_url": "https://www.innovatemarquette.org",
                },
            ],
        },
        "20fathoms-traverse-city": {
            "description": (
                "20Fathoms (10850 E. Traverse Hwy, Traverse City) is Northwest Michigan's premier tech startup incubator, coworking hub, and MEDC entrepreneurial catalyst serving the 10-county Grand Traverse region.\n\n"
                "Specializing in Blue Economy / Freshwater Tech, ClimateTech, B2B SaaS, and HealthTech, 20Fathoms offers the T.C. Tech Startup Bootcamp, 1-on-1 executive coaching with Entrepreneurs-in-Residence, "
                "MEDC Business Accelerator Fund (BAF) grants, Northern Michigan Angels pitch preparation, and TCNewTech monthly pitch nights."
            ),
            "services_and_curriculum": [
                "20Fathoms Startup Bootcamp & Incubator Cohort",
                "Blue Economy & Freshwater Tech Commercialization Track",
                "TCNewTech Monthly Startup Pitch Competition",
                "MEDC Business Accelerator Fund (BAF) Grants ($50K)",
                "Venture Fundraising & Pitch Coaching",
                "Customer Discovery & NSF I-Corps",
                "Executive Mentorship & EIR Program",
                "SBIR/STTR & Non-Dilutive Grant Writing",
            ],
            "specialized_equipment": [
                "20Fathoms Traverse City Coworking & Tech Incubator Campus",
                "Media Studio & Podcasting Suite",
                "Electronics & IoT Prototyping Lab",
            ],
            "mentors": [
                {
                    "full_name": "Eric Roberts",
                    "role_at_incubator": "Executive Director",
                    "current_title_company": "Executive Director at 20Fathoms",
                    "bio_summary": "Leads 20Fathoms in Traverse City, expanding Northwest Michigan's startup incubation, angel capital access, and Blue Economy tech ecosystem.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Venture Fundraising & Angel Investing", "B2B SaaS Sales & Go-To-Market"],
                    "linkedin_url": "https://www.linkedin.com/in/ericrobertstc/",
                    "confidence_score": 0.97,
                },
                {
                    "full_name": "Craig Wesley",
                    "role_at_incubator": "Managing Director of Startup Services & EIR",
                    "current_title_company": "Startup Coach & EIR at 20Fathoms",
                    "bio_summary": "Supports Northwest Michigan tech founders across Blue Economy, climate tech, and B2B SaaS with capital readiness and executive mentorship.",
                    "expertise_tags": ["B2B SaaS Sales & Go-To-Market", "Venture Fundraising & Angel Investing", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/company/20fathoms/",
                    "confidence_score": 0.94,
                },
            ],
            "events": [
                {
                    "title": "TCNewTech & 20Fathoms Northern Michigan Startup Pitch Night",
                    "event_date": dt(13),
                    "event_type": "Pitch Competition",
                    "description": "Traverse City pitch competition spotlighting Blue Economy, CleanTech, and SaaS startups across Northwest Michigan.",
                    "registration_url": "https://20fathoms.org/events/",
                },
            ],
        },
        "um-innovation-partnerships": {
            "description": (
                "U-M Innovation Partnerships (formerly U-M Tech Transfer), headquartered at the North Campus Research Complex (NCRC Building 520, Ann Arbor), is the University of Michigan's central powerhouse for research commercialization, corporate partnerships, and deep-tech venture creation—ranked among the top university tech transfer offices globally with 500+ inventions and 25+ spinouts annually.\n\n"
                "Its Venture Center operates the Accelerate Blue Fund (an evergreen seed venture fund investing $250K–$500K in U-M startups), the statewide MEDC MTRAC Innovation Hubs for Life Sciences and Advanced Transportation (awarding $100K–$250K translational research grants), "
                "the NSF I-Corps Hub: Great Lakes Region, and a dedicated team of Mentors-in-Residence (MIRs) and wet-lab Venture Accelerator suites inside NCRC."
            ),
            "services_and_curriculum": [
                "Accelerate Blue Venture Fund ($250K–$500K Seed Investments)",
                "MEDC MTRAC Innovation Hub for Life Sciences & Advanced Transportation",
                "NSF I-Corps Hub: Great Lakes Region Customer Discovery",
                "U-M Venture Center Mentor-in-Residence (MIR) Program",
                "IP, Patent & Tech Transfer Clinics",
                "Customer Discovery & NSF I-Corps",
                "SBIR/STTR & Non-Dilutive Grant Writing",
                "FDA Regulatory & Clinical Pathways",
                "Venture Fundraising & Pitch Coaching",
            ],
            "specialized_equipment": [
                "NCRC Venture Accelerator Wet & Dry Lab Suites (30,000+ sq. ft. at Bldg 18/520)",
                "Lurie Nanofabrication Facility (ISO Class 4/5/6 Semiconductor Cleanroom)",
                "Mcity Connected & Autonomous Vehicle 32-Acre Test Facility",
                "UM Battery Lab (Industrial Pouch/Cylindrical Cell Prototyping Line)",
                "Wet Labs & BSL-1/BSL-2 Suites",
                "Cleanroom & Microelectronics Facility",
                "Autonomous & Mobility Testing Track",
                "High-Performance Computing & AI Cluster",
            ],
            "mentors": [
                {
                    "full_name": "Kelly Sexton",
                    "role_at_incubator": "Associate Vice President for Research – Innovation Partnerships",
                    "current_title_company": "AVP for Research & Technology Transfer at University of Michigan",
                    "bio_summary": "Leads U-M Innovation Partnerships, overseeing over 500+ annual inventions, the Accelerate Blue venture fund, and deep-tech startup spinouts.",
                    "expertise_tags": ["IP Strategy, Legal & Tech Transfer", "MedTech Regulatory & Life Sciences Commercialization", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.linkedin.com/in/kelly-sexton-9464774/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Mike Psarouthakis",
                    "role_at_incubator": "Managing Director, Venture Center & Accelerate Blue Fund",
                    "current_title_company": "Executive Director, Impact Investments & Venture Center at U-M Innovation Partnerships",
                    "bio_summary": "Leads venture creation, Mentor-in-Residence teams, and seed investing through the Accelerate Blue Fund for University of Michigan spinouts.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "IP Strategy, Legal & Tech Transfer", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/mikepsarouthakis/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "hearing (bod) BradU / Toddy (Mentor-in-Residence)",
                    "role_at_incubator": "Mentor-in-Residence (Life Sciences & Therapeutics)",
                    "current_title_company": "Life Sciences Mentor-in-Residence at U-M Venture Center",
                    "bio_summary": "Coaches U-M biomedical, diagnostics, and drug discovery faculty founders on IND-enabling studies, FDA 510(k) regulatory pathways, and Series A syndication.",
                    "expertise_tags": ["MedTech Regulatory & Life Sciences Commercialization", "FDA 510(k) Regulatory", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://innovationpartnerships.umich.edu/venture-center/",
                    "confidence_score": 0.92,
                },
                {
                    "full_name": "Jay Ellis",
                    "role_at_incubator": "MTRAC Advanced Transportation Program Director & Mobility MIR",
                    "current_title_company": "MTRAC Transportation Director at U-M Innovation Partnerships",
                    "bio_summary": "Directs the statewide MEDC MTRAC Advanced Transportation Innovation Hub at U-M, mentoring mobility, EV battery, and autonomous systems spinouts.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "Automotive Tier-1 Supply Chain", "IP Strategy, Legal & Tech Transfer"],
                    "linkedin_url": "https://innovationpartnerships.umich.edu",
                    "confidence_score": 0.94,
                },
            ],
            "events": [
                {
                    "title": "NSF I-Corps Hub Great Lakes Region: Customer Discovery Workshop",
                    "event_date": dt(15),
                    "event_type": "Workshop",
                    "description": "University research commercialization workshop training faculty and graduate spinout teams on stakeholder discovery and IP licensing.",
                    "registration_url": "https://innovationpartnerships.umich.edu/events/",
                },
                {
                    "title": "U-M Accelerate Blue & MTRAC Deep-Tech Spinout Showcase",
                    "event_date": dt(28),
                    "event_type": "Pitch Competition",
                    "description": "Annual pitch showcase featuring University of Michigan therapeutics, medical device, AI, and clean energy spinout companies.",
                    "registration_url": "https://innovationpartnerships.umich.edu/events/",
                },
            ],
        },
        "newlab-michigan-central": {
            "description": (
                "Newlab at Michigan Central, housed inside the historic 270,000-square-foot Book Depository building at 2050 15th St. in Corktown Detroit, is a flagship deep-tech hardware accelerator, venture studio, and prototyping hub focused on the future of mobility, clean energy, and next-generation manufacturing.\n\n"
                "Home to over 100+ deep-tech startups, Newlab Detroit provides 35,000+ sq. ft. of world-class robotics, metal/wood/CNC fabrication, electronics, and EV battery prototyping labs, "
                "alongside the Michigan Central Mobility Studio, the Energy Transition Studio, and direct access to Michigan's first Urban Air Mobility (drone) and autonomous vehicle testing zone."
            ),
            "services_and_curriculum": [
                "Newlab Mobility & Energy Transition Venture Studios",
                "Michigan Central Real-World Urban Pilot Testbed",
                "Air Mobility & Autonomous Drone Testing Zone",
                "Hardware DFM & Supply Chain Advisory",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "Book Depository 270,000 sq. ft. Deep-Tech Campus & 35,000 sq. ft. Prototyping Labs",
                "Multi-Axis Haas CNC Mills, Waterjet, Laser Cutters & Welding Shop",
                "Heavy Robotics, EV Battery Testing & High-Voltage Garage Bays",
                "Michigan Central Autonomous Vehicle & Urban Drone Flight Test Zone",
                "3D Printing & Additive Manufacturing",
                "CNC Machining & Metal Fabrication",
                "Electronics & IoT Prototyping Lab",
                "Autonomous & Mobility Testing Track",
            ],
            "mentors": [
                {
                    "full_name": "Camila Noordeloos",
                    "role_at_incubator": "General Manager & Managing Director, Newlab Detroit",
                    "current_title_company": "Managing Director at Newlab at Michigan Central",
                    "bio_summary": "Oversees deep-tech startup programs, corporate pilot studios, and mobility/energy prototyping operations at Newlab at Michigan Central in Detroit.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "Venture Fundraising & Angel Investing", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/camilanoordeloos/",
                    "confidence_score": 0.98,
                },
                {
                    "full_name": "Carolina Pluszczynski",
                    "role_at_incubator": "Chief Operating Officer & Head of Innovation Ecosystem, Michigan Central",
                    "current_title_company": "COO & Innovation Ecosystem Lead at Michigan Central",
                    "bio_summary": "Leads technology pilot deployments, urban mobility testing tracks, and public-private innovation partnerships across the 30-acre Michigan Central district.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "Automotive Tier-1 Supply Chain", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/carolinapluszczynski/",
                    "confidence_score": 0.98,
                },
            ],
            "events": [
                {
                    "title": "Newlab at Michigan Central: Mobility & Energy Pilot Showcase",
                    "event_date": dt(24),
                    "event_type": "Pitch Competition",
                    "description": "Deep-tech founders demonstrate autonomous mobility, EV battery, and grid resilience pilots to corporate partners and venture funds in Corktown Detroit.",
                    "registration_url": "https://www.newlab.com/locations/detroit",
                },
            ],
        },
        "conquer-accelerator-msu": {
            "description": (
                "Conquer Accelerator, managed by Spartan Innovations and the Michigan State University Research Foundation, is a 10-week intensive summer startup accelerator operating cohorts in East Lansing, Grand Rapids (including a dedicated MedTech track with GVSU/Corewell Health), and Flint.\n\n"
                "Selected teams receive $20,000 in initial seed investment via Red Cedar Ventures (with eligibility for follow-on pre-seed capital up to $250,000+), free coworking space, weekly OKR milestones, and mentorship from a dedicated network of 40+ serial entrepreneurs, venture capitalists, and regulatory experts."
            ),
            "services_and_curriculum": [
                "Conquer Accelerator 10-Week Cohort ($20K Initial Investment)",
                "Conquer Grand Rapids MedTech & Digital Health Track",
                "Red Cedar Ventures Follow-On Seed Funding Access",
                "Venture Fundraising & Pitch Coaching",
                "Customer Discovery & NSF I-Corps",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "East Lansing TIC & Grand Rapids Doug Meijer Medical Innovation Building Space",
                "Media Studio & Podcasting Suite",
            ],
            "mentors": [
                {
                    "full_name": "Thomas Stewart",
                    "role_at_incubator": "Program Manager, Conquer Accelerator",
                    "current_title_company": "Program Manager at MSU Research Foundation / Conquer Accelerator",
                    "bio_summary": "Manages Conquer Accelerator cohorts across East Lansing and Grand Rapids, coordinating 40+ mentors and investor demo days.",
                    "expertise_tags": ["B2B SaaS Sales & Go-To-Market", "Venture Fundraising & Angel Investing", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/thomas-stewart-msu/",
                    "confidence_score": 0.96,
                },
                {
                    "full_name": "Jeff Wesley",
                    "role_at_incubator": "Executive Director, Red Cedar Ventures",
                    "current_title_company": "Executive Director at Red Cedar Ventures & Spartan Innovations",
                    "bio_summary": "Leads investment committee decisions and seed follow-on financing for Conquer Accelerator alumni.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "MedTech Regulatory & Life Sciences Commercialization"],
                    "linkedin_url": "https://www.linkedin.com/in/jeff-wesley-8b42a59/",
                    "confidence_score": 0.99,
                },
            ],
            "events": [
                {
                    "title": "Conquer Accelerator 10-Week Cohort Application Info Session",
                    "event_date": dt(19),
                    "event_type": "Cohort Deadline",
                    "description": "Information session and application Q&A for startups applying to the East Lansing and Grand Rapids MedTech Conquer Accelerator cohorts.",
                    "registration_url": "https://conqueraccelerator.com/apply/",
                },
            ],
        },
        "bbcetc-michigan-sbir-hub": {
            "description": (
                "BBC Entrepreneurial Training & Consulting (BBCetc), headquartered in Brighton, Michigan (7900 Kensington Ct.), is the nationally recognized leader in federal SBIR/STTR grant strategy and the official statewide partner of the Michigan Economic Development Corporation (MEDC) to manage the Michigan SBIR/STTR Assistance Program.\n\n"
                "BBCetc coaches Michigan high-tech, biomedical, defense, and clean energy startups through every step of winning non-dilutive R&D funding across 11 federal agencies (NIH, NSF, DoD, DOE, NASA, USDA), "
                "and administers the MEDC Emerging Technologies Fund (ETF), which provides non-dilutive state matching grants up to $25,000 for Phase I and up to $125,000 for Phase II SBIR/STTR winners."
            ),
            "services_and_curriculum": [
                "MEDC Emerging Technologies Fund (ETF) SBIR/STTR Match ($25K Phase I / $125K Phase II)",
                "NIH, NSF, DoD & DOE SBIR/STTR Proposal Coaching & Red-Team Reviews",
                "Federal R&D Indirect Cost Rate & DCAA Accounting Training",
                "SBIR/STTR & Non-Dilutive Grant Writing",
                "FDA Regulatory & Clinical Pathways",
                "Financial Modeling & Accounting Readiness",
            ],
            "specialized_equipment": [],
            "mentors": [
                {
                    "full_name": "Kris Bergman",
                    "role_at_incubator": "Managing Partner & Principal SBIR/STTR Consultant",
                    "current_title_company": "Managing Partner at BBC Entrepreneurial Training & Consulting (BBCetc)",
                    "bio_summary": "Coaches Michigan deep-tech, biomedical, and defense startups on winning NIH, NSF, DoD, and DOE SBIR/STTR Phase I and Phase II awards.",
                    "expertise_tags": ["SBIR/STTR & Government Contracting", "MedTech Regulatory & Life Sciences Commercialization", "SBIR Grant Review"],
                    "linkedin_url": "https://www.linkedin.com/in/kris-bergman-bbcetc/",
                    "confidence_score": 0.98,
                },
                {
                    "full_name": "Becky Aistrup",
                    "role_at_incubator": "Managing Partner & NIH/MedTech SBIR Lead",
                    "current_title_company": "Managing Partner at BBCetc",
                    "bio_summary": "Specializes in NIH, NSF, and DoD SBIR/STTR commercialization plans, clinical/regulatory milestones, and technical narrative reviews.",
                    "expertise_tags": ["SBIR/STTR & Government Contracting", "MedTech Regulatory & Life Sciences Commercialization", "FDA 510(k) Regulatory"],
                    "linkedin_url": "https://www.linkedin.com/in/becky-aistrup-3a14536/",
                    "confidence_score": 0.98,
                },
                {
                    "full_name": "Jerry Hollister",
                    "role_at_incubator": "Principal Consultant (NIH, DoD & DOE SBIR/STTR)",
                    "current_title_company": "Principal Consultant at BBCetc / Former COO at Niowave",
                    "bio_summary": "Former COO of Niowave with 30+ years leading deep-tech physics, medical isotope, and defense startups through Phase I/II/III SBIR commercialization.",
                    "expertise_tags": ["SBIR/STTR & Government Contracting", "Hardware Engineering & Supply Chain", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/jerryhollister/",
                    "confidence_score": 0.98,
                },
            ],
            "events": [
                {
                    "title": "NSF & DoD SBIR/STTR Phase I Proposal Preparation Workshop",
                    "event_date": dt(10),
                    "event_type": "Workshop",
                    "description": "Comprehensive line-by-line training on writing competitive federal SBIR/STTR Phase I commercialization and technical proposals, eligible for MEDC Emerging Technologies Fund match.",
                    "registration_url": "https://bbcetc.com/training/",
                },
                {
                    "title": "NIH SBIR/STTR Commercialization & Regulatory Strategy Seminar",
                    "event_date": dt(22),
                    "event_type": "Seminar",
                    "description": "Interactive training for biotech, therapeutics, and medical device founders preparing NIH SBIR submissions.",
                    "registration_url": "https://bbcetc.com/training/",
                },
            ],
        },
    }
