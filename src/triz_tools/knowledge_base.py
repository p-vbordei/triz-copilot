"""
TRIZ Knowledge Base Operations (T033)
Load and manage TRIZ principles and contradiction matrix
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from .models import (
    TRIZKnowledgeBase,
    TRIZPrinciple,
    ContradictionMatrix,
    ContradictionResult,
)


def load_principles_from_file(
    file_path: Optional[Path] = None
) -> TRIZKnowledgeBase:
    """Load TRIZ principles from text file"""
    if file_path is None:
        file_path = Path(__file__).parent / "data" / "triz_principles.txt"
    
    knowledge_base = TRIZKnowledgeBase()
    
    # Parse the principles text file
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Split by principle headers
    principle_pattern = r"## Principle (\d+): (.+?)(?=## Principle|\Z)"
    matches = re.findall(principle_pattern, content, re.DOTALL)
    
    for match in matches:
        principle_num = int(match[0])
        principle_content = match[1]
        
        # Extract principle name
        lines = principle_content.strip().split("\n")
        principle_name = lines[0].strip()
        
        # Extract sub-principles
        sub_principles = []
        sub_pattern = r"^[a-z]\) (.+)$"
        
        # Extract examples
        examples = []
        in_examples = False
        
        description_lines = []
        
        for line in lines[1:]:
            line = line.strip()
            if line.startswith("Examples:"):
                in_examples = True
                continue
            elif line.startswith("## "):
                break
            elif in_examples and line.startswith("- "):
                examples.append(line[2:])
            elif re.match(sub_pattern, line):
                sub_principles.append(re.match(sub_pattern, line).group(1))
            elif line and not in_examples:
                description_lines.append(line)
        
        # Create principle object
        principle = TRIZPrinciple(
            principle_id=principle_num,
            principle_number=principle_num,
            principle_name=principle_name,
            description=" ".join(description_lines) if description_lines else principle_name,
            sub_principles=sub_principles,
            examples=examples,
            domains=_infer_domains(principle_name, examples),
            usage_frequency=_infer_usage_frequency(principle_num),
            innovation_level=_infer_innovation_level(principle_num),
            related_principles=_infer_related_principles(principle_num),
        )
        
        knowledge_base.add_principle(principle)
    
    knowledge_base.mark_loaded()
    return knowledge_base


def load_contradiction_matrix(
    file_path: Optional[Path] = None
) -> ContradictionMatrix:
    """Load contradiction matrix from JSON file"""
    if file_path is None:
        file_path = Path(__file__).parent / "data" / "contradiction_matrix.json"
    
    matrix = ContradictionMatrix()
    
    # Load JSON data
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Load matrix entries
    if "matrix" in data:
        # Handle both list and dict formats
        matrix_data = data["matrix"]
        if isinstance(matrix_data, list):
            # List of entries
            for entry in matrix_data:
                matrix.add_contradiction(
                    improving=entry["improving"],
                    worsening=entry["worsening"],
                    principles=entry["principles"],
                    confidence=entry.get("confidence", 0.7),
                    applications=entry.get("applications", 0)
                )
        else:
            # Dict format (legacy)
            for key, entry in matrix_data.items():
                matrix.add_contradiction(
                    improving=entry["improving"],
                    worsening=entry["worsening"],
                    principles=entry["principles"],
                    confidence=entry.get("confidence", 0.7),
                    applications=entry.get("applications", 0)
                )
    
    return matrix


def _infer_domains(principle_name: str, examples: List[str]) -> List[str]:
    """Infer applicable domains from principle name and examples"""
    domains = []
    
    # Check for common domain keywords
    domain_keywords = {
        "mechanical": ["gear", "bearing", "motor", "machine", "mechanism"],
        "aerospace": ["aircraft", "wing", "rocket", "satellite"],
        "automotive": ["car", "vehicle", "engine", "brake", "tire"],
        "manufacturing": ["production", "assembly", "factory", "process"],
        "electronics": ["circuit", "sensor", "chip", "electronic"],
        "software": ["algorithm", "program", "software", "code"],
        "chemical": ["reaction", "catalyst", "chemical", "compound"],
        "medical": ["medical", "surgical", "health", "patient"],
    }
    
    text = principle_name.lower() + " " + " ".join(examples).lower()
    
    for domain, keywords in domain_keywords.items():
        if any(keyword in text for keyword in keywords):
            domains.append(domain)
    
    # Default domains if none found
    if not domains:
        domains = ["general", "engineering"]
    
    return domains


def _infer_usage_frequency(principle_num: int) -> str:
    """Infer usage frequency based on principle number"""
    # Common principles (based on TRIZ statistics)
    high_usage = [1, 2, 3, 10, 13, 14, 15, 25, 28, 35]
    low_usage = [36, 37, 38, 39]
    
    if principle_num in high_usage:
        return "high"
    elif principle_num in low_usage:
        return "low"
    else:
        return "medium"


def _infer_innovation_level(principle_num: int) -> int:
    """Infer innovation level (1-5) based on principle complexity"""
    # Simple principles
    if principle_num in [1, 2, 3, 4, 5, 13]:
        return 2
    # Complex principles
    elif principle_num in [15, 25, 28, 35, 36, 37, 40]:
        return 4
    # Very complex
    elif principle_num in [38, 39]:
        return 5
    # Default medium
    else:
        return 3


def _infer_related_principles(principle_num: int) -> List[int]:
    """Infer related principles based on common combinations"""
    related_map = {
        1: [2, 3, 4],  # Segmentation related to taking out, local quality, asymmetry
        2: [1, 3, 5],  # Taking out related to segmentation, local quality, merging
        3: [1, 2, 4],  # Local quality related to segmentation, taking out, asymmetry
        5: [6, 7],     # Merging related to universality, nesting
        8: [10, 11],   # Anti-weight related to preliminary action, cushioning
        13: [14, 15],  # Other way round related to curvature, dynamics
        15: [13, 35],  # Dynamics related to other way, parameter changes
        35: [15, 36, 37], # Parameter changes related to dynamics, phase transitions, thermal
        40: [1, 31],   # Composite materials related to segmentation, porous materials
    }
    
    return related_map.get(principle_num, [])