#!/usr/bin/env python3
"""
WireGuard Configuration Manager
Handles configuration file generation and management
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages WireGuard configuration files"""
    
    def __init__(self, configs_dir="configs"):
        self.configs_dir = Path(configs_dir)
        self.configs_dir.mkdir(mode=0o700, exist_ok=True)
    
    def create_server_config(
        self,
        name: str,
        private_key: str,
        address: str = "10.0.0.1/24",
        port: int = 51820,
        dns: str = "1.1.1.1"
    ) -> str:
        """
        Create a server (interface) configuration.
        Returns path to config file.
        """
        config = f"""[Interface]
PrivateKey = {private_key}
Address = {address}
ListenPort = {port}
DNS = {dns}

# Enable IP forwarding for VPN traffic
PostUp = ip link set wg0 up
PostUp = ip route add 0.0.0.0/0 dev wg0
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT
PostUp = iptables -A FORWARD -o wg0 -j ACCEPT
PostUp = iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostUp = sysctl -w net.ipv4.ip_forward=1

PostDown = ip route del 0.0.0.0/0 dev wg0 2>/dev/null || true
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT
PostDown = iptables -D FORWARD -o wg0 -j ACCEPT
postDown = iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# Peers will be added dynamically
"""
        config_path = self.configs_dir / f"{name}.conf"
        self._save_config(config_path, config)
        logger.info(f"Created server config: {config_path}")
        return str(config_path)
    
    def create_client_config(
        self,
        name: str,
        private_key: str,
        address: str,
        server_public_key: str,
        server_endpoint: str,
        dns: str = "1.1.1.1",
        preshared_key: Optional[str] = None
    ) -> str:
        """
        Create a client configuration.
        Returns path to config file.
        """
        preshared_line = f"PresharedKey = {preshared_key}\n" if preshared_key else ""
        
        config = f"""[Interface]
PrivateKey = {private_key}
Address = {address}
DNS = {dns}

# Route all traffic through VPN
PostUp = ip route replace default dev wg0
PostUp = resolvectl default-route wg0 yes
PostUp = resolvectl dns wg0 {dns}

PostDown = ip route del default dev wg0 2>/dev/null || true
PostDown = resolvectl default-route wg0 no

[Peer]
PublicKey = {server_public_key}
{preshared_line}AllowedIPs = 0.0.0.0/0
Endpoint = {server_endpoint}
PersistentKeepalive = 25
"""
        config_path = self.configs_dir / f"{name}.conf"
        self._save_config(config_path, config)
        logger.info(f"Created client config: {config_path}")
        return str(config_path)
    
    def add_peer_to_server(
        self,
        server_config: str,
        peer_name: str,
        public_key: str,
        allowed_ip: str,
        preshared_key: Optional[str] = None
    ):
        """
        Add a peer configuration to server config.
        """
        config_path = Path(server_config)
        
        preshared_line = f"PresharedKey = {preshared_key}\n" if preshared_key else ""
        peer_config = f"""\n[Peer]
# {peer_name}
PublicKey = {public_key}
{preshared_line}AllowedIPs = {allowed_ip}
PersistentKeepalive = 25
"""
        
        with open(config_path, 'a') as f:
            f.write(peer_config)
        
        logger.info(f"Added peer {peer_name} to {server_config}")
    
    def _save_config(self, filepath: Path, content: str):
        """Save configuration with secure permissions (600)"""
        import os
        with open(filepath, 'w') as f:
            f.write(content)
        os.chmod(filepath, 0o600)
        logger.debug(f"Saved config: {filepath}")
    
    def get_config(self, name: str) -> str:
        """Get config file path"""
        config_path = self.configs_dir / f"{name}.conf"
        if not config_path.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")
        return str(config_path)
    
    def list_configs(self):
        """List all configuration files"""
        return list(self.configs_dir.glob("*.conf"))
