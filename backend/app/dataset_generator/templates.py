"""
backend/app/dataset_generator/templates.py — Domain Templates & Prompt Seeds.

Provides structured prompt templates and domain seeds for generating scientific reasoning records.
"""

from typing import Any, Dict


DOMAIN_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "Agriculture": {
        "context": "Soil moisture and crop yield telemetry collected across 500 agricultural test plots.",
        "observation": "Unexpected 14% drop in crop yield despite optimal nitrogen fertilizer application.",
        "identified_problem": "Micro-nutrient imbalance (Zinc deficiency) inhibiting nitrogen absorption.",
        "research_gap": "Lack of real-time multi-spectral soil mineral interaction modeling.",
        "primary_hypothesis": "Foliar application of chelated zinc will restore nitrogen uptake and increase yield by >= 10%.",
        "alternative_hypothesis": "Soil compaction is restricting root growth independently of mineral availability.",
        "experiment_design": "Split-plot randomized control trial applying 2.5 kg/ha chelated zinc vs baseline control.",
        "control_variables": ["Nitrogen application rate", "Irrigation volume", "Solar radiation"],
        "evaluation_metrics": ["yield_per_hectare", "leaf_zinc_concentration", "nitrogen_use_efficiency"],
        "expected_result": "Leaf zinc concentration increases above 25 ppm, boosting crop yield by 12%.",
        "failure_cases": ["Heavy rainfall leaching foliar spray", "Soil pH below 5.5 locking zinc availability"],
        "scientific_conclusion": "Zinc supplementation resolves micronutrient bottleneck and maximizes nitrogen fertilizer efficiency.",
    },
    "Medicine": {
        "context": "Phase II clinical trial data evaluating biomarker responses in targeted immunotherapy.",
        "observation": "30% non-responder rate despite positive target receptor expression.",
        "identified_problem": "Secondary pathway activation conferring treatment resistance.",
        "research_gap": "Unmapped cross-talk mechanisms between receptor tyrosine kinases.",
        "primary_hypothesis": "Dual pathway inhibition will restore drug sensitivity and reduce tumor volume by >= 25%.",
        "alternative_hypothesis": "Efflux transporter upregulation is clearing the therapeutic payload prematurely.",
        "experiment_design": "In vitro patient-derived organoid assay testing monotherapy vs dual inhibitor combination.",
        "control_variables": ["Cell line passage number", "Baseline drug concentration", "Incubation temperature"],
        "evaluation_metrics": ["tumor_cell_viability", "pathway_phosphorylation_ratio", "apoptosis_rate"],
        "expected_result": "Dual inhibition achieves >80% pathway suppression and 30% reduction in cell viability.",
        "failure_cases": ["Off-target cytotoxicity at synergistic concentrations", "Alternative ligand overexpression"],
        "scientific_conclusion": "Combination therapy overcomes primary resistance mechanism in non-responder cohort.",
    },
    "Climate Science": {
        "context": "Satellite ocean surface temperature and dissolved oxygen sensor readings from 2020-2025.",
        "observation": "Accelerated oxygen depletion in coastal upwelling zones exceeding global climate model predictions.",
        "identified_problem": "Thermal stratification reducing vertical ocean mixing.",
        "research_gap": "Underrepresented sub-mesoscale eddy dynamics in coupled climate models.",
        "primary_hypothesis": "Incorporating sub-mesoscale eddy parameterization will reduce oxygen forecasting bias by >= 40%.",
        "alternative_hypothesis": "Agricultural runoff induced eutrophication is the primary driver of oxygen loss.",
        "experiment_design": "High-resolution regional ocean modeling system simulation comparing hydrostatic vs non-hydrostatic dynamics.",
        "control_variables": ["Surface wind stress", "Solar irradiance", "Initial boundary salinity"],
        "evaluation_metrics": ["rmse_dissolved_oxygen", "mixed_layer_depth_error", "stratification_index"],
        "expected_result": "Model forecast RMSE drops from 1.8 mg/L to 0.9 mg/L against in-situ sensor data.",
        "failure_cases": ["Unresolved boundary current instability", "Non-linear biological consumption spikes"],
        "scientific_conclusion": "Sub-mesoscale turbulence parameterization is essential for accurate coastal hypoxic zone predictions.",
    },
    "Default": {
        "context": "General scientific experimental observations and quantitative dataset metrics.",
        "observation": "Anomalous variance observed in primary evaluation metric during baseline control trials.",
        "identified_problem": "Uncontrolled confounding variable affecting measurement precision.",
        "research_gap": "Uncertainty in systematic measurement error bounds under variable environmental conditions.",
        "primary_hypothesis": "Implementing automated calibration feedback loops will reduce measurement error variance by >= 20%.",
        "alternative_hypothesis": "Sensor drift occurs independently of environmental conditions.",
        "experiment_design": "Controlled factorial experiment comparing static calibration vs dynamic feedback calibration.",
        "control_variables": ["Sample temperature", "Ambient humidity", "Input voltage"],
        "evaluation_metrics": ["measurement_variance", "signal_to_noise_ratio", "calibration_drift_rate"],
        "expected_result": "Signal-to-noise ratio improves by 3.5 dB with dynamic feedback calibration.",
        "failure_cases": ["Sensor saturation at extreme ranges", "Feedback loop latency exceeding sample rate"],
        "scientific_conclusion": "Dynamic calibration significantly reduces empirical measurement uncertainty.",
    },
}


def get_template_seed(domain: str) -> Dict[str, Any]:
    """
    Retrieve domain-specific prompt seed and scientific reasoning template.
    """
    normalized_domain = domain.strip().title()
    return DOMAIN_TEMPLATES.get(normalized_domain, DOMAIN_TEMPLATES["Default"])
