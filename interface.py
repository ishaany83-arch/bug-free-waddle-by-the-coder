#!/usr/bin/env python3
"""
WireGuard Interface Manager
Handles interface creation, management, and routing
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class InterfaceManager:
    """Manages WireGuard interfaces"""
    
    def __init__(self):
        self.interfaces = {}
    
    def create_interface(
        self,
        name: str = "wg0",
        config_file: Optional[str] = None
    ) -> bool:
        """
        Create and bring up a WireGuard interface.
        Returns True on success.
        """
        try:
            # Create interface
            subprocess.run(['ip', 'link', 'add', name, 'type', 'wireguard'],
                         check=True, capture_output=True)
            logger.info(f"Created interface: {name}")
            
            # Load configuration if provided
            if config_file:
                self.load_config(name, config_file)
            
            self.interfaces[name] = True
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create interface {name}: {e.stderr.decode()}")
            return False
    
    def load_config(self, interface: str, config_file: str) -> bool:
        """
        Load configuration into interface.
        """
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                logger.error(f"Config file not found: {config_file}")
                return False
            
            # Use wg-quick to load config
            subprocess.run(
                ['wg-quick', 'up', config_file],
                check=True,
                capture_output=True
            )
            logger.info(f"Loaded config into {interface}")
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to load config: {e.stderr.decode()}")
            return False
    
    def bring_up(self, name: str) -> bool:
        """
        Bring up an interface.
        """
        try:
            subprocess.run(['ip', 'link', 'set', name, 'up'],
                         check=True, capture_output=True)
            logger.info(f"Brought up interface: {name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to bring up {name}: {e.stderr.decode()}")
            return False
    
    def bring_down(self, name: str) -> bool:
        """
        Bring down an interface.
        """
        try:
            subprocess.run(['ip', 'link', 'set', name, 'down'],
                         check=True, capture_output=True)
            logger.info(f"Brought down interface: {name}")
            if name in self.interfaces:
                del self.interfaces[name]
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to bring down {name}: {e.stderr.decode()}")
            return False
    
    def assign_ip(self, interface: str, address: str) -> bool:
        """
        Assign IP address to interface.
        """
        try:
            subprocess.run(['ip', 'addr', 'add', address, 'dev', interface],
                         check=True, capture_output=True)
            logger.info(f"Assigned {address} to {interface}")
            return True
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode()
            # File exists error is OK if already assigned
            if "File exists" not in error_msg:
                logger.error(f"Failed to assign IP: {error_msg}")
                return False
            return True
    
    def add_route(self, interface: str, route: str) -> bool:
        """
        Add route through interface.
        """
        try:
            subprocess.run(['ip', 'route', 'add', route, 'dev', interface],
                         check=True, capture_output=True)
            logger.info(f"Added route {route} through {interface}")
            return True
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode()
            if "File exists" not in error_msg:
                logger.error(f"Failed to add route: {error_msg}")
                return False
            return True
    
    def delete_interface(self, name: str) -> bool:
        """
        Delete a WireGuard interface.
        """
        try:
            # Bring down first
            self.bring_down(name)
            # Delete interface
            subprocess.run(['ip', 'link', 'delete', name],
                         check=True, capture_output=True)
            logger.info(f"Deleted interface: {name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to delete {name}: {e.stderr.decode()}")
            return False
    
    def get_status(self, interface: str) -> str:
        """
        Get interface status and peer information.
        """
        try:
            output = subprocess.check_output(
                ['wg', 'show', interface],
                text=True
            )
            return output
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get status: {e}")
            return ""
    
    def get_all_status(self) -> str:
        """
        Get status of all WireGuard interfaces.
        """
        try:
            output = subprocess.check_output(
                ['wg', 'show', 'all'],
                text=True
            )
            return output
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get all status: {e}")
            return ""
