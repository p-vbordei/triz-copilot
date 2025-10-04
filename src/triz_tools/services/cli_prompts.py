"""
CLI Subprocess Prompt Templates
Structured prompts for offloading analysis to subprocess CLI calls
"""

from typing import Dict, Any, List


def get_prompt(task_type: str, **kwargs) -> str:
    """
    Get prompt template for a specific task type.

    Args:
        task_type: Type of analysis task
        **kwargs: Template variables

    Returns:
        Formatted prompt string
    """
    templates = {
        "materials_deep_analysis": MATERIALS_DEEP_ANALYSIS,
        "extract_contradictions": EXTRACT_CONTRADICTIONS,
        "synthesize_solution": SYNTHESIZE_SOLUTION,
        "summarize_findings": SUMMARIZE_FINDINGS,
        "identify_knowledge_gaps": IDENTIFY_KNOWLEDGE_GAPS,
        "extract_material_properties": EXTRACT_MATERIAL_PROPERTIES,
        "compare_materials": COMPARE_MATERIALS,
        "generate_ifr": GENERATE_IFR,
    }

    template = templates.get(task_type)
    if not template:
        raise ValueError(f"Unknown task type: {task_type}")

    return template.format(**kwargs)


# Template: Deep Materials Analysis
MATERIALS_DEEP_ANALYSIS = """You are analyzing materials engineering research findings.

Extract and return ONLY valid JSON (no markdown, no explanation) with this exact structure:

{{
  "materials": [
    {{
      "name": "material name",
      "density": "value with units or null",
      "strength": "value with units or null",
      "formability": "assessment or null",
      "cost": "relative assessment or null",
      "properties": ["key property 1", "key property 2"]
    }}
  ],
  "comparisons": [
    {{
      "material_a": "name",
      "material_b": "name",
      "criterion": "what is compared",
      "winner": "which is better",
      "confidence": 0.8
    }}
  ],
  "recommendations": [
    {{
      "material": "name",
      "use_case": "when to use this",
      "pros": ["advantage 1", "advantage 2"],
      "cons": ["limitation 1", "limitation 2"],
      "score": 0.75
    }}
  ],
  "key_insights": ["insight 1", "insight 2", "insight 3"]
}}

Analyze these {count} research findings (total {total_chars} characters):

{findings}

Return ONLY the JSON object, nothing else."""

# Template: Extract Contradictions
EXTRACT_CONTRADICTIONS = """You are a TRIZ expert analyzing a problem for contradictions.

Extract and return ONLY valid JSON (no markdown, no explanation):

[
  {{
    "type": "technical or physical",
    "improving": "what improves",
    "worsening": "what gets worse",
    "description": "clear description of contradiction",
    "evidence": "quote or reference from text",
    "confidence": 0.9
  }}
]

Find maximum 10 contradictions.

Problem description:
{problem}

Additional context (if available):
{context}

Return ONLY the JSON array, nothing else."""

# Template: Synthesize Solution
SYNTHESIZE_SOLUTION = """You are a TRIZ expert creating solution concepts.

Given this information:
- Problem: {problem}
- TRIZ Principle: {principle_name} - {principle_description}
- Research Findings: {findings_summary}

Create a solution concept and return ONLY valid JSON:

{{
  "title": "concise solution title",
  "description": "detailed description (max 500 chars)",
  "implementation_steps": ["step 1", "step 2", "step 3"],
  "pros": ["advantage 1", "advantage 2", "advantage 3"],
  "cons": ["limitation 1", "limitation 2"],
  "feasibility_score": 0.75,
  "innovation_level": 4,
  "key_insights": ["insight from research 1", "insight from research 2"]
}}

Return ONLY the JSON object, nothing else."""

# Template: Summarize Findings
SUMMARIZE_FINDINGS = """You are summarizing research findings for TRIZ problem solving.

Condense these {count} findings into a concise summary.

Return ONLY valid JSON:

{{
  "main_themes": ["theme 1", "theme 2", "theme 3"],
  "key_principles": [
    {{
      "principle": "TRIZ principle name or number",
      "relevance": "why it's relevant",
      "support": "evidence from findings"
    }}
  ],
  "materials_mentioned": [
    {{
      "material": "name",
      "context": "where/how mentioned",
      "properties": ["prop1", "prop2"]
    }}
  ],
  "contradictions_identified": [
    {{
      "improving": "parameter",
      "worsening": "parameter",
      "source": "which finding"
    }}
  ],
  "implementation_insights": ["insight 1", "insight 2", "insight 3"],
  "confidence": 0.8
}}

Findings:
{findings}

Return ONLY the JSON object, nothing else."""

# Template: Identify Knowledge Gaps
IDENTIFY_KNOWLEDGE_GAPS = """You are analyzing research completeness for TRIZ problem solving.

Given this problem and research summary, identify what's missing.

Problem: {problem}
Research Summary: {summary}

Return ONLY valid JSON:

{{
  "missing_info": [
    {{
      "gap": "what's missing",
      "importance": "high/medium/low",
      "search_query": "suggested query to fill this gap"
    }}
  ],
  "weak_areas": ["area 1", "area 2"],
  "recommended_searches": ["search query 1", "search query 2", "search query 3"]
}}

Return ONLY the JSON object, nothing else."""

# Template: Extract Material Properties
EXTRACT_MATERIAL_PROPERTIES = """You are extracting material properties from technical text.

Extract all material property data and return ONLY valid JSON:

{{
  "materials": [
    {{
      "name": "material name",
      "properties": {{
        "density": "value with units",
        "tensile_strength": "value with units",
        "youngs_modulus": "value with units",
        "yield_strength": "value with units",
        "elongation": "percentage",
        "other": {{"property_name": "value"}}
      }},
      "notes": "any relevant notes"
    }}
  ]
}}

Text:
{text}

Return ONLY the JSON object, nothing else."""

# Template: Compare Materials
COMPARE_MATERIALS = """You are comparing materials for engineering selection.

Compare these materials and return ONLY valid JSON:

{{
  "comparison_table": [
    {{
      "material": "name",
      "density_score": 0.8,
      "strength_score": 0.9,
      "cost_score": 0.6,
      "formability_score": 0.7,
      "overall_score": 0.75
    }}
  ],
  "recommendation": {{
    "best_overall": "material name",
    "best_for_weight": "material name",
    "best_for_strength": "material name",
    "best_for_cost": "material name",
    "reasoning": "explanation of recommendation"
  }},
  "trade_offs": [
    {{
      "scenario": "use case description",
      "recommended": "material name",
      "reason": "why this material for this scenario"
    }}
  ]
}}

Materials data:
{materials_data}

Requirements:
{requirements}

Return ONLY the JSON object, nothing else."""

# Template: Generate IFR
GENERATE_IFR = """You are a TRIZ expert creating an Ideal Final Result statement.

Generate an IFR (Ideal Final Result) for this problem and return ONLY valid JSON:

{{
  "ifr_statement": "The ideal system would... (complete statement)",
  "key_characteristics": [
    "characteristic 1",
    "characteristic 2",
    "characteristic 3"
  ],
  "eliminated_elements": ["what should disappear in ideal state"],
  "self_service_aspects": ["what should happen by itself"]
}}

Problem:
{problem}

Return ONLY the JSON object, nothing else."""
