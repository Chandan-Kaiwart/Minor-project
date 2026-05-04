import requests
import os
import time
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama for beautiful terminal output
init(autoreset=True)

class IoTSecurityClient:
    def __init__(self, target_ip, port=5000):
        self.target_ip = target_ip
        self.port = port
        self.base_url = f"http://{target_ip}:{port}"
        self.save_dir = "captured_evidence"
        
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def log(self, message, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "info":
            print(f"[{Fore.CYAN}{timestamp}{Style.RESET_ALL}] {message}")
        elif level == "success":
            print(f"[{Fore.GREEN}{timestamp}{Style.RESET_ALL}] {Fore.GREEN}{message}")
        elif level == "warn":
            print(f"[{Fore.YELLOW}{timestamp}{Style.RESET_ALL}] {Fore.YELLOW}{message}")
        elif level == "error":
            print(f"[{Fore.RED}{timestamp}{Style.RESET_ALL}] {Fore.RED}{message}")
        elif level == "attack":
            print(f"[{Fore.MAGENTA}{timestamp}{Style.RESET_ALL}] {Fore.MAGENTA}{Style.BRIGHT}{message}")

    def get_status(self):
        try:
            r = requests.get(f"{self.base_url}/status", timeout=3)
            if r.status_code == 200:
                data = r.json()
                self.log("Connected to IoT Device.")
                print(f"    - Crypto: {Fore.YELLOW}{data['crypto_status']}")
                print(f"    - Threat Level: {Fore.RED if data['threat_level'] == 'HIGH' else Fore.GREEN}{data['threat_level']}")
                print(f"    - Secured: {data['secured']}")
                return data
            return None
        except Exception as e:
            self.log(f"Connection Failed: {e}", "error")
            return None

    def launch_attack(self):
        self.log("Injecting ECC Exploitation Payload...", "attack")
        time.sleep(1)
        try:
            r = requests.get(f"{self.base_url}/exploit", timeout=5)
            if r.status_code == 200:
                data = r.json()
                self.log("EXPLOIT SUCCESSFUL!", "success")
                self.log(f"Intercepted Data: {data.get('intercepted_key', 'N/A')}", "success")
                return True
            else:
                self.log(f"Exploit Blocked: {r.json().get('error', 'Unknown')}", "error")
                return False
        except Exception as e:
            self.log(f"Exploit Error: {e}", "error")
            return False

    def capture_and_save(self):
        self.log("Attempting to intercept camera feed...", "info")
        try:
            r = requests.get(f"{self.base_url}/camera", timeout=5, stream=True)
            if r.status_code == 200:
                filename = f"capture_{int(time.time())}.jpg"
                filepath = os.path.join(self.save_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                self.log(f"Snapshot saved to: {filepath}", "success")
                # In a real GUI we'd show it here, in CLI we just save it.
                return True
            else:
                self.log(f"Camera Access Denied: {r.status_code}", "error")
                return False
        except Exception as e:
            self.log(f"Capture Error: {e}", "error")
            return False

    def secure_device(self):
        self.log("Initiating PQC Upgrade (ML-KEM-768)...", "info")
        try:
            r = requests.post(f"{self.base_url}/upgrade_pqc", timeout=5)
            if r.status_code == 200:
                self.log("DEVICE HARDENED: Transitioned to Post-Quantum Security", "success")
                self.log(f"Server Response: {r.json().get('result')}", "info")
                return True
            return False
        except Exception as e:
            self.log(f"Security Upgrade Failed: {e}", "error")
            return False

def show_banner():
    banner = f"""
{Fore.MAGENTA}{Style.BRIGHT}
    ██████╗  ██████╗  ██████╗     ██╗ ██████╗ ████████╗
    ██╔══██╗██╔═══██╗██╔════╝     ██║██╔═══██╗╚══██╔══╝
    ██████╔╝██║   ██║██║          ██║██║   ██║   ██║   
    ██╔═══╝ ██║   ██║██║          ██║██║   ██║   ██║   
    ██║     ╚██████╔╝╚██████╗     ██║╚██████╔╝   ██║   
    ╚═╝      ╚═════╝  ╚═════╝     ╚═╝ ╚═════╝    ╚═╝   
    Quantum-Ready IoT Attack & Defense Simulator
    -------------------------------------------
    """
    print(banner)

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    show_banner()
    
    ip = input(f"{Fore.WHITE}Enter Phone IP Address: ").strip()
    if not ip: ip = "127.0.0.1" # Default to local for testing
    
    client = IoTSecurityClient(ip)
    
    while True:
        print(f"\n{Fore.WHITE}--- MENU ---")
        print("1. Scan Device Status")
        print("2. Launch Attack (ECC Breach)")
        print("3. Capture & Download Image")
        print("4. Secure Device (PQC Upgrade)")
        print("5. Reset Security (Simulate Vulnerability)")
        print("0. Exit")
        
        choice = input(f"\n{Fore.CYAN}Selection > ")
        
        if choice == '1':
            client.get_status()
        elif choice == '2':
            client.launch_attack()
        elif choice == '3':
            client.capture_and_save()
        elif choice == '4':
            client.secure_device()
        elif choice == '5':
            try:
                requests.post(f"{client.base_url}/reset")
                print(f"{Fore.GREEN}Device Reset Successfully.")
            except:
                print(f"{Fore.RED}Reset Failed.")
        elif choice == '0':
            break
        else:
            print(f"{Fore.RED}Invalid Choice.")

if __name__ == "__main__":
    main()
