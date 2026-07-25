"""
ai4sustainablex — Template Registry
4 FREE templates + 13+ PREMIUM templates ($20 one-time unlock).
All templates require 'companyName' and 'context' variables.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from payments import get_payment_manager


@dataclass
class ReportTemplate:
    id: str
    name: str
    category: str
    description: str
    framework: str
    is_premium: bool = False
    sections: List[str] = field(default_factory=list)
    system_prompt: str = ""
    required_fields: List[str] = field(default_factory=lambda: ["companyName", "context"])
    output_formats: List[str] = field(default_factory=lambda: ["markdown", "pdf", "docx"])


class TemplateRegistry:
    """
    4 FREE templates (always available):
      - esg-report-basic, ghg-emissions, sustainability-brief, sme-readiness

    13+ PREMIUM templates (require $20 payment key):
      - carbon-footprint, compliance-checklist, gri-full-report, sbcds-targets,
        cdp-disclosure, ifrs-s1-s2, csrd-esrs, csddd-due-diligence, afolu-flag-redd,
        africa-climate-gender, brsr-report, brsr-core-assurance, sme-brsr-lite,
        supply-chain-due-diligence, social-media-post, newsletter, stakeholder-disclosure
    """

    def __init__(self):
        self._templates: Dict[str, ReportTemplate] = {}
        self._register_all()

    def _register_all(self) -> None:
        # ─── FREE (4) ────────────────────────────────────────
        self._register_free()
        # ─── PREMIUM (13+) ────────────────────────────────────
        self._register_premium()

    def _register_free(self) -> None:
        """4 FREE templates."""

        self.register(ReportTemplate(
            id="esg-report-basic",
            name="Basic ESG Report",
            category="ESG",
            description="General-purpose ESG report covering environmental, social, and governance metrics",
            framework="GRI",
            sections=[
                "Executive Summary",
                "Organizational Overview",
                "Environmental Performance (GHG, Energy, Water, Waste)",
                "Social Performance (Workforce, Diversity, Community)",
                "Governance (Board Oversight, Ethics, Risk Management)",
                "Key Performance Indicators",
                "Materiality Assessment",
                "Targets and Recommendations",
                "Appendix: Methodology",
            ],
            system_prompt=(
                "You are ai4sustainablex, an expert ESG reporting assistant. "
                "Generate a Basic ESG Report for {companyName} using the provided context. "
                "Follow GRI reporting principles. Cite source page numbers. "
                "Flag any data gaps."
            ),
        ))

        self.register(ReportTemplate(
            id="ghg-emissions",
            name="GHG Emissions Analysis",
            category="GRI",
            description="Detailed greenhouse gas emissions analysis following GRI 305",
            framework="GRI",
            sections=[
                "Executive Summary",
                "Methodology and Boundaries",
                "Scope 1: Direct Emissions",
                "Scope 2: Indirect Energy Emissions",
                "Scope 3: Value Chain Emissions",
                "Emission Intensity Ratios",
                "Year-over-Year Comparison",
                "Reduction Targets and Trajectories",
                "Verification and Assurance",
                "Recommendations",
            ],
            system_prompt=(
                "Analyze greenhouse gas emissions for {companyName} using GRI 305. "
                "For each scope, provide total tCO2e, source breakdown, methodology, and data quality. "
                "Evaluate against SBTi 1.5°C pathway. Cite page numbers."
            ),
        ))

        self.register(ReportTemplate(
            id="sustainability-brief",
            name="Sustainability Brief",
            category="General",
            description="Executive-level sustainability summary for stakeholders and board",
            framework="Multi-framework",
            sections=[
                "Key Sustainability Highlights",
                "Performance vs. Targets Dashboard",
                "Material Issues Summary",
                "Stakeholder Engagement Overview",
                "Risk and Opportunity Landscape",
                "Regulatory Compliance Status",
                "Forward-Looking Commitments",
                "Investment and Innovation",
            ],
            system_prompt=(
                "Create an executive sustainability brief for {companyName} suitable for board presentation. "
                "Keep it concise. Use bullet points and traffic-light indicators for key metrics. "
                "Highlight top 3 risks and opportunities."
            ),
        ))

        self.register(ReportTemplate(
            id="sme-readiness",
            name="SME ESG Readiness Assessment",
            category="SME",
            description="ESG readiness and gap assessment tailored for SMEs",
            framework="SME Framework",
            sections=[
                "Company Profile and Context",
                "Current ESG Practices Assessment",
                "Regulatory Requirements Mapping",
                "Data Availability and Collection Readiness",
                "Quick Wins (Low-Effort, High-Impact)",
                "Gap Analysis vs. Major Frameworks",
                "Resource Requirements (People, Tools, Budget)",
                "3-Year ESG Roadmap",
                "Recommended First Report Template",
            ],
            system_prompt=(
                "Assess ESG readiness for {companyName} as an SME. "
                "Focus on practical, low-cost steps. Identify quick wins. "
                "Map regulatory exposure based on jurisdiction. "
                "Propose a 3-year phased roadmap. Keep it actionable."
            ),
        ))

    def _register_premium(self) -> None:
        """13+ PREMIUM templates — require payment key."""

        premium = True

        # Existing premium templates
        self.register(ReportTemplate(
            id="carbon-footprint", name="Carbon Footprint Analysis", category="CDP",
            description="Comprehensive carbon footprint calculation and reduction roadmap",
            framework="CDP", is_premium=premium,
            sections=[
                "Executive Summary", "Organizational Boundary", "Emission Sources Inventory",
                "Carbon Footprint by Scope", "Intensity Metrics and Benchmarks",
                "Hot-Spot Analysis", "Reduction Opportunities Assessment",
                "Net-Zero Pathway (2030/2050)", "Carbon Offsetting Strategy", "Monitoring Plan",
            ],
            system_prompt=(
                "Generate a carbon footprint analysis for {companyName} aligned with CDP and GHG Protocol. "
                "Calculate total footprint across all scopes. Provide intensity metrics. "
                "Identify top 5 hotspots and reduction levers. Outline net-zero pathway."
            ),
        ))

        self.register(ReportTemplate(
            id="compliance-checklist", name="ESG Compliance Checklist", category="Regulatory",
            description="Regulatory compliance checklist aligned with major frameworks",
            framework="Multi-framework", is_premium=premium,
            sections=[
                "Regulatory Requirements by Jurisdiction",
                "Disclosure Requirements (GRI, SASB, TCFD, IFRS)",
                "Data Collection Status", "Gap Analysis",
                "Compliance Timeline", "Recommended Actions",
                "Documentation Requirements", "Internal Controls Assessment",
            ],
            system_prompt=(
                "Generate an ESG regulatory compliance checklist for {companyName}. "
                "Map requirements across GRI, SASB, TCFD, IFRS S1/S2, CSRD, BRSR. "
                "For each: status, evidence, timeline. Prioritize by regulatory risk."
            ),
        ))

        self.register(ReportTemplate(
            id="gri-full-report", name="GRI Standards Full Report", category="GRI",
            description="Complete sustainability report aligned with GRI Universal Standards 2021",
            framework="GRI", is_premium=premium,
            sections=[
                "GRI 2: General Disclosures", "GRI 2: Activities, Workers, Governance",
                "GRI 2: Strategy, Policies, Stakeholder Engagement", "GRI 3: Material Topics",
                "GRI 200: Economic Performance", "GRI 300: Environmental",
                "GRI 400: Social", "GRI Content Index", "Assurance Statement",
            ],
            system_prompt=(
                "Generate a full GRI Standards 2021 report for {companyName}. "
                "Follow the GRI structure exactly. Include GRI Content Index. "
                "Provide requirement reference, response, and page reference."
            ),
        ))

        self.register(ReportTemplate(
            id="sbcds-targets", name="SBTi Target Setting & Validation", category="SBTi",
            description="Science-based target setting report aligned with SBTi criteria",
            framework="SBTi", is_premium=premium,
            sections=[
                "Commitment Letter Summary", "Baseline Emissions Inventory",
                "Target Boundary and Scope", "Near-Term Targets (2030)",
                "Long-Term Net-Zero Targets (2050)", "Scope 3 Screening",
                "FLAG Target (if applicable)", "Target Ambition Assessment (1.5°C vs WB2C)",
                "Implementation Plan", "Annual Progress Tracking",
            ],
            system_prompt=(
                "Generate an SBTi target-setting report for {companyName} following SBTi Corporate Net-Zero Standard v1.2. "
                "Set near-term and long-term targets. Apply FLAG guidance if relevant."
            ),
        ))

        self.register(ReportTemplate(
            id="cdp-disclosure", name="CDP Climate Change Disclosure", category="CDP",
            description="CDP Climate Change questionnaire response and analysis",
            framework="CDP", is_premium=premium,
            sections=[
                "C1: Governance", "C2: Risks and Opportunities", "C3: Business Strategy",
                "C4: Targets and Performance", "C5: Emissions Methodology",
                "C6: Emissions Data (Scope 1,2,3)", "C7: Emissions Breakdown",
                "C8: Energy", "C9: Additional Metrics", "C10: Verification",
                "C11: Carbon Pricing", "C12: Engagement", "CDP Scoring Gap Analysis",
            ],
            system_prompt=(
                "Generate CDP Climate Change questionnaire responses for {companyName}. "
                "Follow CDP 2024 format. Identify data gaps. Estimate likely CDP score band."
            ),
        ))

        self.register(ReportTemplate(
            id="ifrs-s1-s2", name="IFRS S1 & S2 Sustainability Disclosures", category="IFRS-S1",
            description="Sustainability-related and climate-related financial disclosures per ISSB",
            framework="IFRS", is_premium=premium,
            sections=[
                "IFRS S1: Governance", "S1: Strategy", "S1: Risk Management", "S1: Metrics and Targets",
                "IFRS S2: Climate Governance", "S2: Climate Strategy and Scenario Analysis",
                "S2: Climate Risk Management", "S2: Climate Metrics (incl. GHG)",
                "Industry-Specific Metrics", "Cross-Referencing (TCFD, GRI)",
            ],
            system_prompt=(
                "Generate IFRS S1 and S2 disclosures for {companyName}. "
                "Apply climate scenario analysis (at least 2 scenarios). "
                "Provide industry-specific metrics per SASB."
            ),
        ))

        self.register(ReportTemplate(
            id="csrd-esrs", name="CSRD / ESRS Compliance Report", category="CSRD",
            description="Corporate Sustainability Reporting Directive per ESRS standards",
            framework="CSRD", is_premium=premium,
            sections=[
                "ESRS 1: General Requirements", "ESRS 2: General Disclosures",
                "ESRS E1: Climate Change", "ESRS E2: Pollution", "ESRS E3: Water",
                "ESRS E4: Biodiversity", "ESRS E5: Circular Economy",
                "ESRS S1-S4: Social", "ESRS G1: Business Conduct",
                "Double Materiality Assessment", "EU Taxonomy Alignment", "Datapoints Checklist",
            ],
            system_prompt=(
                "Generate a CSRD-compliant sustainability statement for {companyName} per ESRS. "
                "Apply double materiality. Map to EU Taxonomy. Include all Annex I datapoints."
            ),
        ))

        self.register(ReportTemplate(
            id="csddd-due-diligence", name="CSDDD Due Diligence Report", category="CSDDD",
            description="Corporate Sustainability Due Diligence Directive compliance",
            framework="CSDDD", is_premium=premium,
            sections=[
                "Due Diligence Policy", "Risk Identification: Own Operations",
                "Risk Identification: Supply Chain", "Adverse Impact Assessment",
                "Prevention and Mitigation", "Remediation Mechanisms",
                "Stakeholder Engagement", "Monitoring", "Climate Transition Plan",
            ],
            system_prompt=(
                "Generate a CSDDD due diligence report for {companyName} covering human rights "
                "and environmental impacts in operations and supply chain."
            ),
        ))

        self.register(ReportTemplate(
            id="afolu-flag-redd", name="AFOLU, FLAG & REDD+ Carbon Project Report", category="AFOLU",
            description="Agriculture, Forestry, Land Use carbon project analysis",
            framework="AFOLU", is_premium=premium,
            sections=[
                "Project Description and Location", "Baseline Scenario and Additionality",
                "Carbon Stock Assessment", "Emission Reductions Calculation",
                "FLAG Target Setting (SBTi FLAG)", "Leakage Assessment",
                "Biodiversity Co-Benefits", "Community and Livelihood Impacts",
                "Gender Equality and Social Inclusion", "REDD+ Safeguards",
                "MRV Plan", "Carbon Credit Issuance Forecast",
            ],
            system_prompt=(
                "Generate an AFOLU/FLAG/REDD+ carbon project report for {companyName} per VCS/CCB. "
                "Apply SBTi FLAG guidance. Address REDD+ safeguards. Quantify co-benefits."
            ),
        ))

        self.register(ReportTemplate(
            id="africa-climate-gender", name="Africa Climate, Gender & Livelihoods Nexus", category="Africa-Climate",
            description="Climate-gender-livelihoods analysis for African sub-continents with carbon opportunity",
            framework="Multi-framework", is_premium=premium,
            sections=[
                "Executive Summary: The Carbon Opportunity in Africa",
                "Regional Context", "Climate Vulnerability Assessment",
                "Gender Analysis: Differential Impacts", "Livelihoods Baseline",
                "Degraded Lands Restoration Potential", "AR Project Pipeline",
                "REDD+ Readiness", "AFOLU Emission Reduction Potential",
                "FLAG-Compliant Carbon Projects", "Community Benefit Sharing",
                "Gender-Responsive Carbon Finance", "Carbon as Livelihood Elevation Tool",
                "Policy Landscape", "Investment Roadmap", "Gender-Disaggregated Monitoring",
            ],
            system_prompt=(
                "Generate a climate-gender-livelihoods nexus report for {companyName}. "
                "Focus on carbon as opportunity to elevate communities through AR, REDD+, AFOLU/FLAG. "
                "Apply gender-responsive lens. Design benefit-sharing mechanisms."
            ),
        ))

        self.register(ReportTemplate(
            id="brsr-report", name="BRSR Comprehensive Report (India)", category="BRSR",
            description="Business Responsibility and Sustainability Reporting per SEBI BRSR",
            framework="BRSR", is_premium=premium,
            sections=[
                "Section A: General Disclosures", "Section B: Management and Process Disclosures",
                "Section C: P1 Ethics & Transparency", "P2 Product Lifecycle",
                "P3 Employee Wellbeing", "P4 Stakeholder Engagement", "P5 Human Rights",
                "P6 Environment", "P7 Policy Advocacy", "P8 Inclusive Growth", "P9 Customer Value",
                "BRSR Core (Assurance Ready)", "BRSR Lite (SMEs)",
            ],
            system_prompt=(
                "Generate a BRSR report for {companyName} per SEBI format 2023. "
                "Complete all 9 principles. Provide intensity ratios. Map to GRI/SASB/TCFD."
            ),
        ))

        # ─── NEW Premium Templates ────────────────────────────

        self.register(ReportTemplate(
            id="brsr-core-assurance", name="BRSR Core Assurance", category="BRSR",
            description="BRSR Core KPIs with assurance-ready formatting",
            framework="BRSR", is_premium=premium,
            sections=[
                "BRSR Core KPIs Overview", "Environmental KPIs (Energy, Emissions, Water, Waste)",
                "Social KPIs (Employee, Health & Safety, Training)",
                "Governance KPIs (Board, Complaints, Cyber Security)",
                "Intensity Ratios (per INR of Turnover)",
                "Data Sources and Calculation Methodology",
                "Assurance Readiness Checklist", "External Auditor Handover Notes",
            ],
            system_prompt=(
                "Generate BRSR Core KPIs for {companyName}. Format for assurance readiness. "
                "Include calculation methodology. Provide intensity ratios per INR turnover."
            ),
        ))

        self.register(ReportTemplate(
            id="sme-brsr-lite", name="BRSR Lite for SMEs", category="SME",
            description="Simplified BRSR Lite format for small and medium enterprises",
            framework="BRSR", is_premium=premium,
            sections=[
                "Company Overview", "BRSR Lite Disclosures",
                "Environmental Indicators (Simplified)", "Social Indicators (Simplified)",
                "Governance Indicators", "Compliance Status", "Next Steps for BRSR Core",
            ],
            system_prompt=(
                "Generate a BRSR Lite report for {companyName}. Keep it simplified per SEBI format for SMEs. "
                "Provide a clear path to BRSR Core readiness."
            ),
        ))

        self.register(ReportTemplate(
            id="supply-chain-due-diligence", name="Supply Chain Due Diligence", category="CSDDD",
            description="Supply chain ESG due diligence and risk mapping",
            framework="CSDDD", is_premium=premium,
            sections=[
                "Supply Chain Mapping (Tier 1, 2, 3)",
                "Risk Hotspot Identification by Country/Sector",
                "Human Rights Risk Assessment",
                "Environmental Risk Assessment",
                "Supplier Code of Conduct Alignment",
                "Audit and Monitoring Framework",
                "Corrective Action Plan Template",
                "Reporting and Disclosure Requirements",
            ],
            system_prompt=(
                "Generate a supply chain due diligence report for {companyName}. "
                "Map supply chain tiers. Identify high-risk suppliers. "
                "Provide audit framework and corrective action templates."
            ),
        ))

        # ─── Task-Based Templates ─────────────────────────────

        self.register(ReportTemplate(
            id="social-media-post", name="Social Media ESG Post", category="Task",
            description="Generate an ESG/sustainability social media post for LinkedIn/Twitter",
            framework="Multi-framework", is_premium=premium,
            sections=[
                "Post Content (LinkedIn format, 150-200 words)",
                "Key Statistics to Highlight",
                "Hashtags (5-7 relevant)",
                "Image/Graphic Suggestions",
                "Alternative Versions (Twitter/X, Instagram)",
            ],
            system_prompt=(
                "Create a compelling social media post about {companyName}'s ESG/sustainability achievements. "
                "Use the provided context for facts and figures. Format for LinkedIn. "
                "Include relevant hashtags. Suggest visual elements."
            ),
            output_formats=["markdown"],
        ))

        self.register(ReportTemplate(
            id="newsletter", name="ESG Newsletter", category="Task",
            description="Generate an ESG/sustainability newsletter for stakeholders",
            framework="Multi-framework", is_premium=premium,
            sections=[
                "Header and Introduction",
                "Key Achievement Spotlight",
                "Data Snapshot (2-3 key metrics with graphs description)",
                "Upcoming Initiatives",
                "Stakeholder Spotlight",
                "Regulatory Update (1-2 relevant changes)",
                "Call to Action",
                "Footer with Contact and Links",
            ],
            system_prompt=(
                "Generate an ESG newsletter for {companyName}. Use the context for current metrics. "
                "Make it engaging for stakeholders. Include data visual descriptions. "
                "Keep it professional yet accessible."
            ),
            output_formats=["markdown"],
        ))

        self.register(ReportTemplate(
            id="stakeholder-disclosure", name="Stakeholder Disclosure", category="Task",
            description="Formal stakeholder disclosure document for investors/regulators",
            framework="Multi-framework", is_premium=premium,
            sections=[
                "Disclosure Statement Header", "Entity and Reporting Period",
                "Sustainability Governance", "Material Topics and Metrics",
                "Climate-Related Disclosures (TCFD-aligned)",
                "Social and Human Capital",
                "Risk Management and Internal Controls",
                "Forward-Looking Statements",
                "Assurance and External Review Status",
                "Contact for Inquiries",
            ],
            system_prompt=(
                "Generate a formal stakeholder disclosure document for {companyName}. "
                "Use formal, regulatory-grade language. Align with TCFD and IFRS S1 requirements. "
                "Include appropriate disclaimers. Ensure all claims are sourced from context."
            ),
            output_formats=["markdown", "pdf"],
        ))

    # ─── Registry Methods ──────────────────────────────────

    def register(self, template: ReportTemplate) -> None:
        self._templates[template.id] = template

    def get(self, template_id: str) -> Optional[ReportTemplate]:
        return self._templates.get(template_id)

    def is_accessible(self, template_id: str) -> bool:
        """Check if the user can access this template (free or premium unlocked)."""
        tmpl = self._templates.get(template_id)
        if tmpl is None:
            return False
        if not tmpl.is_premium:
            return True
        return get_payment_manager().is_unlocked()

    def list_all(self, premium_only: bool = False, free_only: bool = False,
                 category: Optional[str] = None,
                 show_locked: bool = True) -> List[Dict[str, Any]]:
        """List templates with access info."""
        unlocked = get_payment_manager().is_unlocked()
        result = []
        for tmpl in self._templates.values():
            if premium_only and not tmpl.is_premium:
                continue
            if free_only and tmpl.is_premium:
                continue
            if category and tmpl.category.lower() != category.lower():
                if category not in tmpl.id and category not in tmpl.framework:
                    continue

            accessible = self.is_accessible(tmpl.id) if show_locked else True

            result.append({
                "id": tmpl.id, "name": tmpl.name, "category": tmpl.category,
                "framework": tmpl.framework, "description": tmpl.description,
                "is_premium": tmpl.is_premium, "accessible": accessible,
                "locked": tmpl.is_premium and not unlocked,
                "sections_count": len(tmpl.sections),
                "output_formats": tmpl.output_formats,
                "required_fields": tmpl.required_fields,
            })
        return result

    def search(self, query: str) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        unlocked = get_payment_manager().is_unlocked()
        results = []
        for tmpl in self._templates.values():
            if (query_lower in tmpl.name.lower()
                    or query_lower in tmpl.description.lower()
                    or query_lower in tmpl.framework.lower()
                    or query_lower in tmpl.category.lower()):
                results.append({
                    "id": tmpl.id, "name": tmpl.name, "category": tmpl.category,
                    "framework": tmpl.framework, "description": tmpl.description,
                    "is_premium": tmpl.is_premium,
                    "accessible": self.is_accessible(tmpl.id),
                })
        return results

    def get_categories(self) -> List[str]:
        return sorted(set(t.category for t in self._templates.values()))

    def count(self) -> Dict[str, int]:
        free = sum(1 for t in self._templates.values() if not t.is_premium)
        premium = sum(1 for t in self._templates.values() if t.is_premium)
        unlocked = get_payment_manager().is_unlocked()
        return {
            "total": free + premium, "free": free, "premium": premium,
            "accessible": free + (premium if unlocked else 0),
            "premium_locked": 0 if unlocked else premium,
        }


_registry: Optional[TemplateRegistry] = None


def get_template_registry() -> TemplateRegistry:
    global _registry
    if _registry is None:
        _registry = TemplateRegistry()
    return _registry