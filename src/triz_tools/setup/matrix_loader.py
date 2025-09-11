#!/usr/bin/env python3
"""
Contradiction Matrix Data Loading (T049)
Loads and processes TRIZ contradiction matrix data.
"""

import json
import csv
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import argparse
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from triz_tools.models.contradiction_matrix import ContradictionMatrix, EngineeringParameter
    from triz_tools.contradiction_matrix import get_matrix_lookup
except ImportError:
    from ..models.contradiction_matrix import ContradictionMatrix, EngineeringParameter
    from ..contradiction_matrix import get_matrix_lookup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MatrixLoader:
    """Loads and processes contradiction matrix data"""
    
    # Standard 39 Engineering Parameters
    ENGINEERING_PARAMETERS = [
        (1, "Weight of moving object", "Mass of object in motion"),
        (2, "Weight of stationary object", "Mass of object at rest"),
        (3, "Length of moving object", "Linear dimension of moving object"),
        (4, "Length of stationary object", "Linear dimension of stationary object"),
        (5, "Area of moving object", "Surface area of moving object"),
        (6, "Area of stationary object", "Surface area of stationary object"),
        (7, "Volume of moving object", "3D space occupied by moving object"),
        (8, "Volume of stationary object", "3D space occupied by stationary object"),
        (9, "Speed", "Velocity of object or process"),
        (10, "Force", "Interaction that changes motion"),
        (11, "Stress or pressure", "Force per unit area"),
        (12, "Shape", "External contour or appearance"),
        (13, "Stability of object's composition", "Integrity of system"),
        (14, "Strength", "Ability to resist force"),
        (15, "Duration of action by moving object", "Time of motion"),
        (16, "Duration of action by stationary object", "Time of static action"),
        (17, "Temperature", "Thermal condition"),
        (18, "Illumination intensity", "Brightness of light"),
        (19, "Use of energy by moving object", "Energy consumption in motion"),
        (20, "Use of energy by stationary object", "Energy consumption at rest"),
        (21, "Power", "Rate of energy use"),
        (22, "Loss of energy", "Waste of energy"),
        (23, "Loss of substance", "Waste of material"),
        (24, "Loss of information", "Loss of data"),
        (25, "Loss of time", "Time waste"),
        (26, "Quantity of substance/matter", "Amount of material"),
        (27, "Reliability", "Ability to perform consistently"),
        (28, "Measurement accuracy", "Precision of measurement"),
        (29, "Manufacturing precision", "Accuracy of production"),
        (30, "External harm affects object", "Susceptibility to external factors"),
        (31, "Object-generated harmful factors", "Side effects produced"),
        (32, "Ease of manufacture", "Simplicity of production"),
        (33, "Ease of operation", "Simplicity of use"),
        (34, "Ease of repair", "Simplicity of maintenance"),
        (35, "Adaptability or versatility", "Flexibility"),
        (36, "Device complexity", "Complexity of system"),
        (37, "Difficulty of detecting/measuring", "Complexity of monitoring"),
        (38, "Extent of automation", "Degree of automation"),
        (39, "Productivity", "Rate of output")
    ]
    
    def __init__(self):
        """
        Initialize matrix loader.
        """
        self.matrix = ContradictionMatrix()
        self.loaded_entries = 0
        
        logger.info("Matrix loader initialized")
    
    def load_standard_matrix(self) -> int:
        """
        Load the standard TRIZ contradiction matrix.
        
        Returns:
            Number of entries loaded
        """
        # Load engineering parameters
        for param_id, name, description in self.ENGINEERING_PARAMETERS:
            self.matrix.add_parameter(
                parameter_id=param_id,
                parameter_name=name,
                description=description
            )
        
        logger.info(f"Loaded {len(self.ENGINEERING_PARAMETERS)} engineering parameters")
        
        # Load standard matrix entries
        # This is a subset of the full 39x39 matrix
        # Format: (improving, worsening, [principles], confidence, applications)
        standard_entries = [
            # Weight of moving object improvements
            (1, 2, [5, 8, 13, 30], 0.85, 50),
            (1, 3, [1, 35, 19, 39], 0.80, 45),
            (1, 9, [2, 14, 29, 30], 0.85, 60),
            (1, 10, [8, 10, 18, 37], 0.75, 40),
            (1, 11, [10, 36, 37, 40], 0.80, 55),
            (1, 14, [1, 8, 15, 40], 0.90, 100),
            (1, 27, [3, 11, 1, 27], 0.75, 35),
            (1, 36, [26, 30, 34, 36], 0.70, 30),
            
            # Speed improvements
            (9, 1, [2, 14, 29, 30], 0.85, 60),
            (9, 2, [14, 20, 35, 10], 0.80, 50),
            (9, 11, [6, 18, 38, 40], 0.75, 45),
            (9, 19, [35, 13, 2, 14], 0.80, 55),
            (9, 28, [28, 32, 1, 24], 0.70, 30),
            
            # Strength improvements
            (14, 1, [1, 8, 40, 15], 0.90, 100),
            (14, 2, [40, 26, 27, 1], 0.85, 80),
            (14, 10, [3, 35, 10, 40], 0.85, 75),
            (14, 11, [30, 10, 40, 3], 0.80, 70),
            (14, 36, [1, 13, 35, 40], 0.75, 45),
            
            # Reliability improvements
            (27, 1, [3, 8, 10, 40], 0.75, 40),
            (27, 9, [11, 35, 27, 28], 0.70, 35),
            (27, 14, [11, 3, 10, 32], 0.80, 60),
            (27, 32, [1, 35, 11, 10], 0.75, 50),
            (27, 33, [17, 27, 8, 40], 0.70, 40),
            (27, 36, [13, 35, 1, 39], 0.75, 45),
            
            # Productivity improvements
            (39, 1, [35, 26, 24, 37], 0.80, 65),
            (39, 9, [35, 10, 2, 14], 0.85, 70),
            (39, 25, [35, 20, 10, 28], 0.85, 75),
            (39, 28, [10, 18, 32, 39], 0.80, 60),
            (39, 33, [32, 1, 10, 25], 0.75, 55),
            (39, 36, [35, 22, 1, 39], 0.75, 50),
            
            # Temperature management
            (17, 1, [36, 22, 6, 38], 0.75, 40),
            (17, 11, [35, 39, 19, 2], 0.70, 35),
            (17, 22, [19, 13, 39, 35], 0.80, 55),
            (17, 27, [19, 13, 39, 35], 0.75, 45),
            
            # Manufacturing ease
            (32, 1, [35, 28, 31, 40], 0.80, 60),
            (32, 14, [1, 3, 10, 32], 0.75, 50),
            (32, 27, [1, 35, 11, 10], 0.75, 50),
            (32, 36, [27, 26, 1, 13], 0.80, 55),
            (32, 39, [1, 28, 13, 27], 0.85, 65),
            
            # Ease of operation
            (33, 1, [32, 26, 12, 17], 0.75, 45),
            (33, 27, [17, 27, 8, 40], 0.70, 40),
            (33, 36, [32, 26, 12, 17], 0.80, 55),
            (33, 39, [1, 16, 25, 2], 0.75, 50),
            
            # Automation improvements
            (38, 14, [8, 35, 40, 3], 0.75, 45),
            (38, 27, [11, 27, 32, 35], 0.80, 55),
            (38, 33, [23, 25, 28, 35], 0.85, 60),
            (38, 36, [13, 35, 24, 1], 0.75, 50),
            (38, 39, [1, 10, 34, 28], 0.85, 65),
        ]
        
        for improving, worsening, principles, confidence, applications in standard_entries:
            self.matrix.add_contradiction(
                improving=improving,
                worsening=worsening,
                principles=principles,
                confidence=confidence,
                applications=applications
            )
            self.loaded_entries += 1
        
        logger.info(f"Loaded {self.loaded_entries} matrix entries")
        return self.loaded_entries
    
    def load_from_csv(
        self,
        csv_file: Path,
        encoding: str = "utf-8"
    ) -> int:
        """
        Load matrix from CSV file.
        
        Expected format:
        improving,worsening,principles,confidence,applications
        
        Args:
            csv_file: Path to CSV file
            encoding: File encoding
        
        Returns:
            Number of entries loaded
        """
        if not csv_file.exists():
            logger.error(f"CSV file not found: {csv_file}")
            return 0
        
        count = 0
        
        try:
            with open(csv_file, "r", encoding=encoding) as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        improving = int(row["improving"])
                        worsening = int(row["worsening"])
                        
                        # Parse principles list
                        principles_str = row["principles"].strip("[]")
                        principles = [int(p.strip()) for p in principles_str.split(",")]
                        
                        confidence = float(row.get("confidence", 0.7))
                        applications = int(row.get("applications", 0))
                        
                        self.matrix.add_contradiction(
                            improving=improving,
                            worsening=worsening,
                            principles=principles,
                            confidence=confidence,
                            applications=applications
                        )
                        
                        count += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to parse row: {row}. Error: {str(e)}")
                        continue
            
            self.loaded_entries += count
            logger.info(f"Loaded {count} entries from CSV")
            return count
            
        except Exception as e:
            logger.error(f"Failed to load CSV: {str(e)}")
            return 0
    
    def load_from_json(
        self,
        json_file: Path
    ) -> int:
        """
        Load matrix from JSON file.
        
        Args:
            json_file: Path to JSON file
        
        Returns:
            Number of entries loaded
        """
        if not json_file.exists():
            logger.error(f"JSON file not found: {json_file}")
            return 0
        
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
            
            count = 0
            
            # Load parameters if present
            for param_data in data.get("parameters", []):
                self.matrix.add_parameter(
                    parameter_id=param_data["id"],
                    parameter_name=param_data["name"],
                    description=param_data.get("description", "")
                )
            
            # Load matrix entries
            for entry in data.get("matrix", []):
                self.matrix.add_contradiction(
                    improving=entry["improving"],
                    worsening=entry["worsening"],
                    principles=entry["principles"],
                    confidence=entry.get("confidence", 0.7),
                    applications=entry.get("applications", 0)
                )
                count += 1
            
            self.loaded_entries += count
            logger.info(f"Loaded {count} entries from JSON")
            return count
            
        except Exception as e:
            logger.error(f"Failed to load JSON: {str(e)}")
            return 0
    
    def save_to_json(
        self,
        output_file: Path
    ) -> bool:
        """
        Save matrix to JSON file.
        
        Args:
            output_file: Output file path
        
        Returns:
            True if successful
        """
        try:
            data = {
                "parameters": [],
                "matrix": []
            }
            
            # Save parameters
            for param in self.matrix.parameters.values():
                data["parameters"].append({
                    "id": param.parameter_id,
                    "name": param.parameter_name,
                    "description": param.description
                })
            
            # Save matrix entries
            for key, result in self.matrix.matrix.items():
                data["matrix"].append({
                    "improving": key[0],
                    "worsening": key[1],
                    "principles": result.recommended_principles,
                    "confidence": result.confidence_score,
                    "applications": result.application_frequency
                })
            
            # Write file
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved matrix to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save matrix: {str(e)}")
            return False
    
    def save_to_csv(
        self,
        output_file: Path
    ) -> bool:
        """
        Save matrix to CSV file.
        
        Args:
            output_file: Output file path
        
        Returns:
            True if successful
        """
        try:
            rows = []
            
            for key, result in self.matrix.matrix.items():
                rows.append({
                    "improving": key[0],
                    "worsening": key[1],
                    "principles": str(result.recommended_principles),
                    "confidence": result.confidence_score,
                    "applications": result.application_frequency
                })
            
            if not rows:
                logger.warning("No matrix entries to save")
                return False
            
            # Write CSV
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, "w", newline="") as f:
                fieldnames = ["improving", "worsening", "principles", "confidence", "applications"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            logger.info(f"Saved matrix to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save CSV: {str(e)}")
            return False
    
    def apply_to_lookup(self) -> bool:
        """
        Apply loaded matrix to the global lookup singleton.
        
        Returns:
            True if successful
        """
        try:
            lookup = get_matrix_lookup(reset=True)
            
            # Replace the matrix
            lookup.matrix = self.matrix
            
            # Rebuild reverse index
            lookup._build_reverse_index()
            
            logger.info(f"Applied {len(self.matrix.matrix)} entries to global lookup")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply to lookup: {str(e)}")
            return False
    
    def generate_full_matrix(self) -> int:
        """
        Generate a more complete matrix with common patterns.
        
        Returns:
            Number of entries generated
        """
        # Common principle patterns for different contradiction types
        patterns = {
            # Physical contradictions
            "weight_vs_strength": [1, 8, 15, 40],
            "size_vs_strength": [1, 10, 35, 40],
            "speed_vs_accuracy": [2, 14, 29, 30],
            "speed_vs_safety": [11, 35, 27, 28],
            
            # Resource contradictions
            "cost_vs_quality": [35, 1, 10, 27],
            "energy_vs_performance": [2, 14, 35, 40],
            "material_vs_strength": [35, 40, 27, 39],
            
            # Complexity contradictions
            "simplicity_vs_functionality": [1, 2, 13, 35],
            "automation_vs_flexibility": [35, 1, 24, 15],
            
            # Manufacturing contradictions
            "ease_vs_precision": [1, 13, 32, 35],
            "speed_vs_quality": [10, 18, 32, 39],
        }
        
        count = 0
        
        # Generate entries based on patterns
        for i in range(1, 40):
            for j in range(1, 40):
                if i == j:
                    continue
                
                # Skip if already exists
                if (i, j) in self.matrix.matrix:
                    continue
                
                # Determine pattern based on parameter types
                principles = None
                confidence = 0.6  # Default confidence for generated entries
                
                # Weight-related
                if i in [1, 2] and j in [14, 11]:
                    principles = patterns["weight_vs_strength"]
                    confidence = 0.85
                
                # Speed-related
                elif i == 9 and j in [28, 29]:
                    principles = patterns["speed_vs_accuracy"]
                    confidence = 0.80
                
                # Manufacturing-related
                elif i in [32, 33] and j in [29, 39]:
                    principles = patterns["ease_vs_precision"]
                    confidence = 0.75
                
                # Automation-related
                elif i == 38 and j in [35, 33]:
                    principles = patterns["automation_vs_flexibility"]
                    confidence = 0.70
                
                # Generate some entries with common principles
                elif count < 100:  # Limit generation
                    # Use most common principles
                    principles = [35, 1, 10, 2]  # Most versatile principles
                    confidence = 0.5
                
                if principles:
                    self.matrix.add_contradiction(
                        improving=i,
                        worsening=j,
                        principles=principles,
                        confidence=confidence,
                        applications=0
                    )
                    count += 1
        
        self.loaded_entries += count
        logger.info(f"Generated {count} additional matrix entries")
        return count


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Load TRIZ contradiction matrix")
    parser.add_argument(
        "--standard",
        action="store_true",
        help="Load standard matrix"
    )
    parser.add_argument(
        "--csv",
        type=Path,
        help="Load from CSV file"
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="Load from JSON file"
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate additional entries"
    )
    parser.add_argument(
        "--save-json",
        type=Path,
        help="Save to JSON file"
    )
    parser.add_argument(
        "--save-csv",
        type=Path,
        help="Save to CSV file"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply to global lookup"
    )
    
    args = parser.parse_args()
    
    loader = MatrixLoader()
    
    # Load data
    if args.standard:
        count = loader.load_standard_matrix()
        print(f"Loaded standard matrix with {count} entries")
    
    if args.csv:
        count = loader.load_from_csv(args.csv)
        print(f"Loaded {count} entries from {args.csv}")
    
    if args.json:
        count = loader.load_from_json(args.json)
        print(f"Loaded {count} entries from {args.json}")
    
    if args.generate:
        count = loader.generate_full_matrix()
        print(f"Generated {count} additional entries")
    
    # Save data
    if args.save_json:
        success = loader.save_to_json(args.save_json)
        if success:
            print(f"Saved matrix to {args.save_json}")
    
    if args.save_csv:
        success = loader.save_to_csv(args.save_csv)
        if success:
            print(f"Saved matrix to {args.save_csv}")
    
    # Apply to lookup
    if args.apply:
        success = loader.apply_to_lookup()
        if success:
            print("Applied matrix to global lookup")
    
    print(f"\nTotal entries loaded: {loader.loaded_entries}")
    print(f"Matrix size: {len(loader.matrix.matrix)} contradictions")
    print(f"Parameters defined: {len(loader.matrix.parameters)}")


if __name__ == "__main__":
    main()