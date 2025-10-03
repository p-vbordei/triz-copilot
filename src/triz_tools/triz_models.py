"""
Complete TRIZ Data Models
Based on official TRIZ methodology (Altshuller, Gadd, etc.)

Includes all major TRIZ tools:
- 9 Boxes (Time & Scale)
- Ideality Equation
- Function Analysis (Subject-Action-Object)
- 76 Standard Solutions
- 40 Inventive Principles
- 8 Trends of Technical Evolution
- Contradiction Matrix
- TRIZ Effects Database
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


# ============================================================================
# 9 BOXES - Time & Scale Thinking
# ============================================================================


class TimeFrame(Enum):
    """Time dimension for 9 Boxes"""

    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"


class SystemLevel(Enum):
    """Scale dimension for 9 Boxes"""

    SUB_SYSTEM = "sub_system"  # Components inside
    SYSTEM = "system"  # The system itself
    SUPER_SYSTEM = "super_system"  # Environment/context


@dataclass
class NineBoxCell:
    """Single cell in 9 Boxes matrix"""

    time: TimeFrame
    level: SystemLevel
    description: str
    key_elements: List[str] = field(default_factory=list)
    research_findings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NineBoxes:
    """Complete 9 Boxes analysis"""

    cells: Dict[Tuple[TimeFrame, SystemLevel], NineBoxCell] = field(
        default_factory=dict
    )
    trends_identified: List[str] = field(default_factory=list)
    root_causes_found: List[str] = field(default_factory=list)


# ============================================================================
# IDEALITY - Core TRIZ Metric
# ============================================================================


@dataclass
class IdeaBenefit:
    """A single benefit (desired outcome)"""

    description: str
    importance: int  # 1-10 scale
    current_level: int  # 0-10 how well achieved
    source: str  # Where found in research


@dataclass
class IdeaCost:
    """A single cost (input required)"""

    description: str
    magnitude: int  # 1-10 scale
    type: str  # money, time, materials, effort, energy
    source: str


@dataclass
class IdeaHarm:
    """A single harm (undesired output)"""

    description: str
    severity: int  # 1-10 scale
    type: str  # safety, environmental, waste, side-effects
    source: str


@dataclass
class Ideality:
    """
    Ideality = Sum(Benefits) / (Sum(Costs) + Sum(Harms))

    Higher is better. Goal is to maximize benefits while minimizing costs and harms.
    """

    benefits: List[IdeaBenefit] = field(default_factory=list)
    costs: List[IdeaCost] = field(default_factory=list)
    harms: List[IdeaHarm] = field(default_factory=list)

    @property
    def total_benefits(self) -> float:
        if not self.benefits:
            return 0.0
        return sum(b.importance * (b.current_level / 10.0) for b in self.benefits)

    @property
    def total_costs(self) -> float:
        if not self.costs:
            return 0.0
        return sum(c.magnitude for c in self.costs)

    @property
    def total_harms(self) -> float:
        if not self.harms:
            return 0.0
        return sum(h.severity for h in self.harms)

    @property
    def ideality_score(self) -> float:
        """Calculate Ideality ratio"""
        denominator = self.total_costs + self.total_harms
        if denominator == 0:
            return float("inf") if self.total_benefits > 0 else 0.0
        return self.total_benefits / denominator

    @property
    def ideality_category(self) -> str:
        """Categorize ideality level"""
        score = self.ideality_score
        if score >= 2.0:
            return "EXCELLENT"
        elif score >= 1.0:
            return "GOOD"
        elif score >= 0.5:
            return "ACCEPTABLE"
        else:
            return "POOR"


# ============================================================================
# FUNCTION ANALYSIS - Subject-Action-Object
# ============================================================================


class ActionType(Enum):
    """Types of actions in function analysis"""

    USEFUL = "useful"  # Desired, adequate
    INSUFFICIENT = "insufficient"  # Desired but not enough
    EXCESSIVE = "excessive"  # Desired but too much
    HARMFUL = "harmful"  # Not desired


@dataclass
class FunctionAction:
    """
    Subject-Action-Object relationship

    Example: "Motor (subject) rotates (action) propeller (object)"
    """

    subject: str  # What performs the action
    action: str  # The action/function verb
    object: str  # What receives the action
    action_type: ActionType
    description: str = ""
    magnitude: int = 5  # 1-10 how strong/intense
    research_source: str = ""


@dataclass
class FunctionMap:
    """Complete function analysis of system"""

    components: List[str] = field(default_factory=list)
    functions: List[FunctionAction] = field(default_factory=list)

    @property
    def useful_functions(self) -> List[FunctionAction]:
        return [f for f in self.functions if f.action_type == ActionType.USEFUL]

    @property
    def insufficient_functions(self) -> List[FunctionAction]:
        return [f for f in self.functions if f.action_type == ActionType.INSUFFICIENT]

    @property
    def excessive_functions(self) -> List[FunctionAction]:
        return [f for f in self.functions if f.action_type == ActionType.EXCESSIVE]

    @property
    def harmful_functions(self) -> List[FunctionAction]:
        return [f for f in self.functions if f.action_type == ActionType.HARMFUL]


# ============================================================================
# 76 STANDARD SOLUTIONS - Categories
# ============================================================================


class StandardSolutionCategory(Enum):
    """Categories of 76 Standard Solutions"""

    TRIMMING = "trimming"  # Remove components
    HARM_ELIMINATE = "harm_eliminate"  # Remove harmful action
    HARM_BLOCK = "harm_block"  # Block harmful action
    HARM_CONVERT = "harm_convert"  # Turn harm into benefit
    HARM_CORRECT = "harm_correct"  # Compensate for harm
    INSUFFICIENCY_ENHANCE = "insufficiency_enhance"  # Boost weak function
    INSUFFICIENCY_ADD = "insufficiency_add"  # Add new function
    MEASUREMENT = "measurement"  # Detect/measure problems
    DETECTION = "detection"  # Find hidden issues


@dataclass
class StandardSolution:
    """A single Standard Solution from the 76"""

    number: int  # 1-76
    category: StandardSolutionCategory
    title: str
    description: str
    when_to_use: str
    examples: List[str] = field(default_factory=list)
    principles_related: List[int] = field(default_factory=list)  # Related 40 principles


# ============================================================================
# 8 TRENDS OF TECHNICAL EVOLUTION
# ============================================================================


class EvolutionTrend(Enum):
    """8 major trends of technical system evolution"""

    INCREASING_IDEALITY = "increasing_ideality"
    S_CURVE = "s_curve"  # Infancy → Youth → Maturity → Old Age
    COORDINATION = "coordination"  # Better matching of components
    AUTOMATION = "automation"  # Less human intervention
    SEGMENTATION_FIELDS = "segmentation_fields"  # More parts, more fields
    DYNAMISM = "dynamism"  # More flexible, controllable
    SIMPLICITY_COMPLEXITY = "simplicity_complexity"  # Simple → Complex → Simple
    MATCHING_NEEDS = "matching_needs"  # Better fit user requirements


@dataclass
class TrendAnalysis:
    """Analysis of system evolution trends"""

    trend: EvolutionTrend
    current_stage: str
    next_stage_prediction: str
    research_evidence: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)


# ============================================================================
# CONTRADICTIONS
# ============================================================================


@dataclass
class TechnicalContradiction:
    """Improving one parameter worsens another"""

    improving_parameter: str
    improving_param_number: int  # 1-39
    worsening_parameter: str
    worsening_param_number: int  # 1-39
    description: str
    recommended_principles: List[int] = field(default_factory=list)
    matrix_source: bool = True


@dataclass
class PhysicalContradiction:
    """Opposite properties needed in same object"""

    parameter: str
    requirement_1: str
    requirement_2: str
    description: str
    separation_methods: List[str] = field(
        default_factory=list
    )  # TIME, SPACE, CONDITION, SYSTEM


# ============================================================================
# RESOURCES
# ============================================================================


class ResourceType(Enum):
    """Types of resources in TRIZ"""

    SUBSTANCE = "substance"  # Materials, components
    FIELD = "field"  # Energy, forces, fields
    SPACE = "space"  # Available volume, areas
    TIME = "time"  # Available time, timing
    INFORMATION = "information"  # Data, knowledge
    FUNCTIONAL = "functional"  # Existing capabilities


@dataclass
class Resource:
    """A resource available in or around the system"""

    name: str
    type: ResourceType
    location: str  # Where found (system, sub-system, super-system)
    availability: str  # Always, sometimes, with modification
    potential_use: str = ""


# ============================================================================
# IDEAL OUTCOME
# ============================================================================


@dataclass
class IdealOutcome:
    """
    Wish list of all desired benefits in ideal world.
    No consideration of how to achieve or constraints.
    """

    prime_benefit: str  # Main desired outcome
    ultimate_goal: str  # Long-term vision
    all_desired_benefits: List[IdeaBenefit] = field(default_factory=list)
    ideal_ideality_target: float = float("inf")  # Perfect = infinite
    constraints_to_ignore: List[str] = field(default_factory=list)


# ============================================================================
# SOLUTION CONCEPT
# ============================================================================


@dataclass
class SolutionConcept:
    """A potential solution generated from TRIZ tools"""

    title: str
    description: str
    triz_tools_used: List[str] = field(
        default_factory=list
    )  # Which tools generated this
    principles_applied: List[int] = field(default_factory=list)
    standard_solutions_used: List[int] = field(default_factory=list)
    trends_applied: List[EvolutionTrend] = field(default_factory=list)

    # Ideality components
    expected_benefits: List[IdeaBenefit] = field(default_factory=list)
    expected_costs: List[IdeaCost] = field(default_factory=list)
    expected_harms: List[IdeaHarm] = field(default_factory=list)

    # Evaluation
    ideality: Optional[Ideality] = None
    feasibility: float = 0.5  # 0-1
    innovation_level: int = 3  # 1-5
    implementation_complexity: int = 5  # 1-10

    # Research evidence
    research_sources: List[str] = field(default_factory=list)
    examples_found: List[str] = field(default_factory=list)

    @property
    def ideality_score(self) -> float:
        if self.ideality:
            return self.ideality.ideality_score
        return 0.0

    @property
    def ranking_score(self) -> float:
        """Combined score for ranking solutions"""
        return (
            self.ideality_score * 0.5
            + self.feasibility * 0.3
            + (self.innovation_level / 5.0) * 0.2
        )


# ============================================================================
# GUIDED SESSION - Complete TRIZ Process
# ============================================================================


class TRIZPhase(Enum):
    """6 phases of complete TRIZ methodology"""

    UNDERSTAND_SCOPE = "understand_scope"  # Steps 1-10: 9 Boxes, Ideality Audit
    DEFINE_IDEAL = "define_ideal"  # Steps 11-16: Ideal Outcome, Resources
    FUNCTION_ANALYSIS = (
        "function_analysis"  # Steps 17-26: Subject-Action-Object, Contradictions
    )
    SELECT_TOOLS = "select_tools"  # Steps 27-32: Match problems to tools
    GENERATE_SOLUTIONS = "generate_solutions"  # Steps 33-50: Apply all tools
    RANK_IMPLEMENT = "rank_implement"  # Steps 51-60: Ideality Plot, Implementation


class StepStatus(Enum):
    """Status of each step"""

    PENDING = "pending"
    AWAITING_RESEARCH = "awaiting_research"
    RESEARCH_SUBMITTED = "research_submitted"
    VALIDATED = "validated"
    SKIPPED = "skipped"


@dataclass
class StepInstruction:
    """Instructions for AI to perform research"""

    task: str
    search_queries: List[str]
    extract_requirements: List[str]
    validation_criteria: str
    expected_output_format: str
    why_this_matters: str
    related_triz_tool: str = ""  # Which TRIZ tool this step uses


@dataclass
class TRIZStep:
    """A single step in the 60-step guided TRIZ process"""

    step_number: int
    phase: TRIZPhase
    title: str
    status: StepStatus
    instruction: Optional[StepInstruction] = None
    findings: Dict[str, Any] = field(default_factory=dict)
    validation_result: Optional[str] = None
    triz_tool: str = ""  # Which TRIZ tool/concept this step implements


@dataclass
class TRIZGuidedSession:
    """Complete guided TRIZ research session - 60 steps"""

    session_id: str
    problem: str
    current_step: int
    steps: List[TRIZStep]

    # Accumulated TRIZ artifacts
    nine_boxes: Optional[NineBoxes] = None
    current_ideality: Optional[Ideality] = None
    ideal_outcome: Optional[IdealOutcome] = None
    resources: List[Resource] = field(default_factory=list)
    function_map: Optional[FunctionMap] = None
    technical_contradictions: List[TechnicalContradiction] = field(default_factory=list)
    physical_contradictions: List[PhysicalContradiction] = field(default_factory=list)
    solution_concepts: List[SolutionConcept] = field(default_factory=list)
    evolution_trends: List[TrendAnalysis] = field(default_factory=list)

    # Raw accumulated knowledge
    accumulated_knowledge: Dict[str, Any] = field(default_factory=dict)

    created_at: str = ""
    updated_at: str = ""

    @property
    def progress_percentage(self) -> int:
        return int((self.current_step / 60) * 100)

    @property
    def current_phase(self) -> TRIZPhase:
        if self.current_step <= 10:
            return TRIZPhase.UNDERSTAND_SCOPE
        elif self.current_step <= 16:
            return TRIZPhase.DEFINE_IDEAL
        elif self.current_step <= 26:
            return TRIZPhase.FUNCTION_ANALYSIS
        elif self.current_step <= 32:
            return TRIZPhase.SELECT_TOOLS
        elif self.current_step <= 50:
            return TRIZPhase.GENERATE_SOLUTIONS
        else:
            return TRIZPhase.RANK_IMPLEMENT
