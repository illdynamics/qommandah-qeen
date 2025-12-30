import json
import os
from typing import Dict, Any, List, Optional
from shared.types import LevelData
from shared.exceptions import LevelException, ValidationException

class LevelLoader:
    """
    Loads and validates level data from JSON files.
    """
    
    def __init__(self, levels_directory: str = "levels"):
        """
        Initialize the level loader.
        
        Args:
            levels_directory: Directory containing level JSON files
        """
        self.levels_directory = levels_directory
        
    def load_level(self, level_name: str) -> LevelData:
        """
        Load a level by name.
        
        Args:
            level_name: Name of the level file (without .json extension)
            
        Returns:
            LevelData: Parsed level data
            
        Raises:
            LevelException: If level file cannot be loaded
            ValidationException: If level data is invalid
        """
        try:
            # Construct the file path
            filename = f"{level_name}.json"
            filepath = os.path.join(self.levels_directory, filename)
            
            # Load and parse the JSON file
            with open(filepath, 'r') as f:
                raw_data = json.load(f)
            
            # Validate the level data
            self._validate_level_data(raw_data)
            
            # Convert to LevelData object
            level_data = self._parse_level_data(raw_data)
            
            return level_data
            
        except FileNotFoundError:
            raise LevelException(f"Level file not found: {level_name}")
        except json.JSONDecodeError as e:
            raise LevelException(f"Invalid JSON in level file {level_name}: {e}")
        except Exception as e:
            raise LevelException(f"Error loading level {level_name}: {e}")
    
    def _validate_level_data(self, data: Dict[str, Any]) -> None:
        """
        Validate level data structure.
        
        Args:
            data: Raw level data dictionary
            
        Raises:
            ValidationException: If validation fails
        """
        # Check required fields
        required_fields = ["name", "width", "height", "tiles", "entities"]
        for field in required_fields:
            if field not in data:
                raise ValidationException(f"Missing required field: {field}")
        
        # Validate dimensions
        width = data["width"]
        height = data["height"]
        
        if not isinstance(width, int) or width <= 0:
            raise ValidationException(f"Invalid width: {width}")
        if not isinstance(height, int) or height <= 0:
            raise ValidationException(f"Invalid height: {height}")
        
        # Validate tiles array
        tiles = data["tiles"]
        if not isinstance(tiles, list):
            raise ValidationException("Tiles must be a list")
        
        if len(tiles) != height:
            raise ValidationException(f"Tiles height ({len(tiles)}) doesn't match level height ({height})")
        
        for row_idx, row in enumerate(tiles):
            if not isinstance(row, list):
                raise ValidationException(f"Row {row_idx} must be a list")
            
            if len(row) != width:
                raise ValidationException(f"Row {row_idx} width ({len(row)}) doesn't match level width ({width})")
            
            for tile_idx, tile in enumerate(row):
                if not isinstance(tile, int):
                    raise ValidationException(f"Tile at [{row_idx}][{tile_idx}] must be an integer")
        
        # Validate entities array
        entities = data.get("entities", [])
        if not isinstance(entities, list):
            raise ValidationException("Entities must be a list")
        
        for entity_idx, entity in enumerate(entities):
            if not isinstance(entity, dict):
                raise ValidationException(f"Entity {entity_idx} must be a dictionary")
            
            if "type" not in entity:
                raise ValidationException(f"Entity {entity_idx} missing 'type' field")
            
            if "x" not in entity or "y" not in entity:
                raise ValidationException(f"Entity {entity_idx} missing position fields")
            
            # Validate position is within bounds
            x = entity["x"]
            y = entity["y"]
            
            if not isinstance(x, (int, float)):
                raise ValidationException(f"Entity {entity_idx} x position must be a number")
            if not isinstance(y, (int, float)):
                raise ValidationException(f"Entity {entity_idx} y position must be a number")
            
            if x < 0 or x >= width:
                raise ValidationException(f"Entity {entity_idx} x position {x} out of bounds [0, {width})")
            if y < 0 or y >= height:
                raise ValidationException(f"Entity {entity_idx} y position {y} out of bounds [0, {height})")
        
        # Validate modes (optional)
        modes = data.get("modes", [])
        if not isinstance(modes, list):
            raise ValidationException("Modes must be a list")
        
        for mode_idx, mode in enumerate(modes):
            if not isinstance(mode, str):
                raise ValidationException(f"Mode {mode_idx} must be a string")
    
    def _parse_level_data(self, data: Dict[str, Any]) -> LevelData:
        """
        Parse raw level data into LevelData object.
        
        Args:
            data: Validated level data dictionary
            
        Returns:
            LevelData: Parsed level data object
        """
        return LevelData(
            name=data["name"],
            width=data["width"],
            height=data["height"],
            tiles=data["tiles"],
            entities=data["entities"],
            modes=data.get("modes", []),
            background=data.get("background", "default"),
            music=data.get("music", "")
        )
    
    def get_available_levels(self) -> List[str]:
        """
        Get list of available level files.
        
        Returns:
            List of level names (without .json extension)
        """
        try:
            levels = []
            for filename in os.listdir(self.levels_directory):
                if filename.endswith(".json"):
                    level_name = filename[:-5]  # Remove .json extension
                    levels.append(level_name)
            return sorted(levels)
        except FileNotFoundError:
            return []
    
    def validate_all_levels(self) -> Dict[str, List[str]]:
        """
        Validate all level files in the levels directory.
        
        Returns:
            Dictionary mapping level names to lists of validation errors
        """
        errors = {}
        available_levels = self.get_available_levels()
        
        for level_name in available_levels:
            try:
                self.load_level(level_name)
            except (LevelException, ValidationException) as e:
                errors[level_name] = [str(e)]
        
        return errors