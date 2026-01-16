"""
kinematics.py - Coordinate System Transformations

Converts between Cartesian coordinates (x, y) and wire lengths for the 2-motor system.
The marker is suspended by two wires from the top-left and top-right corners.
"""

import math
from config import Config

class Kinematics:
    def __init__(self, config: Config):
        """
        Initialize kinematics calculator for 2-wire system.
        
        Args:
            config: Configuration object with whiteboard parameters
        """
        self.config = config
        
        # Fixed anchor points for the two wires
        self.anchor_tl = (0.0, 0.0)  # Top-left corner
        self.anchor_tr = (config.WHITEBOARD_WIDTH, 0.0)  # Top-right corner
        
    def cartesian_to_wire_lengths(self, x, y):
        """
        Convert Cartesian position to required wire lengths.
        
        The marker is suspended by two wires:
        - Wire from top-left corner (motor TL)
        - Wire from top-right corner (motor TR)
        
        Args:
            x: X coordinate in mm (0 = left edge)
            y: Y coordinate in mm (0 = top edge)
            
        Returns:
            dict: Wire lengths in mm {'tl': length, 'tr': length}
        """
        # Distance from top-left anchor to position (x, y)
        length_tl = math.sqrt((x - self.anchor_tl[0])**2 + (y - self.anchor_tl[1])**2)
        
        # Distance from top-right anchor to position (x, y)
        length_tr = math.sqrt((x - self.anchor_tr[0])**2 + (y - self.anchor_tr[1])**2)
        
        return {
            'tl': length_tl,
            'tr': length_tr
        }
    
    def wire_lengths_to_steps(self, lengths):
        """
        Convert wire lengths to motor steps.
        
        Args:
            lengths: dict of wire lengths in mm {'tl': ..., 'tr': ...}
            
        Returns:
            dict: Required steps for each motor
        """
        steps_per_mm = self.config.steps_per_mm
        
        return {
            'tl': int(round(lengths['tl'] * steps_per_mm)),
            'tr': int(round(lengths['tr'] * steps_per_mm))
        }
    
    def cartesian_to_steps(self, x, y):
        """
        Direct conversion from Cartesian to motor steps.
        
        Args:
            x: X coordinate in mm
            y: Y coordinate in mm
            
        Returns:
            dict: Required steps for each motor
        """
        lengths = self.cartesian_to_wire_lengths(x, y)
        return self.wire_lengths_to_steps(lengths)
    
    def calculate_delta_steps(self, current_x, current_y, target_x, target_y):
        """
        Calculate change in steps needed to move from current to target position.
        
        Args:
            current_x, current_y: Current position in mm
            target_x, target_y: Target position in mm
            
        Returns:
            dict: Delta steps for each motor (positive = reel in, negative = let out)
        """
        current_steps = self.cartesian_to_steps(current_x, current_y)
        target_steps = self.cartesian_to_steps(target_x, target_y)
        
        # Positive delta = wire getting shorter = reel in (motor forward)
        # Negative delta = wire getting longer = let out (motor reverse)
        return {
            'tl': current_steps['tl'] - target_steps['tl'],
            'tr': current_steps['tr'] - target_steps['tr']
        }
    
    def validate_position(self, x, y):
        """
        Check if a position is within the whiteboard bounds.
        
        Args:
            x, y: Position to validate
            
        Returns:
            bool: True if position is valid
        """
        return (0 <= x <= self.config.WHITEBOARD_WIDTH and
                0 <= y <= self.config.WHITEBOARD_HEIGHT)