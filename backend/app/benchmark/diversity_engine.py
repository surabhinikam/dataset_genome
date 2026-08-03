"""
backend/app/benchmark/diversity_engine.py — Scientific & Cross-Domain Diversity Engine.

Provides deep, multi-theme research topic coverage across all 10 scientific domains:
  1. Agriculture
  2. Healthcare
  3. Climate Science
  4. Biology
  5. Chemistry
  6. Physics
  7. Mathematics
  8. Finance
  9. HR
  10. Market Analysis

Prevents repetitive output (e.g. Healthcare IL-6, Agriculture Salinity, Biology CRISPR)
by maintaining diverse pools of research topics, organisms, diseases, biomarkers,
methodologies, statistical tests, and failure modes.
"""

import random
from typing import Any, Dict, List, Optional


DOMAIN_DIVERSITY_POOLS: Dict[str, List[Dict[str, Any]]] = {
    "Agriculture": [
        {
            "topic": "Crop Drought Tolerance",
            "context": "Semi-arid agricultural basin undergoing severe summer precipitation deficits.",
            "organism": "Sorghum bicolor & Zea mays hybrids",
            "biomarker": "Proline accumulation & ABA signaling trans-factors",
            "methodology": "Drought stress phenotyping with high-throughput thermal imaging",
            "metrics": ["Yield Index", "Leaf Water Potential (MPa)", "Canopy Temperature Depression", "Root Depth Ratio"],
        },
        {
            "topic": "Soil Microbiome Nitrogen Fixation",
            "context": "Organic legumes rotated in nitrogen-depleted clay loam agricultural plots.",
            "organism": "Rhizobium leguminosarum & Cicer arietinum",
            "biomarker": "NifH gene copy abundance & nitrogenase enzyme activity",
            "methodology": "Metagenomic shotgun sequencing & acetylene reduction assay",
            "metrics": ["NifH Abundance Fold", "Acetylene Reduction Rate", "Total Soil Organic N", "Nodulation Index"],
        },
        {
            "topic": "Pest Resistance Epigenetics",
            "context": "Commercial cotton cultivars exposed to multi-generational bollworm pressure.",
            "organism": "Gossypium hirsutum & Helicoverpa zea",
            "biomarker": "DNA methylation patterns at Bt toxin receptor loci",
            "methodology": "Bisulfite sequencing and insect bioassay survival analysis",
            "metrics": ["LC50 Survival Threshold", "DNA Methylation Ratio", "Gossypol Concentration", "Larval Mortality"],
        },
        {
            "topic": "Salinity Ion Exclusion",
            "context": "Soil salinity levels increased by 3.2 dS/m in irrigated agricultural basins.",
            "organism": "Halophytic maize & Arabidopsis thaliana",
            "biomarker": "HKT1;5 transporter expression & Na+/K+ selectivity",
            "methodology": "Hydroponic salt stress trial with RNA-seq expression profiling",
            "metrics": ["Biomass Dry Weight", "Na+/K+ Selectivity Ratio", "Stomatal Conductance", "Yield Index"],
        },
    ],
    "Healthcare": [
        {
            "topic": "Oncology Targeted Immunotherapy",
            "context": "Phase III clinical trial for metastatic non-small cell lung carcinoma (NSCLC).",
            "organism": "Homo sapiens patient tumor biopsy cohort",
            "biomarker": "PD-L1 tumor proportion score & CD8+ T-cell infiltration",
            "methodology": "Multiplex immunohistochemistry & single-cell RNA sequencing",
            "metrics": ["Progression-Free Survival (PFS)", "Objective Response Rate (ORR)", "CD8+ Infiltration Density", "Hazard Ratio"],
        },
        {
            "topic": "Cardiovascular Atherosclerosis Plaque Dynamics",
            "context": "High-risk coronary artery disease cohort monitored via intravascular ultrasound.",
            "organism": "Human arterial endothelium & ApoE-/- murine models",
            "biomarker": "Circulating oxidized LDL & hs-CRP inflammation index",
            "methodology": "Intravascular ultrasound (IVUS) & transcriptomic micro-RNA profiling",
            "metrics": ["Plaque Volume Delta", "hs-CRP Concentration", "Endothelial Shear Stress", "Stent Restenosis Rate"],
        },
        {
            "topic": "Neurodegenerative Tauopathy Kinetics",
            "context": "Longitudinal cohort tracking early-stage Alzheimer's disease progression.",
            "organism": "Human CSF and transgenic amyloid/tau tauopathy models",
            "biomarker": "CSF phosphorylated-tau 181 & neurofilament light chain (NfL)",
            "methodology": "PET imaging tracer binding & ultra-sensitive Single Molecule Array (Simoa)",
            "metrics": ["Tau PET SUVr", "CSF p-tau181 Level", "MMSE Score Delta", "Cortical Thickness Loss"],
        },
        {
            "topic": "Metabolic Insulin Resistance Kinetics",
            "context": "Phase II clinical cohort tracking glucose tolerance and systemic inflammation markers.",
            "organism": "Human skeletal muscle tissue & clinical cohort",
            "biomarker": "Elevated circulating IL-6 & IRS-1 serine phosphorylation",
            "methodology": "Longitudinal serum profiling and hyperinsulinemic-euglycemic clamp assays",
            "metrics": ["M-value Glucose Disposal", "Serum IL-6 Concentration", "HOMA-IR Score", "HbA1c Delta"],
        },
    ],
    "Biology": [
        {
            "topic": "Structural Cryo-EM Proteomics",
            "context": "Resolution of multi-subunit membrane transporter complex in lipid nanodiscs.",
            "organism": "Saccharomyces cerevisiae mitochondrial transport system",
            "biomarker": "Conformational state transition rates (State A to State B)",
            "methodology": "High-resolution Cryo-EM single-particle reconstruction at 2.1 Å",
            "metrics": ["Cryo-EM Map Resolution (Å)", "Fourier Shell Correlation (FSC)", "Transport Rate Vmax", "Subunit Affinity Kd"],
        },
        {
            "topic": "Epigenetic Histone Modifications",
            "context": "Embryonic stem cell differentiation along neural progenitor lineages.",
            "organism": "Mus musculus embryonic stem cells",
            "biomarker": "H3K27me3 & H3K4me3 bivalent chromatin domain marking",
            "methodology": "CUT&Tag sequencing & high-throughput quantitative mass spectrometry",
            "metrics": ["Chromatin Peak Enrichment", "Gene Expression Fold Change", "Neural Marker Expression", "Methylation Half-Life"],
        },
        {
            "topic": "Developmental Cell Lineage Trajectories",
            "context": "Organoid morphogenesis captured during cardiac chamber specification.",
            "organism": "Human induced pluripotent stem cells (iPSCs)",
            "biomarker": "NKX2-5 & TNNT2 transcription factor activation cascades",
            "methodology": "Single-cell RNA-seq pseudotime trajectory reconstruction",
            "metrics": ["Pseudotime Trajectory Velocity", "Cardiomyocyte Differentiation %", "Beating Frequency (Hz)", "Gene Co-expression Score"],
        },
        {
            "topic": "CRISPR-Cas Off-Target Kinetics",
            "context": "Single-molecule fluorescence resonance energy transfer (smFRET) imaging.",
            "organism": "Engineered human cell lines & Cas12a variants",
            "biomarker": "Cas12a off-target cleavage rate & residence time",
            "methodology": "smFRET and high-throughput GUIDE-seq off-target profiling",
            "metrics": ["Cleavage Rate k_cleave", "Off-Target Ratio", "smFRET Efficiency E", "Target Specificity Index"],
        },
    ],
    "Climate Science": [
        {
            "topic": "Marine Aerosol Cloud Albedo Feedback",
            "context": "Satellite radiative flux observations across marine stratocumulus ocean decks.",
            "organism": "Dimethyl sulfide (DMS) producing phytoplankton communities",
            "biomarker": "Sub-micron sea spray aerosol nucleation density",
            "methodology": "Airborne cloud probe sampling & Large Eddy Simulation (LES) modeling",
            "metrics": ["Cloud Droplet Number Density", "Shortwave Radiative Forcing (W/m²)", "Albedo Delta", "Cloud Optical Depth"],
        },
        {
            "topic": "Permafrost Methane Thaw Dynamics",
            "context": "Sub-arctic thermokarst lake expansion across Siberian permafrost zones.",
            "organism": "Methanogenic archaea soil consortia",
            "biomarker": "CH4 flux rates & carbon-13 isotope fractionation ratio",
            "methodology": "Eddy covariance tower measurements & deep core microbial metagenomics",
            "metrics": ["Methane Flux (mg/m²/h)", "Delta 13C Isotope Ratio", "Active Layer Depth (cm)", "Soil Organic Carbon Loss"],
        },
        {
            "topic": "Atlantic Meridional Overturning Circulation (AMOC) Stability",
            "context": "Deep ocean mooring array tracking North Atlantic thermohaline circulation.",
            "organism": "Deep sea benthic micro-faunal proxy records",
            "biomarker": "North Atlantic Deep Water (NADW) transport volume",
            "methodology": "RAPID mooring array transport telemetry & ocean general circulation modeling",
            "metrics": ["AMOC Transport (Sverdrups)", "Subpolar Gyre Salinity", "Deep Ocean Heat Content", "Overturning Variability"],
        },
    ],
    "Chemistry": [
        {
            "topic": "MOF Photoreduction Catalysis",
            "context": "Solar-driven carbon dioxide conversion to synthetic C2 hydrocarbon fuels.",
            "organism": "Metal-organic framework (Cu-ZIF-8) porous crystals",
            "biomarker": "Interfacial Cu-N active site charge transfer lifetime",
            "methodology": "Transient absorption spectroscopy & in-situ DRIFTS reaction monitoring",
            "metrics": ["Turnover Frequency (TOF)", "Faradaic Efficiency (%)", "CO2 Conversion Rate", "Ethylene Selectivity"],
        },
        {
            "topic": "Solid-State Battery Electrolyte Conductance",
            "context": "Next-generation lithium-sulfur solid state energy storage cells.",
            "organism": "Garnet-type LLZO lithium lanthanum zirconium oxide ceramics",
            "biomarker": "Lithium-ion interfacial impedance & dendritic growth limit",
            "methodology": "Electrochemical impedance spectroscopy (EIS) & X-ray computed tomography",
            "metrics": ["Ionic Conductivity (S/cm)", "Interfacial Resistance (Ω·cm²)", "Critical Current Density", "Coulombic Efficiency"],
        },
    ],
    "Physics": [
        {
            "topic": "Topological Flat-Band Graphene Superconductivity",
            "context": "Cryogenic transport measurements in magic-angle (1.1°) twisted bilayer graphene.",
            "organism": "Twisted heterostructure moiré superlattices",
            "biomarker": "Quantized Hall resistance peaks & Chern number topological invariant",
            "methodology": "Scanning tunneling microscopy (STM) & low-temperature magnetotransport",
            "metrics": ["Hall Resistance Quantization", "Superconducting Transition Temp T_c", "Moiré Band Gap", "Density of States"],
        },
        {
            "topic": "Photonic Quantum Entanglement Gates",
            "context": "Integrated silicon-photonics quantum processor execution.",
            "organism": "Integrated optical micro-ring resonators",
            "biomarker": "NOON-state photon pair generation rate & bell fidelity",
            "methodology": "Quantum state tomography & coincidence counting spectrometry",
            "metrics": ["Bell State Fidelity", "Heralding Efficiency", "Single-Photon Indistinguishability", "Gate Error Rate"],
        },
    ],
    "Mathematics": [
        {
            "topic": "Non-Linear PDE Fluid Stability",
            "context": "Navier-Stokes smooth solution global existence and energy conservation bounds.",
            "organism": "3D incompressible fluid continuum domain",
            "biomarker": "Sobolev norm ||u||_H^s & vorticity directional alignment",
            "methodology": "Spectral numerical simulation & analytical energy-method estimates",
            "metrics": ["Sobolev H^s Norm Bound", "Enstrophy Dissipation Rate", "Spectral Energy Decay", "Reynolds Number Re"],
        },
    ],
    "Finance": [
        {
            "topic": "Systemic Algorithmic Market Liquidity",
            "context": "High-frequency order book dynamics across interconnected financial exchanges.",
            "organism": "Institutional high-frequency algorithmic liquidity providers",
            "biomarker": "Order cancel-to-fill ratio & cross-exchange execution correlation",
            "methodology": "Agent-based market microstructure simulation & network contagion graph analysis",
            "metrics": ["Value-at-Risk (VaR) Delta", "Bid-Ask Spread Variance", "Liquidity Recovery Time", "Contagion Index"],
        },
    ],
    "HR": [
        {
            "topic": "Organizational Attrition Network Centrality",
            "context": "Enterprise internal communication graphs and project team interaction metadata.",
            "organism": "Enterprise knowledge-worker workforce graph",
            "biomarker": "Eigenvector centrality decay & social bridge connectivity",
            "methodology": "Anonymized graph neural network (GNN) centrality tracking & survival analysis",
            "metrics": ["Hazard Ratio (HR)", "Eigenvector Centrality Delta", "Model AUROC Score", "Turnover Rate"],
        },
    ],
    "Market Analysis": [
        {
            "topic": "Consumer Adoption Under Macro-Inflation",
            "context": "Retail point-of-sale scanner data and macroeconomic consumer confidence indices.",
            "organism": "Multi-category retail consumer purchasing cohorts",
            "biomarker": "Hardware subscription migration rate & price elasticity coefficient",
            "methodology": "Hierarchical Bayesian choice modeling & econometric regression",
            "metrics": ["Price Elasticity Coefficient", "Subscription Penetration Rate", "Forecast MAPE", "Churn Rate"],
        },
    ],
}


class ScientificDiversityEngine:
    """
    Manages theme selection, cross-domain topic variation, and scientific noise injection.
    """

    def __init__(self) -> None:
        self._history: List[str] = []

    def get_diverse_pool(self, domain: str, index: int = 1) -> Dict[str, Any]:
        """
        Return a domain topic dictionary selected to maximize diversity.
        """
        pools = DOMAIN_DIVERSITY_POOLS.get(domain, DOMAIN_DIVERSITY_POOLS["Healthcare"])
        selected = pools[(index - 1) % len(pools)]
        return selected
