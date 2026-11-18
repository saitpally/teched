// Organization directory for the Blueprints for Pangaea expired-supply finder.
// Researched November 2026. Every entry lists its sources; confirm details by phone/email before shipping anything.
//
// Field guide
//   region:   "semi" (Southeast Michigan) | "mi" (rest of Michigan) | "midwest" | "national"
//   kind:     "training" (a facility that trains clinicians/students) | "partner" (an org that moves surplus to
//             training facilities or other users) | "network" (a group that connects you to many training sites)
//             | "animal" (veterinary / animal welfare) | "msro" (medical surplus recovery org)
//   expired:  "confirmed"  - a source says they take or redirect expired supplies
//             "training"   - training-only use, where expired stock is normally fine; ask first
//             "check"      - policy not published; ask
//             "unexpired"  - source says unexpired only (often 12+ months of shelf life) - use for good-dated stock
//   useful:   supply categories this org is likely to want (see CATEGORIES in app.js)

window.ORGS = [
  // ---------------- SOUTHEAST MICHIGAN: training facilities ----------------
  {
    id: "um-son-clc",
    name: "U-M School of Nursing Clinical Learning Center",
    kind: "training", sub: "Nursing simulation", region: "semi",
    city: "Ann Arbor, MI", lat: 42.2806, lng: -83.7340,
    expired: "training",
    why: "Already reuses simulation kits and is working with suppliers to cut sim-lab waste. Its team co-founded a sustainability special interest group in INACSL with 12 other schools, so it can introduce you to other sim labs.",
    useful: ["syringes", "iv", "gloves", "dressings", "catheters"],
    contact: "Named leads: Melissa Bathish (co-director); colleagues Deb Lee, Jessica Marsack, Meg Czerwinski",
    web: "https://nursing.umich.edu",
    sources: ["https://engaged.umich.edu/news/nursing-center-eyes-reusing-simulated-learning-materials/"]
  },
  {
    id: "um-csc",
    name: "U-M Clinical Simulation Center (Towsley & Med Sci II)",
    kind: "training", sub: "Medical school simulation", region: "semi",
    city: "Ann Arbor, MI", lat: 42.2840, lng: -83.7280,
    expired: "training",
    why: "Two locations and nine simulated clinical rooms that serve medicine, nursing, pharmacy and dentistry. It sits on the same campus as Michigan Medicine, so it can be the simplest hand-off for expired stock.",
    useful: ["syringes", "iv", "gloves", "airway", "catheters", "sutures"],
    contact: "Admin 734-936-8305; G2400 Towsley Center, 1500 E Medical Center Dr",
    web: "https://medschool.umich.edu/centers/clinical-simulation-center",
    sources: ["https://medschool.umich.edu/centers/clinical-simulation-center/about-us", "https://www.michiganmedicine.org/health-lab/medical-simulation-based-training-future-health-care"]
  },
  {
    id: "wcc-nursing",
    name: "Washtenaw Community College Nursing & Surgical Technology labs",
    kind: "training", sub: "Nursing & surgical tech", region: "semi",
    city: "Ann Arbor, MI", lat: 42.2600, lng: -83.6630,
    expired: "training",
    why: "Runs skills and simulation labs plus a two-room mock operating room for surgical technology. Under the Michigan Board of Nursing, up to half of nursing clinical time can be spent in simulation.",
    useful: ["syringes", "iv", "gloves", "dressings", "surgical", "sutures"],
    contact: "Skills/Simulation Lab (TI 101) 734-249-5668; nur@wccnet.edu",
    web: "https://www.wccnet.edu",
    sources: ["https://wccnet.edu/news/launch/2018-winter/healthy-futures.php", "https://arts.wccnet.edu/learn/departments/nhsd/_documents/nursing-student-handbook.pdf", "https://www.wccnet.edu/news/ontherecord/2017-10/simulator.php"]
  },
  {
    id: "emu-son",
    name: "Eastern Michigan University School of Nursing Simulation Lab",
    kind: "training", sub: "Nursing simulation", region: "semi",
    city: "Ypsilanti, MI", lat: 42.2510, lng: -83.6240,
    expired: "training",
    why: "Paid for by student fees and donations, so donated supplies matter here. Partners with WCC on a joint nursing program.",
    useful: ["syringes", "iv", "gloves", "dressings", "catheters"],
    contact: "",
    web: "https://emich.edu/chhs/nursing/360-degree-difference/svrp.php",
    sources: ["https://www.emich.edu/chhs/news/on-campus-nursing-simulation-lab-at-emu-dedicated-to-preparing-students-for-real-life-situations.php"]
  },
  {
    id: "hva-ems",
    name: "Huron Valley Ambulance Center for EMS Education (Emergent Health Partners)",
    kind: "training", sub: "EMT & paramedic", region: "semi",
    city: "Ann Arbor, MI", lat: 42.2390, lng: -83.7380,
    expired: "training",
    why: "Trains EMTs, paramedics and community paramedics, and runs EMT courses with Monroe County Community College. One contact here reaches several ambulance services across south-central Michigan.",
    useful: ["airway", "iv", "dressings", "gloves", "syringes"],
    contact: "1200 State Circle, Ann Arbor, MI 48108",
    web: "https://www.emergenthealth.org",
    sources: ["https://bellevilleareaindependent.com/?p=9216", "https://www.monroeccc.edu/news/17-18/039.html", "https://bellevilleareaindependent.com/?p=17145"]
  },
  {
    id: "mccc-ems",
    name: "Monroe County Community College EMT program",
    kind: "training", sub: "EMT", region: "semi",
    city: "Monroe, MI", lat: 41.9300, lng: -83.4000,
    expired: "training",
    why: "Runs an EMT course with Huron Valley Ambulance. Its nursing faculty also sit on Schoolcraft's simulation lab advisory committee.",
    useful: ["airway", "dressings", "gloves", "iv"],
    contact: "",
    web: "https://www.monroeccc.edu",
    sources: ["https://www.monroeccc.edu/news/17-18/039.html", "https://www.schoolcraft.edu/academics/health-professions/"]
  },
  {
    id: "henryford-sim",
    name: "Henry Ford Center for Simulation, Education and Research",
    kind: "training", sub: "Hospital simulation center", region: "semi",
    city: "Detroit, MI", lat: 42.3677, lng: -83.0850,
    expired: "training",
    why: "A 12,000 sq ft center with a model OR, ED, ICU and endoscopy suite, serving more than 14,000 participants. It has worked with simulation centers at Wayne State, Beaumont, U-M and MSU.",
    useful: ["surgical", "sutures", "airway", "iv", "catheters", "gloves"],
    contact: "313-916-6253; W. Grand Blvd & M-10, Detroit",
    web: "https://henryford.com/HCP/Med-Ed/Sim-Center",
    sources: ["https://henryford.com/HCP/Med-Ed/Sim-Center", "https://prod-cd.henryford.com/HCP/Med-Ed/Sim-Center/Location", "https://www.modeldmedia.com/devnews/henryford112.aspx", "https://www.hourdetroit.com/health/meet-the-robot-helping-to-save-real-lives/"]
  },
  {
    id: "wsu-som",
    name: "Wayne State University School of Medicine simulation (Mazurek Commons)",
    kind: "training", sub: "Medical school simulation", region: "semi",
    city: "Detroit, MI", lat: 42.3540, lng: -83.0560,
    expired: "training",
    why: "Runs high-fidelity simulation for clerkships and for residents in anesthesia, critical care, EM and pediatric dentistry.",
    useful: ["airway", "iv", "syringes", "gloves", "catheters"],
    contact: "",
    web: "https://www.med.wayne.edu/kado/simulation",
    sources: ["https://programs.med.wayne.edu/kado/simulation", "https://campustechnology.com/articles/2009/06/22/wayne-state-opens-medical-training-center-with-patient-mannequins.aspx"]
  },
  {
    id: "wsu-con",
    name: "Wayne State College of Nursing Simulation Lab",
    kind: "training", sub: "Nursing simulation", region: "semi",
    city: "Detroit, MI", lat: 42.3555, lng: -83.0610,
    expired: "training",
    why: "Has a dedicated simulation technology administrator, which gives you a clear person to contact.",
    useful: ["syringes", "iv", "gloves", "dressings", "catheters"],
    contact: "Jason Harper, RN, 221 Cohn; 313-577-0466",
    web: "https://nursing.wayne.edu/clinical-learning-labs",
    sources: ["https://nursing.wayne.edu/clinical-learning-labs"]
  },
  {
    id: "msucom-dmc",
    name: "MSU College of Osteopathic Medicine - Detroit Medical Center site",
    kind: "training", sub: "Medical school", region: "semi",
    city: "Detroit, MI", lat: 42.3530, lng: -83.0590,
    expired: "training",
    why: "MSUCOM's Detroit campus on the DMC grounds. MSU's Learning and Assessment Center serves more than 10,000 learners a year across its medical, nursing and veterinary colleges.",
    useful: ["syringes", "iv", "gloves", "sutures"],
    contact: "",
    web: "https://www.healthsciences.msu.edu/partners/detroit-medical-center",
    sources: ["https://www.healthsciences.msu.edu/partners/detroit-medical-center", "https://osteopathicmedicine.msu.edu/news_overview/news/2024/september/learning-and-assessment-center-msu-celebrated-during-healthcare-simulation-week"]
  },
  {
    id: "udm-star",
    name: "Detroit Mercy STAR Center (College of Health Professions)",
    kind: "training", sub: "Nursing & health professions sim", region: "semi",
    city: "Detroit, MI", lat: 42.4150, lng: -83.1370,
    expired: "training",
    why: "A 5,000 sq ft simulation center built to look and work like a hospital. It also serves Detroit Mercy's Novi and Grand Rapids nursing programs.",
    useful: ["syringes", "iv", "gloves", "dressings", "catheters"],
    contact: "",
    web: "https://healthprofessions.udmercy.edu",
    sources: ["https://www.clickondetroit.com/sponsored/2023/10/02/how-one-schools-state-of-the-art-working-hospital-uses-simulation-to-better-prepare-health-care-students", "https://www.pbs.org/video/university-of-detroit-mercy-launches-star-center-y6j8js"]
  },
  {
    id: "udm-dental",
    name: "Detroit Mercy School of Dentistry simulation lab",
    kind: "training", sub: "Dental", region: "semi",
    city: "Detroit, MI", lat: 42.3320, lng: -83.0700,
    expired: "training",
    why: "Has a 100-station simulation lab. Expired gloves, gauze, syringes and suture work well for dental skills training.",
    useful: ["gloves", "syringes", "sutures", "dressings"],
    contact: "Corktown Campus, 2700 Martin Luther King Jr. Blvd",
    web: "https://dental.udmercy.edu",
    sources: ["https://orthodonticproductsonline.com/miscellaneous/university-of-detroit-mercy-opens-dentistry-school-2008-01-28-01/"]
  },
  {
    id: "wcccd",
    name: "Wayne County Community College District (Nursing, Surgical Tech, Vet Tech)",
    kind: "training", sub: "Nursing, surgical & vet tech", region: "semi",
    city: "Detroit, MI", lat: 42.3290, lng: -83.0530,
    expired: "training",
    why: "One district with nursing, LPN, surgical technology and veterinary technology programs, so one conversation covers human and animal training uses.",
    useful: ["syringes", "iv", "gloves", "surgical", "sutures", "dressings"],
    contact: "Nursing: nursing@wcccd.edu, 8200 W Outer Dr, Detroit",
    web: "https://www.wcccd.edu/academic-and-career-programs/health-sciences",
    sources: ["https://collaboration.acemapp.org/e-content/wayne-county-community-college-district-nursing", "https://skillplum.com/school/wayne-county-community-college-district-detroit-mi/513901-cert-1-2yr", "https://www.petersons.com/college-search/wayne-county-community-college-district-000_10000784.aspx"]
  },
  {
    id: "hfc",
    name: "Henry Ford College School of Nursing & Paramedic program",
    kind: "training", sub: "Nursing & paramedic", region: "semi",
    city: "Dearborn, MI", lat: 42.3220, lng: -83.2370,
    expired: "training",
    why: "Several skills and simulation labs at the East Campus Health Careers center, plus a state-approved paramedic program with its own training ambulance.",
    useful: ["syringes", "iv", "gloves", "airway", "dressings"],
    contact: "Health Careers Office (313) 845-9877; East Campus, 3601 Shafer Rd",
    web: "https://www.hfcc.edu/nursing",
    sources: ["https://www.hfcc.edu/nursing", "https://catalog.hfcc.edu/programs/paramedic-aas", "https://www.hfcc.edu/news/2018/learning-life-saving-skills-ems-and-hfc-ambulance"]
  },
  {
    id: "schoolcraft",
    name: "Schoolcraft College Health Professions Simulation Lab",
    kind: "training", sub: "Nursing, EMT & residents", region: "semi",
    city: "Livonia, MI", lat: 42.4210, lng: -83.4300,
    expired: "training",
    why: "Rents its lab to Trinity Health residents and trains nursing and EMT students. It has intubation, central-line and arterial-line trainers that use up airway and IV disposables.",
    useful: ["airway", "iv", "syringes", "gloves", "catheters"],
    contact: "734-462-4400; EMT: Thomas Worthington, HS363, 18600 Haggerty Rd",
    web: "https://home.schoolcraft.edu/health-professions-simulation-lab",
    sources: ["https://home.schoolcraft.edu/health-professions-simulation-lab", "https://schoolcraftconnection.com/2020/06/23/simulation-makes-perfect", "https://www.schoolcraft.edu/academics/health-professions/emergency-medical-technology"]
  },
  {
    id: "corewell-sli",
    name: "Corewell Health Applebaum Simulation Learning Institute",
    kind: "training", sub: "Hospital simulation center", region: "semi",
    city: "Royal Oak, MI", lat: 42.5170, lng: -83.1940,
    expired: "training",
    why: "Has a surgical skills and tissue lab used by 18 residency programs, Wayne State medical students and Oakland's CRNA program. Surgical packs and suture are an especially good fit here.",
    useful: ["surgical", "sutures", "gloves", "airway", "catheters"],
    contact: "Exec. director Kathryn Ziegler, MD; Angila Beard (director, simulation & clinical education)",
    web: "https://corewellhealth.org/simulation/southeast-michigan",
    sources: ["https://corewellhealth.org/simulation/southeast-michigan/statistics", "https://corewellhealth.org/simulation/southeast-michigan/showcase", "https://corewellhealth.org/simulation/southeast-michigan/team"]
  },
  {
    id: "ouwb-csc",
    name: "OUWB Clinical Skills Training & Simulation Center",
    kind: "training", sub: "Medical school", region: "semi",
    city: "Sterling Heights, MI", lat: 42.6200, lng: -83.0860,
    expired: "training",
    why: "A former family medicine clinic with 16 simulated patient rooms, used by students in all four years of medical school.",
    useful: ["gloves", "syringes", "dressings", "iv"],
    contact: "(248) 964-5854; director Stephanie Marcincavage; 44300 Dequindre Rd",
    web: "https://oakland.edu/medicine/curriculum/clinical-skills-center/",
    sources: ["https://oakland.edu/medicine/curriculum/clinical-skills-center/", "https://oakland.edu/medicine/news/auto-list-news/2020/Take-5-with-Maurice-Kavanagh"]
  },
  {
    id: "macomb",
    name: "Macomb Community College Health & Public Services (incl. Vet Tech & mobile sim unit)",
    kind: "training", sub: "Nursing, respiratory, surg tech, vet tech", region: "semi",
    city: "Clinton Township, MI", lat: 42.6250, lng: -82.9440,
    expired: "training",
    why: "Michigan's largest community college. It runs nursing, respiratory therapy and surgical tech programs, an accredited vet tech teaching hospital, and a new 38-foot mobile simulation unit that visits employers.",
    useful: ["syringes", "iv", "gloves", "airway", "surgical", "sutures", "catheters"],
    contact: "health@macomb.edu; 44575 Garfield Rd, Clinton Twp",
    web: "https://www.macomb.edu/future-students/area-interest/health.html",
    sources: ["https://www.macomb.edu/news/2026/03/nr-mobile-simulation-unit.html", "https://www.macomb.edu/news/2026/04/news-article-page.html", "https://www.macomb.edu/future-students/area-interest/health.html"]
  },

  // ---------------- SOUTHEAST MICHIGAN: partners & outlets ----------------
  {
    id: "wmr",
    name: "World Medical Relief",
    kind: "msro", sub: "Medical surplus recovery", region: "semi",
    city: "Southfield, MI", lat: 42.4650, lng: -83.2350,
    expired: "unexpired",
    why: "Detroit's long-running surplus-recovery group and a mentor org Blueprints has already discussed. It needs at least a year before expiration, so send it good-dated stock. Ask whether it has an outlet for expired items.",
    useful: ["dressings", "surgical", "airway", "equipment", "lab"],
    contact: "(313) 866-5333; 21725 Melrose Ave, Southfield, MI 48075",
    web: "https://worldmedicalrelief.org/product-donations",
    sources: ["https://www.worldmedicalrelief.org/product-donation-form", "https://worldmedicalrelief.org/product-donations"]
  },
  {
    id: "life",
    name: "Life for Relief and Development (LIFE)",
    kind: "msro", sub: "International relief", region: "semi",
    city: "Southfield, MI", lat: 42.4730, lng: -83.2210,
    expired: "check",
    why: "Ships containers of medical supplies and equipment overseas and has sourced shipments through World Medical Relief.",
    useful: ["equipment", "syringes", "gloves", "dressings"],
    contact: "",
    web: "https://lifeusa.org",
    sources: ["https://www.lifeusa.org/post/medical-supplies-shipment-ashty-general-hospital", "https://www.guidestar.org/Profile/95-4402149"]
  },
  {
    id: "hope-clinic",
    name: "The Hope Clinic",
    kind: "partner", sub: "Free clinic", region: "semi",
    city: "Ypsilanti, MI", lat: 42.2440, lng: -83.6130,
    expired: "unexpired",
    why: "A local free clinic that takes good-dated dressings, IV kits, tubing, syringes and ostomy supplies. A close outlet for any stock that hasn't expired yet.",
    useful: ["dressings", "iv", "syringes"],
    contact: "(734) 481-0111 ext. 108; 518 Harriet St",
    web: "https://www.thehopeclinic.org",
    sources: ["https://loanclosets.org/?p=202"]
  },
  {
    id: "hshv",
    name: "Humane Society of Huron Valley",
    kind: "animal", sub: "Animal shelter & clinic", region: "semi",
    city: "Ann Arbor, MI", lat: 42.2400, lng: -83.6900,
    expired: "check",
    why: "Many shelters use expired gauze, syringes and gloves for animal surgery; Ohio shelters take them from EMS agencies. HSHV hasn't published a medical-supply policy, so ask first.",
    useful: ["gloves", "syringes", "dressings", "sutures"],
    contact: "2280 S Industrial Hwy, Ann Arbor",
    web: "https://www.hshv.org",
    sources: ["https://www.yahoo.com/now/unwanted-expired-no-problem-animal-104115285.html", "https://recycleannarbor.org/a-z-recycling-guide/292-pet-supplies-good-condition"]
  },

  // ---------------- REST OF MICHIGAN ----------------
  {
    id: "msu-cvm",
    name: "MSU College of Veterinary Medicine (LeBlanc Clinical Skills Lab & mobile surgery unit)",
    kind: "animal", sub: "Veterinary school", region: "mi",
    city: "East Lansing, MI", lat: 42.7230, lng: -84.4680,
    expired: "training",
    why: "Vet and vet-tech students practice on models in the clinical skills lab. A 32-foot mobile surgery unit runs free spay/neuter for Michigan shelters and depends on donated gowns, gloves and suture.",
    useful: ["gloves", "sutures", "surgical", "syringes", "dressings"],
    contact: "",
    web: "https://cvm.msu.edu/hospital/services/community-medicine/support-our-mission-donating",
    sources: ["https://cvm.msu.edu/news/2018/college-receives-donation-to-support-new-clinical-skills-lab", "https://cvm.msu.edu/hospital/services/community-medicine/support-our-mission-donating"]
  },
  {
    id: "msu-lac",
    name: "MSU Learning and Assessment Center",
    kind: "training", sub: "University simulation center", region: "mi",
    city: "East Lansing, MI", lat: 42.7190, lng: -84.4700,
    expired: "training",
    why: "Serves more than 10,000 learners a year across MSU's osteopathic, human medicine, nursing and veterinary colleges, plus residency programs statewide.",
    useful: ["syringes", "iv", "gloves", "airway", "catheters"],
    contact: "Exec. director Mary Kay Smith, PhD, RN",
    web: "https://lac.msu.edu",
    sources: ["https://osteopathicmedicine.msu.edu/news_overview/news/2024/september/learning-and-assessment-center-msu-celebrated-during-healthcare-simulation-week"]
  },
  {
    id: "kcc-ems",
    name: "Kellogg Community College EMS Sim Lab",
    kind: "training", sub: "EMT & paramedic", region: "mi",
    city: "Battle Creek, MI", lat: 42.3200, lng: -85.1800,
    expired: "training",
    why: "A newly upgraded EMS sim lab with an ambulance simulator, training EMTs, first responders and paramedics.",
    useful: ["airway", "dressings", "iv", "gloves"],
    contact: "",
    web: "https://kellogg.edu/ems",
    sources: ["https://daily.kellogg.edu/2022/03/30/saving-lives-through-education-ems-sim-lab-upgrades-offer-new-opportunities-for-students/"]
  },
  {
    id: "wmed-sim",
    name: "WMed (Western Michigan Univ. Homer Stryker MD School of Medicine) Simulation Center",
    kind: "training", sub: "Medical school simulation", region: "mi",
    city: "Kalamazoo, MI", lat: 42.2920, lng: -85.5850,
    expired: "training",
    why: "Its curriculum includes more than 100 hours of simulation-based learning, and it takes requests from outside groups.",
    useful: ["syringes", "iv", "gloves", "airway"],
    contact: "simulation@wmed.edu",
    web: "https://wmed.edu/node/201",
    sources: ["https://wmed.edu/node/499", "https://wmed.edu/node/201"]
  },
  {
    id: "wmu-nursing",
    name: "WMU Bronson School of Nursing Simulation & Skills Lab",
    kind: "training", sub: "Nursing simulation", region: "mi",
    city: "Kalamazoo, MI", lat: 42.2830, lng: -85.6150,
    expired: "training",
    why: "Three nursing clinical labs plus a high-fidelity SimMan suite.",
    useful: ["syringes", "iv", "gloves", "dressings", "catheters"],
    contact: "",
    web: "https://wmich.edu/hhs/facilities/simulationlab",
    sources: ["https://wmich.edu/hhs/facilities/simulationlab", "https://wmich.edu/nursing/about/facilities"]
  },
  {
    id: "intl-aid",
    name: "International Aid",
    kind: "msro", sub: "Medical relief & biomed training", region: "mi",
    city: "Spring Lake, MI", lat: 43.0770, lng: -86.1970,
    expired: "check",
    why: "West Michigan relief group that reconditions medical equipment and runs biomedical training. It has partnered with Spectrum Health (now Corewell West) on surplus.",
    useful: ["equipment", "lab", "dressings"],
    contact: "616-846-7490; info@internationalaid.org; 17011 Hickory St",
    web: "https://internationalaid.org",
    sources: ["https://www.idealist.org/en/nonprofit/8d6655b2b64a4dc58ed5d5ba5e5c7da2-international-aid-spring-lake", "https://www.mnnonline.org/?p=69772", "https://ccih.org/?p=4409"]
  },

  // ---------------- MIDWEST ----------------
  {
    id: "utoledo-iisc",
    name: "University of Toledo Interprofessional Immersive Simulation Center",
    kind: "training", sub: "University simulation center", region: "midwest",
    city: "Toledo, OH", lat: 41.6200, lng: -83.6170,
    expired: "training",
    why: "About 50 miles from Ann Arbor, the closest major out-of-state sim center. A 65,000 sq ft virtual hospital with fresh-tissue surgical labs, accredited by both ACS and SSH.",
    useful: ["surgical", "sutures", "airway", "iv", "catheters", "gloves"],
    contact: "iisc@utoledo.edu; 419-383-4455",
    web: "https://www.utoledo.edu/centers/iisc/",
    sources: ["https://www.utoledo.edu/centers/iisc/", "https://www.utoledo.edu/centers/iisc/facilities.html"]
  },
  {
    id: "medwish",
    name: "MedWish (MedWish-Medworks) Alternative Recycling Program",
    kind: "partner", sub: "Surplus recovery with expired-supply program", region: "midwest",
    city: "Cleveland, OH", lat: 41.5060, lng: -81.6630,
    expired: "confirmed",
    why: "Probably the closest model to what Blueprints is building. Its Alternative Recycling Program passes expired and non-sterile supplies to domestic nonprofits, including schools and animal shelters. Pickup is by appointment.",
    useful: ["gloves", "syringes", "dressings", "iv", "catheters", "surgical"],
    contact: "(216) 692-1685; 1625 E 31st St, Cleveland, OH 44114",
    web: "https://medwish.org",
    sources: ["https://form.jotform.com/90495683029971", "https://clevelandmagazine.com/articles/medwish-founder-changes-the-worlds-medical-landscape", "https://sbnonline.com/article/medwish-international-collects-scrapped-yet-new-medical-supplies-relief-developing-countries/"]
  },
  {
    id: "firelands",
    name: "Firelands Regional Medical Center School of Nursing",
    kind: "training", sub: "Hospital nursing school", region: "midwest",
    city: "Sandusky, OH", lat: 41.4490, lng: -82.7080,
    expired: "confirmed",
    why: "Its hospital already sends expired disposables to its own nursing school and other local teaching sites, which makes it a useful model to show Michigan Medicine.",
    useful: ["syringes", "iv", "gloves", "dressings"],
    contact: "",
    web: "https://www.firelands.com",
    sources: ["https://www.firelands.com/empower/giving-back/sharing-is-caring/"]
  },
  {
    id: "osu-cseac",
    name: "Ohio State Clinical Skills Education and Assessment Center",
    kind: "training", sub: "Medical school simulation", region: "midwest",
    city: "Columbus, OH", lat: 39.9960, lng: -83.0170,
    expired: "training",
    why: "A large multidisciplinary skills lab in Prior Hall covering basic clinical skills and advanced surgical and procedural training.",
    useful: ["surgical", "sutures", "airway", "iv", "syringes", "gloves"],
    contact: "376 W 10th Ave, Columbus",
    web: "https://medicine.osu.edu/departments/clinical-skills-center",
    sources: ["https://medicine.osu.edu/departments/clinical-skills-center"]
  },
  {
    id: "m25",
    name: "Matthew 25: Ministries",
    kind: "msro", sub: "Humanitarian aid", region: "midwest",
    city: "Blue Ash (Cincinnati), OH", lat: 39.2600, lng: -84.3800,
    expired: "check",
    why: "Sends medical supplies to hundreds of partner organizations around Greater Cincinnati and abroad. Its rules on expired supplies aren't published.",
    useful: ["dressings", "gloves", "equipment"],
    contact: "(513) 793-6256; drop-off 11083 Kenwood Rd",
    web: "https://m25m.org",
    sources: ["https://www.cincinnatimagazine.com/article/matthew-25-ministries-gives-profile/", "https://m25m.org/?p=11737"]
  },
  {
    id: "iu-fairbanks",
    name: "IU Health Simulation Center at Fairbanks Hall",
    kind: "training", sub: "Health system + university sim", region: "midwest",
    city: "Indianapolis, IN", lat: 39.7790, lng: -86.1680,
    expired: "training",
    why: "A 30,000 sq ft center run with IU's schools of medicine and nursing, hosting about 1,000 events a year.",
    useful: ["syringes", "iv", "gloves", "airway", "catheters"],
    contact: "340 W 10th St, Indianapolis",
    web: "https://iuhealth.org/sim-center",
    sources: ["https://iuhealth.org/sim-center/about", "https://medicine.iu.edu/emergency-medicine/education/fellowship/medical-simulation"]
  },
  {
    id: "pcure-chi",
    name: "Project C.U.R.E. Chicago",
    kind: "msro", sub: "Medical surplus recovery", region: "midwest",
    city: "Woodridge, IL", lat: 41.7470, lng: -88.0500,
    expired: "unexpired",
    why: "Distribution center for the world's largest distributor of donated medical supplies, and a mentor org Blueprints has already discussed. It wants items that still have usable life.",
    useful: ["equipment", "surgical", "dressings"],
    contact: "",
    web: "https://projectcure.org/chicago",
    sources: ["https://projectcure.org/take-action/donate/donate-medical-equipment-supplies/hospitals/", "https://www.idealist.org/en/volunteer-opportunity/85cdd14af0ee463d87611c0bf07601ee-warehouse-volunteers-needed-project-cure-chicago-project-cure-woodridge"]
  },
  {
    id: "hshs-mo",
    name: "Hospital Sisters Mission Outreach",
    kind: "partner", sub: "Surplus recovery that redirects expired goods", region: "midwest",
    city: "Springfield, IL", lat: 39.8500, lng: -89.6400,
    expired: "confirmed",
    why: "Receives expired goods and passes them to nursing schools, animal shelters and daycare centers. It never ships expired items overseas, so it already runs the two-track system Blueprints needs.",
    useful: ["gloves", "syringes", "dressings", "iv", "surgical", "equipment"],
    contact: "217-525-8843; 4930 LaVerna Rd, Springfield, IL",
    web: "https://hshs.org/mission-outreach/about",
    sources: ["https://healthtrustpg.com/thesource/healthcare-facility-management/supplying-the-developing-world/", "https://sralab.org/lifecenter/resources/listing-used-equipment"]
  },
  {
    id: "wustl-sim",
    name: "Washington University School of Medicine simulation centers",
    kind: "training", sub: "Medical school simulation", region: "midwest",
    city: "St. Louis, MO", lat: 38.6350, lng: -90.2640,
    expired: "training",
    why: "Five centers, including a surgical skills institute (WISE) and a pediatric center, so there are several departments that could use supplies.",
    useful: ["surgical", "sutures", "airway", "iv"],
    contact: "",
    web: "https://simulation.wustl.edu/simulation-centers",
    sources: ["https://simulation.wustl.edu/simulation-centers"]
  },
  {
    id: "pcure-kc",
    name: "Project C.U.R.E. Kansas City",
    kind: "msro", sub: "Medical surplus recovery", region: "midwest",
    city: "Kansas City, MO", lat: 39.0997, lng: -94.5786,
    expired: "unexpired",
    why: "A second Midwest Project C.U.R.E. warehouse. It wants items that still have usable life.",
    useful: ["equipment", "surgical", "dressings"],
    contact: "",
    web: "https://projectcure.org",
    sources: ["https://projectcure.org/take-action/donate/donate-medical-equipment-supplies/hospitals/"]
  },
  {
    id: "ku-wichita",
    name: "KU School of Medicine-Wichita Simulation Center",
    kind: "training", sub: "Medical school simulation", region: "midwest",
    city: "Wichita, KS", lat: 37.6870, lng: -97.3300,
    expired: "training",
    why: "A proven case study: it took a large surgery-center donation, kept what it could use and passed the rest to local nursing, respiratory therapy and loan-closet programs.",
    useful: ["surgical", "gloves", "syringes", "equipment"],
    contact: "Program director Erin Doyle",
    web: "https://www.kumc.edu/school-of-medicine/campuses/wichita.html",
    sources: ["https://www.kumc.edu/school-of-medicine/campuses/wichita/about/news/news-archive/surgicare-of-wichitas-donation-aids-simulation-center-others-across-wichita.html"]
  },
  {
    id: "matter",
    name: "MATTER",
    kind: "partner", sub: "Hospital surplus partner", region: "midwest",
    city: "Minneapolis, MN", lat: 44.9778, lng: -93.2650,
    expired: "confirmed",
    why: "Lists non-hazardous expired medical supplies among the donations it accepts. Works with health systems such as Allina, and in some cases covers transport from the hospital.",
    useful: ["gloves", "syringes", "dressings", "surgical", "equipment"],
    contact: "",
    web: "https://www.matter.ngo",
    sources: ["https://www.matter.ngo/?p=24447", "https://www.matter.ngo/wp-content/uploads/2024/04/MATTER_Allina_Case-Study_2024.pdf"]
  },
  {
    id: "ghm",
    name: "Global Health Ministries",
    kind: "msro", sub: "Medical surplus recovery", region: "midwest",
    city: "Fridley (Minneapolis), MN", lat: 45.0860, lng: -93.2630,
    expired: "unexpired",
    why: "Needs more than a year before expiration because of processing and shipping time. Use it for good-dated surplus. It has also linked up with animal rescues that take what it can't use.",
    useful: ["dressings", "surgical", "equipment"],
    contact: "763-586-9590; office@ghm.org; 7831 Hickory St NE",
    web: "https://www.ghm.org/hospitals-and-health-systems",
    sources: ["https://www.ghm.org/hospitals-and-health-systems", "https://www.life-source.org/latest/medical-supplies-donated-to-local-nonprofits/"]
  },
  {
    id: "wtc-xr",
    name: "Western Technical College Simulation & XR Lab",
    kind: "training", sub: "EMS & nursing sim", region: "midwest",
    city: "La Crosse, WI", lat: 43.8130, lng: -91.2400,
    expired: "training",
    why: "Trains local EMS agencies as well as its own students, so a single lab reaches several ambulance services.",
    useful: ["airway", "dressings", "iv", "gloves"],
    contact: "",
    web: "https://www.westerntc.edu/node/19262",
    sources: ["https://www.westerntc.edu/node/19262"]
  },

  // ---------------- NETWORKS & NATIONAL ----------------
  {
    id: "inacsl",
    name: "INACSL Sustainability Special Interest Group",
    kind: "network", sub: "Simulation educators' network", region: "national",
    city: "National (U-M is a founding member)", lat: null, lng: null,
    expired: "training",
    why: "Started by U-M's nursing simulation team and 12 other schools to cut sim-lab waste. A single introduction here could reach many simulation coordinators looking for practice supplies.",
    useful: ["syringes", "iv", "gloves", "dressings", "catheters"],
    contact: "Ask the U-M School of Nursing CLC for an introduction",
    web: "https://www.inacsl.org",
    sources: ["https://engaged.umich.edu/news/nursing-center-eyes-reusing-simulated-learning-materials/"]
  },
  {
    id: "animalaid",
    name: "Project AnimalAid",
    kind: "animal", sub: "Veterinary supply redistribution", region: "national",
    city: "Boulder, CO (ships nationally)", lat: 40.0150, lng: -105.2705,
    expired: "confirmed",
    why: "Takes gloves and suture up to two years past expiration and sends them to more than 125 animal-welfare nonprofits, including U.S. low-cost clinics.",
    useful: ["gloves", "sutures", "syringes", "catheters", "dressings", "equipment"],
    contact: "",
    web: "https://www.projectanimalaid.org",
    sources: ["https://www.aaha.org/newstat/publications/project-animalaid-gets-supplies-and-equipment-to-organizations-in-need/", "https://coloradogives.org/ProjectAnimalAid"]
  }
];
