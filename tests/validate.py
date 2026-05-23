import requests
import argparse
from colorama import init, Fore, Style

init(autoreset=True)

def run_test(target_url, malicious_host):
    print(f"\n{Fore.CYAN}[*] Starting Automated Validation Test{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[*] Target: {target_url}{Style.RESET_ALL}")
    
    # 1. Clear state/initial check
    try:
        requests.get(target_url)
    except requests.exceptions.RequestException:
        print(f"{Fore.RED}[!] Cannot connect to target. Is it running?{Style.RESET_ALL}")
        return

    # 2. Attempt Poisoning
    print(f"\n{Fore.YELLOW}[*] Phase 1: Attempting to poison cache with Host: {malicious_host}{Style.RESET_ALL}")
    headers = {'Host': malicious_host}
    try:
        requests.get(target_url, headers=headers)
    except requests.exceptions.ConnectionError:
        print(f"{Fore.GREEN}[i] Target closed connection (expected if mitigation is active and dropping invalid hosts){Style.RESET_ALL}")
    
    # 3. Verify Poisoning (Simulate Victim)
    print(f"\n{Fore.YELLOW}[*] Phase 2: Simulating Victim Request{Style.RESET_ALL}")
    response = requests.get(target_url)
    
    if malicious_host in response.text:
        print(f"\n{Fore.RED}[!!!] VULNERABILITY CONFIRMED: Cache poisoning succeeded.{Style.RESET_ALL}")
        print(f"{Fore.RED}[!!!] Victim received malicious host: {malicious_host}{Style.RESET_ALL}")
        print(f"\n{Fore.MAGENTA}Conclusion: The server is currently VULNERABLE.{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.GREEN}[+++] MITIGATION CONFIRMED: Cache poisoning failed.{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+++] Victim received safe content.{Style.RESET_ALL}")
        
        # Check if the mitigation returned 444 (Connection closed) or routed correctly
        if response.status_code == 200:
             print(f"\n{Fore.GREEN}Conclusion: The server is SECURE. Mitigation is active and working correctly.{Style.RESET_ALL}")
        else:
             print(f"\n{Fore.YELLOW}Conclusion: The server rejected the request (Status: {response.status_code}). Mitigation is active.{Style.RESET_ALL}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validation Test for Cache Poisoning Mitigation")
    parser.add_argument("-t", "--target", default="http://localhost:8080", help="Target URL")
    parser.add_argument("-m", "--malicious-host", default="test-mitigation-hacker.com", help="Test Malicious Host")
    args = parser.parse_args()
    
    run_test(args.target, args.malicious_host)
