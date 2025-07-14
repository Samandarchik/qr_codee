from scapy.all import *
from scapy.layers.dns import DNSQR, DNSRR
from scapy.layers.inet import IP, TCP, UDP
from scapy.packet import Raw
import threading
import time
from datetime import datetime

class NetworkMonitor:
    def __init__(self):
        self.captured_requests = []
        
    def packet_handler(self, packet):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if packet.haslayer(IP):
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            
            # HTTP trafikini aniqlash
            if packet.haslayer(Raw):
                try:
                    payload = packet[Raw].load.decode('utf-8', errors='ignore')
                    
                    # HTTP GET requestlarini topish
                    if "GET" in payload[:100]:
                        print(f"[{timestamp}] HTTP GET Request")
                        print(f"From: {src_ip} -> To: {dst_ip}")
                        
                        # URL ni ajratib olish
                        lines = payload.split('\n')
                        for line in lines:
                            if line.startswith('GET'):
                                print(f"URL: {line}")
                                break
                            elif line.startswith('Host:'):
                                print(f"Host: {line}")
                                break
                        print("-" * 60)
                    
                    # HTTP POST requestlarini topish
                    elif "POST" in payload[:100]:
                        print(f"[{timestamp}] HTTP POST Request")
                        print(f"From: {src_ip} -> To: {dst_ip}")
                        
                        lines = payload.split('\n')
                        for line in lines:
                            if line.startswith('POST'):
                                print(f"URL: {line}")
                                break
                            elif line.startswith('Host:'):
                                print(f"Host: {line}")
                                break
                        print("-" * 60)
                        
                except Exception as e:
                    pass
            
            # DNS requestlarini kuzatish
            elif packet.haslayer(UDP) and packet[UDP].dport == 53:
                if packet.haslayer(DNSQR):
                    try:
                        dns_query = packet[DNSQR].qname.decode('utf-8')
                        print(f"[{timestamp}] DNS Query: {dns_query}")
                        print(f"From: {src_ip}")
                        print("-" * 60)
                    except:
                        print(f"[{timestamp}] DNS Query detected (couldn't decode)")
                        print(f"From: {src_ip}")
                        print("-" * 60)
    
    def start_monitoring(self, interface=None):
        print("Network monitoring started...")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        try:
            if interface:
                sniff(iface=interface, prn=self.packet_handler, store=0)
            else:
                # Interface belgilanmagan bo'lsa barcha interfacelarni kuzatish
                sniff(prn=self.packet_handler, store=0)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
        except Exception as e:
            print(f"Error: {e}")

# Ishlatish
if __name__ == "__main__":
    monitor = NetworkMonitor()
    
    # macOS uchun odatiy WiFi interface nomi
    # En0 yoki en1 bo'lishi mumkin
    monitor.start_monitoring(interface="en0")  # yoki interface=None qiling