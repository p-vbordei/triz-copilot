"""
Materials Database Model (T026)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np


@dataclass
class Material:
    """Engineering material with properties and applications"""
    material_id: str
    material_name: str
    material_class: str  # metals, polymers, ceramics, composites
    chemical_formula: str = ""
    density_kg_m3: float = 0.0
    tensile_strength_mpa: float = 0.0
    youngs_modulus_gpa: float = 0.0
    thermal_conductivity_w_mk: float = 0.0
    melting_point_c: float = 0.0
    cost_index: float = 5.0  # 1.0-10.0
    applications: List[str] = field(default_factory=list)
    advantages: List[str] = field(default_factory=list)
    disadvantages: List[str] = field(default_factory=list)
    availability: str = "commercial"  # research, limited, commercial, commodity
    sustainability_score: float = 5.0  # 1.0-10.0
    similar_materials: List[str] = field(default_factory=list)
    triz_parameters: List[int] = field(default_factory=list)
    embedding_vector: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "material_id": self.material_id,
            "material_name": self.material_name,
            "material_class": self.material_class,
            "chemical_formula": self.chemical_formula,
            "density_kg_m3": self.density_kg_m3,
            "tensile_strength_mpa": self.tensile_strength_mpa,
            "youngs_modulus_gpa": self.youngs_modulus_gpa,
            "thermal_conductivity_w_mk": self.thermal_conductivity_w_mk,
            "melting_point_c": self.melting_point_c,
            "cost_index": self.cost_index,
            "applications": self.applications,
            "advantages": self.advantages,
            "disadvantages": self.disadvantages,
            "availability": self.availability,
            "sustainability_score": self.sustainability_score,
            "similar_materials": self.similar_materials,
            "triz_parameters": self.triz_parameters,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Material":
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k != "embedding_vector"})
    
    def get_strength_to_weight_ratio(self) -> float:
        """Calculate specific strength"""
        if self.density_kg_m3 > 0:
            return self.tensile_strength_mpa / (self.density_kg_m3 / 1000)
        return 0.0
    
    def get_stiffness_to_weight_ratio(self) -> float:
        """Calculate specific stiffness"""
        if self.density_kg_m3 > 0:
            return self.youngs_modulus_gpa / (self.density_kg_m3 / 1000)
        return 0.0


class MaterialsDatabase:
    """Database of engineering materials"""
    
    def __init__(self):
        self.materials: Dict[str, Material] = {}
        self._loaded = False
    
    def add_material(self, material: Material) -> None:
        """Add material to database"""
        self.materials[material.material_id] = material
    
    def get_material(self, material_id: str) -> Optional[Material]:
        """Get material by ID"""
        return self.materials.get(material_id)
    
    def get_all_materials(self) -> List[Material]:
        """Get all materials"""
        return list(self.materials.values())
    
    def search_by_class(self, material_class: str) -> List[Material]:
        """Find materials by class"""
        results = []
        for material in self.materials.values():
            if material.material_class.lower() == material_class.lower():
                results.append(material)
        return results
    
    def search_by_property_range(
        self,
        property_name: str,
        min_value: float,
        max_value: float
    ) -> List[Material]:
        """Find materials within property range"""
        results = []
        for material in self.materials.values():
            value = getattr(material, property_name, None)
            if value is not None and min_value <= value <= max_value:
                results.append(material)
        return results
    
    def find_lightweight_strong_materials(
        self,
        max_density: float = 3000,
        min_strength: float = 300
    ) -> List[Material]:
        """Find materials that are both lightweight and strong"""
        results = []
        for material in self.materials.values():
            if (material.density_kg_m3 <= max_density and 
                material.tensile_strength_mpa >= min_strength):
                results.append(material)
        
        # Sort by strength-to-weight ratio
        results.sort(key=lambda m: m.get_strength_to_weight_ratio(), reverse=True)
        return results
    
    def get_materials_for_triz_parameter(self, parameter_id: int) -> List[Material]:
        """Get materials relevant to a TRIZ parameter"""
        results = []
        for material in self.materials.values():
            if parameter_id in material.triz_parameters:
                results.append(material)
        return results
    
    def is_loaded(self) -> bool:
        """Check if database is loaded"""
        return self._loaded and len(self.materials) > 0
    
    def mark_loaded(self) -> None:
        """Mark database as loaded"""
        self._loaded = True