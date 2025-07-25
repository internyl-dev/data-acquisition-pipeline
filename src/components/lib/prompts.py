prompts = {
    "overview": """
You are given a partially filled JSON schema shown after ADD NEWLY FOUND INFORMATION ONTO THIS SCHEMA. Your task is to update only the 'overview' section using information from the text after WEBPAGE CONTENTS START HERE.

If the webpage content does NOT relate to or mention the program described in TARGET INTERNSHIP INFORMATION, return only: {"unrelated_website": true}

Core rules:
- Do NOT infer or guess.
- Only update fields you can confirm directly from the content.
- Leave all other fields exactly as they are: "not provided" or [].

Fill:
- "title": Full program name if explicitly given.
- "provider": Organization offering the program.
- "description": A summary or mission statement if present.
- "link": Direct program or application URL if shown.
- "subject": List of academic topics explicitly stated.
- "tags": Keywords like "free", "residential", or "virtual" if explicitly mentioned.

Never derive subject or tags from context — extract only literal keywords.
""",



    "eligibility": """
You are updating the 'eligibility' section of the JSON schema shown after ADD NEWLY FOUND INFORMATION ONTO THIS SCHEMA, using only data from WEBPAGE CONTENTS START HERE.

If the webpage content does NOT relate to or mention the program described in TARGET INTERNSHIP INFORMATION, return only: {"unrelated_website": true}

Core rules:
- Use only explicitly stated information.
- Never infer grade level from age or the reverse.
- Leave all untouched fields as "not provided" or [].

Fill:
- "essay_required", "recommendation_required", "transcript_required": Use true, false, or "not provided".
- "other": List any extra requirements mentioned like "An interview is required" or "A portfolio is required".
- "grades": Convert phrases like "rising 11th and 12th graders" to "Rising Junior" and "Rising Senior". Don't include "Rising" if not specified.
- "age": Fill "minimum" or "maximum" only if exact numbers are provided.

Be literal and precise — convert 9th, 10th, 11th, and 12th grade to freshman, sophomore, junior, and senior respectively.
""",



    "dates": """
You are updating the 'dates' section of the JSON schema shown after ADD NEWLY FOUND INFORMATION ONTO THIS SCHEMA using content from WEBPAGE CONTENTS START HERE.

If the webpage content does NOT relate to or mention the program described in TARGET INTERNSHIP INFORMATION, return only: {"unrelated_website": true}

Core rules:
- Never infer or estimate.
- Always use mm-dd-yyyy for dates.
- Leave unchanged fields as "not provided".

Update deadlines:
- Add each deadline as a separate object.
- Fields: "name", "priority" ("high" only for the most important application deadline, rank other priorities yourself based on context), "term", "date", "rolling_basis", "time".

Update program dates:
- Include term (Summer, Winter, Spring, Fall), start, and end dates only if both are clearly stated.
- Use mm-dd-yyyy format.

Update duration_weeks:
- Use a number only if the duration is clearly stated (e.g., "6-week program").
- Otherwise, use "not provided".

Do not infer dates or duration from vague phrases or context.
""",



    "locations": """
Update the 'locations' section of the schema shown after ADD NEWLY FOUND INFORMATION ONTO THIS SCHEMA using data from WEBPAGE CONTENTS START HERE.

If the webpage content does NOT relate to or mention the program described in TARGET INTERNSHIP INFORMATION, return only: {"unrelated_website": true}

Core rules:
- Use only explicitly mentioned info.
- Do not infer location from organization or known campuses.
- Leave untouched fields as "not provided".

Fill:
- "virtual": true if clearly online, false if clearly in-person, "hybrid" if both, "both available" if both are available, "not provided" if unclear.
- "state", "city", "address": Use only if directly stated.

Include only the main residential/instructional site — ignore travel destinations or event locations.
""",



    "costs": """
You are updating the 'costs' section of the schema shown after ADD NEWLY FOUND INFORMATION ONTO THIS SCHEMA using content from WEBPAGE CONTENTS START HERE.

If the webpage content does NOT relate to or mention the program described in TARGET INTERNSHIP INFORMATION, return only: {"unrelated_website": true}

Core rules:
- Use only direct mentions — do not assume or calculate.
- Leave all other values as "not provided" or null.

Cost objects (tuition, fees, etc.):
- "free": Set to true only if explicitly stated. If true, set "lowest" and "highest" to null.
- "lowest"/"highest": Use numbers only if directly stated; if not stated and not free, leave as "not provided".
- "financial-aid-available": Use true, false, or "not provided".

Stipend:
- "available": true only if explicitly mentioned, false if clearly absent.
- "amount": Use number if stated. If "available" is false, set to null.

Include each cost type as a separate object if multiple are mentioned.
""",



    "contact": """
Update the 'contact' section of the schema shown after ADD NEWLY FOUND INFORMATION ONTO THIS SCHEMA using data found in WEBPAGE CONTENTS START HERE.

If the webpage content does NOT relate to or mention the program described in TARGET INTERNSHIP INFORMATION, return only: {"unrelated_website": true}

Core rules:
- Only include contact info shown directly in the webpage content.
- Do not infer or assume from context or page layout.
- Leave fields as "not provided" if missing.
- Only include the most important contact to an applicant.

Fill:
- "email": Must be a complete and valid address (e.g., contact@school.edu).
- "phone": Must be clearly formatted and complete (123-456-7890).

Do not copy from social links or headers unless the contact is fully visible in the content. 
""",



    "all": """
You are given a partially filled JSON schema after the line: ADD NEWLY FOUND INFORMATION ONTO THIS SCHEMA. 
Extract structured data from the HTML/plaintext that follows WEBPAGE CONTENTS START HERE and update the JSON schema accordingly.

If the webpage content does NOT relate to or mention the program described in TARGET INTERNSHIP INFORMATION, return only:
{"unrelated_website": true}

—————
GLOBAL RULES:
- Do NOT add or remove any keys from the schema.
- Do NOT infer, guess, or hallucinate information.
- Use "not provided" for missing text fields or categories.
- Use mm-dd-yyyy for all dates.
- Only update values that are explicitly supported by the provided text.
- Do not change or overwrite any field that already contains data unless new text confirms a change or addition.
- Do not include any rationale or explanation in the output—just structured values.

—————
SECTION INSTRUCTIONS:

1. OVERVIEW:
- "title": Use the full program name only if explicitly stated.
- "provider": The organization running the program.
- "description": A concise summary, directly quoted or reworded from mission/program overview.
- "link": A direct URL to the program or application if provided.
- "subject": List only explicitly stated academic topics (e.g., biology, computer science).
- "tags": Use literal keywords only (e.g., "free", "residential", "virtual").

Never derive subject areas or tags from theme or domain unless exact keywords appear in the text.

2. ELIGIBILITY:
- "essay_required", "recommendation_required", "transcript_required": Use true, false, or "not provided".
- "other": List any extra requirements verbatim (e.g., "An interview is required").
- "grades": Convert stated grades (e.g., 11th) into ["Junior"], and use "Rising" only if explicitly stated (e.g., "Rising Seniors").
- "age": Fill "minimum" and "maximum" with numeric values only if exact ages or age ranges are given.

Never infer age from grade or vice versa.

3. DATES:
- "deadlines": For each deadline found, fill all subfields:
  - "name" (e.g., "Priority Deadline", "Final Application Deadline")
  - "priority" ("high" only for the most important application deadline, "medium"/"low" for others)
  - "term", "date", "rolling_basis", and "time" — use "not provided" if not stated.
- "dates": Include program term, start, and end dates only if both dates are provided. Leave subfields as "not provided" if only partial data is available.
- "duration_weeks": Use a number only if clearly stated (e.g., "6-week program" → 6); otherwise "not provided".

Never derive duration from vague phrases like “a few weeks”.

4. LOCATIONS:
- "virtual": Use:
  - true — if the program is explicitly online only
  - false — if explicitly in-person
  - "hybrid" — if the program combines online and in-person in one experience
  - "both available" — if users can choose between online or in-person
  - "not provided" — if unclear
- "state", "city", "address": Only fill if explicitly stated in the text.

Do not infer the location based on provider, university, or assumptions.

5. COSTS:
Each cost-related item gets its own object:
- "name": Label of the cost (e.g., Tuition, Housing).
- "free": true only if clearly stated. If true, both "lowest" and "highest" must be null.
- "lowest" / "highest": Use only numeric values if explicitly stated (e.g., $2500). Else use "not provided".
- "financial-aid-available": true, false, or "not provided".

Stipend:
- "available": true if explicitly mentioned; false if explicitly absent; "not provided" if unclear.
- "amount": Use numeric value only if stated. If "available" is false, set amount to null.

Never calculate cost or stipend from scattered clues.

6. CONTACT:
Include only the most relevant applicant-facing contact info:
- "email": Must be a complete email address found directly in the content.
- "phone": Must be a valid phone number with format (e.g., 123-456-7890).
- If not explicitly present, use "not provided".

Never extract contact info from headers, footers, or social links unless it appears clearly in main content.

—————
FINAL NOTE:
Return only the updated JSON. Never explain your reasoning. Preserve the schema structure. Only change fields if the corresponding information appears in the provided text.

THIS IS AN EXAMPLE INPUT AND OUTPUT
INPUT:
ADD NEWLY FOUND INFORMATION ONTO THIS SCHEMA: {'overview': {'title': 'not provided', 'provider': 'not provided', 'description': 'not provided', 'link': 'not provided', 'subject': [], 'tags': []}}\n\nTARGET INTERNSHIP INFORMATION: not provided\nnot provided\nnot provided\n\nWEBPAGE CONTENTS START HERE: \n\nSearch\nSuggested Searches\nClimate Change\nArtemis\nExpedition 64\nMars perseverance\nSpaceX Crew-2\nInternational Space Station\nView All Topics A-Z\nHomeMissionsHumans in SpaceEarthThe Solar SystemThe UniverseScienceAeronauticsTechnologyLearning ResourcesAbout NASAEspañol\nNews & Events\nMultimedia\nNASA+\nFeatured3 min readNASA’s Hubble and Webb Telescopes Reveal Two Faces of a Star Cluster Duoarticle4 days ago4 min readNASA Mission Monitoring Air Quality from Space Extended article1 week ago2 min readHubble Observations Give “Missing” Globular Cluster Time to Shinearticle1 week ago\nMissionsSearch All NASA MissionsA to Z List of MissionsUpcoming Launches and LandingsSpaceships and RocketsCommunicating with MissionsArtemisJames Webb Space TelescopeHubble Space TelescopeInternational Space StationOSIRIS-RexHumans in SpaceWhy Go to SpaceAstronautsCommercial SpaceDestinationsSpaceships and RocketsLiving in SpaceEarthExplore Earth ScienceClimate ChangeEarth, Our PlanetEarth Science in ActionEarth MultimediaEarth DataEarth Science ResearchersThe Solar SystemThe SunMercuryVenusEarthThe MoonMarsJupiterSaturnUranusNeptunePluto & Dwarf PlanetsAsteroids, Comets & MeteorsThe Kuiper BeltThe Oort CloudSkywatchingThe UniverseExoplanetsThe Search for Life in the UniverseStarsGalaxiesBlack HolesThe Big BangDark EnergyDark MatterScienceEarth SciencePlanetary ScienceAstrophysics & Space ScienceThe Sun & HeliophysicsBiological & Physical SciencesLunar ScienceCitizen ScienceAstromaterialsAeronautics ResearchHuman Space Travel ResearchAeronauticsScience in the AirNASA AircraftFlight InnovationSupersonic FlightAir Traffic SolutionsGreen Aviation TechDrones & YouTechnologyTechnology Transfer & SpinoffsSpace Travel TechnologyTechnology Living in SpaceManufacturing and MaterialsRoboticsScience InstrumentsComputingLearning ResourcesFor Kids and StudentsFor EducatorsFor Colleges and UniversitiesFor ProfessionalsScience for EveryoneRequests for Exhibits, Artifacts, or SpeakersSTEM Engagement at NASAAbout NASANASA's ImpactsCenters and FacilitiesDirectoratesOrganizationsPeople of NASACareersInternshipsOur HistoryDoing Business with NASAGet InvolvedContactNASA en EspañolCienciaAeronáuticaCiencias TerrestresSistema SolarUniversoNews & EventsNews ReleasesRecently PublishedVideo Series on NASA+Podcasts & AudioBlogsNewslettersSocial MediaMedia ResourcesEventsUpcoming Launches & LandingsVirtual Guest ProgramMultimediaNASA+ImagesNASA LiveNASA AppsPodcastsImage of the Daye-BooksInteractivesSTEM MultimediaNASA Brand & Usage Guidelines\nFeatured\n3 min read\nNASA’s Hubble and Webb Telescopes Reveal Two Faces of a Star Cluster Duo\narticle\n4 days ago\n4 min read\nNASA Mission Monitoring Air Quality from Space Extended\narticle\n1 week ago\n5 min read\nHow NASA’s SPHEREx Mission Will Share Its All-Sky Map With the World\narticle\n1 week ago\nHighlights\n4 min read\nNASA’s SpaceX Crew-11 to Support Health Studies for Deep Space Travel\narticle\n6 hours ago\n2 min read\nNASA Announces Winners of 2025 Human Lander Challenge\narticle\n2 weeks ago\n4 min read\nNASA, Australia Team Up for Artemis II Lunar Laser Communications Test\narticle\n2 weeks ago\nHighlights\n6 min read\nMeet Mineral Mappers Flying NASA Tech Out West\narticle\n1 day ago\n3 min read\nNASA Aircraft, Sensor Technology, Aid in Texas Flood Recovery Efforts\narticle\n2 days ago\n2 min read\nPolar Tourists Give Positive Reviews to NASA Citizen Science in Antarctica\narticle\n2 days ago\nHighlights\n6 min read\nAdvances in NASA Imaging Changed How World Sees Mars\narticle\n29 minutes ago\n7 min read\nNASA’s Parker Solar Probe Snaps Closest-Ever Images to Sun\narticle\n1 day ago\n4 min read\nComet 3I/ATLAS\narticle\n1 week ago\nFeatured\n2 min read\nHubble Snaps Galaxy Cluster’s Portrait\narticle\n9 hours ago\n3 min read\nNASA’s Roman Space Telescope Team Installs Observatory’s Solar Panels\narticle\n1 day ago\n8 min read\nNASA’s Webb Scratches Beyond Surface of Cat’s Paw for 3rd Anniversary\narticle\n1 day ago\nHighlights\n2 min read\nHubble Snaps Galaxy Cluster’s Portrait\narticle\n9 hours ago\n7 min read\nNASA’s Parker Solar Probe Snaps Closest-Ever Images to Sun\narticle\n1 day ago\n6 min read\nMeet Mineral Mappers Flying NASA Tech Out West\narticle\n1 day ago\nHighlights\n2 min read\nX-59 Model Tested in Japanese Supersonic Wind Tunnel\narticle\n6 hours ago\n6 min read\nMeet Mineral Mappers Flying NASA Tech Out West\narticle\n1 day ago\n3 min read\nNASA Aircraft, Sensor Technology, Aid in Texas Flood Recovery Efforts\narticle\n2 days ago\nHighlights\n3 min read\nNASA’s Roman Space Telescope Team Installs Observatory’s Solar Panels\narticle\n1 day ago\n4 min read\nNASA-Assisted Scientists Get Bird’s-Eye View of Population Status\narticle\n2 weeks ago\n1 min read\nTesting NASA-Developed Heat Shield Made by U.S. Company\narticle\n2 weeks ago\nFeatured\n1 min read\nJuly 2025\narticle\n1 week ago\n2 min read\nNASA Announces Winners of 2025 Human Lander Challenge\narticle\n2 weeks ago\n5 min read\nWhat Are Asteroids? (Ages 14-18)\narticle\n2 weeks ago\nFeatured\n5 min read\nNASA Advances Pressure Sensitive Paint Research Capability\narticle\n1 week ago\n5 min read\nWhat’s Up: July 2025 Skywatching Tips from NASA\narticle\n1 week ago\n11 min read\n3 Years of Science: 10 Cosmic Surprises from NASA’s Webb Telescope\narticle\n1 week ago\nHighlights\n3 min read\nPódcast en español de la NASA estrena su tercera temporada\narticle\n1 week ago\n5 min read\nLas carreras en la NASA despegan con las pasantías\narticle\n2 months ago\n4 min read\nEl X-59 de la NASA completa las pruebas electromagnéticas\narticle\n4 months ago\nNASA Pathways\nWe strategically hire our Pathways Interns based on long-term potential and alignment with NASA’s future workforce needs. Specializing in multi-semester experiences, the Pathways Internship Program prepares you for a career at NASA and offers a direct pipeline to full-time employment at NASA upon graduation.\nIf you have a passion for our mission and feel the calling to change the history of humanity, the Pathways Internship Program is a great way for you to launch your career with NASA!\nPathways Opportunities\nWho We Look For\nThe Experience\nCareers After Graduation\nTypes of Internships\nWhere We Work\nEligibility Requirements\nHow To Apply\nResume Tips\nMeet Our Interns\nProgram Points of Contact\nFrequently Asked Questions\nApplication Resources\nPathways Opportunities\nFuture opportunities will be posted here and on USAJOBS. Stay tuned for updates on opening and closing dates!\nWho We Look For\nWe’re looking for students who are captivated with our Vision, Mission, and Core Values and embody characteristics integral to NASA’s success. Top candidates are well-rounded students from a variety of backgrounds who demonstrate curiosity, team-orientation, excellence, a passion for exploration, agility, and resilience. Prior experience is not required! During the hiring process, we assess the following 12 competencies:\n•Accountability, Attention to Detail, Customer Service, Decision Making, Flexibility, Integrity/Honesty, Interpersonal Skills, Learning, Reading, Self-Management (Achievement), Stress Tolerance, and Teamwork\nThe Experience\nAs a Pathways Intern, we invest in you on purpose—assigning you with challenging, meaningful work aligned with your academic or career interests, providing you with life-long learning and growth opportunities, and cultivating a supportive community that offers you a home away from home.\nCareers After Graduation\nThroughout your Pathways Internship, you’re given the autonomy to define your own career trajectory at NASA. At the beginning of your internship, we will work with you to develop an “Individual Development Plan” that will help put your experience and path in your hands by defining assignments, training events, and learning opportunities that will help you achieve your career goals.\nAs you get closer to graduation, we will evaluate your experience and consider you for full-time employment that would begin after you complete your degree. No additional job applications needed!\nTypes of Internships\nWe offer a variety of internship opportunities across a variety of disciplines within the following OPM occupational classifications. We post the specific disciplines and skillsets we hire for in the weeks prior to applications opening.\nEngineering, Science, and Technology\nGS-899: Engineering\nGS-1399: Physical Sciences\nBusiness\nGS-0099: Safety & Occupational Health\nGS-199: Social Sciences\nGS-299: Human Resources\nGS-399: Administration and Program Management & Analysis\nGS-599: Accounting & Budget\nGS-1099: Communication & Public Relations\nGS-1199: Procurement and Contracts\nGS-1599: Math & Statistics\nGS-2299: Information Technology\nWhere We Work\nThere are several NASA centers located across the nation engaged in a variety of work. For examples of the work that our interns perform across the country, take a look at our Facebook and Instagram accounts.\nEligibility Requirements\nAll Pathways Interns must meet the following eligibility requirements:\nBe a U.S. citizen;\nBe at least 16 years of age;\nBe enrolled or accepted for enrollment on at least a half-time basis in an accredited educational institution and maintain enrollment at least half time as defined by the institution;\nBe pursuing a degree or certificate;\nCurrently have and maintain a cumulative 2.9 grade point average on a 4.0 scale;\nBe able to complete at least 480 hours of work prior to completing your degree/certificate requirements; View JSC specific requirements here.\nRequired to sign a Pathways Participant Agreement.\nRequired to undergo a pre-employment background investigation\nMale applicants born after December 31, 1959, must certify that they have registered with the Selective Service System, or are exempt from having to do so under the Selective Service Law.\nVacancies also require that applicants be available to begin work between a predetermined timeframe, typically the subsequent two semesters following the closing date of the vacancy for which you applied.\nHow to Apply\nAll of our Pathways Internship vacancies are posted on USAJobs.gov. Each vacancy lists multiple NASA Center locations and has different educational requirements (e.g., specific academic majors). To begin the process, follow these steps:Step 1: Do your research. Learn about the type of work performed at each of our NASA facilities so that you’ll be able to find where you’d best fit at NASA based on your academic and career interests.\nStep 2: Prepare your application. Visit USAJobs.gov to create your profile, build your resume, and set up a notification that will alert you when our positions open. Check out our tips below for building your resume.\nStep 3: Apply to a vacancy during the open application window. When you apply, be sure to apply to the vacancy that aligns with BOTH your academic major and preferred geographic location(s) in order to route your application to the type of work you’re interested in. Take a look at our Applicant Guide for lots of information on what to expect during the application process.\nUse of Artificial Intelligence\nCan I use ChatGPT or other artificial intelligence tools to assist in drafting application and assessment responses?NASA prohibits candidates from plagiarizing any portion of their employment application to include responses to questions in which you must provide a narrative response. You must create your own responses originally and not copy or adapt them from other sources. While NASA encourages you to create your narratives with great care, including correct use of grammar and style, you are prohibited from using any artificial intelligence (AI) or AI-assisted tool, to include but not limited to ChatGPT.  Any information you provide during the application process is subject to verification. NASA will discontinue your candidacy if we find you have violated this prohibition on use of AI tools in the application process.\nWriting Your Resume\nNASA wants to get to know you and see your story – so be clear and concise, but elaborate! Your resume is your best opportunity to demonstrate what sets you apart from other applicants. Write your USAJobs resume in a narrative format, where you highlight your accomplishments by using the CAR method (Challenge/Action/Result).\nMeet Our Interns\nAre you ready for your NASA Internship? Meet some of our interns and learn their backgrounds, why they chose a NASA internship, and what they’re working on!\nPathways Program Points of Contact\nAmes Research Center\nArmstrong Flight Research Center\nGlenn Research Center\nGoddard Space Flight Center, Wallops Flight Facility, and The IV&V Facility\nNASA Headquarters\nJohnson Space Center & The White Sands Test Facility.\nKennedy Space Center\nLangley Research Center\nMarshall Space Flight Center\nNASA Shared Services Center\nStennis Space Center\nFrequently Asked Questions\nNot finding what you’re looking for? Find the answers to some of our most frequently asked questions about our Internships & Pathways program here.\nApplication Resources\nPathways Applicant Guide\nView for more information on writing your resume, the assessment, application and hiring FAQs, and more.\nResume Tips\nCheck out these tips for building your resume\nPathways Video Playlist\nThese videos will help you do your research, prepare your application, and apply to a vacancy during the open application window!\nInternships Program Slides\nPresentation slide deck with an overview of both the Pathways and  OSTEM internship programs.\nFacebook logo\n@NASAInterns\n@NASAPeople@NASAInterns\nInstagram logo\n@NASAInternships\nLinkedin logo\n@NASA\nKeep Exploring\nDiscover More Topics From NASA\nCenters and Facilities\nNASA Internship Programs\nHumans In Space\nPeople of NASA\nWas this page helpful?\nWas this page helpful?\nYes\nNo\nNotifications

EXPECTED OUTPUT:
{"overview":{"title":"High School Internship Program","provider":"The Met","description":"The Met High School Internship Program offers paid opportunities for students who are two to three years from graduating high school to connect with art, museums, and creative professionals as they develop professional skills, network, and gain work experience.","link":"not provided","subject":[],"tags":["paid"]},"eligibility":{"essay_required":true,"recommendation_required":true,"transcript_required":"not provided","other":["Must be in grades 10 or 11 or obtaining their High School Equivalency degree","Must reside in or attend a high school or home school in New York, New Jersey, or Connecticut on the application deadline date","Interviews are required for finalists only"],"grades":["Sophomore","Junior"],"age":{"minimum":"not provided","maximum":"not provided"}},"dates":{"deadlines":[{"name":"Application Deadline","priority":"high","term":"Summer 2025","date":"03-07-2025","rolling_basis":false,"time":"6:00 PM"},{"name":"Interview Notification","priority":"medium","term":"Summer 2025","date":"04-18-2025","rolling_basis":false,"time":"not provided"}],"dates":[{"term":"Summer 2025","start":"07-07-2025","end":"08-08-2025"}],"duration_weeks":"not provided"},"locations":{"virtual":false,"state":"not provided","city":"not provided","address":"not provided"},"costs":{"costs":[],"stipend":{"available":true,"amount":null}},"contact":{"email":"highschoolinterns@metmuseum.org","phone":"not provided"}}
"""
}
