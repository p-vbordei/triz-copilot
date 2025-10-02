#!/usr/bin/env python3
"""
Materials Database Ingestion (T048)
Ingests engineering materials data into the system.
"""

import json
import csv
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from triz_tools.services.materials_service import Material, get_materials_service
    from triz_tools.services.vector_service import get_vector_service
    from triz_tools.services.embedding_service import get_embedding_service
except ImportError:
    from ..services.materials_service import Material, get_materials_service
    from ..services.vector_service import get_vector_service
    from ..services.embedding_service import get_embedding_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MaterialsIngestion:
    """Handles ingestion of materials data"""
    
    def __init__(self):
        """
        Initialize materials ingestion.
        """
        self.materials_service = get_materials_service()
        self.vector_service = get_vector_service()
        self.embedding_service = get_embedding_service()

        self.collection_name = "materials_database"
        self.ingested_count = 0
        
        logger.info("Materials ingestion initialized")
    
    def ingest_csv(
        self,
        csv_file: Path,
        encoding: str = "utf-8"
    ) -> int:
        """
        Ingest materials from CSV file.
        
        Expected CSV columns:
        - material_id: Unique identifier
        - name: Material name
        - category: Material category
        - density: Density (g/cm³)
        - tensile_strength: Tensile strength (MPa)
        - yield_strength: Yield strength (MPa)
        - elastic_modulus: Elastic modulus (GPa)
        - thermal_conductivity: Thermal conductivity (W/m·K)
        - advantages: Semicolon-separated list
        - disadvantages: Semicolon-separated list
        - applications: Semicolon-separated list
        - cost_index: Cost index (1-10)
        - sustainability_score: Sustainability (0-1)
        
        Args:
            csv_file: Path to CSV file
            encoding: File encoding
        
        Returns:
            Number of materials ingested
        """
        if not csv_file.exists():
            logger.error(f"CSV file not found: {csv_file}")
            return 0
        
        materials = []
        
        try:
            with open(csv_file, "r", encoding=encoding) as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        # Map field names from different CSV formats
                        name = row.get("name") or row.get("material_name")
                        category = row.get("category") or row.get("material_class", "unknown")

                        # Parse properties with field name mapping
                        properties = {}
                        prop_mappings = {
                            "density": ["density", "density_kg_m3"],
                            "tensile_strength": ["tensile_strength", "tensile_strength_mpa"],
                            "yield_strength": ["yield_strength", "yield_strength_mpa"],
                            "elastic_modulus": ["elastic_modulus", "youngs_modulus_gpa"],
                            "thermal_conductivity": ["thermal_conductivity", "thermal_conductivity_w_mk"]
                        }

                        for prop_key, possible_names in prop_mappings.items():
                            for name_variant in possible_names:
                                if name_variant in row and row[name_variant]:
                                    try:
                                        properties[prop_key] = float(row[name_variant])
                                        break
                                    except (ValueError, TypeError):
                                        pass

                        # Parse lists - split by comma or semicolon
                        advantages = [a.strip() for a in row.get("advantages", "").replace(";", ",").split(",") if a.strip()]
                        disadvantages = [d.strip() for d in row.get("disadvantages", "").replace(";", ",").split(",") if d.strip()]
                        applications = [a.strip() for a in row.get("applications", "").replace(";", ",").split(",") if a.strip()]

                        # Create material
                        material = Material(
                            material_id=row["material_id"],
                            name=name,
                            category=category,
                            properties=properties,
                            advantages=advantages,
                            disadvantages=disadvantages,
                            applications=applications,
                            cost_index=float(row.get("cost_index", 5.0)),
                            sustainability_score=float(row.get("sustainability_score", 0.5))
                        )
                        
                        materials.append(material)
                        
                    except Exception as e:
                        logger.warning(f"Failed to parse row: {row}. Error: {str(e)}")
                        continue
            
            logger.info(f"Parsed {len(materials)} materials from CSV")
            
            # Add to materials service
            for material in materials:
                self.materials_service.materials[material.material_id] = material
                self.ingested_count += 1
            
            # Generate embeddings and store in vector DB
            self._generate_material_embeddings(materials)
            
            return len(materials)
            
        except Exception as e:
            logger.error(f"Failed to ingest CSV: {str(e)}")
            return 0
    
    def ingest_json(
        self,
        json_file: Path
    ) -> int:
        """
        Ingest materials from JSON file.
        
        Args:
            json_file: Path to JSON file
        
        Returns:
            Number of materials ingested
        """
        if not json_file.exists():
            logger.error(f"JSON file not found: {json_file}")
            return 0
        
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
            
            materials = []
            
            for mat_data in data.get("materials", []):
                try:
                    material = Material(**mat_data)
                    materials.append(material)
                except Exception as e:
                    logger.warning(f"Failed to parse material: {mat_data}. Error: {str(e)}")
                    continue
            
            logger.info(f"Parsed {len(materials)} materials from JSON")
            
            # Add to materials service
            for material in materials:
                self.materials_service.materials[material.material_id] = material
                self.ingested_count += 1
            
            # Generate embeddings and store in vector DB
            self._generate_material_embeddings(materials)
            
            return len(materials)
            
        except Exception as e:
            logger.error(f"Failed to ingest JSON: {str(e)}")
            return 0
    
    def ingest_directory(
        self,
        directory: Path,
        pattern: str = "*.csv"
    ) -> int:
        """
        Ingest all materials files from directory.
        
        Args:
            directory: Directory path
            pattern: File pattern
        
        Returns:
            Total materials ingested
        """
        if not directory.exists():
            logger.error(f"Directory not found: {directory}")
            return 0
        
        total = 0
        
        # Process CSV files
        for csv_file in directory.glob("*.csv"):
            logger.info(f"Processing {csv_file}")
            count = self.ingest_csv(csv_file)
            total += count
        
        # Process JSON files
        for json_file in directory.glob("*.json"):
            logger.info(f"Processing {json_file}")
            count = self.ingest_json(json_file)
            total += count
        
        return total
    
    def _generate_material_embeddings(
        self,
        materials: List[Material]
    ):
        """
        Generate embeddings for materials.
        
        Args:
            materials: List of materials
        """
        logger.info(f"Generating embeddings for {len(materials)} materials")
        
        # Ensure collection exists
        try:
            self.vector_service.create_collection(
                collection_name=self.collection_name,
                vector_size=768  # nomic-embed-text dimension
            )
        except Exception as e:
            logger.debug(f"Collection may already exist: {str(e)}")
        
        for material in materials:
            try:
                # Create text representation
                text = self._material_to_text(material)
                
                # Generate embedding
                embedding = self.embedding_service.generate_embedding(text)
                
                if embedding is not None:
                    # Store in vector DB with correct method name
                    try:
                        # Use insert_vectors with proper parameters
                        import uuid
                        self.vector_service.insert_vectors(
                            collection_name=self.collection_name,
                            vectors=[embedding],
                            payloads=[{
                                "material_id": material.material_id,
                                "name": material.name,
                                "category": material.category,
                                "properties": material.properties,
                                "advantages": material.advantages,
                                "applications": material.applications,
                                "cost_index": material.cost_index,
                                "sustainability_score": material.sustainability_score
                            }],
                            ids=[abs(hash(material.material_id)) % (10 ** 8)]  # Generate numeric ID from string
                        )
                    except AttributeError:
                        # Fallback for different API
                        logger.warning(f"Could not insert vector for {material.name} - API mismatch")
                        pass
                    
                    logger.debug(f"Added embedding for {material.name}")
                
            except Exception as e:
                logger.warning(f"Failed to generate embedding for {material.name}: {str(e)}")
                continue
    
    def _material_to_text(self, material: Material) -> str:
        """
        Convert material to text for embedding.
        
        Args:
            material: Material object
        
        Returns:
            Text representation
        """
        parts = [
            f"Material: {material.name}",
            f"Category: {material.category}"
        ]
        
        # Add properties
        for prop, value in material.properties.items():
            parts.append(f"{prop.replace('_', ' ').title()}: {value}")
        
        # Add advantages
        if material.advantages:
            parts.append(f"Advantages: {', '.join(material.advantages)}")
        
        # Add applications
        if material.applications:
            parts.append(f"Applications: {', '.join(material.applications)}")
        
        return " | ".join(parts)
    
    def create_default_database(self) -> int:
        """
        Create default materials database.
        
        Returns:
            Number of materials created
        """
        default_csv = Path(__file__).parent.parent / "data" / "materials_database.csv"
        
        if not default_csv.exists():
            # Create default CSV
            logger.info("Creating default materials database")
            
            default_materials = [
                {
                    "material_id": "al_7075",
                    "name": "Aluminum 7075",
                    "category": "metals",
                    "density": 2.81,
                    "tensile_strength": 572,
                    "yield_strength": 503,
                    "elastic_modulus": 71.7,
                    "thermal_conductivity": 130,
                    "advantages": "High strength-to-weight ratio;Good fatigue resistance;Excellent machinability",
                    "disadvantages": "Lower corrosion resistance;Difficult to weld",
                    "applications": "Aircraft structures;Aerospace components;High-stress parts",
                    "cost_index": 7.5,
                    "sustainability_score": 0.7
                },
                {
                    "material_id": "ti_6al4v",
                    "name": "Titanium Ti-6Al-4V",
                    "category": "metals",
                    "density": 4.43,
                    "tensile_strength": 950,
                    "yield_strength": 880,
                    "elastic_modulus": 113.8,
                    "thermal_conductivity": 6.7,
                    "advantages": "Excellent strength-to-weight;Superior corrosion resistance;Biocompatible",
                    "disadvantages": "Very expensive;Difficult to machine",
                    "applications": "Aerospace structures;Medical implants;Marine applications",
                    "cost_index": 9.5,
                    "sustainability_score": 0.6
                },
                {
                    "material_id": "cfrp",
                    "name": "Carbon Fiber Reinforced Polymer",
                    "category": "composites",
                    "density": 1.55,
                    "tensile_strength": 1500,
                    "yield_strength": 0,
                    "elastic_modulus": 150,
                    "thermal_conductivity": 7,
                    "advantages": "Exceptional strength-to-weight;High stiffness;Design flexibility",
                    "disadvantages": "High cost;Complex manufacturing;Difficult to repair",
                    "applications": "Aerospace primary structures;Racing vehicles;Sports equipment",
                    "cost_index": 9.0,
                    "sustainability_score": 0.4
                },
                {
                    "material_id": "steel_4340",
                    "name": "AISI 4340 Steel",
                    "category": "metals",
                    "density": 7.85,
                    "tensile_strength": 1280,
                    "yield_strength": 1090,
                    "elastic_modulus": 205,
                    "thermal_conductivity": 44,
                    "advantages": "High strength;Good toughness;Heat treatable",
                    "disadvantages": "Heavy weight;Susceptible to corrosion",
                    "applications": "Aircraft landing gear;Power transmission;Heavy machinery",
                    "cost_index": 5.0,
                    "sustainability_score": 0.8
                },
                {
                    "material_id": "peek",
                    "name": "PEEK (Polyetheretherketone)",
                    "category": "polymers",
                    "density": 1.32,
                    "tensile_strength": 100,
                    "yield_strength": 95,
                    "elastic_modulus": 3.6,
                    "thermal_conductivity": 0.25,
                    "advantages": "High temperature resistance;Chemical resistance;Biocompatible",
                    "disadvantages": "Very expensive;Requires high processing temps",
                    "applications": "Medical implants;Aerospace components;Chemical processing",
                    "cost_index": 9.8,
                    "sustainability_score": 0.5
                }
            ]
            
            # Write CSV
            default_csv.parent.mkdir(parents=True, exist_ok=True)
            
            with open(default_csv, "w", newline="") as f:
                fieldnames = list(default_materials[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(default_materials)
            
            logger.info(f"Created default database at {default_csv}")
        
        # Ingest the default database
        return self.ingest_csv(default_csv)
    
    def export_database(
        self,
        output_file: Path,
        format_type: str = "json"
    ) -> bool:
        """
        Export materials database.
        
        Args:
            output_file: Output file path
            format_type: Export format (json or csv)
        
        Returns:
            True if successful
        """
        try:
            materials = list(self.materials_service.materials.values())
            
            if format_type == "json":
                data = {
                    "materials": [
                        {
                            "material_id": m.material_id,
                            "name": m.name,
                            "category": m.category,
                            "properties": m.properties,
                            "advantages": m.advantages,
                            "disadvantages": m.disadvantages,
                            "applications": m.applications,
                            "cost_index": m.cost_index,
                            "sustainability_score": m.sustainability_score
                        }
                        for m in materials
                    ]
                }
                
                with open(output_file, "w") as f:
                    json.dump(data, f, indent=2)
            
            elif format_type == "csv":
                if not materials:
                    logger.warning("No materials to export")
                    return False
                
                # Flatten for CSV
                rows = []
                for m in materials:
                    row = {
                        "material_id": m.material_id,
                        "name": m.name,
                        "category": m.category,
                        "cost_index": m.cost_index,
                        "sustainability_score": m.sustainability_score
                    }
                    
                    # Add properties
                    for prop, value in m.properties.items():
                        row[prop] = value
                    
                    # Add lists
                    row["advantages"] = ";".join(m.advantages)
                    row["disadvantages"] = ";".join(m.disadvantages)
                    row["applications"] = ";".join(m.applications)
                    
                    rows.append(row)
                
                # Write CSV
                fieldnames = list(rows[0].keys())
                with open(output_file, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
            
            logger.info(f"Exported {len(materials)} materials to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export database: {str(e)}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Ingest materials database")
    parser.add_argument(
        "--csv",
        type=Path,
        help="CSV file to ingest"
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="JSON file to ingest"
    )
    parser.add_argument(
        "--directory",
        type=Path,
        help="Directory containing materials files"
    )
    parser.add_argument(
        "--create-default",
        action="store_true",
        help="Create and ingest default database"
    )
    parser.add_argument(
        "--export",
        type=Path,
        help="Export database to file"
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Export format"
    )
    
    args = parser.parse_args()
    
    ingestion = MaterialsIngestion()
    
    if args.create_default:
        count = ingestion.create_default_database()
        print(f"Created and ingested {count} default materials")
    
    if args.csv:
        count = ingestion.ingest_csv(args.csv)
        print(f"Ingested {count} materials from {args.csv}")
    
    if args.json:
        count = ingestion.ingest_json(args.json)
        print(f"Ingested {count} materials from {args.json}")
    
    if args.directory:
        count = ingestion.ingest_directory(args.directory)
        print(f"Ingested {count} materials from {args.directory}")
    
    if args.export:
        success = ingestion.export_database(args.export, args.format)
        if success:
            print(f"Exported database to {args.export}")
        else:
            print("Export failed")
    
    if ingestion.ingested_count > 0:
        print(f"\nTotal materials ingested: {ingestion.ingested_count}")


if __name__ == "__main__":
    main()