"""
Contradiction Matrix Model (T023)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ContradictionResult:
    """Result of contradiction analysis"""
    improving_parameter: int
    worsening_parameter: int
    recommended_principles: List[int]
    confidence_score: float
    explanation: str
    application_frequency: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "improving_parameter": self.improving_parameter,
            "worsening_parameter": self.worsening_parameter,
            "recommended_principles": self.recommended_principles,
            "confidence_score": self.confidence_score,
            "explanation": self.explanation,
            "application_frequency": self.application_frequency,
        }


@dataclass
class EngineeringParameter:
    """TRIZ Engineering Parameter"""
    parameter_id: int
    parameter_name: str
    description: str = ""
    measurement_units: List[str] = field(default_factory=list)
    typical_domains: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "parameter_id": self.parameter_id,
            "parameter_name": self.parameter_name,
            "description": self.description,
            "measurement_units": self.measurement_units,
            "typical_domains": self.typical_domains,
        }


class ContradictionMatrix:
    """TRIZ Contradiction Matrix - Maps parameter conflicts to principles"""
    
    def __init__(self):
        self.matrix: Dict[Tuple[int, int], ContradictionResult] = {}
        self.parameters: Dict[int, EngineeringParameter] = {}
        self._initialize_parameters()
    
    def _initialize_parameters(self) -> None:
        """Initialize the 39 engineering parameters"""
        parameter_names = [
            "Weight of moving object",
            "Weight of stationary object",
            "Length of moving object",
            "Length of stationary object",
            "Area of moving object",
            "Area of stationary object",
            "Volume of moving object",
            "Volume of stationary object",
            "Speed",
            "Force",
            "Stress or pressure",
            "Shape",
            "Stability of object's composition",
            "Strength",
            "Duration of action by moving object",
            "Duration of action by stationary object",
            "Temperature",
            "Illumination intensity",
            "Use of energy by moving object",
            "Use of energy by stationary object",
            "Power",
            "Loss of energy",
            "Loss of substance",
            "Loss of information",
            "Loss of time",
            "Quantity of substance/matter",
            "Reliability",
            "Measurement accuracy",
            "Manufacturing precision",
            "Object-affected harmful factors",
            "Object-generated harmful factors",
            "Ease of manufacture",
            "Ease of operation",
            "Ease of repair",
            "Adaptability or versatility",
            "Device complexity",
            "Difficulty of detecting and measuring",
            "Extent of automation",
            "Productivity",
        ]
        
        for i, name in enumerate(parameter_names, 1):
            self.parameters[i] = EngineeringParameter(
                parameter_id=i,
                parameter_name=name
            )
    
    def add_contradiction(
        self,
        improving: int,
        worsening: int,
        principles: List[int],
        confidence: float = 0.7,
        applications: int = 0
    ) -> None:
        """Add a contradiction to the matrix"""
        if improving == worsening:
            raise ValueError("Improving and worsening parameters cannot be the same")
        
        if not (1 <= improving <= 39 and 1 <= worsening <= 39):
            raise ValueError("Parameters must be between 1 and 39")
        
        result = ContradictionResult(
            improving_parameter=improving,
            worsening_parameter=worsening,
            recommended_principles=principles,
            confidence_score=confidence,
            explanation=f"Improving {self.parameters[improving].parameter_name} "
                       f"while worsening {self.parameters[worsening].parameter_name}",
            application_frequency=applications
        )
        
        self.matrix[(improving, worsening)] = result
    
    def lookup(self, improving: int, worsening: int) -> Optional[ContradictionResult]:
        """Look up a contradiction in the matrix"""
        return self.matrix.get((improving, worsening))
    
    def add_parameter(
        self,
        parameter_id: int,
        parameter_name: str,
        description: str = "",
        measurement_units: Optional[List[str]] = None,
        typical_domains: Optional[List[str]] = None
    ) -> None:
        """Add or update an engineering parameter"""
        self.parameters[parameter_id] = EngineeringParameter(
            parameter_id=parameter_id,
            parameter_name=parameter_name,
            description=description,
            measurement_units=measurement_units or [],
            typical_domains=typical_domains or []
        )
    
    def get_parameter(self, param_id: int) -> Optional[EngineeringParameter]:
        """Get parameter by ID"""
        return self.parameters.get(param_id)
    
    def get_all_parameters(self) -> List[EngineeringParameter]:
        """Get all engineering parameters"""
        return list(self.parameters.values())
    
    def validate_parameters(self, improving: int, worsening: int) -> Tuple[bool, str]:
        """Validate parameter IDs"""
        if not (1 <= improving <= 39):
            return False, f"Improving parameter {improving} out of range (1-39)"
        if not (1 <= worsening <= 39):
            return False, f"Worsening parameter {worsening} out of range (1-39)"
        if improving == worsening:
            return False, "Parameters cannot be the same (no contradiction)"
        return True, "Valid parameters"