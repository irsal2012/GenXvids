"""
Template customization engine for dynamic parameter modification
"""

from typing import Dict, Any, List, Optional
import json
import copy
from app.schemas.template import TemplateConfig, Scene, SceneElement
import logging

logger = logging.getLogger(__name__)


class TemplateCustomizer:
    """Engine for customizing template parameters dynamically"""
    
    @staticmethod
    def customize_template(
        template_config: Dict[str, Any],
        customizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply customizations to a template configuration
        
        Args:
            template_config: Original template configuration
            customizations: Dictionary of customizations to apply
            
        Returns:
            Customized template configuration
        """
        try:
            # Deep copy to avoid modifying original
            customized_config = copy.deepcopy(template_config)
            
            # Apply global customizations
            if "duration" in customizations:
                customized_config["duration"] = customizations["duration"]
                # Adjust scene durations proportionally
                TemplateCustomizer._adjust_scene_durations(
                    customized_config, customizations["duration"]
                )
            
            if "aspect_ratio" in customizations:
                customized_config["aspect_ratio"] = customizations["aspect_ratio"]
            
            if "default_style" in customizations:
                customized_config["default_style"] = customizations["default_style"]
            
            # Apply element-specific customizations
            if "elements" in customizations:
                TemplateCustomizer._customize_elements(
                    customized_config, customizations["elements"]
                )
            
            # Apply scene-specific customizations
            if "scenes" in customizations:
                TemplateCustomizer._customize_scenes(
                    customized_config, customizations["scenes"]
                )
            
            return customized_config
            
        except Exception as e:
            logger.error(f"Template customization failed: {str(e)}")
            raise ValueError(f"Failed to customize template: {str(e)}")
    
    @staticmethod
    def _adjust_scene_durations(config: Dict[str, Any], new_total_duration: float):
        """Adjust scene durations proportionally to match new total duration"""
        if "scenes" not in config:
            return
        
        scenes = config["scenes"]
        if not scenes:
            return
        
        # Calculate current total duration
        current_total = sum(scene.get("duration", 0) for scene in scenes)
        if current_total <= 0:
            return
        
        # Calculate scaling factor
        scale_factor = new_total_duration / current_total
        
        # Apply scaling to each scene
        for scene in scenes:
            if "duration" in scene:
                scene["duration"] = scene["duration"] * scale_factor
    
    @staticmethod
    def _customize_elements(config: Dict[str, Any], element_customizations: Dict[str, Any]):
        """Apply element-specific customizations"""
        if "scenes" not in config:
            return
        
        for scene in config["scenes"]:
            if "elements" not in scene:
                continue
            
            for element in scene["elements"]:
                element_id = element.get("id")
                if element_id in element_customizations:
                    customization = element_customizations[element_id]
                    TemplateCustomizer._apply_element_customization(element, customization)
    
    @staticmethod
    def _apply_element_customization(element: Dict[str, Any], customization: Dict[str, Any]):
        """Apply customization to a specific element"""
        # Update element properties
        if "properties" in customization:
            if "properties" not in element:
                element["properties"] = {}
            element["properties"].update(customization["properties"])
        
        # Update position
        if "position" in customization:
            element["position"] = customization["position"]
        
        # Update size
        if "size" in customization:
            element["size"] = customization["size"]
        
        # Update animations
        if "animations" in customization:
            element["animations"] = customization["animations"]
    
    @staticmethod
    def _customize_scenes(config: Dict[str, Any], scene_customizations: Dict[str, Any]):
        """Apply scene-specific customizations"""
        if "scenes" not in config:
            return
        
        for scene in config["scenes"]:
            scene_id = scene.get("id")
            if scene_id in scene_customizations:
                customization = scene_customizations[scene_id]
                
                # Update scene duration
                if "duration" in customization:
                    scene["duration"] = customization["duration"]
                
                # Update scene type
                if "type" in customization:
                    scene["type"] = customization["type"]
                
                # Update transitions
                if "transitions" in customization:
                    scene["transitions"] = customization["transitions"]
    
    @staticmethod
    def get_customizable_elements(template_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract all customizable elements from a template
        
        Returns:
            List of customizable element information
        """
        customizable_elements = []
        
        if "scenes" not in template_config:
            return customizable_elements
        
        customizable_element_ids = template_config.get("customizable_elements", [])
        
        for scene in template_config["scenes"]:
            if "elements" not in scene:
                continue
            
            for element in scene["elements"]:
                element_id = element.get("id")
                if element_id in customizable_element_ids:
                    customizable_elements.append({
                        "id": element_id,
                        "type": element.get("type"),
                        "scene_id": scene.get("id"),
                        "current_properties": element.get("properties", {}),
                        "position": element.get("position", {}),
                        "size": element.get("size", {}),
                        "customization_options": TemplateCustomizer._get_element_customization_options(element)
                    })
        
        return customizable_elements
    
    @staticmethod
    def _get_element_customization_options(element: Dict[str, Any]) -> Dict[str, Any]:
        """Get available customization options for an element based on its type"""
        element_type = element.get("type")
        
        base_options = {
            "position": {
                "x": {"type": "number", "min": 0, "max": 100, "description": "X position (%)"},
                "y": {"type": "number", "min": 0, "max": 100, "description": "Y position (%)"}
            },
            "size": {
                "width": {"type": "number", "min": 1, "max": 100, "description": "Width (%)"},
                "height": {"type": "number", "min": 1, "max": 100, "description": "Height (%)"}
            }
        }
        
        if element_type == "text":
            base_options["properties"] = {
                "text": {"type": "string", "description": "Text content"},
                "fontSize": {"type": "number", "min": 8, "max": 200, "description": "Font size"},
                "fontFamily": {"type": "string", "description": "Font family"},
                "color": {"type": "color", "description": "Text color"},
                "textAlign": {"type": "select", "options": ["left", "center", "right"], "description": "Text alignment"},
                "fontWeight": {"type": "select", "options": ["normal", "bold", "100", "200", "300", "400", "500", "600", "700", "800", "900"], "description": "Font weight"}
            }
        elif element_type == "image":
            base_options["properties"] = {
                "src": {"type": "string", "description": "Image source URL"},
                "opacity": {"type": "number", "min": 0, "max": 1, "description": "Image opacity"},
                "filter": {"type": "string", "description": "CSS filter effects"}
            }
        elif element_type == "shape":
            base_options["properties"] = {
                "shapeType": {"type": "select", "options": ["rectangle", "circle", "triangle"], "description": "Shape type"},
                "fillColor": {"type": "color", "description": "Fill color"},
                "strokeColor": {"type": "color", "description": "Stroke color"},
                "strokeWidth": {"type": "number", "min": 0, "max": 20, "description": "Stroke width"}
            }
        
        return base_options
    
    @staticmethod
    def validate_customizations(
        template_config: Dict[str, Any],
        customizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate customizations against template configuration
        
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        try:
            customizable_element_ids = template_config.get("customizable_elements", [])
            
            # Validate element customizations
            if "elements" in customizations:
                for element_id, element_customization in customizations["elements"].items():
                    if element_id not in customizable_element_ids:
                        warnings.append(f"Element '{element_id}' is not marked as customizable")
                    
                    # Find the element in the template
                    element = TemplateCustomizer._find_element_by_id(template_config, element_id)
                    if not element:
                        errors.append(f"Element '{element_id}' not found in template")
                        continue
                    
                    # Validate element customization
                    element_errors = TemplateCustomizer._validate_element_customization(
                        element, element_customization
                    )
                    errors.extend(element_errors)
            
            # Validate global customizations
            if "duration" in customizations:
                duration = customizations["duration"]
                if not isinstance(duration, (int, float)) or duration <= 0:
                    errors.append("Duration must be a positive number")
            
            if "aspect_ratio" in customizations:
                valid_ratios = ["16:9", "9:16", "1:1", "21:9"]
                if customizations["aspect_ratio"] not in valid_ratios:
                    errors.append(f"Invalid aspect ratio. Must be one of: {valid_ratios}")
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def _find_element_by_id(template_config: Dict[str, Any], element_id: str) -> Optional[Dict[str, Any]]:
        """Find an element by ID in the template configuration"""
        if "scenes" not in template_config:
            return None
        
        for scene in template_config["scenes"]:
            if "elements" not in scene:
                continue
            
            for element in scene["elements"]:
                if element.get("id") == element_id:
                    return element
        
        return None
    
    @staticmethod
    def _validate_element_customization(
        element: Dict[str, Any],
        customization: Dict[str, Any]
    ) -> List[str]:
        """Validate customization for a specific element"""
        errors = []
        element_type = element.get("type")
        
        # Validate properties based on element type
        if "properties" in customization:
            properties = customization["properties"]
            
            if element_type == "text":
                if "fontSize" in properties:
                    font_size = properties["fontSize"]
                    if not isinstance(font_size, (int, float)) or font_size < 8 or font_size > 200:
                        errors.append("Font size must be between 8 and 200")
            
            elif element_type == "image":
                if "opacity" in properties:
                    opacity = properties["opacity"]
                    if not isinstance(opacity, (int, float)) or opacity < 0 or opacity > 1:
                        errors.append("Opacity must be between 0 and 1")
        
        # Validate position
        if "position" in customization:
            position = customization["position"]
            for coord in ["x", "y"]:
                if coord in position:
                    value = position[coord]
                    if not isinstance(value, (int, float)) or value < 0 or value > 100:
                        errors.append(f"Position {coord} must be between 0 and 100")
        
        # Validate size
        if "size" in customization:
            size = customization["size"]
            for dimension in ["width", "height"]:
                if dimension in size:
                    value = size[dimension]
                    if not isinstance(value, (int, float)) or value < 1 or value > 100:
                        errors.append(f"Size {dimension} must be between 1 and 100")
        
        return errors
    
    @staticmethod
    def generate_preview_config(
        template_config: Dict[str, Any],
        customizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a preview configuration with customizations applied
        
        This creates a lightweight version suitable for preview generation
        """
        try:
            # Apply customizations
            preview_config = TemplateCustomizer.customize_template(template_config, customizations)
            
            # Reduce duration for faster preview generation
            if preview_config.get("duration", 0) > 10:
                preview_config["duration"] = 10
                TemplateCustomizer._adjust_scene_durations(preview_config, 10)
            
            # Simplify animations for preview
            if "scenes" in preview_config:
                for scene in preview_config["scenes"]:
                    if "elements" in scene:
                        for element in scene["elements"]:
                            if "animations" in element:
                                # Keep only the first animation for preview
                                element["animations"] = element["animations"][:1]
            
            return preview_config
            
        except Exception as e:
            logger.error(f"Preview generation failed: {str(e)}")
            raise ValueError(f"Failed to generate preview: {str(e)}")
