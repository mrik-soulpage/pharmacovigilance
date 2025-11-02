"""
Synthetic Data Generator for Pharmacovigilance Literature Monitoring PoC

Generates:
1. Sample products with search strategies
2. Synthetic articles with various ICSR scenarios
3. Test cases covering all classification types
"""

import json
import random
from datetime import datetime, timedelta
import pandas as pd

# Sample product data
PRODUCTS = [
    # Simple search strategies (Non-EU)
    {
        "inn": "Amlodipine",
        "search_strategy": "Amlodipine AND ((case report) OR (case series) OR (case study))",
        "is_eu_product": False,
        "territories": ["US", "UK", "DE", "FR"],
        "dosage_forms": ["Tablet", "Capsule"],
        "routes": ["Oral"],
        "marketing_status": "Active"
    },
    {
        "inn": "Metformin",
        "search_strategy": "Metformin AND ((case report) OR (case series) OR (case study))",
        "is_eu_product": False,
        "territories": ["US", "CA", "UK"],
        "dosage_forms": ["Tablet"],
        "routes": ["Oral"],
        "marketing_status": "Active"
    },
    {
        "inn": "Lisinopril",
        "search_strategy": "Lisinopril AND ((case report) OR (case series) OR (case study))",
        "is_eu_product": False,
        "territories": ["US", "UK", "AU"],
        "dosage_forms": ["Tablet"],
        "routes": ["Oral"],
        "marketing_status": "Active"
    },
    {
        "inn": "Omeprazole",
        "search_strategy": "Omeprazole AND ((case report) OR (case series) OR (case study))",
        "is_eu_product": False,
        "territories": ["US", "UK", "DE", "FR", "ES"],
        "dosage_forms": ["Capsule", "Tablet"],
        "routes": ["Oral"],
        "marketing_status": "Active"
    },
    {
        "inn": "Simvastatin",
        "search_strategy": "Simvastatin AND ((case report) OR (case series) OR (case study))",
        "is_eu_product": False,
        "territories": ["US", "CA", "UK"],
        "dosage_forms": ["Tablet"],
        "routes": ["Oral"],
        "marketing_status": "Active"
    },
    # Complex search strategies (EU products)
    {
        "inn": "Cisatracurium",
        "search_strategy": '(Cisatracurium OR "cisatracurium besilate" OR "cisatracurium besylate") AND ((case report) OR (case series) OR (case study) OR (adverse effects) OR (toxicity) OR (fatal outcomes) OR (pregnancy) OR (lactation) OR (teratogenic) OR (genotoxic) OR (mutagenic) OR (abuse) OR (misuse) OR (off label use) OR (medication errors) OR (interactions) OR (overdose) OR (pediatric population) OR (elderly population) OR (lack of efficacy))',
        "is_eu_product": True,
        "territories": ["DE", "FR", "IT", "ES", "NL"],
        "dosage_forms": ["Injection"],
        "routes": ["Intravenous"],
        "marketing_status": "Active"
    },
    {
        "inn": "Methylprednisolone",
        "search_strategy": "Methylprednisolone AND ((case report) OR (case series) OR (case study) OR (adverse effects) OR (toxicity) OR (fatal outcomes) OR (pregnancy) OR (lactation) OR (teratogenic) OR (genotoxic) OR (mutagenic) OR (abuse) OR (misuse) OR (off label use) OR (medication errors) OR (interactions) OR (overdose) OR (pediatric population) OR (elderly population) OR (lack of efficacy))",
        "is_eu_product": True,
        "territories": ["DE", "FR", "IT", "ES", "UK"],
        "dosage_forms": ["Injection", "Tablet"],
        "routes": ["Intravenous", "Oral"],
        "marketing_status": "Active"
    },
    {
        "inn": "Cisplatin",
        "search_strategy": "Cisplatin AND ((case report) OR (case series) OR (case study) OR (adverse effects) OR (toxicity) OR (fatal outcomes) OR (pregnancy) OR (lactation) OR (teratogenic) OR (genotoxic) OR (mutagenic) OR (abuse) OR (misuse) OR (off label use) OR (medication errors) OR (interactions) OR (overdose) OR (pediatric population) OR (elderly population) OR (lack of efficacy))",
        "is_eu_product": True,
        "territories": ["DE", "FR", "IT", "ES", "UK", "NL"],
        "dosage_forms": ["Injection"],
        "routes": ["Intravenous"],
        "marketing_status": "Active"
    },
    {
        "inn": "Metronidazole",
        "search_strategy": "Metronidazole AND ((case report) OR (case series) OR (case study) OR (adverse effects) OR (toxicity) OR (fatal outcomes) OR (pregnancy) OR (lactation) OR (teratogenic) OR (genotoxic) OR (mutagenic) OR (abuse) OR (misuse) OR (off label use) OR (medication errors) OR (interactions) OR (overdose) OR (pediatric population) OR (elderly population) OR (lack of efficacy))",
        "is_eu_product": True,
        "territories": ["DE", "FR", "IT", "ES", "UK"],
        "dosage_forms": ["Tablet", "Injection", "Gel"],
        "routes": ["Oral", "Intravenous", "Topical"],
        "marketing_status": "Active"
    },
    {
        "inn": "Doxorubicin",
        "search_strategy": "Doxorubicin AND ((case report) OR (case series) OR (case study) OR (adverse effects) OR (toxicity) OR (fatal outcomes) OR (pregnancy) OR (lactation) OR (teratogenic) OR (genotoxic) OR (mutagenic) OR (abuse) OR (misuse) OR (off label use) OR (medication errors) OR (interactions) OR (overdose) OR (pediatric population) OR (elderly population) OR (lack of efficacy))",
        "is_eu_product": True,
        "territories": ["DE", "FR", "IT", "ES", "UK", "NL", "BE"],
        "dosage_forms": ["Injection"],
        "routes": ["Intravenous"],
        "marketing_status": "Active"
    },
    # Additional products for comprehensive testing
    {
        "inn": "Warfarin",
        "search_strategy": "Warfarin AND ((case report) OR (case series) OR (case study))",
        "is_eu_product": False,
        "territories": ["US", "UK", "CA"],
        "dosage_forms": ["Tablet"],
        "routes": ["Oral"],
        "marketing_status": "Active"
    },
    {
        "inn": "Insulin Glargine",
        "search_strategy": "Insulin Glargine AND ((case report) OR (case series) OR (case study))",
        "is_eu_product": False,
        "territories": ["US", "UK", "DE", "FR"],
        "dosage_forms": ["Injection"],
        "routes": ["Subcutaneous"],
        "marketing_status": "Active"
    },
    {
        "inn": "Levothyroxine",
        "search_strategy": "Levothyroxine AND ((case report) OR (case series) OR (case study))",
        "is_eu_product": False,
        "territories": ["US", "UK", "CA", "AU"],
        "dosage_forms": ["Tablet"],
        "routes": ["Oral"],
        "marketing_status": "Active"
    },
    {
        "inn": "Atorvastatin",
        "search_strategy": "Atorvastatin AND ((case report) OR (case series) OR (case study))",
        "is_eu_product": False,
        "territories": ["US", "UK", "DE", "FR", "ES"],
        "dosage_forms": ["Tablet"],
        "routes": ["Oral"],
        "marketing_status": "Active"
    },
    {
        "inn": "Losartan",
        "search_strategy": "Losartan AND ((case report) OR (case series) OR (case study))",
        "is_eu_product": False,
        "territories": ["US", "UK", "CA"],
        "dosage_forms": ["Tablet"],
        "routes": ["Oral"],
        "marketing_status": "Active"
    },
]

