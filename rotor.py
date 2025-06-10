import random
from typing import List, Optional, Dict

class Rotor:
    def __init__(self, wiring: Optional[List[int]] = None, position: int = 0, 
                 ring_setting: int = 0, notch: Optional[int] = None):
        """
        Initialize a rotor with the specified wiring, position, and ring setting.
        
        Args:
            wiring: Optional custom wiring (list of 256 integers)
            position: Initial position (0-255)
            ring_setting: Ring setting (0-255)
            notch: Notch position where rotor causes next rotor to step (0-255)
        """
        # Initialize wiring with random permutation if not provided
        self.wiring = wiring if wiring is not None else self._generate_random_wiring()
        self.position = position % 256
        self.ring_setting = ring_setting % 256
        self.notch = random.randint(0, 255) if notch is None else (notch % 256)
        
        # Create reverse mapping for backward pass
        self.reverse_wiring = [0] * 256
        for i, val in enumerate(self.wiring):
            self.reverse_wiring[val] = i
    
    def _generate_random_wiring(self) -> List[int]:
        """Generate a random but valid wiring configuration."""
        # Create a list of 256 unique integers (0-255)
        wiring = list(range(256))
        random.shuffle(wiring)
        
        # Ensure no character maps to itself (like in real Enigma)
        for i in range(256):
            if wiring[i] == i:
                # Swap with next position (wrapping around if needed)
                next_pos = (i + 1) % 256
                wiring[i], wiring[next_pos] = wiring[next_pos], wiring[i]
        
        return wiring
    
    def set_position(self, position: int) -> None:
        """Set the rotor position (0-255)."""
        self.position = position % 256
    
    def set_ring_setting(self, setting: int) -> None:
        """Set the ring setting (0-255)."""
        self.ring_setting = setting % 256
    
    def rotate(self, step: int = 1) -> bool:
        """
        Rotate the rotor by the specified number of steps.
        
        Args:
            step: Number of steps to rotate (can be negative)
            
        Returns:
            bool: True if the rotor made a full rotation (passed a notch)
        """
        old_position = self.position
        self.position = (self.position + step) % 256
        
        # Check if we passed the notch position
        if step > 0:
            return old_position <= self.notch < self.position or \
                   self.position < old_position <= self.notch or \
                   self.notch < self.position < old_position
        else:
            return old_position > self.notch >= self.position or \
                   self.position > old_position > self.notch or \
                   self.notch >= old_position > self.position
    
    def forward(self, char_code: int) -> int:
        """
        Encrypt a character in the forward direction (right to left).
        
        Args:
            char_code: ASCII code (0-255)
        Returns:
            int: Encrypted character code
        """
        # Apply ring setting and position
        shifted_pos = (char_code + self.position - self.ring_setting) % 256
        
        # Pass through the rotor wiring
        encrypted = self.wiring[shifted_pos]
        
        # Apply inverse of ring setting and position
        result = (encrypted - self.position + self.ring_setting) % 256
        
        return result
    
    def backward(self, char_code: int) -> int:
        """
        Encrypt a character in the backward direction (left to right).
        
        Args:
            char_code: ASCII code (0-255)
        Returns:
            int: Encrypted character code
        """
        # Apply ring setting and position
        shifted_pos = (char_code + self.position - self.ring_setting) % 256
        
        # Pass through the reverse wiring
        encrypted = self.reverse_wiring[shifted_pos]
        
        # Apply inverse of ring setting and position
        result = (encrypted - self.position + self.ring_setting) % 256
        
        return result
    
    def is_at_notch(self) -> bool:
        """Check if the rotor is at the notch position."""
        return self.position == self.notch
    
    def __str__(self) -> str:
        """String representation of the rotor's current state."""
        return f"Rotor(pos={self.position:02X}, notch={self.notch:02X}, ring={self.ring_setting:02X})"