# WireGuard VPN Implementation

A complete, production-ready WireGuard VPN implementation with a powerful CLI tool for managing VPN servers and clients.

## 🎯 Features

- ✅ **Full WireGuard Protocol Support** - Built on the proven WireGuard cryptographic standards
- ✅ **Server & Client Setup** - Complete templates for both roles
- ✅ **Automatic Key Generation** - Cryptographically secure keypair generation
- ✅ **Peer Management** - Add, remove, and manage VPN peers
- ✅ **Configuration Management** - Auto-generate WireGuard configurations
- ✅ **Interface Control** - Bring interfaces up/down and manage settings
- ✅ **CLI Tool** - Comprehensive command-line interface for all operations
- ✅ **Secure Key Storage** - Keys stored with restrictive permissions (600)
- ✅ **Logging** - Full operational logging for debugging

## 📋 Prerequisites

### System Requirements
- Linux (Ubuntu 18.04+, Debian 10+, or compatible)
- Root/sudo access (required for interface management)
- Python 3.7+

### Install WireGuard
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install wireguard wireguard-tools

# Or install from source
git clone https://git.zx2c4.com/wireguard-linux-compat
cd wireguard-linux-compat
make
sudo make install
```

### Install Python Dependencies
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

### 1. Generate Keys

Generate keypairs for server and clients:

```bash
# Generate server keypair
python3 wireguard_vpn.py generate-keys --name server

# Generate client keypair
python3 wireguard_vpn.py generate-keys --name client1
python3 wireguard_vpn.py generate-keys --name client2
```

Keys are stored in the `keys/` directory with secure permissions.

### 2. Create Server

Set up your VPN server:

```bash
python3 wireguard_vpn.py create-server \
  --name server \
  --address 10.0.0.1/24 \
  --port 51820
```

This creates a server configuration file in `configs/server.conf`

### 3. Create Clients

Create client configurations pointing to your server:

```bash
# Get server public key first
cat keys/server_public.key

# Create client config
python3 wireguard_vpn.py create-client \
  --name client1 \
  --server-public-key <server-public-key> \
  --server-endpoint <server-ip>:51820 \
  --client-address 10.0.0.2/32
```

### 4. Start VPN (Root Required)

Bring up the WireGuard interface:

```bash
sudo python3 wireguard_vpn.py start --name wg0
```

### 5. Verify Status

Check if the interface is running:

```bash
sudo python3 wireguard_vpn.py status --name wg0
```

## 📚 CLI Commands Reference

### Key Management
```bash
# Generate new keypair
python3 wireguard_vpn.py generate-keys --name <name>
```

### Server Setup
```bash
# Create server configuration
python3 wireguard_vpn.py create-server \
  --name <server-name> \
  --address <10.0.0.1/24> \
  --port <51820>
```

### Client Setup
```bash
# Create client configuration
python3 wireguard_vpn.py create-client \
  --name <client-name> \
  --server-public-key <key> \
  --server-endpoint <ip:port> \
  --client-address <10.0.0.x/32>
```

### Interface Control
```bash
# Start interface
sudo python3 wireguard_vpn.py start --name wg0

# Stop interface
sudo python3 wireguard_vpn.py stop --name wg0

# Check status
sudo python3 wireguard_vpn.py status --name wg0

# Show all interfaces
sudo python3 wireguard_vpn.py show-all-status
```

### Configuration Management
```bash
# List all configurations
python3 wireguard_vpn.py list-configs

# Show specific configuration
python3 wireguard_vpn.py show-config --name server

# List all peers
python3 wireguard_vpn.py list-peers
```

## 📁 File Structure

```
.
├── wireguard_vpn.py          # Main CLI application
├── key_manager.py            # Cryptographic key management
├── config.py                 # Configuration file management
├── peer.py                   # Peer configuration and management
├── interface.py              # WireGuard interface control
├── requirements.txt          # Python dependencies
├── .env.example              # Environment configuration template
├── .gitignore                # Git ignore rules
├── keys/                     # Generated cryptographic keys (mode 700)
│   ├── server_private.key
│   ├── server_public.key
│   ├── client1_private.key
│   ├── client1_public.key
│   └── ...
├── configs/                  # Generated WireGuard configurations (mode 700)
│   ├── server.conf
│   ├── client1.conf
│   └── ...
└── peers.json                # Peer management database
```

## 🔒 Security Considerations

1. **Key Permissions**: Private keys are stored with `600` permissions (read/write for owner only)
2. **Config Permissions**: Configuration files are stored with `600` permissions
3. **Preshared Keys**: Generate and use preshared keys for additional security
4. **Firewall**: Ensure firewall rules allow WireGuard port (default 51820 UDP)
5. **Key Rotation**: Regularly rotate keys for enhanced security
6. **Endpoint Restrictions**: Validate all endpoint addresses before adding peers

## 🔧 Advanced Usage

### Using Preshared Keys

```bash
# Generate preshared key (done automatically)
# To view the PSK:
cat keys/client1_psk.key
```

### Manual Configuration

Edit configurations directly in `configs/` directory before applying:

```bash
nano configs/server.conf
```

### Network Configuration

Add IP address to interface:

```bash
sudo ip address add 10.0.0.1/24 dev wg0
```

Set up IP forwarding on server:

```bash
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -A FORWARD -i wg0 -j ACCEPT
sudo iptables -A FORWARD -o wg0 -j ACCEPT
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

## 📊 Monitoring

View active connections:

```bash
sudo wg show
```

View specific interface:

```bash
sudo wg show wg0
```

View peer statistics:

```bash
sudo ip link show wg0
```

## 🐛 Troubleshooting

### Interface won't start
```bash
# Check if wireguard is installed
wg --version

# Check kernel module
lsmod | grep wireguard

# Load module if not present
sudo modprobe wireguard
```

### Permission denied errors
```bash
# Ensure commands are run with sudo
sudo python3 wireguard_vpn.py start --name wg0
```

### Can't connect to VPN
- Verify firewall allows UDP port 51820
- Check that client has correct server endpoint
- Verify peer public keys match between configs
- Check IP routing rules

### No connectivity after connecting
```bash
# Check routes
ip route

# Check iptables rules
sudo iptables -L -n

# Check DNS
cat /etc/resolv.conf
```

## 📖 WireGuard Resources

- [WireGuard Official Site](https://www.wireguard.com/)
- [WireGuard Installation Guide](https://www.wireguard.com/install/)
- [WireGuard Quick Start](https://www.wireguard.com/quickstart/)
- [WireGuard Community](https://www.wireguard.com/#community)

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guide
- All functions have docstrings
- Security best practices are followed
- Changes are tested before submission

## 📝 License

This project is provided as-is for educational and private use.

## ⚠️ Disclaimer

This VPN implementation is for educational and authorized use only. Users are responsible for:
- Complying with local laws and regulations
- Obtaining proper authorization before deploying
- Maintaining security of their keys and credentials
- Regular security audits and updates

**Never share private keys or configurations**

---

## 🎓 Learning Resources

### Understanding WireGuard

WireGuard is a modern VPN protocol that uses:
- **Curve25519** for key exchange
- **ChaCha20** for encryption
- **Poly1305** for authentication
- Stateless design for better scalability

### Basic Flow

1. **Key Generation**: Create private/public key pairs
2. **Configuration**: Create interface config with allowed peers
3. **Interface Setup**: Create and configure wg0 interface
4. **Peer Addition**: Add peers with their public keys
5. **Traffic Flow**: WireGuard encrypts and routes traffic through peers

Enjoy your secure VPN! 🔐