# Synthetic article templates
ARTICLE_TEMPLATES = {
    "icsr_cannot_exclude": [
        {
            "title": "Severe Hepatotoxicity Following {drug} Administration in a 45-Year-Old Male Patient",
            "abstract": "We report a case of a 45-year-old male patient (initials J.M.) who developed severe hepatotoxicity after receiving {drug} {dose} {route}. The patient was treated by Dr. Sarah Johnson at Memorial Hospital. Laboratory findings showed elevated liver enzymes (ALT 450 U/L, AST 380 U/L) three days after initiation of therapy. The adverse event was reported to the hospital's pharmacovigilance department. The patient recovered after discontinuation of {drug} and supportive care.",
            "adverse_events": ["Hepatotoxicity", "Elevated liver enzymes"],
            "has_all_criteria": True,
            "ownership_excluded": False,
            "exclusion_reason": None
        },
        {
            "title": "Acute Kidney Injury Associated with {drug} in Elderly Patient: A Case Report",
            "abstract": "A 72-year-old female patient (ID: 2024-PV-1234) presented with acute kidney injury following treatment with {drug} {dose} {route}. The case was documented by Dr. Michael Chen, nephrologist at City General Hospital. Serum creatinine increased from 1.2 mg/dL to 3.8 mg/dL within 48 hours of drug administration. The patient required temporary dialysis. This adverse drug reaction was classified as serious and reported to regulatory authorities.",
            "adverse_events": ["Acute kidney injury", "Elevated serum creatinine"],
            "has_all_criteria": True,
            "ownership_excluded": False,
            "exclusion_reason": None
        },
        {
            "title": "Anaphylactic Reaction to {drug}: Case Report and Literature Review",
            "abstract": "We describe a case of anaphylactic reaction in a 38-year-old male (patient code: ANP-2025-087) following intravenous administration of {drug} 50mg. The reaction occurred within 15 minutes of drug administration and was managed by Dr. Emily Rodriguez in the emergency department. The patient developed urticaria, bronchospasm, and hypotension (BP 80/50 mmHg). Treatment with epinephrine, corticosteroids, and antihistamines resulted in complete recovery. This case highlights the importance of monitoring for hypersensitivity reactions.",
            "adverse_events": ["Anaphylaxis", "Urticaria", "Bronchospasm", "Hypotension"],
            "has_all_criteria": True,
            "ownership_excluded": False,
            "exclusion_reason": None
        },
    ],
    "icsr_can_exclude": [
        {
            "title": "Cardiotoxicity Following {drug} Treatment in Japanese Population",
            "abstract": "A 55-year-old male patient (initials T.K.) from Tokyo, Japan, developed cardiotoxicity after receiving {drug} manufactured by Takeda Pharmaceuticals. The patient was under the care of Dr. Hiroshi Yamamoto at Tokyo Medical Center. Echocardiography revealed reduced ejection fraction (35%) after three cycles of chemotherapy. The brand name Takeda-{drug} was confirmed from the medication records. The patient's condition improved with dose reduction and cardiac supportive therapy.",
            "adverse_events": ["Cardiotoxicity", "Reduced ejection fraction"],
            "has_all_criteria": True,
            "ownership_excluded": True,
            "exclusion_reason": "Different manufacturer (Takeda Pharmaceuticals) and territory (Japan) not covered by Hikma"
        },
        {
            "title": "Neurological Complications with Intrathecal {drug} Administration",
            "abstract": "We report a case of a 42-year-old female (patient ID: NT-2025-456) who experienced neurological complications following intrathecal administration of {drug} 10mg. The case was managed by Dr. Robert Williams, neurosurgeon at Regional Medical Center. The patient developed severe headache, confusion, and seizures 24 hours post-administration. The intrathecal route of administration is not approved for this medication.",
            "adverse_events": ["Neurological complications", "Headache", "Confusion", "Seizures"],
            "has_all_criteria": True,
            "ownership_excluded": True,
            "exclusion_reason": "Different route of administration (intrathecal) not in Hikma's approved formulations"
        },
        {
            "title": "Severe Skin Reaction to {drug} Transdermal Patch",
            "abstract": "A 60-year-old male patient (initials R.P.) developed severe contact dermatitis after application of {drug} transdermal patch. Dr. Lisa Anderson, dermatologist at Skin Care Clinic, documented the case. The patient presented with erythema, vesicles, and intense pruritus at the application site. Patch testing confirmed hypersensitivity to the adhesive component. The transdermal formulation was discontinued.",
            "adverse_events": ["Contact dermatitis", "Erythema", "Vesicles", "Pruritus"],
            "has_all_criteria": True,
            "ownership_excluded": True,
            "exclusion_reason": "Different dosage form (transdermal patch) not manufactured by Hikma"
        },
    ],
    "relevant_safety_info": [
        {
            "title": "Efficacy and Safety of {drug} in Treatment of Refractory Hypertension: A Retrospective Study",
            "abstract": "This retrospective study evaluated the efficacy and safety of {drug} in 150 patients with refractory hypertension over a 12-month period. The study was conducted at five medical centers. Mean blood pressure reduction was 18/12 mmHg. Adverse events were mild and included dizziness (12%), headache (8%), and fatigue (5%). No serious adverse events were reported. {drug} demonstrated good tolerability and efficacy in this patient population.",
            "adverse_events": ["Dizziness", "Headache", "Fatigue"],
            "has_all_criteria": False,
            "is_relevant": True,
            "justification": "Population study with safety and efficacy data useful for aggregate reporting and signal detection"
        },
        {
            "title": "Long-term Cardiovascular Outcomes with {drug} Therapy: 5-Year Follow-up Data",
            "abstract": "We present 5-year follow-up data from a cohort of 500 patients treated with {drug} for cardiovascular disease prevention. The study assessed major adverse cardiovascular events (MACE), including myocardial infarction, stroke, and cardiovascular death. MACE occurred in 8.5% of patients. Common adverse effects included myalgia (15%), gastrointestinal disturbances (10%), and elevated liver enzymes (3%). The benefit-risk profile remained favorable throughout the follow-up period.",
            "adverse_events": ["Myalgia", "Gastrointestinal disturbances", "Elevated liver enzymes"],
            "has_all_criteria": False,
            "is_relevant": True,
            "justification": "Long-term safety data from large cohort useful for periodic safety update reports"
        },
        {
            "title": "Comparative Safety Analysis of {drug} vs Alternative Therapies in Elderly Patients",
            "abstract": "This comparative study analyzed safety outcomes of {drug} versus alternative therapies in 300 elderly patients (age >65 years). The primary endpoint was incidence of adverse drug reactions. {drug} showed a favorable safety profile with lower rates of serious adverse events (4.2% vs 7.8%, p=0.03). Common adverse reactions included mild gastrointestinal symptoms and dizziness. The study supports the use of {drug} in elderly populations with appropriate monitoring.",
            "adverse_events": ["Gastrointestinal symptoms", "Dizziness"],
            "has_all_criteria": False,
            "is_relevant": True,
            "justification": "Comparative safety data in special population (elderly) relevant for risk management activities"
        },
    ],
    "irrelevant": [
        {
            "title": "Molecular Mechanisms of {drug} Action in Cell Culture Models",
            "abstract": "This study investigated the molecular mechanisms of {drug} using HeLa cell culture models. We examined the effects on cell proliferation, apoptosis pathways, and gene expression profiles. {drug} demonstrated dose-dependent cytotoxicity with IC50 of 2.5 μM. Western blot analysis revealed activation of caspase-3 and PARP cleavage. Gene expression analysis identified 150 differentially expressed genes. These findings provide insights into the cellular mechanisms of {drug} action.",
            "adverse_events": [],
            "has_all_criteria": False,
            "is_relevant": False,
            "justification": "Laboratory study using cell culture models - no human safety data"
        },
        {
            "title": "Pharmacokinetic Study of {drug} in Rat Models",
            "abstract": "The pharmacokinetic properties of {drug} were evaluated in male Wistar rats (n=24). Animals received single doses of 10, 25, or 50 mg/kg via oral gavage. Blood samples were collected at multiple time points over 24 hours. Plasma concentrations were measured using HPLC-MS/MS. The mean Cmax, Tmax, and AUC values were determined. The elimination half-life was approximately 4.2 hours. These preclinical data support further development of {drug}.",
            "adverse_events": [],
            "has_all_criteria": False,
            "is_relevant": False,
            "justification": "Animal study - preclinical pharmacokinetic data not relevant for human pharmacovigilance"
        },
        {
            "title": "Cost-Effectiveness Analysis of {drug} for Treatment of Chronic Disease",
            "abstract": "This economic evaluation assessed the cost-effectiveness of {drug} compared to standard therapy for chronic disease management. A Markov model was constructed using published efficacy data and local cost data. The incremental cost-effectiveness ratio (ICER) was calculated. {drug} demonstrated an ICER of $45,000 per quality-adjusted life year (QALY). Sensitivity analyses confirmed robustness of results. {drug} represents good value for money in this indication.",
            "adverse_events": [],
            "has_all_criteria": False,
            "is_relevant": False,
            "justification": "Health economics study - no safety or clinical data relevant for pharmacovigilance"
        },
        {
            "title": "Environmental Impact Assessment of {drug} Manufacturing Processes",
            "abstract": "This study evaluated the environmental impact of {drug} manufacturing, including waste generation, water consumption, and carbon emissions. Life cycle assessment methodology was applied. The manufacturing process generated 2.5 kg CO2 equivalent per gram of active pharmaceutical ingredient. Recommendations for reducing environmental footprint include solvent recycling and energy efficiency improvements. Sustainable manufacturing practices are essential for pharmaceutical industry.",
            "adverse_events": [],
            "has_all_criteria": False,
            "is_relevant": False,
            "justification": "Environmental study - not related to drug safety or adverse events"
        },
        {
            "title": "Survey of Patient Satisfaction with {drug} Therapy",
            "abstract": "A cross-sectional survey assessed patient satisfaction with {drug} therapy among 200 outpatients. A validated questionnaire measured treatment satisfaction, quality of life, and adherence. Overall satisfaction score was 7.8/10. Factors associated with higher satisfaction included fewer daily doses and perceived efficacy. Patient education and shared decision-making improved adherence rates. These findings can inform strategies to optimize patient experience with {drug} therapy.",
            "adverse_events": [],
            "has_all_criteria": False,
            "is_relevant": False,
            "justification": "Patient satisfaction survey - no specific adverse event or safety data"
        },
    ],
}

