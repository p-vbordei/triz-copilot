"""
TRIZ Direct Tool Access (T039)
Implementation of direct TRIZ tool functions
"""

import json
from pathlib import Path
from typing import Dict, List, Any

from .models import (
    TRIZToolResponse,
    TRIZKnowledgeBase,
    TRIZPrinciple,
    ContradictionMatrix,
    ContradictionResult,
)
from .knowledge_base import load_principles_from_file, load_contradiction_matrix


# Initialize knowledge base and matrix
_knowledge_base: TRIZKnowledgeBase = None
_contradiction_matrix: ContradictionMatrix = None


def _ensure_knowledge_loaded():
    """Ensure TRIZ knowledge is loaded"""
    global _knowledge_base, _contradiction_matrix
    
    if _knowledge_base is None:
        _knowledge_base = load_principles_from_file()
    
    if _contradiction_matrix is None:
        _contradiction_matrix = load_contradiction_matrix()


def triz_tool_get_principle(principle_number: int) -> TRIZToolResponse:
    """Get detailed information about a specific TRIZ principle"""
    try:
        # Validate principle number
        if not (1 <= principle_number <= 40):
            return TRIZToolResponse(
                success=False,
                message=f"Invalid principle number: {principle_number}. Must be between 1-40.",
                data={}
            )
        
        # Ensure knowledge is loaded
        _ensure_knowledge_loaded()
        
        # Get principle
        principle = _knowledge_base.get_principle(principle_number)
        if not principle:
            return TRIZToolResponse(
                success=False,
                message=f"Principle {principle_number} not found in knowledge base",
                data={}
            )
        
        # Prepare response data
        response_data = {
            "principle_id": principle.principle_id,
            "principle_number": principle.principle_number,
            "principle_name": principle.principle_name,
            "description": principle.description,
            "sub_principles": principle.sub_principles,
            "examples": principle.examples,
            "domains": principle.domains,
            "usage_frequency": principle.usage_frequency,
            "innovation_level": principle.innovation_level,
            "related_principles": principle.related_principles,
            "patent_references": principle.patent_references,
        }
        
        return TRIZToolResponse(
            success=True,
            message=f"Retrieved principle {principle_number}: {principle.principle_name}",
            data=response_data
        )
        
    except Exception as e:
        return TRIZToolResponse(
            success=False,
            message=f"Error retrieving principle: {str(e)}",
            data={}
        )


def triz_tool_contradiction_matrix(
    improving_param: int,
    worsening_param: int
) -> TRIZToolResponse:
    """Query the TRIZ contradiction matrix for recommended principles"""
    try:
        # Ensure knowledge is loaded
        _ensure_knowledge_loaded()
        
        # Validate parameters
        valid, message = _contradiction_matrix.validate_parameters(improving_param, worsening_param)
        if not valid:
            return TRIZToolResponse(
                success=False,
                message=message,
                data={}
            )
        
        # Look up contradiction
        result = _contradiction_matrix.lookup(improving_param, worsening_param)
        
        if result:
            # Found in matrix
            response_data = {
                "improving_parameter": improving_param,
                "worsening_parameter": worsening_param,
                "recommended_principles": result.recommended_principles,
                "confidence_score": result.confidence_score,
                "explanation": result.explanation,
                "application_frequency": result.application_frequency,
            }
        else:
            # Not in matrix, provide general recommendations
            # Common principles for general contradictions
            default_principles = [1, 2, 13, 15, 35]  # Segmentation, Taking out, Other way, Dynamics, Parameter changes
            response_data = {
                "improving_parameter": improving_param,
                "worsening_parameter": worsening_param,
                "recommended_principles": default_principles,
                "confidence_score": 0.5,
                "explanation": f"No specific matrix entry found. Suggested general principles for exploration.",
                "application_frequency": 0,
            }
        
        # Add parameter names
        improving_name = _contradiction_matrix.get_parameter(improving_param).parameter_name
        worsening_name = _contradiction_matrix.get_parameter(worsening_param).parameter_name
        response_data["parameter_names"] = {
            "improving": improving_name,
            "worsening": worsening_name,
        }
        
        return TRIZToolResponse(
            success=True,
            message=f"Matrix lookup: Improving {improving_name} vs Worsening {worsening_name}",
            data=response_data
        )
        
    except Exception as e:
        return TRIZToolResponse(
            success=False,
            message=f"Error querying contradiction matrix: {str(e)}",
            data={}
        )


def triz_tool_brainstorm(principle_number: int, context: str) -> TRIZToolResponse:
    """Generate ideas applying a specific TRIZ principle to given context"""
    try:
        # Validate inputs
        if not (1 <= principle_number <= 40):
            return TRIZToolResponse(
                success=False,
                message=f"Invalid principle number: {principle_number}. Must be between 1-40.",
                data={}
            )
        
        if not context or not context.strip():
            return TRIZToolResponse(
                success=False,
                message="Context cannot be empty for brainstorming",
                data={}
            )
        
        # Ensure knowledge is loaded
        _ensure_knowledge_loaded()
        
        # Get principle
        principle = _knowledge_base.get_principle(principle_number)
        if not principle:
            return TRIZToolResponse(
                success=False,
                message=f"Principle {principle_number} not found",
                data={}
            )
        
        # Generate ideas based on principle and context
        ideas = []
        
        # Idea 1: Direct application
        ideas.append({
            "title": f"Direct {principle.principle_name} Application",
            "description": f"Apply {principle.principle_name} to {context} by {principle.description.lower()}",
            "how_principle_applies": f"Using the core concept of {principle.principle_name} to address the challenge"
        })
        
        # Idea 2: Based on sub-principles
        if principle.sub_principles:
            for i, sub in enumerate(principle.sub_principles[:2], 1):
                ideas.append({
                    "title": f"{principle.principle_name} Variant {i}",
                    "description": f"In the context of {context}, {sub}",
                    "how_principle_applies": f"This applies the sub-principle: {sub}"
                })
        
        # Idea 3: Based on examples
        if principle.examples:
            example = principle.examples[0]
            ideas.append({
                "title": f"Adapted from {example}",
                "description": f"Similar to how {example} works, apply this concept to {context}",
                "how_principle_applies": f"Transfer the {principle.principle_name} approach from {example} to your problem"
            })
        
        # Ensure at least 3 ideas
        while len(ideas) < 3:
            ideas.append({
                "title": f"Creative Application {len(ideas) + 1}",
                "description": f"Explore how {principle.principle_name} might unexpectedly apply to {context}",
                "how_principle_applies": f"Think outside the box using {principle.principle_name}"
            })
        
        response_data = {
            "principle_number": principle_number,
            "principle_name": principle.principle_name,
            "context": context,
            "ideas": ideas,
            "principle_application": f"Applying {principle.principle_name} to generate innovative solutions",
        }
        
        return TRIZToolResponse(
            success=True,
            message=f"Generated {len(ideas)} ideas using {principle.principle_name}",
            data=response_data
        )
        
    except Exception as e:
        return TRIZToolResponse(
            success=False,
            message=f"Error during brainstorming: {str(e)}",
            data={}
        )