"""
AI service for ICSR detection and article classification using OpenAI
"""
import json
import logging
from typing import Dict, Optional
from openai import OpenAI
import httpx

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a pharmacovigilance expert analyzing medical literature for Individual Case Safety Reports (ICSRs) and adverse drug reactions. 
Your task is to understand the article abstract and analyze it and determine if it is an ICSR or not based on the analysis requirements below.
[The article is provided in the user prompt as `Title` and `Abstract`.]

ANALYSIS REQUIREMENTS:

1. ICSR DETECTION
An Individual Case Safety Report (ICSR) must contain ALL FOUR of these criteria:
a) Identifiable patient (age, gender, initials, patient ID, case number, etc.)
b) Identifiable reporter (physician name, healthcare professional, institution, contact info)
c) Suspected drug or product (specific medication name, brand, dosage, route of administration)
d) Adverse reaction (specific side effect, adverse event, or safety concern)

2. ADVERSE EVENTS EXTRACTION
If adverse events are mentioned, extract them as a list with specific details.

3. OWNERSHIP EXCLUSION ANALYSIS
If this is an ICSR, determine if Hikma's ownership can be excluded based on:
- Different manufacturer/brand name mentioned
- Territory not in approved list
- Different dosage form than approved
- Different route of administration
- Batch number from another manufacturer

4. SAFETY INFORMATION CLASSIFICATION
For non-ICSR articles, classify as:
- Relevant: Clinical efficacy data, population studies, treatment outcomes, aggregate safety data
- Irrelevant: Animal studies, in-vitro/lab studies, environmental studies, cost-effectiveness, surveys, study protocols

RESPONSE FORMAT (JSON):
{{
"is_icsr": boolean,
"criteria_present": {{
    "identifiable_patient": boolean,
    "identifiable_reporter": boolean,
    "suspected_drug": boolean,
    "adverse_reaction": boolean
}},
"criteria_evidence": {{
    "patient_info": "quote or description",
    "reporter_info": "quote or description",
    "drug_info": "quote or description",
    "reaction_info": "quote or description"
}},
"adverse_events": ["event1", "event2", ...],
"icsr_description": "brief description of the ICSR if applicable",
"ownership_analysis": {{
    "can_exclude": boolean,
    "exclusion_reason": "reason if can exclude, otherwise empty string",
    "territory_mentioned": "country/territory if mentioned",
    "brand_mentioned": "brand name if mentioned",
    "dosage_form_mentioned": "dosage form if mentioned"
}},
"safety_classification": {{
    "has_relevant_safety_info": boolean,
    "justification": "explanation for classification"
}},
"minimum_criteria_available": boolean,
"reasoning": "brief explanation of the analysis"
}}

Provide your ICSR analysis in the JSON format specified above.
"""


class AIService:
    """Service for AI-powered article analysis"""
    
    def __init__(self, api_key: str, model: str = "gpt-4.1-mini"):
        """
        Initialize AI service
        
        Args:
            api_key: OpenAI API key
            model: Model to use for analysis
        """
        # Create httpx client with trust_env=False to disable proxy auto-detection
        if api_key:
            http_client = httpx.Client(trust_env=False)
            self.client = OpenAI(api_key=api_key, http_client=http_client)
        else:
            self.client = None
        self.model = model
    
    def _build_analysis_prompt(
        self,
        title: str,
        abstract: str,
        product_name: str,
        product_territories: list = None,
        product_dosage_forms: list = None
    ) -> str:
        """Build analysis prompt"""
        
        territories_str = ", ".join(product_territories) if product_territories else "Not specified"
        dosage_forms_str = ", ".join(product_dosage_forms) if product_dosage_forms else "Not specified"
        
        prompt = f"""Analyze the following medical article for determining ICSR.
            ARTICLE INFORMATION:
            Title: {title}
            Abstract: {abstract}

            PRODUCT INFORMATION:
            Product Name (INN): {product_name}
            Approved Territories: {territories_str}
            Approved Dosage Forms: {dosage_forms_str}
        """        
        return prompt
    
    def _calculate_confidence(self, analysis: Dict) -> float:
        """
        Calculate confidence score based on analysis results
        
        Args:
            analysis: Analysis results dictionary
            
        Returns:
            Confidence score (0-1)
        """
        score = 0.0
        
        # Base score for clear determination
        score += 0.3
        
        # ICSR criteria clarity (40%)
        if analysis.get("is_icsr"):
            criteria = analysis.get("criteria_present", {})
            criteria_count = sum([
                criteria.get("identifiable_patient", False),
                criteria.get("identifiable_reporter", False),
                criteria.get("suspected_drug", False),
                criteria.get("adverse_reaction", False)
            ])
            score += (criteria_count / 4) * 0.4
        else:
            # For non-ICSR, check if classification is clear
            safety_class = analysis.get("safety_classification", {})
            if safety_class.get("justification"):
                score += 0.4
        
        # Evidence quality (20%)
        evidence = analysis.get("criteria_evidence", {})
        evidence_count = sum([
            1 for v in evidence.values()
            if v and len(str(v)) > 10
        ])
        score += (evidence_count / 4) * 0.2
        
        # Reasoning quality (10%)
        reasoning = analysis.get("reasoning", "")
        if reasoning and len(reasoning) > 20:
            score += 0.1
        
        return min(score, 1.0)
    
    def test_connection(self) -> bool:
        """
        Test OpenAI API connection
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.client:
            return False
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Test"}
                ],
                max_tokens=5
            )
            return bool(response.choices)
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {str(e)}")
            return False
    
    def analyze_article(
        self,
        title: str,
        abstract: str,
        product_name: str,
        product_territories: list = None,
        product_dosage_forms: list = None
    ) -> Optional[Dict]:
        """
        Analyze article for ICSR criteria and safety information
        
        Args:
            title: Article title
            abstract: Article abstract
            product_name: Product/INN name
            product_territories: List of territories where product is marketed
            product_dosage_forms: List of approved dosage forms
            
        Returns:
            Dictionary with analysis results
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return None
        
        try:
            prompt = self._build_analysis_prompt(
                title,
                abstract,
                product_name,
                product_territories,
                product_dosage_forms
            )
            
            logger.info(f"Analyzing article: {title[:50]}...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        # "content": "You are a pharmacovigilance expert analyzing medical literature for Individual Case Safety Reports (ICSRs) and adverse drug reactions. You must respond with valid JSON only."
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            # print("\RESULT: ", result)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(result)
            result["confidence_score"] = confidence
            
            logger.info(f"Analysis complete. ICSR: {result.get('is_icsr')}, Confidence: {confidence:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing article: {str(e)}")
            return None