def generate_pmid():
    """Generate realistic PMID"""
    return random.randint(40000000, 41000000)

def generate_doi():
    """Generate realistic DOI"""
    prefix = "10." + str(random.randint(1000, 9999))
    suffix = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))
    return f"{prefix}/{suffix}"

def generate_authors(num_authors=None):
    """Generate author list"""
    first_names = ["John", "Sarah", "Michael", "Emily", "David", "Lisa", "Robert", "Jennifer", "William", "Mary"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    
    if num_authors is None:
        num_authors = random.randint(2, 6)
    
    authors = []
    for _ in range(num_authors):
        first = random.choice(first_names)
        last = random.choice(last_names)
        authors.append(f"{last} {first[0]}")
    
    return "; ".join(authors)

def generate_journal():
    """Generate journal name"""
    journals = [
        "Journal of Clinical Pharmacology",
        "British Journal of Clinical Pharmacology",
        "Clinical Pharmacology & Therapeutics",
        "European Journal of Clinical Pharmacology",
        "Pharmacotherapy",
        "American Journal of Medicine",
        "Internal Medicine",
        "Journal of Medical Case Reports",
        "BMC Pharmacology and Toxicology",
        "Drug Safety",
    ]
    return random.choice(journals)

def generate_citation(authors, journal, year):
    """Generate citation"""
    first_author = authors.split(";")[0].strip()
    volume = random.randint(10, 150)
    issue = random.randint(1, 12)
    pages = f"{random.randint(100, 999)}-{random.randint(100, 999)}"
    return f"{first_author} et al. {journal}. {year};{volume}({issue}):{pages}."

def get_dose_and_route(product):
    """Get appropriate dose and route for product"""
    dosage_form = random.choice(product["dosage_forms"])
    route = random.choice(product["routes"])
    
    if "Injection" in dosage_form:
        doses = ["50mg", "100mg", "250mg", "500mg", "1g"]
    elif "Tablet" in dosage_form or "Capsule" in dosage_form:
        doses = ["5mg", "10mg", "20mg", "40mg", "80mg"]
    else:
        doses = ["as prescribed"]
    
    return random.choice(doses), route

def generate_articles(products, num_articles=100):
    """Generate synthetic articles"""
    articles = []
    article_id = 1
    
    # Ensure we have examples of each type
    categories = [
        ("icsr_cannot_exclude", 30),  # 30% ICSRs that cannot be excluded
        ("icsr_can_exclude", 20),      # 20% ICSRs that can be excluded
        ("relevant_safety_info", 25),  # 25% relevant safety information
        ("irrelevant", 25),             # 25% irrelevant articles
    ]
    
    for category, percentage in categories:
        num_in_category = int(num_articles * percentage / 100)
        templates = ARTICLE_TEMPLATES[category]
        
        for _ in range(num_in_category):
            product = random.choice(products)
            template = random.choice(templates)
            dose, route = get_dose_and_route(product)
            
            # Fill in template
            title = template["title"].format(drug=product["inn"])
            abstract = template["abstract"].format(
                drug=product["inn"],
                dose=dose,
                route=route.lower()
            )
            
            # Generate metadata
            authors = generate_authors()
            journal = generate_journal()
            year = random.choice([2024, 2025])
            create_date = datetime(year, random.randint(1, 12), random.randint(1, 28))
            
            article = {
                "id": article_id,
                "pmid": generate_pmid(),
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "first_author": authors.split(";")[0].strip(),
                "journal": journal,
                "publication_year": year,
                "create_date": create_date.strftime("%Y-%m-%d"),
                "pmcid": f"PMC{random.randint(1000000, 9999999)}" if random.random() > 0.5 else "",
                "doi": generate_doi(),
                "citation": generate_citation(authors, journal, year),
                "product_inn": product["inn"],
                "product_id": products.index(product) + 1,
                "category": category,
                "adverse_events": template["adverse_events"],
                "has_all_icsr_criteria": template["has_all_criteria"],
                "ownership_excluded": template.get("ownership_excluded", None),
                "exclusion_reason": template.get("exclusion_reason", None),
                "is_relevant_safety_info": template.get("is_relevant", None),
                "justification": template.get("justification", ""),
            }
            
            articles.append(article)
            article_id += 1
    
    return articles

def create_tracker_format(articles, week_number="XX"):
    """Create Excel tracker format matching the sample"""
    tracker_data = []
    
    search_date = datetime.now().strftime("%Y-%m-%d")
    period_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    period_to = datetime.now().strftime("%Y-%m-%d")
    
    for article in articles:
        # Determine ICSR status
        if article["category"] in ["icsr_cannot_exclude", "icsr_can_exclude"]:
            icsr_status = "Y"
            icsr_desc = ", ".join(article["adverse_events"])
        else:
            icsr_status = "N"
            icsr_desc = ""
        
        # Determine ownership exclusion
        if article["category"] == "icsr_can_exclude":
            ownership_excluded = "Y"
            exclusion_reason = article["exclusion_reason"]
        elif article["category"] == "icsr_cannot_exclude":
            ownership_excluded = "N"
            exclusion_reason = ""
        else:
            ownership_excluded = ""
            exclusion_reason = ""
        
        # Determine other safety info
        if article["category"] == "relevant_safety_info":
            other_safety_info = "Y"
            safety_justification = article["justification"]
        elif article["category"] == "irrelevant":
            other_safety_info = "N"
            safety_justification = article["justification"]
        else:
            other_safety_info = "Y" if icsr_status == "Y" else ""
            safety_justification = "ICSR" if icsr_status == "Y" else ""
        
        row = {
            "INN": article["product_inn"],
            "Date of search": search_date,
            "Search period (From)": period_from,
            "Search period (To)": period_to,
            "Search strategy": f"{article['product_inn']} AND ((case report) OR (case series))",
            "Number of results": 1,
            "PMID*": article["pmid"],
            "Title*": article["title"],
            "Authors*": article["authors"],
            "Citation*": article["citation"],
            "First Author*": article["first_author"],
            "Journal/ Book*": article["journal"],
            "Publication Year*": article["publication_year"],
            "Create Date*": article["create_date"],
            "PMCID*": article["pmcid"],
            "NIHMS ID*": "",
            "DOI*": article["doi"],
            "ICSR (Y/N/NA)": icsr_status,
            "ICSR description (if applicable)": icsr_desc,
            "Hikma ownership can be excluded (Y/N/NA)": ownership_excluded,
            "Reason for exclusion (if applicable)": exclusion_reason,
            "ICSR is a duplicate (Y/N/NA)": "N" if icsr_status == "Y" else "",
            "Minimum criteria for reporting available? (Y/N/NA)": "Y" if article["category"] == "icsr_cannot_exclude" else "",
            "Full article available (Y/N/NA)": "Y" if icsr_status == "Y" else "",
            "Date reference sent to PV Operations (if applicable)": "",
            "Date article ordered (if applicable)": "",
            "Date article sent to PV Operations (if applicable)": "",
            "ICSR code (if applicable)": "",
            "Other safety information (Y/N/NA)": other_safety_info,
            "Justification for answer in column AC": safety_justification,
            "Conducted by": "System",
            "Qc'd by": "",
            "Comments": "",
        }
        
        tracker_data.append(row)
    
    return pd.DataFrame(tracker_data)

def main():
    """Main function to generate all synthetic data"""
    print("Generating synthetic data for Pharmacovigilance Literature Monitoring PoC...")
    
    # Generate products
    print(f"\n1. Generating {len(PRODUCTS)} products...")
    products_df = pd.DataFrame(PRODUCTS)
    products_df["id"] = range(1, len(PRODUCTS) + 1)
    products_df.to_csv("/home/ubuntu/pharma_pv_poc/synthetic_data/products.csv", index=False)
    products_df.to_json("/home/ubuntu/pharma_pv_poc/synthetic_data/products.json", orient="records", indent=2)
    print(f"   ✓ Saved products.csv and products.json")
    
    # Generate articles
    num_articles = 100
    print(f"\n2. Generating {num_articles} synthetic articles...")
    articles = generate_articles(PRODUCTS, num_articles)
    articles_df = pd.DataFrame(articles)
    articles_df.to_csv("/home/ubuntu/pharma_pv_poc/synthetic_data/articles.csv", index=False)
    articles_df.to_json("/home/ubuntu/pharma_pv_poc/synthetic_data/articles.json", orient="records", indent=2)
    print(f"   ✓ Saved articles.csv and articles.json")
    
    # Generate tracker format
    print(f"\n3. Generating Excel tracker format...")
    tracker_df = create_tracker_format(articles)
    
    # Create Excel with multiple sheets
    with pd.ExcelWriter("/home/ubuntu/pharma_pv_poc/synthetic_data/synthetic_tracker.xlsx", engine="openpyxl") as writer:
        tracker_df.to_excel(writer, sheet_name="Week XX", index=False)
        
        # Create legends sheet
        legends_data = {
            "Column": ["INN", "ICSR (Y/N/NA)", "ICSR description", "Hikma ownership can be excluded", 
                       "Other safety information (Y/N/NA)"],
            "Description": [
                "International Nonproprietary Name - Generic drug name",
                "Whether article contains Individual Case Safety Report with all 4 criteria",
                "Description of adverse events identified in the ICSR",
                "Whether Hikma's ownership can be excluded based on territory, dosage form, brand, etc.",
                "Whether article contains other valuable safety information for aggregate reporting"
            ]
        }
        legends_df = pd.DataFrame(legends_data)
        legends_df.to_excel(writer, sheet_name="Legends", index=False)
    
    print(f"   ✓ Saved synthetic_tracker.xlsx with Week XX and Legends sheets")
    
    # Generate statistics
    print(f"\n4. Generating statistics...")
    stats = {
        "total_articles": len(articles),
        "icsr_cannot_exclude": len([a for a in articles if a["category"] == "icsr_cannot_exclude"]),
        "icsr_can_exclude": len([a for a in articles if a["category"] == "icsr_can_exclude"]),
        "relevant_safety_info": len([a for a in articles if a["category"] == "relevant_safety_info"]),
        "irrelevant": len([a for a in articles if a["category"] == "irrelevant"]),
        "products_covered": len(set([a["product_inn"] for a in articles])),
        "eu_products": len([p for p in PRODUCTS if p["is_eu_product"]]),
        "non_eu_products": len([p for p in PRODUCTS if not p["is_eu_product"]]),
    }
    
    with open("/home/ubuntu/pharma_pv_poc/synthetic_data/statistics.json", "w") as f:
        json.dump(stats, f, indent=2)
    
    print(f"\n   Statistics:")
    print(f"   - Total articles: {stats['total_articles']}")
    print(f"   - ICSRs (cannot exclude): {stats['icsr_cannot_exclude']}")
    print(f"   - ICSRs (can exclude): {stats['icsr_can_exclude']}")
    print(f"   - Relevant safety info: {stats['relevant_safety_info']}")
    print(f"   - Irrelevant: {stats['irrelevant']}")
    print(f"   - Products covered: {stats['products_covered']}")
    print(f"   - EU products: {stats['eu_products']}")
    print(f"   - Non-EU products: {stats['non_eu_products']}")
    
    print(f"\n✓ Synthetic data generation complete!")
    print(f"\nGenerated files:")
    print(f"   - products.csv / products.json")
    print(f"   - articles.csv / articles.json")
    print(f"   - synthetic_tracker.xlsx")
    print(f"   - statistics.json")

if __name__ == "__main__":
    main()

