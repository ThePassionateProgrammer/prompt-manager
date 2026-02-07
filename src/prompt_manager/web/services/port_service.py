"""
Port Management Service

Handles port availability checking, process management, and port setup.
"""

import socket
import subprocess
import time
from typing import List, Optional


class PortService:
    """Service for managing port availability and setup."""
    
    def __init__(self, default_port: int = 8000, max_attempts: int = 10):
        self.default_port = default_port
        self.max_attempts = max_attempts
    
    def check_port_available(self, port: int) -> bool:
        """Check if a port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def get_processes_using_port(self, port: int) -> List[str]:
        """Get list of processes using a specific port."""
        try:
            result = subprocess.run(['lsof', '-i', f':{port}'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Skip header line
                    return lines[1:]  # Return process lines
            return []
        except FileNotFoundError:
            return []
    
    def kill_processes_on_port(self, port: int) -> bool:
        """Kill processes using a specific port."""
        try:
            result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        print(f"Killing process {pid} on port {port}")
                        subprocess.run(['kill', '-9', pid])
                return True
            return False
        except FileNotFoundError:
            return False
    
    def find_available_port(self, start_port: Optional[int] = None) -> Optional[int]:
        """Find an available port starting from start_port."""
        start = start_port or self.default_port
        for port in range(start, start + self.max_attempts):
            if self.check_port_available(port):
                return port
        return None
    
    def setup_port(self) -> Optional[int]:
        """Setup port with user interaction."""
        print("🔍 Checking port availability...")
        
        if self.check_port_available(self.default_port):
            print(f"✅ Port {self.default_port} is available")
            return self.default_port
        
        print(f"❌ Port {self.default_port} is in use")
        
        # Show what's using the port
        processes = self.get_processes_using_port(self.default_port)
        if processes:
            print(f"📋 Processes using port {self.default_port}:")
            for process in processes:
                print(f"   {process}")
        
        while True:
            print("\n🛠️  Port Management Options:")
            print("1. Kill processes on port 8000 and use it")
            print("2. Use a different port")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                if self.kill_processes_on_port(self.default_port):
                    print(f"✅ Killed processes on port {self.default_port}")
                    # Wait a moment for the port to be released
                    time.sleep(1)
                    if self.check_port_available(self.default_port):
                        print(f"✅ Port {self.default_port} is now available")
                        return self.default_port
                    else:
                        print(f"❌ Port {self.default_port} still not available")
                else:
                    print(f"❌ Failed to kill processes on port {self.default_port}")
            
            elif choice == "2":
                available_port = self.find_available_port(self.default_port + 1)
                if available_port:
                    print(f"✅ Found available port: {available_port}")
                    return available_port
                else:
                    print("❌ No available ports found")
            
            elif choice == "3":
                print("👋 Exiting...")
                return None
            
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
