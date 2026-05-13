#!/usr/bin/env python3
"""
WireGuard VPN Test Suite
Tests website access and connectivity
"""

import subprocess
import requests
import socket
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class VPNTester:
    """Tests VPN connectivity and website access"""
    
    def __init__(self, interface: str = "wg0"):
        self.interface = interface
        self.test_urls = [
            'https://www.google.com',
            'https://www.cloudflare.com',
            'https://www.github.com',
            'https://www.wikipedia.org',
            'http://ipv4.icanhazip.com'  # Returns your IP
        ]
    
    def test_interface_up(self) -> bool:
        """Check if VPN interface is up"""
        try:
            result = subprocess.run(
                ['ip', 'link', 'show', self.interface],
                capture_output=True,
                text=True
            )
            return 'UP' in result.stdout
        except Exception as e:
            logger.error(f"Failed to check interface: {e}")
            return False
    
    def test_dns_resolution(self) -> bool:
        """Test DNS resolution"""
        try:
            socket.gethostbyname('www.google.com')
            return True
        except socket.gaierror as e:
            logger.error(f"DNS resolution failed: {e}")
            return False
    
    def test_website_access(self, url: str = None) -> Tuple[bool, str]:
        """Test access to websites through VPN"""
        if url is None:
            url = self.test_urls[0]
        
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200, f"✓ {url}: {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, f"✗ {url}: {str(e)}"
    
    def test_all_websites(self):
        """Test access to all test URLs"""
        print("\n🌐 Testing Website Access Through VPN\n")
        results = []
        
        for url in self.test_urls:
            success, message = self.test_website_access(url)
            print(message)
            results.append(success)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n✅ Success Rate: {success_rate:.1f}%")
        return success_rate >= 80
    
    def test_get_public_ip(self):
        """Get your public IP through VPN"""
        try:
            response = requests.get('http://ipv4.icanhazip.com', timeout=5)
            if response.status_code == 200:
                ip = response.text.strip()
                print(f"\n🌍 Your Public IP Through VPN: {ip}")
                return ip
        except Exception as e:
            logger.error(f"Failed to get public IP: {e}")
        return None
    
    def run_full_test(self) -> bool:
        """Run full VPN connectivity test"""
        print(f"\n{'='*50}")
        print("WireGuard VPN Connectivity Test")
        print(f"{'='*50}\n")
        
        print(f"🔧 Interface: {self.interface}")
        
        # Test 1: Interface
        print(f"\n1️⃣ Checking interface status...")
        if self.test_interface_up():
            print(f"✓ Interface {self.interface} is UP")
        else:
            print(f"✗ Interface {self.interface} is DOWN or not found")
            return False
        
        # Test 2: DNS
        print(f"\n2️⃣ Testing DNS resolution...")
        if self.test_dns_resolution():
            print(f"✓ DNS resolution working")
        else:
            print(f"✗ DNS resolution failed")
            return False
        
        # Test 3: Website Access
        print(f"\n3️⃣ Testing website access through VPN...")
        all_success = self.test_all_websites()
        
        # Test 4: Public IP
        print(f"\n4️⃣ Getting public IP...")
        self.test_get_public_ip()
        
        # Summary
        print(f"\n{'='*50}")
        if all_success:
            print("✅ VPN is working! Website access is available.")
        else:
            print("⚠️ Some tests failed. Check your configuration.")
        print(f"{'='*50}\n")
        
        return all_success

if __name__ == '__main__':
    tester = VPNTester(interface='wg0')
    tester.run_full_test()
