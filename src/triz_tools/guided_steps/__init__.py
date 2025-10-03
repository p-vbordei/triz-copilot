"""
Guided TRIZ Step Instruction Generators
Each phase has its own module with step-by-step research instructions
"""

from . import phase1_understand_scope
from . import phase2_define_ideal
from . import phase3_function_analysis
from . import phase4_select_tools
from . import phase5_generate_solutions
from . import phase6_rank_implement

__all__ = [
    "phase1_understand_scope",
    "phase2_define_ideal",
    "phase3_function_analysis",
    "phase4_select_tools",
    "phase5_generate_solutions",
    "phase6_rank_implement",
]
