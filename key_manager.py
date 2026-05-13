#!/usr/bin/env python3
"""
WireGuard Key Manager
Handles cryptographic key generation and management
"""

import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class KeyManager:
    """Manages WireGuard cryptographic keys"""
    
    def __init__(self, keys_dir="keys"):
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(mode=0o700, exist_ok=True)
    
    def generate_keypair(self, name):
        """
        Generate a new WireGuard keypair.
        Returns (private_key, public_key)
        """
        try:
            # Generate private key
            private_key = subprocess.check_output(
                ['wg', 'genkey'],
                text=True
            ).strip()
            
            # Generate public key from private key
            public_key = subprocess.check_output(
                ['wg', 'pubkey'],
                input=private_key,
                text=True
            ).strip()
            
            # Generate preshared key
            preshared_key = subprocess.check_output(
                ['wg', 'genpsk'],
                text=True
            ).strip()
            
            # Save keys with secure permissions
            self._save_key(f"{name}_private.key", private_key)
            self._save_key(f"{name}_public.key", public_key)
            self._save_key(f"{name}_psk.key", preshared_key)
            
            logger.info(f"Generated keypair for {name}")
            return private_key, public_key
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate keys: {e}")
            raise
    
    def _save_key(self, filename, content):
        """Save key with secure permissions (600)"""
        filepath = self.keys_dir / filename
        with open(filepath, 'w') as f:
            f.write(content)
        os.chmod(filepath, 0o600)
        logger.debug(f"Saved {filename}")
    
    def load_key(self, filename):
        """Load a key from file"""
        filepath = self.keys_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Key file not found: {filepath}")
        with open(filepath, 'r') as f:
            return f.read().strip()
    
    def get_public_key(self, name):
        """Get public key for a peer"""
        return self.load_key(f"{name}_public.key")
    
    def get_private_key(self, name):
        """Get private key (use with caution)"""
        return self.load_key(f"{name}_private.key")
    
    def get_preshared_key(self, name):
        """Get preshared key for enhanced security"""
        return self.load_key(f"{name}_psk.key")
