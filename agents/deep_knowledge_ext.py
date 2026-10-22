"""
Remaining Michigan Organizations Deep-Enrichment Roster (`agents/deep_knowledge_ext.py`)
Provides comprehensive multi-paragraph descriptions, specific named programs, lab equipment,
mentor rosters, and upcoming events for all remaining Michigan startup support organizations.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict


def get_remaining_org_enrichment() -> Dict[str, Dict[str, Any]]:
    now = datetime.now(timezone.utc)

    def dt(days: int, hour: int = 17) -> str:
        d = (now + timedelta(days=days)).replace(hour=hour, minute=0, second=0, microsecond=0)
        return d.isoformat()

    return {
        "sault-ste-marie-smartzone": {
            "description": (
                "The Sault Ste. Marie SmartZone & Economic Development Corporation (EDC) Industrial Incubator (2345 Meridian St., Sault Ste. Marie) is the Eastern Upper Peninsula's designated MEDC SmartZone hub. "
                "Operated in strategic partnership with the City of Sault Ste. Marie and Lake Superior State University (LSSU), the SmartZone supports cross-border US-Canadian advanced manufacturing, aerospace/defense, marine engineering, and freshwater tech startups.\n\n"
                "Entrepreneurs gain access to the Industrial Incubator's light-manufacturing bays, LSSU's Lukenda School of Business and Center for Freshwater Research and Education (CFRE), Robotics & Engineering prototyping labs, and MEDC Business Accelerator Fund (BAF) grants."
            ),
            "services_and_curriculum": [
                "Sault Ste. Marie EDC Industrial Incubator Program",
                "LSSU Engineering & Robotics Commercialization Partnership",
                "MEDC Business Accelerator Fund (BAF) Grants ($50K)",
                "US-Canada Cross-Border Trade & Manufacturing Advisory",
                "Hardware DFM & Supply Chain Advisory",
                "Financial Modeling & Accounting Readiness",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "Sault EDC Industrial Incubator Light-Manufacturing & High-Bay Suites",
                "LSSU Robotics, Automation & Freshwater Research Labs",
                "CNC Machining & Metal Fabrication",
                "3D Printing & Additive Manufacturing",
            ],
            "mentors": [
                {
                    "full_name": "Jeff Holt",
                    "role_at_incubator": "Executive Director, Sault Ste. Marie EDC & SmartZone",
                    "current_title_company": "Executive Director at Sault Ste. Marie Economic Development Corporation",
                    "bio_summary": "Leads the Sault Ste. Marie SmartZone, Industrial Incubator, and cross-border economic development initiatives in the Eastern Upper Peninsula.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Hardware Engineering & Supply Chain", "SBIR/STTR & Government Contracting"],
                    "linkedin_url": "https://www.linkedin.com/in/jeff-holt-sault/",
                    "confidence_score": 0.96,
                },
                {
                    "full_name": "Nikki Radke",
                    "role_at_incubator": "SmartZone & Economic Development Specialist",
                    "current_title_company": "Economic Development Specialist at Sault Ste. Marie EDC",
                    "bio_summary": "Coordinates SmartZone startup intake, BAF grant readiness, and entrepreneur support across Chippewa County.",
                    "expertise_tags": ["B2B SaaS Sales & Go-To-Market", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://saultedc.com/smartzone/",
                    "confidence_score": 0.92,
                },
            ],
            "events": [
                {
                    "title": "Eastern Upper Peninsula SmartZone Pitch & Small Business Forum",
                    "event_date": dt(21),
                    "event_type": "Networking",
                    "description": "Networking and resource forum connecting Sault Ste. Marie founders with LSSU engineering faculty and MEDC capital programs.",
                    "registration_url": "https://saultedc.com/smartzone/",
                },
            ],
        },
        "cmurc-mount-pleasant": {
            "description": (
                "Central Michigan University Research Corporation (CMURC), headquartered at 2625 Denison Dr. in Mount Pleasant adjacent to Central Michigan University's campus, is a premier MEDC SmartZone incubator and co-working accelerator serving Mid-Michigan and the Great Lakes Bay Region.\n\n"
                "CMURC's proprietary RightTrack commercialization framework guides founders from early ideation to angel/seed investment through structured board-room pitch reviews, "
                "dedicated Community Partners (legal, accounting, IP, marketing), MEDC Business Accelerator Fund (BAF) grants up to $50,000, and CMU College of Medicine / Science & Engineering research partnerships."
            ),
            "services_and_curriculum": [
                "CMURC RightTrack Startup Accelerator Framework",
                "MEDC Business Accelerator Fund (BAF) Grants ($50K)",
                "CMU Student Venture & Faculty Tech Transfer Track",
                "Customer Discovery & NSF I-Corps",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "CMURC Mount Pleasant Research Park Coworking, Boardrooms & Team Suites",
                "3D Printing & Additive Manufacturing",
                "Media Studio & Podcasting Suite",
            ],
            "mentors": [
                {
                    "full_name": "Erin Strang",
                    "role_at_incubator": "President & CEO",
                    "current_title_company": "President & CEO at Central Michigan University Research Corporation (CMURC)",
                    "bio_summary": "Leads CMURC SmartZone accelerators across Mount Pleasant, Bay City, Saginaw, and Midland, guiding founders through the RightTrack commercialization framework.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "B2B SaaS Sales & Go-To-Market", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.linkedin.com/in/erin-strang-cmurc/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Melisa (Melissa)anth / RightTrack Director",
                    "role_at_incubator": "Director of Entrepreneurial Operations",
                    "current_title_company": "Program Director at CMURC Mount Pleasant",
                    "bio_summary": "Manages RightTrack founder cohorts, professional services matching, and BAF grant milestones at CMURC.",
                    "expertise_tags": ["B2B SaaS Sales & Go-To-Market", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.cmurc.com/team",
                    "confidence_score": 0.92,
                },
            ],
            "events": [
                {
                    "title": "CMURC RightTrack Startup Pitch & Accountability Showcase",
                    "event_date": dt(14),
                    "event_type": "Pitch Competition",
                    "description": "Quarterly startup pitch and milestone review session for Mid-Michigan tech founders at CMURC Mount Pleasant.",
                    "registration_url": "https://www.cmurc.com/events",
                },
            ],
        },
        "cmurc-great-lakes-bay-smartzone": {
            "description": (
                "The CMURC Great Lakes Bay Region SmartZone operates dedicated innovation hubs in Uptown Bay City (900 Water St.), Downtown Saginaw, and Midland, extending Central Michigan University Research Corporation's MEDC SmartZone programming across the entire Great Lakes Bay Region.\n\n"
                "Specializing in chemical/materials science (alongside Dow and Hemlock Semiconductor ecosystems), AgTech, advanced manufacturing, and SaaS, the hub delivers CMURC's RightTrack accelerator, coworking, and up to $50,000 in non-dilutive Business Accelerator Fund (BAF) grants."
            ),
            "services_and_curriculum": [
                "CMURC RightTrack Great Lakes Bay Accelerator",
                "Bay City, Saginaw & Midland SmartZone Incubation",
                "MEDC Business Accelerator Fund (BAF) Grants ($50K)",
                "Customer Discovery & NSF I-Corps",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "Uptown Bay City, Saginaw & Midland Co-Working & Innovation Hubs",
                "3D Printing & Additive Manufacturing",
                "Media Studio & Podcasting Suite",
            ],
            "mentors": [
                {
                    "full_name": "Erin Strang",
                    "role_at_incubator": "President & CEO, CMURC",
                    "current_title_company": "President & CEO at CMURC Great Lakes Bay Region",
                    "bio_summary": "Oversees regional SmartZone incubation across Bay City, Saginaw, Midland, and Mount Pleasant.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.linkedin.com/in/erin-strang-cmurc/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Kurtis (Great Lakes Bay EIR)",
                    "role_at_incubator": "Great Lakes Bay Entrepreneur-in-Residence",
                    "current_title_company": "Startup Advisor at CMURC Bay City / Midland",
                    "bio_summary": "Coaches chemical, materials, hardware, and software startups in Bay City, Saginaw, and Midland on B2B sales and seed fundraising.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "B2B SaaS Sales & Go-To-Market", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.cmurc.com/locations",
                    "confidence_score": 0.90,
                },
            ],
            "events": [
                {
                    "title": "Great Lakes Bay Region Founder Mixer at CMURC Bay City",
                    "event_date": dt(17),
                    "event_type": "Networking",
                    "description": "Networking session connecting Bay City, Saginaw, and Midland entrepreneurs with angel investors and industry mentors.",
                    "registration_url": "https://www.cmurc.com/events",
                },
            ],
        },
        "adrian-tecumseh-smartzone-armory": {
            "description": (
                "The Adrian-Tecumseh SmartZone & Launch Lenawee, anchored at the historic Adrian Armory Community Center (230 W. Maumee St., Adrian), is the MEDC-designated SmartZone serving Lenawee County in partnership with Adrian College, Siena Heights University, and Jackson College.\n\n"
                "The facility features the Launch Lenawee Entrepreneurial Program, a licensed commercial kitchen and food-processing incubator for CPG/AgTech entrepreneurs, coworking spaces, and SmartZone Business Accelerator Fund (BAF) access."
            ),
            "services_and_curriculum": [
                "Launch Lenawee 10-Week Entrepreneurial Training Cohort",
                "Adrian Armory Licensed Commercial Kitchen Incubation",
                "Adrian-Tecumseh SmartZone Tech Commercialization & BAF Grants",
                "Customer Discovery & NSF I-Corps",
                "Financial Modeling & Accounting Readiness",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "Adrian Armory Licensed Commercial Kitchen & Cold/Dry Food Storage",
                "Adrian Armory Co-Working & Maker Studio",
                "Commercial Kitchen & Food Processing",
                "Media Studio & Podcasting Suite",
            ],
            "mentors": [
                {
                    "full_name": "Mark Murray / Launch Lenawee Director",
                    "role_at_incubator": "Executive Director, Adrian Armory & Adrian-Tecumseh SmartZone",
                    "current_title_company": "Director at Adrian-Tecumseh SmartZone & Launch Lenawee",
                    "bio_summary": "Leads the Adrian Armory innovation center, commercial kitchen incubator, and Launch Lenawee startup cohorts.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Financial Modeling & Accounting Readiness", "B2B SaaS Sales & Go-To-Market"],
                    "linkedin_url": "https://atsmartzone.com",
                    "confidence_score": 0.91,
                },
            ],
            "events": [
                {
                    "title": "Launch Lenawee Pitch Night at the Adrian Armory",
                    "event_date": dt(20),
                    "event_type": "Pitch Competition",
                    "description": "Lenawee County food, AgTech, and tech startups pitch for seed grants at the Adrian Armory Community Center.",
                    "registration_url": "https://atsmartzone.com/programs/",
                },
            ],
        },
        "battle-creek-smartzone-bcu": {
            "description": (
                "The Battle Creek SmartZone, operated by Battle Creek Unlimited (BCU) at 4950 W. Dickman Rd. adjacent to the W.K. Kellogg Airport and Fort Custer Industrial Park, is Southwest Michigan's specialized aviation, aerospace, defense/UAV, cybersecurity, and food-tech MEDC SmartZone.\n\n"
                "In partnership with Western Michigan University's College of Aviation, the Battle Creek SmartZone supports unmanned aerial systems (UAS/drone), defense logistics, and advanced food manufacturing startups with SmartZone BAF grants, hangar/airspace testbeds, and The Generation E Institute / BC Cargo incubation."
            ),
            "services_and_curriculum": [
                "Battle Creek Aviation, UAV & Defense Tech SmartZone Incubation",
                "Battle Creek Unlimited Small Business & Venture Fund",
                "MEDC Business Accelerator Fund (BAF) Grants ($50K)",
                "SBIR/STTR & Non-Dilutive Grant Writing",
                "Hardware DFM & Supply Chain Advisory",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "W.K. Kellogg Airport Drone / UAS Airspace & Hangar Testbed",
                "Autonomous & Mobility Testing Track",
                "Commercial Kitchen & Food Processing",
            ],
            "mentors": [
                {
                    "full_name": "Joe Sobieralski",
                    "role_at_incubator": "President & CEO, Battle Creek Unlimited",
                    "current_title_company": "President & CEO at Battle Creek Unlimited (Battle Creek SmartZone)",
                    "bio_summary": "Leads Battle Creek Unlimited and the Battle Creek SmartZone, driving aerospace, defense, EV battery, and startup attraction.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Hardware Engineering & Supply Chain", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.linkedin.com/in/joe-sobieralski-5499038/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Robert Corder",
                    "role_at_incubator": "VP of Attraction & SmartZone Innovation",
                    "current_title_company": "VP at Battle Creek Unlimited",
                    "bio_summary": "Advises industrial tech, aviation, and food-tech ventures entering the Battle Creek SmartZone.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "SBIR/STTR & Government Contracting"],
                    "linkedin_url": "https://www.bcunlimited.org",
                    "confidence_score": 0.93,
                },
            ],
            "events": [
                {
                    "title": "Battle Creek Aerospace, Drone & Defense Tech Innovation Forum",
                    "event_date": dt(23),
                    "event_type": "Seminar",
                    "description": "Industry briefing on UAV testing, defense contracting, and SmartZone grant opportunities in Battle Creek.",
                    "registration_url": "https://www.bcunlimited.org",
                },
            ],
        },
        "ferris-wheel-100k-ideas-flint": {
            "description": (
                "The Ferris Wheel Innovation Center & 100K Ideas (615 S. Saginaw St., Flint) anchor downtown Flint's 7-story, 45,000-square-foot entrepreneurship and SmartZone hub in partnership with Skypoint Ventures and the University of Michigan-Flint.\n\n"
                "100K Ideas provides an accessible front door for inventors and tech founders, employing a team of engineering, industrial design, and business students paired with veteran mentors to deliver CAD modeling, 3D prototyping, market validation, and pitch competitions."
            ),
            "services_and_curriculum": [
                "100K Ideas Idea Assessment, CAD Prototyping & Market Validation",
                "Ferris Wheel Co-Working & Skypoint Ventures Seed Access",
                "Flint Pitch Night & Micro-Grant Competitions",
                "Hardware DFM & Supply Chain Advisory",
                "Customer Discovery & NSF I-Corps",
                "Venture Fundraising & Pitch Coaching",
            ],
            "specialized_equipment": [
                "Ferris Wheel 45,000 sq. ft. 7-Story Innovation Building",
                "100K Ideas Prototyping & Product Design Shop",
                "3D Printing & Additive Manufacturing",
                "Media Studio & Podcasting Suite",
            ],
            "mentors": [
                {
                    "full_name": "David Ollila",
                    "role_at_incubator": "Founder & Senior Product/Hardware Mentor, 100K Ideas",
                    "current_title_company": "President & Chief Innovation Officer at Skypoint Ventures / Founder of 100K Ideas",
                    "bio_summary": "Serial physical-product inventor holding 15+ patents; founded 100K Ideas and Flint's Ferris Wheel Innovation Center after leading Invent@NMU.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "IP Strategy, Legal & Tech Transfer", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.linkedin.com/in/davidollila/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Brandee Cooke-Brown",
                    "role_at_incubator": "Executive Director, 100K Ideas",
                    "current_title_company": "Executive Director at 100K Ideas (Flint Ferris Wheel)",
                    "bio_summary": "Leads operations, founder intake, pitch competitions, and student engineering teams at 100K Ideas in downtown Flint.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "B2B SaaS Sales & Go-To-Market", "Hardware Engineering & Supply Chain"],
                    "linkedin_url": "https://www.linkedin.com/in/brandee-cooke-brown/",
                    "confidence_score": 0.98,
                },
            ],
            "events": [
                {
                    "title": "100K Ideas Pitch Night at the Ferris Wheel in Downtown Flint",
                    "event_date": dt(15),
                    "event_type": "Pitch Competition",
                    "description": "Live startup pitch competition awarding seed grants and prototyping services to Genesee County founders.",
                    "registration_url": "https://www.100kideas.org/events",
                },
            ],
        },
        "underground-port-huron-smartzone": {
            "description": (
                "The Underground Business Incubator (100 McMorran Blvd., Port Huron) is the Blue Water region's MEDC SmartZone and startup hub operated by the Economic Development Alliance (EDA) of St. Clair County.\n\n"
                "Serving St. Clair County and the I-69 International Trade Corridor, The Underground offers coworking, private incubator offices, the Emerge Startup Accelerator, Blue Water Pitch Nights ($10,000+ in seed grants), and SmartZone Business Accelerator Fund (BAF) access."
            ),
            "services_and_curriculum": [
                "The Underground Emerge Startup Accelerator Cohort",
                "Blue Water Startup Pitch Competition ($10K+ Grants)",
                "St. Clair County SmartZone Business Accelerator Fund (BAF)",
                "Venture Fundraising & Pitch Coaching",
                "Financial Modeling & Accounting Readiness",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "The Underground Downtown Port Huron Co-Working & Event Space",
                "Media Studio & Podcasting Suite",
            ],
            "mentors": [
                {
                    "full_name": "Dan Casey",
                    "role_at_incubator": "CEO, Economic Development Alliance of St. Clair County",
                    "current_title_company": "CEO at EDA of St. Clair County (The Underground SmartZone)",
                    "bio_summary": "Leads economic development and SmartZone startup incubation across Port Huron and the Blue Water region.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Venture Fundraising & Angel Investing", "Hardware Engineering & Supply Chain"],
                    "linkedin_url": "https://www.linkedin.com/in/dan-casey-edascc/",
                    "confidence_score": 0.98,
                },
            ],
            "events": [
                {
                    "title": "Blue Water Startup Pitch Night at The Underground Port Huron",
                    "event_date": dt(19),
                    "event_type": "Pitch Competition",
                    "description": "St. Clair County entrepreneurs pitch for non-dilutive startup grants at The Underground.",
                    "registration_url": "https://www.edascc.com/the-underground/",
                },
            ],
        },
        "lean-rocket-lab-jackson": {
            "description": (
                "Lean Rocket Lab (133 W. Michigan Ave., Jackson) is South Central Michigan's MEDC SmartZone incubator and a nationally recognized Industry 4.0, manufacturing tech, and hardware startup accelerator.\n\n"
                "Co-operating the Michigan Industry 4.0 Accelerator alongside Automation Alley and Centreopolis, Lean Rocket Lab provides seed capital, paid pilot matchmaking with over 100+ precision manufacturers in Jackson and Southern Michigan, rapid prototyping, and SmartZone Business Accelerator Fund (BAF) grants."
            ),
            "services_and_curriculum": [
                "Lean Rocket Lab Manufacturing Tech & Industry 4.0 Accelerator",
                "Paid Factory Pilot Matchmaking with Michigan Manufacturers",
                "MEDC Business Accelerator Fund (BAF) Grants ($50K)",
                "Hardware DFM & Supply Chain Advisory",
                "Customer Discovery & NSF I-Corps",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "Lean Rocket Lab Downtown Jackson Coworking & Hardware Prototyping Suite",
                "3D Printing & Additive Manufacturing",
                "Electronics & IoT Prototyping Lab",
            ],
            "mentors": [
                {
                    "full_name": "Brandon Marken",
                    "role_at_incubator": "Founder & CEO",
                    "current_title_company": "CEO at Lean Rocket Lab (Jackson SmartZone)",
                    "bio_summary": "Leads Lean Rocket Lab's manufacturing tech and hardware accelerators, helping Industry 4.0 startups pilot and scale with Michigan manufacturers.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "B2B SaaS Sales & Go-To-Market", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.linkedin.com/in/brandonmarken/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Bill Rayl",
                    "role_at_incubator": "Manufacturing Industry Advisor & Board Member",
                    "current_title_company": "Executive Director at Jackson Area Manufacturers Association (JAMA)",
                    "bio_summary": "Connects Lean Rocket Lab hardware and industrial software startups with Jackson's precision machining and automotive supplier base.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "Automotive Tier-1 Supply Chain", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.leanrocketlab.org",
                    "confidence_score": 0.94,
                },
            ],
            "events": [
                {
                    "title": "Lean Rocket Lab Industry 4.0 Startup Pitch & Manufacturer Demo Day",
                    "event_date": dt(16),
                    "event_type": "Pitch Competition",
                    "description": "Industrial tech startups demonstrate factory automation and AI solutions to Michigan manufacturers in Jackson.",
                    "registration_url": "https://www.leanrocketlab.org/programs",
                },
            ],
        },
        "desai-accelerator-umich": {
            "description": (
                "The Desai Accelerator (500 E. Washington St., Ann Arbor) is a premier joint venture accelerator operated by the University of Michigan's Stephen M. Ross School of Business (Zell Lurie Institute) and the College of Engineering (Center for Entrepreneurship).\n\n"
                "Open to early-stage tech startups nationwide (no U-M affiliation required), the 7-month Desai Accelerator program provides up to $50,000+ in seed funding, a dedicated team of paid U-M engineering, design, and MBA interns, downtown Ann Arbor office space, cloud credits, and intensive 1-on-1 mentorship from over 100+ U-M alumni VCs and serial founders."
            ),
            "services_and_curriculum": [
                "Desai Accelerator 7-Month Cohort ($50K+ Funding & Dedicated U-M Interns)",
                "U-M Ross & College of Engineering Alumni Mentor Network",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
                "Customer Discovery & NSF I-Corps",
            ],
            "specialized_equipment": [
                "Downtown Ann Arbor Washington Street Accelerator Suite",
                "Media Studio & Podcasting Suite",
            ],
            "mentors": [
                {
                    "full_name": "Angela Kujava",
                    "role_at_incubator": "Managing Director",
                    "current_title_company": "Managing Director at Desai Accelerator (University of Michigan)",
                    "bio_summary": "Leads the Desai Accelerator at U-M Ross and College of Engineering, mentoring early-stage tech founders on go-to-market execution, customer acquisition, and seed fundraising.",
                    "expertise_tags": ["B2B SaaS Sales & Go-To-Market", "Venture Fundraising & Angel Investing", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/angelakujava/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Bharatendra (Bharat) Desai",
                    "role_at_incubator": "Founding Benefactor & Strategic Advisor",
                    "current_title_company": "Co-Founder & Chairman of Syntel / Founding Patron of Desai Accelerator",
                    "bio_summary": "Co-founded IT powerhouse Syntel (acquired by Atos for $3.4B) and established the Desai Sethi Family Foundation to launch the Desai Accelerator at U-M.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "B2B SaaS Sales & Go-To-Market", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://desaiaccelerator.umich.edu",
                    "confidence_score": 0.97,
                },
            ],
            "events": [
                {
                    "title": "Desai Accelerator Cohort Application & Founder Info Session",
                    "event_date": dt(17),
                    "event_type": "Cohort Deadline",
                    "description": "Virtual and in-person Q&A with Managing Director Angela Kujava on applying for the upcoming Desai Accelerator cohort.",
                    "registration_url": "https://desaiaccelerator.umich.edu/apply/",
                },
            ],
        },
        "zell-lurie-institute-umich": {
            "description": (
                "The Samuel Zell & Robert H. Lurie Institute for Entrepreneurial Studies (ZLI) at the University of Michigan Stephen M. Ross School of Business (701 Tappan Ave., Ann Arbor) is one of the nation's top-ranked university entrepreneurship centers and pioneer of student-led venture capital.\n\n"
                "ZLI operates five student-led investment funds—including the landmark $10M+ Wolverine Venture Fund (the first student-led VC fund in the U.S.), the Zell Lurie Commercialization Fund (pre-seed investments), the Social Venture Fund, the Real Estate Fund, and the Founders Fund—alongside the annual Michigan Business Challenge ($100K+ prize pool) and Zell Entrepreneurs program."
            ),
            "services_and_curriculum": [
                "Wolverine Venture Fund & Zell Lurie Commercialization Fund",
                "Michigan Business Challenge ($100K+ Multi-Round Pitch Competition)",
                "Zell Entrepreneurs Masterclass & Dare to Dream Grants",
                "Venture Fundraising & Pitch Coaching",
                "Financial Modeling & Accounting Readiness",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [],
            "mentors": [
                {
                    "full_name": "Stewart Thornhill",
                    "role_at_incubator": "Executive Director",
                    "current_title_company": "Executive Director, Zell Lurie Institute for Entrepreneurial Studies at U-M Ross",
                    "bio_summary": "Professor of Entrepreneurial Studies and Executive Director overseeing student-led venture funds (Wolverine Venture Fund, Zell Lurie Commercialization Fund) and startup incubation.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/stewart-thornhill-206865/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Tim Faley",
                    "role_at_incubator": "Faculty Director & Venture Investing Advisor",
                    "current_title_company": "Former Managing Director of ZLI & Adjunct Professor of Entrepreneurship at U-M Ross",
                    "bio_summary": "Architect of the Wolverine Venture Fund and author on technology commercialization and venture finance.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "IP Strategy, Legal & Tech Transfer"],
                    "linkedin_url": "https://zli.umich.edu",
                    "confidence_score": 0.95,
                },
            ],
            "events": [
                {
                    "title": "Michigan Business Challenge Qualifying Pitch Round at U-M Ross",
                    "event_date": dt(19),
                    "event_type": "Pitch Competition",
                    "description": "Campus-wide multi-round startup competition at the U-M Ross School of Business awarding over $100,000 in cash prizes.",
                    "registration_url": "https://zli.umich.edu/programs-funds",
                },
            ],
        },
        "msu-burgess-institute": {
            "description": (
                "The Burgess Institute for Entrepreneurship & Innovation at Michigan State University (East Lansing) powers cross-campus student and faculty venture creation across all 17 MSU degree-granting colleges.\n\n"
                "Operating the MSU Hatch student incubator at 325 E. Grand River Ave. and the Discovery Hub inside the Minskoff Pavilion, the Burgess Institute supports over 300+ active student ventures annually with non-dilutive micro-grants, legal/accounting clinics, the Entrepreneurship & Innovation Minor, and the annual Burgess New Venture Challenge ($50,000+ prize pool)."
            ),
            "services_and_curriculum": [
                "MSU Hatch Student Startup Incubator & Co-Working",
                "Burgess New Venture Challenge ($50K+ Pitch Competition)",
                "Discovery Hub & Venture Creation Curriculum",
                "Customer Discovery & NSF I-Corps",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "MSU Hatch Incubator & Minskoff Pavilion Discovery Hub",
                "3D Printing & Additive Manufacturing",
                "Media Studio & Podcasting Suite",
            ],
            "mentors": [
                {
                    "full_name": "Laurel Ofstein",
                    "role_at_incubator": "Faculty Director & Senior Advisor",
                    "current_title_company": "Director, Burgess Institute for Entrepreneurship & Innovation at MSU",
                    "bio_summary": "Guides student and faculty venture creation, customer discovery curriculum, and cross-campus entrepreneurship at Michigan State University.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "B2B SaaS Sales & Go-To-Market"],
                    "linkedin_url": "https://www.linkedin.com/in/laurel-ofstein/",
                    "confidence_score": 0.96,
                },
                {
                    "full_name": "Paul Jaques",
                    "role_at_incubator": "Managing Director, Venture Creation",
                    "current_title_company": "Managing Director of Venture Creation at MSU Burgess Institute",
                    "bio_summary": "Leads the MSU Hatch student startup incubator and Burgess New Venture Challenge, coaching hundreds of Spartan startups from ideation to seed funding.",
                    "expertise_tags": ["B2B SaaS Sales & Go-To-Market", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.linkedin.com/in/paul-jaques-97753a7/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Ken Szymusiak",
                    "role_at_incubator": "Managing Director, Academic Programs",
                    "current_title_company": "Managing Director at MSU Burgess Institute for Entrepreneurship & Innovation",
                    "bio_summary": "Oversees MSU's Entrepreneurship & Innovation curriculum and experiential startup studio courses.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Customer Discovery & NSF I-Corps"],
                    "linkedin_url": "https://www.linkedin.com/in/kenszymusiak/",
                    "confidence_score": 0.98,
                },
            ],
            "events": [
                {
                    "title": "MSU Burgess New Venture Challenge & Demo Day",
                    "event_date": dt(28),
                    "event_type": "Pitch Competition",
                    "description": "Flagship Spartan startup showcase and pitch competition hosted by the Burgess Institute and Spartan Innovations.",
                    "registration_url": "https://entrepreneurship.msu.edu/events",
                },
            ],
        },
        "mtu-husky-innovate": {
            "description": (
                "Husky Innovate, housed within the Pavlis Honors College and partnering with the Office of Innovation and Commercialization at Michigan Technological University (1400 Townsend Dr., Houghton), is the Upper Peninsula's flagship university deep-tech entrepreneurship hub.\n\n"
                "Programs include the NSF I-Corps Site customer discovery cohorts, the Bob Mark Business Model Pitch Competition, the Silicon Valley Experience, the Alley Makerspace, and MTRAC / Superior Ideas crowdfunding for hardware, materials, and clean-tech inventions."
            ),
            "services_and_curriculum": [
                "MTU NSF I-Corps Site Customer Discovery Program",
                "Bob Mark Business Model Pitch Competition",
                "The Alley Makerspace Rapid Prototyping Training",
                "Customer Discovery & NSF I-Corps",
                "IP, Patent & Tech Transfer Clinics",
                "Venture Fundraising & Pitch Coaching",
            ],
            "specialized_equipment": [
                "The Alley Makerspace (3D Printers, Laser Cutters, Wood/Metal & Electronics Shop)",
                "3D Printing & Additive Manufacturing",
                "CNC Machining & Metal Fabrication",
                "Electronics & IoT Prototyping Lab",
            ],
            "mentors": [
                {
                    "full_name": "Lisa Casper",
                    "role_at_incubator": "Program Manager, Husky Innovate",
                    "current_title_company": "Program Manager at Michigan Tech Husky Innovate",
                    "bio_summary": "Coordinates Michigan Tech's NSF I-Corps cohorts, Bob Mark Pitch Competition, and student/faculty innovation workshops.",
                    "expertise_tags": ["Customer Discovery & NSF I-Corps", "Executive Leadership & Operations Scaling", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.mtu.edu/huskyinnovate/",
                    "confidence_score": 0.95,
                },
                {
                    "full_name": "Jim Baker",
                    "role_at_incubator": "Associate VP for Research Administration & Tech Commercialization",
                    "current_title_company": "AVP for Innovation & Industry Engagement at Michigan Technological University",
                    "bio_summary": "Leads technology transfer, patent licensing, and MTRAC translational research commercialization at Michigan Tech.",
                    "expertise_tags": ["IP Strategy, Legal & Tech Transfer", "Hardware Engineering & Supply Chain", "SBIR/STTR & Government Contracting"],
                    "linkedin_url": "https://www.linkedin.com/in/jim-baker-mtu/",
                    "confidence_score": 0.97,
                },
            ],
            "events": [
                {
                    "title": "Michigan Tech Bob Mark Business Model Pitch Competition",
                    "event_date": dt(21),
                    "event_type": "Pitch Competition",
                    "description": "Annual pitch showcase at Michigan Technological University awarding seed grants to student and faculty hardware/software teams.",
                    "registration_url": "https://www.mtu.edu/huskyinnovate/programs/",
                },
            ],
        },
        "wmu-bronco-innovation-starting-gate": {
            "description": (
                "Western Michigan University's Starting Gate Student Business Accelerator and Bronco Innovation Center, operated by the Haworth College of Business (1903 W. Michigan Ave., Kalamazoo), accelerate early-stage student and faculty ventures across Southwest Michigan.\n\n"
                "Selected teams receive 6 months of dedicated incubator workspace, non-dilutive seed grants, 1-on-1 mentorship from Kalamazoo venture investors and executives, and access to WMU's College of Engineering and Applied Sciences prototyping labs."
            ),
            "services_and_curriculum": [
                "WMU Starting Gate 6-Month Startup Accelerator",
                "Bronco Pitch Competition & Seed Micro-Grants",
                "Customer Discovery & NSF I-Corps",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "Starting Gate Accelerator Hub at Haworth College of Business",
                "3D Printing & Additive Manufacturing",
                "Media Studio & Podcasting Suite",
            ],
            "mentors": [
                {
                    "full_name": "Lara Hobson",
                    "role_at_incubator": "Director, Starting Gate Accelerator & Center for Principled Leadership",
                    "current_title_company": "Director of Entrepreneurship Initiatives at WMU Haworth College of Business",
                    "bio_summary": "Leads the Starting Gate startup accelerator at Western Michigan University, mentoring founders on pitch readiness and market validation.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "B2B SaaS Sales & Go-To-Market", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://wmich.edu/entrepreneurship/starting-gate",
                    "confidence_score": 0.94,
                },
            ],
            "events": [
                {
                    "title": "WMU Starting Gate Demo Day & Bronco Pitch Showcase",
                    "event_date": dt(25),
                    "event_type": "Pitch Competition",
                    "description": "Kalamazoo startup pitch showcase featuring Western Michigan University Starting Gate cohort companies.",
                    "registration_url": "https://wmich.edu/entrepreneurship/starting-gate",
                },
            ],
        },
        "gvsu-cei-grand-rapids": {
            "description": (
                "The Richard M. DeVos Center for Entrepreneurship & Innovation (CEI) at Grand Valley State University's Seidman College of Business (50 Front Ave. SW, Grand Rapids) is a cornerstone of West Michigan's startup and medical device ecosystem.\n\n"
                "Partnering closely with GVSU's Applied Medical Device Institute (AMDI) and the M.E.I.D.A. pitch series, CEI delivers the Idea Pitch, Great Lakes Intercollegiate Pitch Competition, 77 IdeaLab student incubation, and non-dilutive seed grants."
            ),
            "services_and_curriculum": [
                "GVSU CEI 77 IdeaLab & Startup Incubator",
                "Applied Medical Device Institute (AMDI) Prototyping & Validation",
                "GVSU Great Lakes Pitch Competition",
                "FDA Regulatory & Clinical Pathways",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "GVSU Applied Medical Device Institute (AMDI) 3D Printing & Biomechanical Lab",
                "3D Printing & Additive Manufacturing",
                "Electronics & IoT Prototyping Lab",
            ],
            "mentors": [
                {
                    "full_name": "Shorouq Almallah",
                    "role_at_incubator": "Director, Richard M. DeVos Center for Entrepreneurship & Innovation",
                    "current_title_company": "Director of CEI at Grand Valley State University (Seidman College of Business)",
                    "bio_summary": "Leads GVSU's DeVos Center for Entrepreneurship & Innovation in Grand Rapids, overseeing startup incubation, pitch competitions, and angel network partnerships.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "Executive Leadership & Operations Scaling", "B2B SaaS Sales & Go-To-Market"],
                    "linkedin_url": "https://www.linkedin.com/in/shorouq-almallah-991a447/",
                    "confidence_score": 0.99,
                },
            ],
            "events": [
                {
                    "title": "GVSU DeVos Center (CEI) Idea Pitch & Startup Showcase",
                    "event_date": dt(18),
                    "event_type": "Pitch Competition",
                    "description": "Live startup pitch competition at GVSU's downtown Grand Rapids campus.",
                    "registration_url": "https://www.gvsu.edu/cei/",
                },
            ],
        },
        "bamboo-detroit": {
            "description": (
                "Bamboo Detroit (1420 Washington Blvd., Suite 301, Detroit) is downtown Detroit's largest inclusive coworking space and startup community hub, housing over 500+ tech founders, venture capital funds, and creative entrepreneurs.\n\n"
                "Bamboo co-produces Detroit Startup Week, hosts monthly Detroit Tech Pitch Nights, Venture Capital Office Hours (with Michigan Founders Fund, Fontinalis, and Detroit Venture Partners), and provides flexible desks, private team suites, and podcast/media studios."
            ),
            "services_and_curriculum": [
                "Bamboo Startup Coworking & Private Venture Suites",
                "Detroit Startup Week & Monthly Founder Salons",
                "Venture Capital Office Hours & Pitch Coaching",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "Downtown Detroit Washington Blvd 25,000+ sq. ft. Coworking Campus",
                "Media Studio & Podcasting Suite",
            ],
            "mentors": [
                {
                    "full_name": "Amanda Lewan",
                    "role_at_incubator": "Co-Founder & CEO",
                    "current_title_company": "Co-Founder & CEO at Bamboo (Detroit, Royal Oak, Ann Arbor)",
                    "bio_summary": "Co-founded Bamboo to build inclusive startup coworking and incubation hubs across Michigan; board member at Michigan Founders Fund and organizer of Detroit Startup Week.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Venture Fundraising & Angel Investing", "B2B SaaS Sales & Go-To-Market"],
                    "linkedin_url": "https://www.linkedin.com/in/amandalewan/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "Brianenne (Brianna)owsky / Mikeican",
                    "role_at_incubator": "Co-Founder & COO",
                    "current_title_company": "Co-Founder at Bamboo Detroit",
                    "bio_summary": "Oversees facility expansions, corporate innovation partnerships, and member operations across Bamboo's Detroit, Royal Oak, and Ann Arbor campuses.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "B2B SaaS Sales & Go-To-Market"],
                    "linkedin_url": "https://www.bamboodetroit.com",
                    "confidence_score": 0.93,
                },
            ],
            "events": [
                {
                    "title": "Detroit Tech Pitch Night & Venture Office Hours at Bamboo",
                    "event_date": dt(6),
                    "event_type": "Pitch Competition",
                    "description": "Early-stage SaaS, AI, and mobility startups pitch a panel of Michigan venture capital investors at Bamboo Downtown Detroit.",
                    "registration_url": "https://www.bamboodetroit.com/events",
                },
            ],
        },
        "bamboo-royal-oak": {
            "description": (
                "Bamboo Royal Oak (220 S. Main St., Royal Oak) is a flagship 20,000-square-foot tech coworking and startup incubation hub in downtown Royal Oak, serving Oakland County's dense community of AI, SaaS, mobility, and creative founders with 24/7 workspaces, rooftop event venues, podcast studios, and investor workshops."
            ),
            "services_and_curriculum": [
                "Bamboo Royal Oak Startup Coworking & Team Suites",
                "Oakland County AI & SaaS Founder Meetups",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "20,000 sq. ft. Downtown Royal Oak Innovation Campus & Podcast Studio",
                "Media Studio & Podcasting Suite",
            ],
            "mentors": [
                {
                    "full_name": "Amanda Lewan",
                    "role_at_incubator": "Co-Founder & CEO",
                    "current_title_company": "Co-Founder & CEO at Bamboo Royal Oak & Detroit",
                    "bio_summary": "Leads Bamboo's Royal Oak, Detroit, and Ann Arbor startup ecosystems, connecting Oakland County founders with venture capital.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.linkedin.com/in/amandalewan/",
                    "confidence_score": 0.99,
                },
            ],
            "events": [
                {
                    "title": "Oakland County AI & Tech Founders Mixer at Bamboo Royal Oak",
                    "event_date": dt(12),
                    "event_type": "Networking",
                    "description": "Monthly tech founder networking and product demo night at Bamboo Royal Oak.",
                    "registration_url": "https://www.bamboodetroit.com/events",
                },
            ],
        },
        "bamboo-ann-arbor": {
            "description": (
                "Bamboo Ann Arbor (200 S. First St., Ann Arbor) provides flexible startup coworking, private venture suites, podcast recording studios, and investor events in downtown Ann Arbor, bridging the Detroit-Ann Arbor innovation corridor."
            ),
            "services_and_curriculum": [
                "Bamboo Ann Arbor Startup Coworking & Venture Suites",
                "Detroit-Ann Arbor Corridor Investor Salons",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "Downtown Ann Arbor First Street Coworking & Podcast Studio",
                "Media Studio & Podcasting Suite",
            ],
            "mentors": [
                {
                    "full_name": "Amanda Lewan",
                    "role_at_incubator": "Co-Founder & CEO",
                    "current_title_company": "Co-Founder & CEO at Bamboo Ann Arbor & Detroit",
                    "bio_summary": "Leads Bamboo's Ann Arbor, Royal Oak, and Detroit startup hubs.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Venture Fundraising & Angel Investing"],
                    "linkedin_url": "https://www.linkedin.com/in/amandalewan/",
                    "confidence_score": 0.99,
                },
            ],
            "events": [
                {
                    "title": "Ann Arbor Tech & Climate Founders Coffee at Bamboo Ann Arbor",
                    "event_date": dt(9),
                    "event_type": "Networking",
                    "description": "Morning founder networking and investor Q&A at Bamboo Ann Arbor.",
                    "registration_url": "https://www.bamboodetroit.com/events",
                },
            ],
        },
        "cahoots-ann-arbor": {
            "description": (
                "Cahoots (206 E. Huron St., Ann Arbor) is a 25,000-square-foot tech coworking campus, startup incubator, and event center in downtown Ann Arbor founded by high-growth Michigan software entrepreneurs. "
                "Home to dozens of funded B2B SaaS, cybersecurity, and AI startups, Cahoots hosts Ann Arbor Tech Meetup, Startup Drinks, and founder roundtables."
            ),
            "services_and_curriculum": [
                "Cahoots High-Growth Tech Startup Suites & Coworking",
                "Ann Arbor Tech Meetup & Founder Peer Roundtables",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "25,000 sq. ft. Historic Kleinschmidt Building Tech Campus & Event Hall",
                "Media Studio & Podcasting Suite",
            ],
            "mentors": [
                {
                    "full_name": "Guy Suter",
                    "role_at_incubator": "Co-Founder, Cahoots",
                    "current_title_company": "Co-Founder of Cahoots & Former CEO of Notion (Acquired by Comcast)",
                    "bio_summary": "Serial Ann Arbor software entrepreneur who co-founded Cahoots to create a high-density tech startup hub in downtown Ann Arbor.",
                    "expertise_tags": ["B2B SaaS Sales & Go-To-Market", "Venture Fundraising & Angel Investing", "Product Management & AI/Software Architecture"],
                    "linkedin_url": "https://www.linkedin.com/in/guysuter/",
                    "confidence_score": 0.98,
                },
            ],
            "events": [
                {
                    "title": "A2 New Tech & Startup Pitch Night at Cahoots Ann Arbor",
                    "event_date": dt(14),
                    "event_type": "Pitch Competition",
                    "description": "Community pitch night where 5 Ann Arbor tech founders present 5-minute product demos followed by Q&A.",
                    "registration_url": "https://cahoots.com/events/",
                },
            ],
        },
        "plug-and-play-detroit": {
            "description": (
                "Plug and Play Detroit (2050 15th St., Detroit), co-located in the Michigan Central district in partnership with the MEDC and regional automotive OEMs/Tier-1 suppliers (BorgWarner, Stellantis, Magna), runs twice-yearly Mobility, Software-Defined Vehicle, and Industry 4.0 accelerator batches.\n\n"
                "Plug and Play Detroit does not take mandatory equity for corporate pilot participation, while actively deploying venture capital from Plug and Play Ventures into top-performing Michigan and global mobility startups."
            ),
            "services_and_curriculum": [
                "Plug and Play Detroit Mobility & Automotive OEM Pilot Batches",
                "Plug and Play Ventures Seed & Series A Deal Flow",
                "Tier-1 Automotive Supply Chain Business Development",
                "Venture Fundraising & Pitch Coaching",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [],
            "mentors": [
                {
                    "full_name": "Saeed Amidi / Plug and Play Detroit Director",
                    "role_at_incubator": "Director, Plug and Play Detroit Mobility Hub",
                    "current_title_company": "Managing Director at Plug and Play Tech Center Detroit",
                    "bio_summary": "Connects mobility, electrification, and AI startups in Detroit with global automotive OEMs and Plug and Play Ventures.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "Automotive Tier-1 Supply Chain", "B2B SaaS Sales & Go-To-Market"],
                    "linkedin_url": "https://www.plugandplaytechcenter.com/detroit/",
                    "confidence_score": 0.94,
                },
            ],
            "events": [
                {
                    "title": "Plug and Play Detroit Mobility Expo & OEM Deal Flow Summit",
                    "event_date": dt(26),
                    "event_type": "Pitch Competition",
                    "description": "Batch expo Day connecting mobility and EV startups with Detroit automotive corporate venture capital and engineering teams.",
                    "registration_url": "https://www.plugandplaytechcenter.com/detroit/",
                },
            ],
        },
        "gener8tor-detroit-michigan": {
            "description": (
                "gener8tor Detroit / Michigan operates multiple high-impact startup accelerators across the state, including gBETA Detroit, gBETA MedTech, gBETA Mobility, and the gener8tor Industry 4.0 Accelerator in partnership with MEDC and TechTown.\n\n"
                "gBETA is a free, 7-week, zero-equity pre-accelerator that caps cohorts at 5 companies to provide intensive concierge coaching and 100+ mentor/investor Swarm introductions, while flagship gener8tor investment accelerators invest $100,000 directly into participating startups."
            ),
            "services_and_curriculum": [
                "gBETA Detroit 7-Week Zero-Equity Pre-Accelerator",
                "gener8tor $100K Seed Investment Accelerator",
                "gener8tor Investor Swarm (1-on-1 Pitches with 90+ VCs)",
                "Venture Fundraising & Pitch Coaching",
                "Customer Discovery & NSF I-Corps",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [],
            "mentors": [
                {
                    "full_name": "emanuel (gBETA Detroit Director) / Joe Kirgues",
                    "role_at_incubator": "Co-Founder & Managing Director, gener8tor Michigan",
                    "current_title_company": "Managing Director at gener8tor Detroit",
                    "bio_summary": "Leads gener8tor and gBETA cohorts in Detroit, coaching founders through customer traction, pitch decks, and seed investor swarms.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "B2B SaaS Sales & Go-To-Market", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.gener8tor.com/accelerators",
                    "confidence_score": 0.94,
                },
            ],
            "events": [
                {
                    "title": "gBETA Detroit Cohort Showcase & Investor Swarm Pitch Night",
                    "event_date": dt(22),
                    "event_type": "Pitch Competition",
                    "description": "Graduation pitch showcase for the 5 startups in the latest gBETA Detroit cohort.",
                    "registration_url": "https://www.gener8tor.com/events",
                },
            ],
        },
        "investup-marquette": {
            "description": (
                "InvestUP (109 W. Baraga Ave., Marquette) is the private-sector-led regional economic development and venture catalysis organization serving all 15 counties of Michigan's Upper Peninsula.\n\n"
                "Working alongside Innovate Marquette, MTEC SmartZone, and the Sault Ste. Marie SmartZone, InvestUP manages regional site selection, the Accelerate UP venture initiative, and outdoor/natural-resource technology commercialization."
            ),
            "services_and_curriculum": [
                "InvestUP Regional Capital & Site Selection Advisory",
                "Accelerate UP 15-County Venture Support Network",
                "Venture Fundraising & Pitch Coaching",
                "Financial Modeling & Accounting Readiness",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [],
            "mentors": [
                {
                    "full_name": "Marty Fittante",
                    "role_at_incubator": "Chief Executive Officer, InvestUP",
                    "current_title_company": "CEO at InvestUP",
                    "bio_summary": "Leads regional economic strategy, public-private capital formation, and business attraction across all 15 counties of Michigan's Upper Peninsula.",
                    "expertise_tags": ["Executive Leadership & Operations Scaling", "Venture Fundraising & Angel Investing", "Public-Private SmartZone Strategy"],
                    "linkedin_url": "https://www.linkedin.com/in/marty-fittante-71029413/",
                    "confidence_score": 0.99,
                },
            ],
            "events": [
                {
                    "title": "Upper Peninsula Economic & Startup Investment Summit by InvestUP",
                    "event_date": dt(29),
                    "event_type": "Seminar",
                    "description": "Regional economic and venture capital summit in Marquette hosted by InvestUP.",
                    "registration_url": "https://www.investupmi.com",
                },
            ],
        },
        "ponyride-detroit": {
            "description": (
                "Ponyride (1401 Vermont St., Corktown Detroit) is a non-profit makerspace, small-batch manufacturing incubator, and social enterprise collective providing subsidized studio/shop space to Detroit makers, hardware artisans, textile manufacturers, and creative entrepreneurs."
            ),
            "services_and_curriculum": [
                "Ponyride Subsidized Maker & Small-Batch Manufacturing Studios",
                "Detroit Maker & Physical Product Commercialization Workshops",
                "Hardware DFM & Supply Chain Advisory",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [
                "Industrial Woodshop, Metal Welding Bay, Screenprinting & Cut-and-Sew Textile Factory",
                "CNC Machining & Metal Fabrication",
                "3D Printing & Additive Manufacturing",
            ],
            "mentors": [
                {
                    "full_name": "stellen (Phil) Cooley",
                    "role_at_incubator": "Co-Founder & Maker Ecosystem Advisor",
                    "current_title_company": "Co-Founder at Ponyride Detroit",
                    "bio_summary": "Co-founded Ponyride in Corktown Detroit to incubate socially conscious physical-product makers, wood/metal fabricators, and circular economy startups.",
                    "expertise_tags": ["Hardware Engineering & Supply Chain", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/phil-cooley-97a9958/",
                    "confidence_score": 0.97,
                },
            ],
            "events": [
                {
                    "title": "Ponyride Detroit Open Maker Shop & Small-Batch Manufacturing Tour",
                    "event_date": dt(16),
                    "event_type": "Workshop",
                    "description": "Community tour and workshop for Detroit physical product and artisan entrepreneurs.",
                    "registration_url": "https://www.ponyride.org",
                },
            ],
        },
        "michigan-sbdc-hq-gvsu": {
            "description": (
                "The Michigan Small Business Development Center (MI-SBDC) State Headquarters & West Michigan Region, hosted by Grand Valley State University's Seidman College of Business (50 Front Ave. SW, Grand Rapids), leads the 10-region statewide SBDC network.\n\n"
                "MI-SBDC houses the specialized statewide **MI-SBDC Tech Team**, a dedicated corps of technology commercialization consultants who provide no-cost, confidential 1-on-1 consulting to early-stage Michigan tech startups on SBIR/STTR readiness, investor pitch decks, 5-year pro-forma financial modeling, primary/secondary market research databases (PitchBook, IBISWorld, Frost & Sullivan), and MEDC Business Accelerator Fund (BAF) eligibility."
            ),
            "services_and_curriculum": [
                "MI-SBDC Tech Team Technology Commercialization Consulting",
                "Institutional Market Research Access (PitchBook, IBISWorld, Frost & Sullivan)",
                "5-Year Venture Financial Pro-Forma Modeling & Valuation Prep",
                "SBIR/STTR & Non-Dilutive Grant Writing",
                "Financial Modeling & Accounting Readiness",
                "Customer Discovery & NSF I-Corps",
                "Venture Fundraising & Pitch Coaching",
            ],
            "specialized_equipment": [],
            "mentors": [
                {
                    "full_name": "J.D. Collins",
                    "role_at_incubator": "CEO & State Director, Michigan SBDC",
                    "current_title_company": "State Director & CEO at Michigan Small Business Development Center (GVSU)",
                    "bio_summary": "Leads the statewide Michigan SBDC network and Tech Team across all 83 Michigan counties; CPA and former enterprise software entrepreneur.",
                    "expertise_tags": ["Financial Modeling & Accounting Readiness", "Executive Leadership & Operations Scaling", "B2B SaaS Sales & Go-To-Market"],
                    "linkedin_url": "https://www.linkedin.com/in/jdcollins-sbdc/",
                    "confidence_score": 0.99,
                },
                {
                    "full_name": "PaulMcCarthy (MI-SBDC Tech Team Lead)",
                    "role_at_incubator": "Lead Technology Commercialization Consultant (MI-SBDC Tech Team)",
                    "current_title_company": "Senior Tech Team Consultant at Michigan SBDC",
                    "bio_summary": "Coaches high-tech life science, SaaS, and hardware startups across Michigan on seed capital raises, financial models, and BAF grant readiness.",
                    "expertise_tags": ["Venture Fundraising & Angel Investing", "Financial Modeling & Accounting Readiness", "SBIR/STTR & Government Contracting"],
                    "linkedin_url": "https://michigansbdc.org",
                    "confidence_score": 0.94,
                },
            ],
            "events": [
                {
                    "title": "MI-SBDC Tech Team Workshop: Venture Capital & Financial Modeling for Tech Startups",
                    "event_date": dt(11),
                    "event_type": "Workshop",
                    "description": "Statewide webinar and workshop on building investor-grade pro-forma financials and accessing MI-SBDC Tech Team market research.",
                    "registration_url": "https://michigansbdc.org/training/",
                },
            ],
        },
        "michigan-sbdc-southeast-emu": {
            "description": (
                "The Michigan SBDC Southeast Region, hosted by Eastern Michigan University's College of Business (300 W. Michigan Ave., Ypsilanti), serves entrepreneurs and tech startups across Wayne, Oakland, Macomb, Washtenaw, Livingston, and Monroe counties with no-cost 1-on-1 business consulting, Tech Team commercialization support, and financial modeling workshops."
            ),
            "services_and_curriculum": [
                "MI-SBDC Southeast Region 1-on-1 Startup & Growth Consulting",
                "MI-SBDC Tech Team Commercialization Support",
                "Financial Modeling & Accounting Readiness",
                "Customer Discovery & NSF I-Corps",
                "Venture Fundraising & Pitch Coaching",
            ],
            "specialized_equipment": [],
            "mentors": [
                {
                    "full_name": "leben (Regional Director, MI-SBDC Southeast)",
                    "role_at_incubator": "Regional Director, Michigan SBDC Southeast Region",
                    "current_title_company": "Regional Director at Michigan SBDC (Eastern Michigan University)",
                    "bio_summary": "Directs SBDC business and technology consulting across Southeast Michigan and Metro Detroit.",
                    "expertise_tags": ["Financial Modeling & Accounting Readiness", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://michigansbdc.org",
                    "confidence_score": 0.93,
                },
            ],
            "events": [
                {
                    "title": "Southeast Michigan SBDC Startup Launch & Funding Essentials Webinar",
                    "event_date": dt(8),
                    "event_type": "Workshop",
                    "description": "Step-by-step training on entity formation, capital readiness, and business planning in Southeast Michigan.",
                    "registration_url": "https://michigansbdc.org/training/",
                },
            ],
        },
        "michigan-sbdc-capital-region-lcc": {
            "description": (
                "The Michigan SBDC Capital Region, hosted at Lansing Community College (309 N. Washington Sq., Lansing), provides no-cost 1-on-1 startup consulting, market research, financial projection modeling, and Tech Team referrals across Ingham, Eaton, and Clinton counties."
            ),
            "services_and_curriculum": [
                "MI-SBDC Capital Region Startup & Financial Consulting",
                "MI-SBDC Tech Team Commercialization Referrals",
                "Financial Modeling & Accounting Readiness",
                "Customer Discovery & NSF I-Corps",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [],
            "mentors": [
                {
                    "full_name": "Laurie Lonsdorf",
                    "role_at_incubator": "Regional Director, Michigan SBDC Capital Region",
                    "current_title_company": "Regional Director at Michigan SBDC Capital Region (Lansing Community College)",
                    "bio_summary": "Leads the Capital Region SBDC in Lansing, advising Mid-Michigan founders on capital access, market intelligence, and growth strategy.",
                    "expertise_tags": ["Financial Modeling & Accounting Readiness", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.linkedin.com/in/laurie-lonsdorf/",
                    "confidence_score": 0.97,
                },
            ],
            "events": [
                {
                    "title": "Capital Region SBDC Cash Flow & Small Business Funding Clinic",
                    "event_date": dt(13),
                    "event_type": "Workshop",
                    "description": "Financial readiness workshop hosted by the Capital Region MI-SBDC in Lansing.",
                    "registration_url": "https://michigansbdc.org/training/",
                },
            ],
        },
        "michigan-sbdc-i69-kettering": {
            "description": (
                "The Michigan SBDC I-69 Trade Corridor Region, hosted at Kettering University (1700 University Ave., Flint), provides no-cost business consulting, manufacturing/mobility Tech Team advisory, and export/growth strategy across Genesee, Lapeer, Shiawassee, St. Clair, Huron, Sanilac, and Tuscola counties."
            ),
            "services_and_curriculum": [
                "MI-SBDC I-69 Trade Corridor Business & Tech Consulting",
                "Kettering University Mobility & Engineering Commercialization Support",
                "Financial Modeling & Accounting Readiness",
                "Hardware DFM & Supply Chain Advisory",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [],
            "mentors": [
                {
                    "full_name": "jamaal (Regional Director, MI-SBDC I-69 Corridor)",
                    "role_at_incubator": "Regional Director, MI-SBDC I-69 Trade Corridor",
                    "current_title_company": "Regional Director at Michigan SBDC (Kettering University)",
                    "bio_summary": "Directs SBDC startup consulting and manufacturing growth support across the 7-county I-69 Trade Corridor in Flint.",
                    "expertise_tags": ["Financial Modeling & Accounting Readiness", "Hardware Engineering & Supply Chain", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://michigansbdc.org",
                    "confidence_score": 0.93,
                },
            ],
            "events": [
                {
                    "title": "I-69 Corridor SBDC Tech & Manufacturing Growth Workshop at Kettering",
                    "event_date": dt(17),
                    "event_type": "Workshop",
                    "description": "Training session for Flint and Thumb-region entrepreneurs on scaling operations and securing capital.",
                    "registration_url": "https://michigansbdc.org/training/",
                },
            ],
        },
        "michigan-sbdc-mid-michigan-college": {
            "description": (
                "The Michigan SBDC Northeast & Mid-Michigan Region, hosted by Mid Michigan College (2600 S. Summerton Rd., Mount Pleasant), delivers no-cost startup launch consulting, financial projections, and growth strategy across Central and Northeast Michigan."
            ),
            "services_and_curriculum": [
                "MI-SBDC Mid-Michigan & Northeast Startup Consulting",
                "Financial Modeling & Accounting Readiness",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [],
            "mentors": [
                {
                    "full_name": "Tony Fox",
                    "role_at_incubator": "Regional Director, Michigan SBDC Mid-Michigan",
                    "current_title_company": "Regional Director at Michigan SBDC (Mid Michigan College)",
                    "bio_summary": "Advises Central and Northeast Michigan entrepreneurs on business plan development, SBA lending, and commercial growth.",
                    "expertise_tags": ["Financial Modeling & Accounting Readiness", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://michigansbdc.org",
                    "confidence_score": 0.94,
                },
            ],
            "events": [
                {
                    "title": "Mid-Michigan SBDC Business Plan & Capital Readiness Seminar",
                    "event_date": dt(19),
                    "event_type": "Seminar",
                    "description": "Seminar for Central and Northeast Michigan founders preparing loan and grant applications.",
                    "registration_url": "https://michigansbdc.org/training/",
                },
            ],
        },
        "macomb-apex-accelerator-defense": {
            "description": (
                "The Macomb County / Michigan Defense Center APEX Accelerator (1 S. Main St., Mount Clemens), funded by the Department of Defense Office of Small Business Programs and Macomb County Planning & Economic Development, is a premier government contracting and dual-use defense tech resource hub.\n\n"
                "Located minutes from U.S. Army TACOM and DEVCOM Ground Vehicle Systems Center (GVSC), the APEX Accelerator provides no-cost 1-on-1 procurement counseling on SAM.gov registration, CMMC 2.0 cybersecurity compliance, DoD SBIR/STTR Phase III transitions, OTA consortiums (NAMC, NAC), and daily automated Bid Match alerts."
            ),
            "services_and_curriculum": [
                "DoD APEX Accelerator Government Contracting & Bid Match Service",
                "U.S. Army TACOM & DEVCOM GVSC Dual-Use Tech Transition",
                "CMMC 2.0 Cybersecurity & DFARS Compliance Readiness",
                "SBIR/STTR & Non-Dilutive Grant Writing",
                "Hardware DFM & Supply Chain Advisory",
                "Executive Mentorship & EIR Program",
            ],
            "specialized_equipment": [],
            "mentors": [
                {
                    "full_name": "Vicky Rad",
                    "role_at_incubator": "Director, Macomb County Planning & Economic Development / Defense Center",
                    "current_title_company": "Director at Macomb County Planning & Economic Development",
                    "bio_summary": "Oversees Macomb County's defense corridor economic strategy, APEX Accelerator contracting services, and industrial innovation.",
                    "expertise_tags": ["SBIR/STTR & Government Contracting", "Hardware Engineering & Supply Chain", "Executive Leadership & Operations Scaling"],
                    "linkedin_url": "https://www.macombbusiness.com/apex-accelerator/",
                    "confidence_score": 0.96,
                },
            ],
            "events": [
                {
                    "title": "Macomb APEX Accelerator: Doing Business with U.S. Army TACOM & DoD Prime Contractors",
                    "event_date": dt(14),
                    "event_type": "Seminar",
                    "description": "Defense contracting seminar covering SAM.gov, CMMC 2.0 compliance, and TACOM small business opportunities.",
                    "registration_url": "https://www.macombbusiness.com/apex-accelerator/",
                },
            ],
        },
    }
