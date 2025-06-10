from typing import Dict, List, Optional, Tuple, Union
import random
from rotor import Rotor

class RotorMachine:
    def __init__(self, num_rotors: int = 3):
        """
        Initialize the rotor machine with the specified number of rotors.
        
        Args:
            num_rotors: Number of rotors to use (default: 3)
        """
        if not isinstance(num_rotors, int) or num_rotors < 1:
            raise ValueError("Number of rotors must be a positive integer")
            
        self.num_rotors = num_rotors
        self.rotors: List[Rotor] = []
        self.reflector: Dict[int, int] = self._create_reflector()
        self.plugboard: List[int] = [i for i in range(256)]  # Faster list-based plugboard
        
        # Initialize rotors with random wirings and positions
        for i in range(num_rotors):
            # Space notches evenly
            notch = (i * (256 // num_rotors)) % 256
            self.rotors.append(Rotor(notch=notch))
    
    def _create_reflector(self) -> Dict[int, int]:
        """Create a reflector that maps each character to another (involutory permutation)."""
        # Create pairs of characters that map to each other
        chars = list(range(256))
        random.shuffle(chars)
        reflector = {}
        
        for i in range(0, 256, 2):
            if i + 1 < 256:
                a, b = chars[i], chars[i + 1]
                reflector[a] = b
                reflector[b] = a
        
        return reflector
    
    def set_rotor_positions(self, positions: List[int]) -> None:
        """Set the positions of all rotors."""
        if len(positions) != len(self.rotors):
            raise ValueError(f"Expected {len(self.rotors)} positions, got {len(positions)}")
            
        for rotor, pos in zip(self.rotors, positions):
            rotor.set_position(pos % 256)
    
    def set_ring_settings(self, settings: List[int]) -> None:
        """Set the ring settings of all rotors."""
        if len(settings) != len(self.rotors):
            raise ValueError(f"Expected {len(self.rotors)} settings, got {len(settings)}")
            
        for rotor, setting in zip(self.rotors, settings):
            rotor.set_ring_setting(setting % 256)
    
    def set_plugboard(self, connections: List[Tuple[Union[int, str], Union[int, str]]]) -> None:
        """Set the plugboard connections."""
        # Reset plugboard to default (no connections)
        self.plugboard = [i for i in range(256)]
        
        # Add new connections
        for a, b in connections:
            if isinstance(a, str):
                a = ord(a[0]) if a else 0
            if isinstance(b, str):
                b = ord(b[0]) if b else 0
                
            a = a % 256
            b = b % 256
            
            # Skip if trying to connect a character to itself
            if a == b:
                continue
                
            # Clear any existing connections for these characters
            self.plugboard[a] = a
            self.plugboard[b] = b
            
            # Create new connection
            self.plugboard[a] = b
            self.plugboard[b] = a
    
    def rotate_rotors(self) -> None:
        """Rotate the rotors according to the Enigma machine's stepping mechanism."""
        # Rightmost rotor always rotates
        rotate_next = self.rotors[-1].rotate()
        
        # Check for double-stepping (middle rotor)
        if len(self.rotors) > 1 and self.rotors[-2].is_at_notch():
            rotate_next = True
        
        # Rotate middle rotor if needed
        if len(self.rotors) > 1 and rotate_next:
            rotate_next = self.rotors[-2].rotate()
            
            # If middle rotor was on a notch and rotated, rotate the left rotor too
            if len(self.rotors) > 2 and rotate_next:
                self.rotors[-3].rotate()
    
    def encrypt(self, char: int) -> int:
        """
        Encrypt a single character (0-255).
        
        Args:
            char: The input character (0-255)
            
        Returns:
            The encrypted character (0-255)
        """
        if not 0 <= char <= 255:
            raise ValueError("Character must be in range 0-255")
            
        # Rotate rotors before encryption
        self.rotate_rotors()
        
        # Apply plugboard (forward)
        result = self.plugboard[char]
        
        # Forward pass through rotors (right to left)
        for rotor in reversed(self.rotors):
            result = rotor.forward(result)
        
        # Pass through reflector
        result = self.reflector.get(result, result)
        
        # Backward pass through rotors (left to right)
        for rotor in self.rotors:
            result = rotor.backward(result)
        
        # Apply plugboard (backward)
        result = self.plugboard[result]
        
        return result % 256
    
    def decrypt(self, char: int) -> int:
        """
        Decrypt a single character (0-255).
        
        Note: For a reciprocal cipher like the Enigma, decryption is the same as encryption
        with the same settings.
        
        Args:
            char: The input character (0-255)
            
        Returns:
            The decrypted character (0-255)
        """
        return self.encrypt(char)
    
    def encrypt_char(self, char: int) -> int:
        """
        Alias for encrypt() for backward compatibility.
        """
        return self.encrypt(char)
    
    def decrypt_char(self, char: int) -> int:
        """
        Alias for decrypt() for backward compatibility.
        """
        return self.decrypt(char)
    
    def process_text(self, text: str) -> str:
        """Process text through the machine (encrypt/decrypt)."""
        return ''.join(
            chr(self.encrypt_char(ord(char))) 
            if 0 <= ord(char) < 256 else char 
            for char in text
        )
    
    # Alias for backward compatibility
    encrypt_text = process_text
    decrypt_text = process_text
    
    def get_rotor_positions(self) -> List[int]:
        """Get current positions of all rotors."""
        return [rotor.position for rotor in self.rotors]
    
    def get_ring_settings(self) -> List[int]:
        """Get ring settings of all rotors."""
        return [rotor.ring_setting for rotor in self.rotors]
    
    def reset(self) -> None:
        """Reset all rotors to position 0."""
        for rotor in self.rotors:
            rotor.set_position(0)
    
    def __str__(self) -> str:
        """String representation of the machine's state."""
        return (
            f"RotorMachine(rotors={len(self.rotors)}, "
            f"positions={self.get_rotor_positions()}, "
            f"rings={self.get_ring_settings()})"
        )
