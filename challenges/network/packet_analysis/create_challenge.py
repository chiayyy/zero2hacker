#!/usr/bin/env python3
"""
Network Packet Analysis Challenge
Difficulty: Medium
Points: 75
Category: Network Security

Description:
Analyze this network capture file to find the hidden flag.
The flag was transmitted over the network in an insecure manner.

This script creates a sample PCAP file with hidden data.
"""

import os
import base64
from scapy.all import *

def create_challenge_pcap():
    """Create a PCAP file with hidden flag for analysis"""
    packets = []

    # Normal traffic to mask the real data
    packets.append(IP(dst="8.8.8.8")/ICMP())
    packets.append(IP(dst="1.1.1.1")/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname="google.com")))

    # HTTP traffic with flag
    flag = "flag{network_forensics_master}"
    encoded_flag = base64.b64encode(flag.encode()).decode()

    # Create HTTP request with flag in User-Agent header
    http_request = f"""GET /api/data HTTP/1.1\r
Host: suspicious.example.com\r
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 SecretData:{encoded_flag}\r
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r
Accept-Language: en-US,en;q=0.5\r
Accept-Encoding: gzip, deflate\r
Connection: keep-alive\r
\r
"""

    # Create TCP packet with HTTP request
    tcp_packet = IP(src="192.168.1.100", dst="203.0.113.42")/TCP(sport=12345, dport=80, flags="PA")/Raw(load=http_request)
    packets.append(tcp_packet)

    # HTTP response
    http_response = """HTTP/1.1 200 OK\r
Server: Apache/2.4.41\r
Content-Type: application/json\r
Content-Length: 45\r
\r
{"status": "success", "message": "Data received"}"""

    response_packet = IP(src="203.0.113.42", dst="192.168.1.100")/TCP(sport=80, dport=12345, flags="PA")/Raw(load=http_response)
    packets.append(response_packet)

    # More normal traffic
    packets.append(IP(dst="github.com")/TCP(dport=443, flags="S"))
    packets.append(IP(dst="stackoverflow.com")/TCP(dport=80, flags="S"))

    # FTP traffic with suspicious filename
    ftp_command = f"STOR secret_{encoded_flag}.txt\r\n"
    ftp_packet = IP(src="192.168.1.100", dst="192.168.1.50")/TCP(sport=54321, dport=21, flags="PA")/Raw(load=ftp_command)
    packets.append(ftp_packet)

    # Save to PCAP file
    wrpcap("network_capture.pcap", packets)
    print("PCAP file created: network_capture.pcap")
    print(f"Hidden flag: {flag}")
    print(f"Encoded flag: {encoded_flag}")

def analyze_pcap():
    """Analyze the PCAP file to demonstrate solution"""
    print("\n=== PCAP Analysis ===")

    try:
        packets = rdpcap("network_capture.pcap")
        print(f"Total packets: {len(packets)}")

        for i, packet in enumerate(packets):
            print(f"\nPacket {i+1}:")

            if packet.haslayer(TCP) and packet.haslayer(Raw):
                raw_data = packet[Raw].load.decode('utf-8', errors='ignore')

                # Check for HTTP traffic
                if "HTTP" in raw_data:
                    print(f"  HTTP Traffic found:")
                    print(f"  {packet[IP].src} -> {packet[IP].dst}")

                    # Look for User-Agent with SecretData
                    if "SecretData:" in raw_data:
                        lines = raw_data.split('\r\n')
                        for line in lines:
                            if "SecretData:" in line:
                                encoded_data = line.split("SecretData:")[1].strip()
                                try:
                                    decoded = base64.b64decode(encoded_data).decode()
                                    print(f"  *** HIDDEN FLAG FOUND: {decoded} ***")
                                except:
                                    pass

                # Check for FTP traffic
                elif "STOR secret_" in raw_data:
                    print(f"  FTP Traffic found:")
                    print(f"  {packet[IP].src} -> {packet[IP].dst}")
                    filename = raw_data.strip()
                    if "secret_" in filename:
                        encoded_part = filename.split("secret_")[1].split(".txt")[0]
                        try:
                            decoded = base64.b64decode(encoded_part).decode()
                            print(f"  *** HIDDEN FLAG IN FILENAME: {decoded} ***")
                        except:
                            pass

            elif packet.haslayer(ICMP):
                print(f"  ICMP: {packet[IP].src} -> {packet[IP].dst}")

            elif packet.haslayer(DNS):
                print(f"  DNS Query: {packet[DNS].qd.qname.decode()}")

    except Exception as e:
        print(f"Error analyzing PCAP: {e}")

if __name__ == "__main__":
    print("Creating network analysis challenge...")
    create_challenge_pcap()
    analyze_pcap()

    print("\n=== Challenge Instructions ===")
    print("1. Use Wireshark or similar tools to analyze network_capture.pcap")
    print("2. Look for suspicious HTTP traffic")
    print("3. Examine HTTP headers for hidden data")
    print("4. Check FTP commands for encoded information")
    print("5. Decode any base64 encoded strings you find")
    print("\nTools you can use:")
    print("- Wireshark")
    print("- tshark")
    print("- tcpdump")
    print("- scapy (Python)")
    print("- NetworkMiner")