"""
backend/app/benchmark/generator.py — Domain-Specific Generator for Official Benchmark v1.0.

Generates scientifically rigorous BenchmarkSample instances using BenchmarkSampleBuilder
across 10 supported domains and 4 balanced difficulty levels.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional

from app.benchmark.models import BenchmarkSample, BenchmarkSampleBuilder

logger = logging.getLogger("dataset_genome.benchmark.generator")

SUPPORTED_DOMAINS = [
    "Agriculture",
    "Healthcare",
    "Climate Science",
    "Biology",
    "Chemistry",
    "Physics",
    "Mathematics",
    "Finance",
    "HR",
    "Market Analysis",
]

DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard", "Expert"]


class BenchmarkGenerator:
    """
    Generator engine synthesizing official Dataset Genome Benchmark samples
    across 10 scientific domains and 4 difficulty levels.
    """

    def generate_sample(
        self,
        domain: str = "Agriculture",
        difficulty: str = "Medium",
        index: int = 1,
    ) -> BenchmarkSample:
        """
        Generate a single complete 16-field BenchmarkSample using BenchmarkSampleBuilder.
        """
        if domain not in SUPPORTED_DOMAINS:
            domain = "Agriculture"
        if difficulty not in DIFFICULTY_LEVELS:
            difficulty = "Medium"

        sample_id = f"bm-{domain.lower().replace(' ', '-')[:6]}-{difficulty.lower()[:3]}-{index:03d}-{uuid.uuid4().hex[:4]}"

        # Domain template data
        templates = self._get_domain_templates(domain, difficulty)

        builder = BenchmarkSampleBuilder(sample_id=sample_id, domain=domain, difficulty=difficulty)
        builder.set_inquiry(
            prompt=templates["prompt"],
            context=templates["context"],
            observation=templates["observation"],
        )
        builder.set_problem(
            problem_identification=templates["problem"],
            research_gap=templates["research_gap"],
        )
        builder.set_hypotheses(
            primary=templates["primary_hypothesis"],
            alternative=templates["alternative_hypothesis"],
        )
        builder.set_experiment(
            design=templates["experiment_design"],
            metrics=templates["evaluation_metrics"],
            expected_results=templates["expected_results"],
            failure_cases=templates["failure_cases"],
        )
        builder.set_conclusion(scientific_conclusion=templates["scientific_conclusion"])
        builder.set_metadata({
            "generated_by": "DatasetGenomeBenchmarkGenerator-v1.0",
            "domain_category": domain,
            "difficulty_rating": difficulty,
            "benchmark_version": "v1.0",
        })

        return builder.build()

    def generate_benchmark_suite(
        self,
        samples_per_domain: int = 4,
        domains: Optional[List[str]] = None,
    ) -> List[BenchmarkSample]:
        """
        Generate a complete benchmark dataset suite balanced across domains and difficulty levels.
        """
        target_domains = domains or SUPPORTED_DOMAINS
        logger.info(
            f"BenchmarkGenerator synthesizing benchmark dataset suite for {len(target_domains)} domains "
            f"({samples_per_domain} samples/domain)..."
        )

        samples: List[BenchmarkSample] = []
        global_idx = 0
        for dom in target_domains:
            for idx in range(1, samples_per_domain + 1):
                # Cycle through difficulty levels uniformly across global sample count
                diff = DIFFICULTY_LEVELS[global_idx % len(DIFFICULTY_LEVELS)]
                sample = self.generate_sample(domain=dom, difficulty=diff, index=idx)
                samples.append(sample)
                global_idx += 1

        logger.info(f"BenchmarkGenerator successfully generated {len(samples)} benchmark sample(s).")
        return samples

    def _get_domain_templates(self, domain: str, difficulty: str) -> Dict[str, Any]:
        """Return scientific templates tailored to domain and difficulty level."""
        d = domain.lower()
        if "agri" in d:
            return {
                "prompt": f"Analyze crop yield resistance under elevated soil salinity ({difficulty} complexity).",
                "context": "Soil salinity levels increased by 3.2 dS/m in irrigated agricultural basins.",
                "observation": "Halophytic maize variants maintain 88% stomatal conductance compared to glycophytic controls.",
                "problem": "Unclear osmotic regulation pathway in drought-tolerant hybrid cultivars.",
                "research_gap": "Lack of high-resolution transcriptomic tracking for sodium ion transporter genes.",
                "primary_hypothesis": "Upregulation of HKT1;5 transporters drives vascular Na+ exclusion under saline stress.",
                "alternative_hypothesis": "Osmotic adjustment is primarily mediated by proline biosynthesis pathway upregulation.",
                "experiment_design": {
                    "methodology": "Hydroponic salt stress trial with RNA-seq gene expression profiling",
                    "variables": {"independent": "NaCl concentration (0-200 mM)", "dependent": "Yield & Na+/K+ ratio"},
                    "control": "Non-saline nutrient solution baseline",
                },
                "evaluation_metrics": ["Biomass Dry Weight", "Na+/K+ Selectivity Ratio", "Stomatal Conductance", "Yield Index"],
                "expected_results": "HKT1;5 expression increases 4.2-fold within 12h of NaCl exposure.",
                "failure_cases": ["Hyper-accumulation of toxic Na+ in leaf tips", "Severe osmotic cell lysis"],
                "scientific_conclusion": "Vascular ion exclusion via HKT1;5 upregulation preserves photosynthesis under salt stress.",
            }
        elif "health" in d:
            return {
                "prompt": f"Investigate biomarker kinetics for early detection of metabolic resistance ({difficulty} complexity).",
                "context": "Phase II clinical cohort tracking glucose tolerance and systemic inflammation markers.",
                "observation": "Elevated circulating IL-6 correlates with early insulin receptor desensitization.",
                "problem": "Delayed clinical onset detection for metabolic insulin resistance.",
                "research_gap": "Absence of predictive inflammatory biomarker panels for pre-symptomatic diagnosis.",
                "primary_hypothesis": "IL-6 elevation precedes IRS-1 serine phosphorylation in skeletal muscle tissue.",
                "alternative_hypothesis": "Free fatty acid accumulation directly triggers TNF-alpha receptor activation.",
                "experiment_design": {
                    "methodology": "Longitudinal serum profiling and hyperinsulinemic-euglycemic clamp assays",
                    "variables": {"independent": "Serum IL-6 assay levels", "dependent": "Glucose disposal rate (M-value)"},
                    "control": "Healthy normoglycemic age-matched controls",
                },
                "evaluation_metrics": ["M-value Glucose Disposal", "Serum IL-6 Concentration", "HOMA-IR Score"],
                "expected_results": "IL-6 levels above 4.5 pg/mL predict HOMA-IR progression within 6 months.",
                "failure_cases": ["Transient non-specific cytokine spikes during acute viral infection"],
                "scientific_conclusion": "Pro-inflammatory IL-6 kinetics serve as a robust early biomarker for insulin resistance.",
            }
        elif "climate" in d:
            return {
                "prompt": f"Evaluate marine aerosol cloud albedo feedback loops ({difficulty} complexity).",
                "context": "Satellite radiative flux observations across marine stratocumulus ocean decks.",
                "observation": "Cloud droplet effective radius decreased from 14 µm to 9.5 µm downwind of shipping lanes.",
                "problem": "Uncertainty in aerosol-cloud-radiation interaction radiative forcing estimates.",
                "research_gap": "Inadequate parameterization of dimethyl sulfide aerosol nucleation rates in climate models.",
                "primary_hypothesis": "Increased bio-aerosols enhance cloud albedo by 0.35 W/m² negative radiative forcing.",
                "alternative_hypothesis": "Cloud thinning from dry-air entrainment offsets albedo brightening effects.",
                "experiment_design": {
                    "methodology": "Airborne cloud probe sampling and LES cloud resolving numerical simulation",
                    "variables": {"independent": "Aerosol number concentration N_a", "dependent": "Cloud Optical Depth τ"},
                    "control": "Pristine Southern Ocean marine boundary layer",
                },
                "evaluation_metrics": ["Cloud Droplet Number Density", "Shortwave Radiative Forcing", "Albedo Delta"],
                "expected_results": "Twomey effect brightens stratocumulus decks by 8.2% under double aerosol loading.",
                "failure_cases": ["Aerosol scavenging by precipitation out-washing"],
                "scientific_conclusion": "Marine bio-aerosol nucleation produces net cooling radiative forcing.",
            }
        elif "bio" in d:
            return {
                "prompt": f"Characterize CRISPR-Cas micro-RNA off-target binding kinetic rates ({difficulty} complexity).",
                "context": "Single-molecule fluorescence resonance energy transfer (smFRET) single-cell imaging.",
                "observation": "Cas12a exhibits extended residence time on DNA mismatches at positions 18-20.",
                "problem": "Unintended genome editing at distal off-target sites.",
                "research_gap": "Structural basis of mismatch tolerance in the PAM-distal gRNA duplex region.",
                "primary_hypothesis": "Loop 1 conformational flexibility accommodates seed-distal transition mismatches.",
                "alternative_hypothesis": "Supercoiling torque accelerates off-target R-loop propagation.",
                "experiment_design": {
                    "methodology": "smFRET and high-throughput GUIDE-seq off-target profiling",
                    "variables": {"independent": "gRNA-target mismatch position", "dependent": "Cleavage Rate k_cleave"},
                    "control": "Fully matched target sequence",
                },
                "evaluation_metrics": ["Cleavage Rate k_cleave", "Off-Target Ratio", "smFRET Efficiency E"],
                "expected_results": "Engineered Cas12a variant reduces off-target cleavage by 14-fold.",
                "failure_cases": ["Loss of target site cleavage activity"],
                "scientific_conclusion": "Restricting Loop 1 flexibility restores high-fidelity genome editing specificity.",
            }
        elif "chem" in d:
            return {
                "prompt": f"Synthesize high-efficiency MOF catalysts for CO2 photoreduction ({difficulty} complexity).",
                "context": "Solar-driven carbon dioxide conversion to synthetic C2 hydrocarbon fuels.",
                "observation": "Copper-doped ZIF-8 metal-organic framework exhibits 92% selectivity for ethylene.",
                "problem": "Low solar-to-fuel conversion efficiency and catalytic degradation.",
                "research_gap": "Unknown charge transfer dynamics across metal node to organic linker interface.",
                "primary_hypothesis": "Interfacial Cu-N site binding lowers the activation energy for C-C coupling.",
                "alternative_hypothesis": "Light absorption occurs exclusively via organic linker ligand-to-metal charge transfer.",
                "experiment_design": {
                    "methodology": "Transient absorption spectroscopy and in-situ DRIFTS reaction monitoring",
                    "variables": {"independent": "Dopant Cu molar concentration", "dependent": "Ethylene Turnover Frequency (TOF)"},
                    "control": "Undoped ZIF-8 baseline MOF",
                },
                "evaluation_metrics": ["Turnover Frequency (TOF)", "Faradaic Efficiency (%)", "CO2 Conversion Rate"],
                "expected_results": "Cu-ZIF-8 achieves 4.8 mmol/g/h ethylene yield under 1 sun illumination.",
                "failure_cases": ["Leaching of active Cu species into aqueous electrolyte"],
                "scientific_conclusion": "Interfacial dual Cu-N active sites lower C-C coupling kinetic barrier.",
            }
        elif "phys" in d:
            return {
                "prompt": f"Map topological edge states in twisted bilayer graphene devices ({difficulty} complexity).",
                "context": "Cryogenic transport measurements in magic-angle (1.1°) twisted bilayer graphene.",
                "observation": "Quantized Hall resistance peaks observed at fractional moiré band filling factors.",
                "problem": "Elucidating origin of correlated insulating states and unconventional superconductivity.",
                "research_gap": "Role of electron-phonon coupling vs strong Coulomb interactions in flat moiré bands.",
                "primary_hypothesis": "Inter-layer flat band hybridization generates non-trivial Chern number topological states.",
                "alternative_hypothesis": "Nematic order breaks rotational symmetry independent of topology.",
                "experiment_design": {
                    "methodology": "Scanning tunneling microscopy (STM) and low-temperature magnetotransport",
                    "variables": {"independent": "Back-gate voltage V_bg & twist angle θ", "dependent": "Hall Resistance R_xy"},
                    "control": "Untwisted monolayer graphene device",
                },
                "evaluation_metrics": ["Hall Resistance Quantization", "Superconducting Transition Temp T_c", "Moiré Band Gap"],
                "expected_results": "Quantized conductance R_xy = h/2e² verified at filling factor ν = 2.",
                "failure_cases": ["Thermal broadening of flat band gap above 4.2 K"],
                "scientific_conclusion": "Topological flat moiré bands drive room-pressure correlated electronic states.",
            }
        elif "math" in d:
            return {
                "prompt": f"Prove bound limits for non-linear PDE transport stability ({difficulty} complexity).",
                "context": "Navier-Stokes smooth solution global existence and energy conservation bounds.",
                "observation": "Sobolev norm ||u||_H^s remains bounded under high-frequency turbulent perturbations.",
                "problem": "Preventing finite-time singularity blow-up in 3D incompressible fluid dynamics.",
                "research_gap": "Lack of global A-priori estimates for vorticity stretching terms.",
                "primary_hypothesis": "Directional alignment of vorticity vectors suppresses non-linear energy cascade.",
                "alternative_hypothesis": "Viscous dissipation at Kolmogorov length scale dominates independent of alignment.",
                "experiment_design": {
                    "methodology": "Spectral numerical simulation and analytical energy-method estimates",
                    "variables": {"independent": "Reynolds Number Re", "dependent": "Maximum Enstrophy Ω_max"},
                    "control": "Standard 2D Euler laminar flow baseline",
                },
                "evaluation_metrics": ["Sobolev H^s Norm Bound", "Enstrophy Dissipation Rate", "Spectral Energy Decay"],
                "expected_results": "Global smoothness preserved for all t > 0 under directional alignment condition.",
                "failure_cases": ["Local enstrophy accumulation exceeding critical threshold"],
                "scientific_conclusion": "Vorticity alignment prevents finite-time singularity formation in 3D transport.",
            }
        elif "fin" in d:
            return {
                "prompt": f"Model systemic risk propagation in algorithmic market liquidity ({difficulty} complexity).",
                "context": "High-frequency order book dynamics across interconnected financial exchanges.",
                "observation": "Flash crash cascade triggered when order cancel-to-fill ratio exceeded 45:1.",
                "problem": "Sudden market liquidity evaporations in high-frequency trading environments.",
                "research_gap": "Inadequate cross-exchange feedback loop dynamics in traditional Black-Scholes risk models.",
                "primary_hypothesis": "Algorithmic execution correlation causes positive feedback liquidity contraction.",
                "alternative_hypothesis": "Macroeconomic news sentiment shock drives order book imbalance independently.",
                "experiment_design": {
                    "methodology": "Agent-based market microstructure simulation and network contagion graph analysis",
                    "variables": {"independent": "Algo correlation coefficient ρ", "dependent": "Bid-Ask Spread Variance"},
                    "control": "Uncorrelated random market-maker baseline",
                },
                "evaluation_metrics": ["Value-at-Risk (VaR) Delta", "Bid-Ask Spread Variance", "Liquidity Recovery Time"],
                "expected_results": "Cross-algo correlation > 0.75 increases systemic liquidity crash probability by 3.8x.",
                "failure_cases": ["Spurious correlation artifacts during low-volume trading windows"],
                "scientific_conclusion": "Correlated algorithmic order execution amplifies systemic market liquidity risk.",
            }
        elif "hr" in d:
            return {
                "prompt": f"Analyze organizational attrition predictors using network centrality ({difficulty} complexity).",
                "context": "Enterprise internal communication graphs and project team interaction metadata.",
                "observation": "Employees experiencing a 30% drop in eigenvector centrality exhibit 3.2x higher turnover.",
                "problem": "Reactive employee retention strategies leading to institutional knowledge loss.",
                "research_gap": "Underestimating social network isolation as a primary driver of workplace burnout.",
                "primary_hypothesis": "Loss of informal communication hub status precedes voluntary resignation by 90 days.",
                "alternative_hypothesis": "Direct compensation dissatisfaction is the sole statistically significant attrition driver.",
                "experiment_design": {
                    "methodology": "Anonymized graph neural network (GNN) centrality tracking and longitudinal survival analysis",
                    "variables": {"independent": "Graph Eigenvector Centrality", "dependent": "Retention Probability (Hazard Ratio)"},
                    "control": "Stable project team baseline cohort",
                },
                "evaluation_metrics": ["Hazard Ratio (HR)", "Eigenvector Centrality Delta", "Model AUROC Score"],
                "expected_results": "GNN network centrality features boost attrition prediction accuracy from 68% to 89%.",
                "failure_cases": ["Graph sparsity in remote-first team communication channels"],
                "scientific_conclusion": "Informal organizational network isolation is a strong predictive indicator of attrition.",
            }
        else:  # Market Analysis
            return {
                "prompt": f"Predict consumer technology adoption curves under macro-inflation ({difficulty} complexity).",
                "context": "Retail point-of-sale scanner data and macroeconomic consumer confidence indices.",
                "observation": "Premium consumer hardware demand shifted towards subscription leasing models.",
                "problem": "Inaccurate demand forecasting during stagflation economic cycles.",
                "research_gap": "Lack of price elasticity models incorporating real wage purchasing power degradation.",
                "primary_hypothesis": "Substitution effect drives 42% growth in hardware-as-a-service market share.",
                "alternative_hypothesis": "Consumer delay of purchase decisions accounts for total market volume shift.",
                "experiment_design": {
                    "methodology": "Hierarchical Bayesian choice modeling and cross-category econometric regression",
                    "variables": {"independent": "Real Wage Inflation Rate", "dependent": "Hardware Subscription Market Share"},
                    "control": "Historical baseline economic growth expansion cycle",
                },
                "evaluation_metrics": ["Price Elasticity Coefficient", "Subscription Penetration Rate", "Forecast MAPE"],
                "expected_results": "Subscription model preference increases linearly when inflation exceeds 5.0%.",
                "failure_cases": ["Supply chain inventory bottlenecks skewing consumer choice availability"],
                "scientific_conclusion": "Stagflation shifts consumer technology purchasing preference toward recurring subscription models.",
            }
