"""
main.py - Main Entry Point for Whiteboard Bot

This is what you run on the Raspberry Pi. It receives position data
from your laptop and executes the movements using the 2-motor system.
"""

import json
import signal
import sys
from motion_controller import MotionController
from config import Config

class WhiteboardBot:
    def __init__(self):
        """Initialize the whiteboard bot system"""
        print("Initializing Whiteboard Bot (2-motor system)...")
        
        # Load configuration
        self.config = Config()
        
        # Initialize motion controller
        self.controller = MotionController(self.config)
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
        print("Whiteboard Bot ready!")
        print(f"Whiteboard size: {self.config.WHITEBOARD_WIDTH}mm x "
              f"{self.config.WHITEBOARD_HEIGHT}mm")
        print(f"Steps per mm: {self.config.steps_per_mm:.2f}")
        print("2 motors: Top-Left and Top-Right corners")
        
    def process_positions(self, positions):
        """
        Process an array of positions received from laptop.
        
        Args:
            positions: List of dicts with 'x' and 'y' keys, or list of (x, y) tuples
                      Example: [{"x": 100, "y": 200}, {"x": 150, "y": 250}]
                      Or: [(100, 200), (150, 250)]
        """
        # Convert to list of tuples if needed
        if positions and isinstance(positions[0], dict):
            position_tuples = [(p['x'], p['y']) for p in positions]
        else:
            position_tuples = positions
        
        # Execute the path
        self.controller.execute_path(position_tuples)
    
    def draw_test_pattern(self):
        """Draw a test pattern to verify calibration"""
        print("Drawing test pattern...")
        
        w = self.config.WHITEBOARD_WIDTH
        h = self.config.WHITEBOARD_HEIGHT
        margin = 50  # mm from edge
        
        # Draw a rectangle
        corners = [
            (margin, margin),                    # Top-left
            (w - margin, margin),                # Top-right
            (w - margin, h - margin),            # Bottom-right
            (margin, h - margin),                # Bottom-left
            (margin, margin)                     # Back to start
        ]
        
        self.controller.execute_path(corners)
        
        # Draw an X
        self.controller.move_to(margin, margin)
        self.controller.move_to(w - margin, h - margin)
        self.controller.move_to(w / 2, h / 2)
        self.controller.move_to(w - margin, margin)
        self.controller.move_to(margin, h - margin)
        
        # Return to center
        self.controller.home()
        
    def run_example(self):
        """
        Example of how to use the bot when you receive position data.
        
        This simulates receiving data from your laptop.
        """
        print("\n=== Running Example ===\n")
        
        # First, home the system
        self.controller.home()
        
        # Example 1: Single move
        print("\nExample 1: Move to specific position")
        self.controller.move_to(300, 200)
        
        # Example 2: Draw a square
        print("\nExample 2: Draw a square")
        square_positions = [
            (200, 200),
            (400, 200),
            (400, 400),
            (200, 400),
            (200, 200)
        ]
        self.process_positions(square_positions)
        
        # Position Processing
        print("\nExample 3: Process JSON position data")
        json_positions = json.loads('''
        [
            {"x": 100, "y": 100},
            {"x": 500, "y": 100},
            {"x": 500, "y": 500},
            {"x": 100, "y": 500}
        ]
        ''')
        self.process_positions(json_positions)
        
        # Return home
        self.controller.home()
    
    def shutdown(self, signum=None, frame=None):
        print("\nShutting down Whiteboard Bot...")
        self.controller.cleanup()
        sys.exit(0)

def main():
    bot = WhiteboardBot()
    bot.run_example()

if __name__ == "__main__":
    main()