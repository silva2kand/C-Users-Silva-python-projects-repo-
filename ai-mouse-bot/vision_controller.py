"""
Vision and Control Module for the AI Mouse Bot
Handles screen analysis, object detection, and mouse control.
"""

import cv2
import numpy as np
import pyautogui
import time
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import json
import os

# Configure pyautogui for safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

class ElementType(Enum):
    """Types of UI elements the bot can interact with."""
    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    IMAGE = "image"
    TEXT = "text"
    UNKNOWN = "unknown"

@dataclass
class UIElement:
    """Represents a UI element on the screen."""
    element_type: ElementType
    position: Tuple[int, int]  # (x, y) coordinates
    size: Tuple[int, int]      # (width, height)
    confidence: float          # Confidence score (0.0 to 1.0)
    text: str = ""             # Extracted text if applicable
    metadata: Dict = None      # Additional metadata

class VisionController:
    """Handles computer vision and mouse control for the AI Mouse Bot."""
    
    def __init__(self):
        # Initialize screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Load element templates and configurations
        self.templates = self._load_templates()
        
        # Initialize OpenCV parameters
        self.method = cv2.TM_CCOEFF_NORMED
        self.threshold = 0.8  # Confidence threshold for template matching
        
        # Initialize OCR if needed (using Tesseract)
        self.ocr_initialized = False
        try:
            import pytesseract
            self.ocr_initialized = True
        except ImportError:
            print("Tesseract OCR not available. Text recognition will be limited.")
    
    def _load_templates(self) -> Dict[str, any]:
        """Load UI element templates and configurations."""
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        os.makedirs(templates_dir, exist_ok=True)
        
        # Default templates (can be extended by loading from files)
        templates = {
            "close_button": {
                "type": ElementType.BUTTON,
                "templates": [],
                "color_range": None,
                "min_size": (10, 10),
                "max_size": (50, 50)
            },
            # Add more default templates as needed
        }
        
        # Load custom templates from files if they exist
        for filename in os.listdir(templates_dir):
            if filename.endswith('.png') or filename.endswith('.jpg'):
                name = os.path.splitext(filename)[0]
                if name not in templates:
                    templates[name] = {
                        "type": ElementType.UNKNOWN,
                        "templates": [],
                        "color_range": None,
                        "min_size": (10, 10),
                        "max_size": (200, 200)
                    }
                
                # Load the template image
                template_path = os.path.join(templates_dir, filename)
                template = cv2.imread(template_path, cv2.IMREAD_COLOR)
                if template is not None:
                    templates[name]["templates"].append(template)
        
        return templates
    
    def capture_screen(self, region: Tuple[int, int, int, int] = None) -> np.ndarray:
        """Capture the screen or a region of the screen."""
        if region:
            x, y, w, h = region
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
        else:
            screenshot = pyautogui.screenshot()
        
        # Convert to OpenCV format (BGR)
        frame = np.array(screenshot)
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    def find_element(self, element_name: str, region: Tuple[int, int, int, int] = None) -> Optional[UIElement]:
        """Find a UI element on the screen."""
        if element_name not in self.templates:
            print(f"No template found for element: {element_name}")
            return None
        
        element_config = self.templates[element_name]
        
        # Capture the screen
        screen = self.capture_screen(region)
        
        # Try to find the element using template matching
        for template in element_config.get("templates", []):
            result = cv2.matchTemplate(screen, template, self.method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
            if self.method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc
                confidence = 1 - min_val
            else:
                top_left = max_loc
                confidence = max_val
            
            # If we found a match with sufficient confidence
            if confidence > self.threshold:
                h, w = template.shape[:2]
                center = (top_left[0] + w // 2, top_left[1] + h // 2)
                
                if region:
                    center = (center[0] + region[0], center[1] + region[1])
                
                return UIElement(
                    element_type=element_config["type"],
                    position=center,
                    size=(w, h),
                    confidence=float(confidence),
                    metadata={"method": "template_matching"}
                )
        
        # If template matching failed, try color-based detection if color range is defined
        if element_config.get("color_range"):
            return self._find_by_color(element_config, screen, region)
        
        return None
    
    def _find_by_color(self, element_config: Dict, screen: np.ndarray, region: Tuple[int, int, int, int]) -> Optional[UIElement]:
        """Find elements based on color range."""
        # Convert to HSV color space
        hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
        
        # Create mask for the color range
        lower, upper = element_config["color_range"]
        mask = cv2.inRange(hsv, lower, upper)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Filter by size
            x, y, w, h = cv2.boundingRect(contour)
            if (w < element_config["min_size"][0] or h < element_config["min_size"][1] or
                w > element_config["max_size"][0] or h > element_config["max_size"][1]):
                continue
            
            # Calculate center
            center = (x + w // 2, y + h // 2)
            if region:
                center = (center[0] + region[0], center[1] + region[1])
            
            return UIElement(
                element_type=element_config["type"],
                position=center,
                size=(w, h),
                confidence=0.9,  # High confidence for color match
                metadata={"method": "color_detection"}
            )
        
        return None
    
    def get_text_from_region(self, region: Tuple[int, int, int, int]) -> str:
        """Extract text from a screen region using OCR."""
        if not self.ocr_initialized:
            return ""
        
        try:
            import pytesseract
            # Capture the region
            screenshot = pyautogui.screenshot(region=region)
            
            # Use pytesseract to extract text
            text = pytesseract.image_to_string(screenshot)
            return text.strip()
        except Exception as e:
            print(f"Error in OCR: {e}")
            return ""
    
    def move_mouse(self, position: Tuple[int, int], duration: float = 0.5) -> None:
        """Move the mouse cursor to the specified position."""
        try:
            pyautogui.moveTo(position[0], position[1], duration=duration)
            return True
        except pyautogui.FailSafeException:
            print("Emergency stop triggered! Move mouse to corner to reset.")
            return False
    
    def click(self, position: Tuple[int, int] = None, button: str = 'left', clicks: int = 1) -> bool:
        """Perform a mouse click at the specified position or current position."""
        try:
            if position:
                self.move_mouse(position)
            pyautogui.click(button=button, clicks=clicks)
            return True
        except pyautogui.FailSafeException:
            print("Emergency stop triggered! Move mouse to corner to reset.")
            return False
    
    def type_text(self, text: str, interval: float = 0.1) -> None:
        """Type the specified text."""
        pyautogui.typewrite(text, interval=interval)
    
    def scroll(self, clicks: int, direction: str = 'down') -> None:
        """Scroll the mouse wheel."""
        # On Windows, positive values scroll down, negative scroll up
        amount = abs(clicks)
        if direction.lower() == 'up':
            amount = -amount
        pyautogui.scroll(amount)
    
    def drag(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], duration: float = 0.5) -> bool:
        """Drag from start_pos to end_pos."""
        try:
            self.move_mouse(start_pos, duration=0.1)
            pyautogui.dragTo(end_pos[0], end_pos[1], duration=duration, button='left')
            return True
        except pyautogui.FailSafeException:
            print("Emergency stop triggered! Move mouse to corner to reset.")
            return False

# Example usage
if __name__ == "__main__":
    vc = VisionController()
    
    # Example: Find and click the Windows Start button (you'd need to add the template)
    # start_button = vc.find_element("windows_start")
    # if start_button:
    #     print(f"Found Start button at {start_button.position}")
    #     vc.click(start_button.position)
    # else:
    #     print("Could not find Start button")
    
    # Example: Type some text
    # vc.type_text("Hello, World!")
    
    # Example: Scroll down
    # vc.scroll(5, 'down')
