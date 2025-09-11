"""
Materials Recommendation Service (T032)
Recommends engineering materials based on TRIZ analysis.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Material:
    """Engineering material data"""
    material_id: str
    name: str
    category: str
    properties: Dict[str, float]
    advantages: List[str]
    disadvantages: List[str]
    applications: List[str]
    cost_index: float  # 1-10 scale
    sustainability_score: float  # 0-1 scale
    
    def matches_requirements(self, requirements: Dict[str, Any]) -> float:
        """Calculate match score for requirements"""
        score = 0.0
        total_weight = 0.0
        
        for req_prop, req_value in requirements.items():
            if req_prop in self.properties:
                # Calculate how well property matches
                actual = self.properties[req_prop]
                if isinstance(req_value, dict):
                    # Range requirement
                    if "min" in req_value and actual >= req_value["min"]:
                        score += 1.0
                    if "max" in req_value and actual <= req_value["max"]:
                        score += 1.0
                    total_weight += 2.0
                else:
                    # Target value
                    diff = abs(actual - req_value) / max(actual, req_value)
                    score += max(0, 1.0 - diff)
                    total_weight += 1.0
        
        return score / total_weight if total_weight > 0 else 0.0


class MaterialsService:
    """Service for materials recommendation"""
    
    def __init__(self, data_file: Optional[Path] = None):
        """
        Initialize materials service.
        
        Args:
            data_file: Path to materials database
        """
        self.materials: Dict[str, Material] = {}
        self._load_materials_database(data_file)
        
        # Category mappings
        self.categories = {
            "metals": ["steel", "aluminum", "titanium", "copper", "brass"],
            "polymers": ["plastic", "rubber", "elastomer", "thermoplastic"],
            "ceramics": ["ceramic", "glass", "porcelain", "silicon"],
            "composites": ["carbon fiber", "fiberglass", "kevlar", "composite"],
            "natural": ["wood", "bamboo", "cork", "natural fiber"]
        }
        
        logger.info(f"Materials service initialized with {len(self.materials)} materials")
    
    def _load_materials_database(self, data_file: Optional[Path] = None):
        """Load materials from database"""
        if data_file is None:
            # Use default materials
            self._load_default_materials()
        elif data_file.exists():
            try:
                with open(data_file, "r") as f:
                    data = json.load(f)
                    for mat_data in data.get("materials", []):
                        material = Material(**mat_data)
                        self.materials[material.material_id] = material
            except Exception as e:
                logger.error(f"Failed to load materials: {str(e)}")
                self._load_default_materials()
        else:
            self._load_default_materials()
    
    def _load_default_materials(self):
        """Load default materials database"""
        default_materials = [
            Material(
                material_id="al_7075",
                name="Aluminum 7075",
                category="metals",
                properties={
                    "density": 2.81,  # g/cm³
                    "tensile_strength": 572,  # MPa
                    "yield_strength": 503,  # MPa
                    "elastic_modulus": 71.7,  # GPa
                    "thermal_conductivity": 130,  # W/m·K
                },
                advantages=[
                    "High strength-to-weight ratio",
                    "Good fatigue resistance",
                    "Excellent machinability"
                ],
                disadvantages=[
                    "Lower corrosion resistance",
                    "Difficult to weld",
                    "Higher cost than standard aluminum"
                ],
                applications=[
                    "Aircraft structures",
                    "Aerospace components",
                    "High-stress parts"
                ],
                cost_index=7.5,
                sustainability_score=0.7
            ),
            Material(
                material_id="ti_6al4v",
                name="Titanium Ti-6Al-4V",
                category="metals",
                properties={
                    "density": 4.43,  # g/cm³
                    "tensile_strength": 950,  # MPa
                    "yield_strength": 880,  # MPa
                    "elastic_modulus": 113.8,  # GPa
                    "thermal_conductivity": 6.7,  # W/m·K
                },
                advantages=[
                    "Excellent strength-to-weight ratio",
                    "Superior corrosion resistance",
                    "Biocompatible",
                    "High temperature resistance"
                ],
                disadvantages=[
                    "Very expensive",
                    "Difficult to machine",
                    "Poor thermal conductor"
                ],
                applications=[
                    "Aerospace structures",
                    "Medical implants",
                    "Marine applications"
                ],
                cost_index=9.5,
                sustainability_score=0.6
            ),
            Material(
                material_id="cfrp",
                name="Carbon Fiber Reinforced Polymer",
                category="composites",
                properties={
                    "density": 1.55,  # g/cm³
                    "tensile_strength": 1500,  # MPa
                    "elastic_modulus": 150,  # GPa
                    "thermal_conductivity": 7,  # W/m·K
                },
                advantages=[
                    "Exceptional strength-to-weight ratio",
                    "High stiffness",
                    "Design flexibility",
                    "Fatigue resistance"
                ],
                disadvantages=[
                    "High cost",
                    "Complex manufacturing",
                    "Difficult to repair",
                    "Brittle failure mode"
                ],
                applications=[
                    "Aerospace primary structures",
                    "Racing vehicles",
                    "Sports equipment"
                ],
                cost_index=9.0,
                sustainability_score=0.4
            ),
            Material(
                material_id="steel_4340",
                name="AISI 4340 Steel",
                category="metals",
                properties={
                    "density": 7.85,  # g/cm³
                    "tensile_strength": 1280,  # MPa
                    "yield_strength": 1090,  # MPa
                    "elastic_modulus": 205,  # GPa
                    "thermal_conductivity": 44,  # W/m·K
                },
                advantages=[
                    "High strength",
                    "Good toughness",
                    "Heat treatable",
                    "Good fatigue life"
                ],
                disadvantages=[
                    "Heavy weight",
                    "Susceptible to corrosion",
                    "Requires heat treatment"
                ],
                applications=[
                    "Aircraft landing gear",
                    "Power transmission",
                    "Heavy machinery"
                ],
                cost_index=5.0,
                sustainability_score=0.8
            )
        ]
        
        for material in default_materials:
            self.materials[material.material_id] = material
    
    def recommend_materials(
        self,
        requirements: Dict[str, Any],
        constraints: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recommend materials based on requirements.
        
        Args:
            requirements: Property requirements
            constraints: Additional constraints
            top_k: Number of recommendations
        
        Returns:
            List of material recommendations
        """
        if constraints is None:
            constraints = []
        
        recommendations = []
        
        for material in self.materials.values():
            # Check constraints
            skip = False
            for constraint in constraints:
                if "no_" in constraint:
                    excluded = constraint.replace("no_", "")
                    if excluded in material.category or excluded in material.name.lower():
                        skip = True
                        break
            
            if skip:
                continue
            
            # Calculate match score
            match_score = material.matches_requirements(requirements)
            
            # Consider cost and sustainability
            cost_factor = 1.0 - (material.cost_index / 10.0) * 0.3
            sustainability_factor = material.sustainability_score * 0.2
            
            total_score = match_score * cost_factor + sustainability_factor
            
            recommendations.append({
                "material": material,
                "match_score": match_score,
                "total_score": total_score,
                "cost_index": material.cost_index,
                "sustainability": material.sustainability_score
            })
        
        # Sort by total score
        recommendations.sort(key=lambda x: x["total_score"], reverse=True)
        
        # Format results
        results = []
        for rec in recommendations[:top_k]:
            material = rec["material"]
            results.append({
                "material_id": material.material_id,
                "name": material.name,
                "category": material.category,
                "match_score": round(rec["match_score"], 2),
                "properties": material.properties,
                "advantages": material.advantages[:3],
                "disadvantages": material.disadvantages[:2],
                "applications": material.applications[:2],
                "cost_index": material.cost_index,
                "sustainability_score": material.sustainability_score
            })
        
        return results
    
    def get_material(self, material_id: str) -> Optional[Material]:
        """Get material by ID"""
        return self.materials.get(material_id)
    
    def search_materials(
        self,
        query: str,
        category: Optional[str] = None
    ) -> List[Material]:
        """
        Search materials by text query.
        
        Args:
            query: Search query
            category: Filter by category
        
        Returns:
            List of matching materials
        """
        query_lower = query.lower()
        results = []
        
        for material in self.materials.values():
            # Check category filter
            if category and material.category != category:
                continue
            
            # Search in various fields
            if (query_lower in material.name.lower() or
                query_lower in material.category or
                any(query_lower in app.lower() for app in material.applications) or
                any(query_lower in adv.lower() for adv in material.advantages)):
                
                results.append(material)
        
        return results
    
    def compare_materials(
        self,
        material_ids: List[str],
        properties: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple materials.
        
        Args:
            material_ids: List of material IDs
            properties: Properties to compare
        
        Returns:
            Comparison table
        """
        if properties is None:
            properties = ["density", "tensile_strength", "cost_index"]
        
        comparison = {
            "materials": [],
            "properties": {}
        }
        
        for mat_id in material_ids:
            material = self.materials.get(mat_id)
            if material:
                comparison["materials"].append({
                    "id": mat_id,
                    "name": material.name,
                    "category": material.category
                })
                
                for prop in properties:
                    if prop not in comparison["properties"]:
                        comparison["properties"][prop] = []
                    
                    value = material.properties.get(prop, 
                            getattr(material, prop, None))
                    comparison["properties"][prop].append(value)
        
        return comparison
    
    def get_materials_for_principle(
        self,
        principle_id: int
    ) -> List[Material]:
        """
        Get materials relevant to a TRIZ principle.
        
        Args:
            principle_id: TRIZ principle number
        
        Returns:
            List of relevant materials
        """
        # Map principles to material properties
        principle_materials = {
            1: ["composites"],  # Segmentation
            2: ["composites", "polymers"],  # Taking out
            3: ["composites"],  # Local quality
            14: ["metals", "composites"],  # Spheroidality
            17: ["composites"],  # Another dimension
            24: ["composites", "polymers"],  # Intermediary
            26: ["polymers"],  # Copying
            27: ["polymers", "composites"],  # Cheap short-living
            28: ["smart materials"],  # Mechanics substitution
            30: ["polymers", "elastomers"],  # Flexible shells
            31: ["porous materials"],  # Porous materials
            32: ["optical materials"],  # Color changes
            35: ["smart materials", "composites"],  # Parameter changes
            36: ["phase change materials"],  # Phase transitions
            40: ["composites"]  # Composite materials
        }
        
        categories = principle_materials.get(principle_id, ["metals"])
        
        results = []
        for material in self.materials.values():
            if material.category in categories:
                results.append(material)
        
        return results


# Singleton instance
_materials_service: Optional[MaterialsService] = None


def get_materials_service(
    data_file: Optional[Path] = None,
    reset: bool = False
) -> MaterialsService:
    """Get or create materials service singleton"""
    global _materials_service
    
    if reset or _materials_service is None:
        _materials_service = MaterialsService(data_file=data_file)
    
    return _materials_service