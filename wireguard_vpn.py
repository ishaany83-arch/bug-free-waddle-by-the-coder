#!/usr/bin/env python3
"""
WireGuard VPN CLI Tool
Complete command-line interface for managing WireGuard VPN
"""

import click
import logging
import sys
from pathlib import Path
from key_manager import KeyManager
from config import ConfigManager
from peer import PeerManager, Peer
from interface import InterfaceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize managers
key_manager = KeyManager()
config_manager = ConfigManager()
peer_manager = PeerManager()
interface_manager = InterfaceManager()

@click.group()
def cli():
    """WireGuard VPN Management Tool
    
    A complete CLI for managing WireGuard VPN servers and clients.
    Ensures secure website access through encrypted tunnels.
    """
    pass

# ============= KEY MANAGEMENT =============

@cli.command()
@click.option('--name', required=True, help='Name of the keypair')
def generate_keys(name):
    """Generate new WireGuard keypair"""
    try:
        click.echo(f"Generating keypair for '{name}'...")
        private_key, public_key = key_manager.generate_keypair(name)
        click.echo(f"✓ Keys generated successfully!\n")
        click.echo(f"Public Key:  {public_key}")
        click.echo(f"\n📁 Keys stored in: keys/{name}_*")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)

# ============= SERVER SETUP =============

@cli.command()
@click.option('--name', default='server', help='Server name')
@click.option('--address', default='10.0.0.1/24', help='Server VPN address')
@click.option('--port', default=51820, type=int, help='Listen port')
@click.option('--dns', default='1.1.1.1', help='DNS server')
def create_server(name, address, port, dns):
    """Create WireGuard server configuration
    
    This creates a server that will route website traffic for all connected clients.
    """
    try:
        # Check if keys exist
        try:
            private_key = key_manager.get_private_key(name)
        except FileNotFoundError:
            click.echo(f"✗ Keys not found. Run: wireguard_vpn.py generate-keys --name {name}")
            sys.exit(1)
        
        # Create config
        config_path = config_manager.create_server_config(
            name=name,
            private_key=private_key,
            address=address,
            port=port,
            dns=dns
        )
        
        click.echo(f"✓ Server configuration created!")
        click.echo(f"\n📁 Config file: {config_path}")
        click.echo(f"🔧 Address: {address}")
        click.echo(f"🔌 Port: {port}")
        click.echo(f"🌐 DNS: {dns}")
        click.echo(f"\n✅ Website access will be available for all connected clients")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)

# ============= CLIENT SETUP =============

@cli.command()
@click.option('--name', required=True, help='Client name')
@click.option('--server-public-key', required=True, help='Server public key')
@click.option('--server-endpoint', required=True, help='Server endpoint (IP:PORT)')
@click.option('--client-address', required=True, help='Client VPN address (e.g., 10.0.0.2/32)')
@click.option('--dns', default='1.1.1.1', help='DNS server')
def create_client(name, server_public_key, server_endpoint, client_address, dns):
    """Create WireGuard client configuration
    
    This creates a client that will tunnel ALL traffic through the VPN for secure website access.
    """
    try:
        # Check if keys exist
        try:
            private_key = key_manager.get_private_key(name)
            preshared_key = key_manager.get_preshared_key(name)
        except FileNotFoundError:
            click.echo(f"✗ Keys not found. Run: wireguard_vpn.py generate-keys --name {name}")
            sys.exit(1)
        
        # Create config
        config_path = config_manager.create_client_config(
            name=name,
            private_key=private_key,
            address=client_address,
            server_public_key=server_public_key,
            server_endpoint=server_endpoint,
            dns=dns,
            preshared_key=preshared_key
        )
        
        click.echo(f"✓ Client configuration created!")
        click.echo(f"\n📁 Config file: {config_path}")
        click.echo(f"🔐 Client Address: {client_address}")
        click.echo(f"🌍 Server Endpoint: {server_endpoint}")
        click.echo(f"🌐 DNS: {dns}")
        click.echo(f"✅ All traffic will be encrypted and routed through the VPN")
        click.echo(f"✅ Website access will be secure and private")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)

# ============= INTERFACE CONTROL =============

@cli.command()
@click.option('--name', default='wg0', help='Interface name')
@click.option('--config', help='Config file to load')
def start(name, config):
    """Start WireGuard interface (requires root)
    
    This brings up the VPN interface and enables website access through the tunnel.
    """
    try:
        if config:
            click.echo(f"Starting {name} with config: {config}")
            success = interface_manager.load_config(name, config)
        else:
            click.echo(f"Starting {name}...")
            interface_manager.create_interface(name)
            success = interface_manager.bring_up(name)
        
        if success:
            click.echo(f"✓ Interface started!")
            click.echo(f"✅ Website access is now available through VPN")
        else:
            click.echo(f"✗ Failed to start interface", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--name', default='wg0', help='Interface name')
def stop(name):
    """Stop WireGuard interface (requires root)"""
    try:
        click.echo(f"Stopping {name}...")
        success = interface_manager.bring_down(name)
        if success:
            click.echo(f"✓ Interface stopped!")
        else:
            click.echo(f"✗ Failed to stop interface", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--name', default='wg0', help='Interface name')
def status(name):
    """Show WireGuard interface status"""
    try:
        output = interface_manager.get_status(name)
        click.echo(output)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
def show_all_status():
    """Show status of all WireGuard interfaces"""
    try:
        output = interface_manager.get_all_status()
        click.echo(output)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)

# ============= CONFIGURATION MANAGEMENT =============

@cli.command()
@click.option('--name', required=True, help='Configuration name')
def show_config(name):
    """Display configuration file"""
    try:
        config_path = config_manager.get_config(name)
        with open(config_path, 'r') as f:
            content = f.read()
        click.echo(content)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
def list_configs():
    """List all configurations"""
    try:
        configs = config_manager.list_configs()
        if configs:
            click.echo("📁 Available configurations:")
            for config in configs:
                click.echo(f"  - {config.name}")
        else:
            click.echo("No configurations found")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)

# ============= PEER MANAGEMENT =============

@cli.command()
@click.option('--server-config', required=True, help='Server config file')
@click.option('--peer-name', required=True, help='Peer name')
@click.option('--public-key', required=True, help='Peer public key')
@click.option('--allowed-ip', required=True, help='Peer allowed IP')
def add_peer(server_config, peer_name, public_key, allowed_ip):
    """Add peer to server configuration"""
    try:
        preshared_key = None
        try:
            preshared_key = key_manager.get_preshared_key(peer_name)
        except:
            pass
        
        config_manager.add_peer_to_server(
            server_config=server_config,
            peer_name=peer_name,
            public_key=public_key,
            allowed_ip=allowed_ip,
            preshared_key=preshared_key
        )
        click.echo(f"✓ Peer '{peer_name}' added!")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
def list_peers():
    """List all configured peers"""
    try:
        peers = peer_manager.list_peers()
        if peers:
            click.echo("👥 Configured peers:")
            for peer in peers:
                click.echo(f"  - {peer.name}")
                click.echo(f"    Public Key: {peer.public_key[:20]}...")
                click.echo(f"    Allowed IPs: {peer.allowed_ips}")
        else:
            click.echo("No peers configured")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
