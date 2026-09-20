"""
ID SHIELD - Multi-Network & Any-Device Connectivity Manager
Allows ID SHIELD to run seamlessly on:
  1. Localhost (127.0.0.1:5050)
  2. Local Wi-Fi / Hotspot / LAN (e.g. 192.168.1.64:5050 - any phone, iPad, laptop on same network)
  3. Global Public Web (HTTPS Tunnel - any phone on 4G/5G, remote network, worldwide)
"""

import os
import sys
import time
import socket
import subprocess
import threading
import re

NETWORK_STATE = {
    "local_ip": "127.0.0.1",
    "port": 5050,
    "localhost_url": "http://127.0.0.1:5050",
    "lan_url": "http://127.0.0.1:5050",
    "public_url": None,
    "tunnel_type": None,
    "tunnel_status": "initializing"
}

_tunnel_process = None
_tunnel_thread = None

def get_local_ip():
    """Finds the primary local network IPv4 address (Wi-Fi, Ethernet, Hotspot)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1.0)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"

def update_network_state(port=5050):
    """Refreshes the local network state."""
    ip = get_local_ip()
    NETWORK_STATE["local_ip"] = ip
    NETWORK_STATE["port"] = port
    NETWORK_STATE["localhost_url"] = f"http://127.0.0.1:{port}"
    NETWORK_STATE["lan_url"] = f"http://{ip}:{port}"
    return NETWORK_STATE

def get_network_info():
    """Returns current active network addresses."""
    return NETWORK_STATE

def _run_cloudflare_tunnel(port):
    """Runs Cloudflare Quick Tunnel and extracts public HTTPS URL."""
    global _tunnel_process
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cf_path = os.path.join(base_dir, "cloudflared.exe")

    if not os.path.exists(cf_path):
        cf_path = "cloudflared"

    try:
        cmd = [cf_path, "tunnel", "--url", f"http://127.0.0.1:{port}"]
        creationflags = 0
        if sys.platform == "win32" and hasattr(subprocess, "CREATE_NO_WINDOW"):
            creationflags = subprocess.CREATE_NO_WINDOW

        _tunnel_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            creationflags=creationflags
        )

        NETWORK_STATE["tunnel_type"] = "Cloudflare Tunnel"
        NETWORK_STATE["tunnel_status"] = "connecting"

        url_regex = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

        while True:
            line = _tunnel_process.stdout.readline()
            if not line:
                break
            if not NETWORK_STATE["public_url"]:
                match = url_regex.search(line)
                if match:
                    found_url = match.group(0)
                    NETWORK_STATE["public_url"] = found_url
                    NETWORK_STATE["tunnel_status"] = "active"
                    print("\n" + "=" * 70)
                    print("  [ID SHIELD] LIVE ON ANY DEVICE & ANY NETWORK")
                    print(f"  * Public Global Web (HTTPS) : {found_url}")
                    print(f"  * Local Wi-Fi / LAN Network  : {NETWORK_STATE['lan_url']}")
                    print(f"  * Localhost Machine          : {NETWORK_STATE['localhost_url']}")
                    print("=" * 70 + "\n")

        _tunnel_process.wait()
    except Exception as e:
        print(f"[Tunnel Manager] Cloudflare tunnel note: {e}")
        NETWORK_STATE["tunnel_status"] = "fallback"
        _run_pinggy_tunnel(port)

def _run_pinggy_tunnel(port):
    """Fallback tunnel using SSH / Pinggy if needed."""
    global _tunnel_process
    try:
        ssh_cmd = [
            "ssh", "-p", "443",
            "-R0:localhost:" + str(port),
            "-o", "StrictHostKeyChecking=no",
            "-o", "ServerAliveInterval=30",
            "-T", "a.pinggy.io"
        ]
        creationflags = 0
        if sys.platform == "win32" and hasattr(subprocess, "CREATE_NO_WINDOW"):
            creationflags = subprocess.CREATE_NO_WINDOW

        _tunnel_process = subprocess.Popen(
            ssh_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            creationflags=creationflags
        )

        NETWORK_STATE["tunnel_type"] = "Pinggy SSL Tunnel"
        NETWORK_STATE["tunnel_status"] = "connecting"

        url_regex = re.compile(r"https://[a-zA-Z0-9-]+\.free\.pinggy\.link|https://[a-zA-Z0-9-]+\.a\.pinggy\.link")

        while True:
            line = _tunnel_process.stdout.readline()
            if not line:
                break
            if not NETWORK_STATE["public_url"]:
                match = url_regex.search(line)
                if match:
                    found_url = match.group(0)
                    NETWORK_STATE["public_url"] = found_url
                    NETWORK_STATE["tunnel_status"] = "active"
                    print("\n" + "=" * 70)
                    print("  [ID SHIELD] LIVE ON ANY DEVICE & ANY NETWORK")
                    print(f"  * Public Global Web (HTTPS) : {found_url}")
                    print(f"  * Local Wi-Fi / LAN Network  : {NETWORK_STATE['lan_url']}")
                    print(f"  * Localhost Machine          : {NETWORK_STATE['localhost_url']}")
                    print("=" * 70 + "\n")

        _tunnel_process.wait()
    except Exception as e:
        print(f"[Tunnel Manager] Fallback note: {e}")
        NETWORK_STATE["tunnel_status"] = "unavailable"

def start_tunnel_background(port=5050):
    """Starts the tunnel in a background thread."""
    global _tunnel_thread
    update_network_state(port)

    def worker():
        time.sleep(1.0)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cf_path = os.path.join(base_dir, "cloudflared.exe")
        if os.path.exists(cf_path):
            _run_cloudflare_tunnel(port)
        else:
            _run_pinggy_tunnel(port)

    _tunnel_thread = threading.Thread(target=worker, daemon=True)
    _tunnel_thread.start()

def stop_tunnel():
    """Stops active tunnel process."""
    global _tunnel_process
    if _tunnel_process:
        try:
            _tunnel_process.terminate()
        except Exception:
            pass
