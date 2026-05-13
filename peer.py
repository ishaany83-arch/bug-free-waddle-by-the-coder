#!/usr/bin/env python3
"""
WireGuard Peer Manager
Handles peer configuration and management
"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)

@dataclass
class Peer:
    """Represents a WireGuard peer"""
    name: str
    public_key: str
    allowed_ips: str
    endpoint: Optional[str] = None
    preshared_key: Optional[str] = None
    persistent_keepalive: int = 25

class PeerManager:
    """Manages WireGuard peers"""
    
    def __init__(self, peers_file="peers.json"):
        self.peers_file = Path(peers_file)
        self.peers = self._load_peers()
    
    def add_peer(self, peer: Peer):
        """Add a new peer"""
        if peer.name in self.peers:
            logger.warning(f"Peer {peer.name} already exists, updating")
        self.peers[peer.name] = peer
        self._save_peers()
        logger.info(f"Added peer: {peer.name}")
    
    def remove_peer(self, name: str):
        """Remove a peer"""
        if name in self.peers:
            del self.peers[name]
            self._save_peers()
            logger.info(f"Removed peer: {name}")
        else:
            logger.warning(f"Peer not found: {name}")
    
    def get_peer(self, name: str) -> Optional[Peer]:
        """Get peer by name"""
        return self.peers.get(name)
    
    def list_peers(self) -> List[Peer]:
        """List all peers"""
        return list(self.peers.values())
    
    def _load_peers(self) -> dict:
        """Load peers from file"""
        if self.peers_file.exists():
            try:
                with open(self.peers_file, 'r') as f:
                    data = json.load(f)
                    return {name: Peer(**peer_data) for name, peer_data in data.items()}
            except Exception as e:
                logger.error(f"Failed to load peers: {e}")
        return {}
    
    def _save_peers(self):
        """Save peers to file"""
        data = {name: {
            'name': peer.name,
            'public_key': peer.public_key,
            'allowed_ips': peer.allowed_ips,
            'endpoint': peer.endpoint,
            'preshared_key': peer.preshared_key,
            'persistent_keepalive': peer.persistent_keepalive
        } for name, peer in self.peers.items()}
        with open(self.peers_file, 'w') as f:
            json.dump(data, f, indent=2)
        logger.debug("Saved peers to file")
