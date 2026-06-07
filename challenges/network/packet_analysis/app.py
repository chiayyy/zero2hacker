#!/usr/bin/env python3
"""
Network Packet Analysis Challenge - Web Interface
Difficulty: Medium | Points: 75 | Category: Network Security
"""
from flask import Flask, render_template_string, send_file, request
import os, base64

app = Flask(__name__)

FLAG = "FLAG{wireshark_wizard}"
PCAP_PATH = os.path.join(os.path.dirname(__file__), "network_capture.pcap")

def generate_pcap():
    if os.path.exists(PCAP_PATH):
        return True
    try:
        from scapy.all import IP, TCP, UDP, ICMP, DNS, DNSQR, Raw, wrpcap
        packets = []
        packets.append(IP(dst="8.8.8.8")/ICMP())
        packets.append(IP(dst="1.1.1.1")/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname="google.com")))
        encoded_flag = base64.b64encode(FLAG.encode()).decode()
        http_req = (
            f"GET /api/data HTTP/1.1\r\n"
            f"Host: suspicious.example.com\r\n"
            f"User-Agent: Mozilla/5.0 SecretData:{encoded_flag}\r\n"
            f"Accept: */*\r\n\r\n"
        )
        packets.append(IP(src="192.168.1.100", dst="203.0.113.42")/TCP(sport=12345, dport=80, flags="PA")/Raw(load=http_req))
        http_resp = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\":\"ok\"}"
        packets.append(IP(src="203.0.113.42", dst="192.168.1.100")/TCP(sport=80, dport=12345, flags="PA")/Raw(load=http_resp))
        packets.append(IP(src="192.168.1.100", dst="192.168.1.50")/TCP(sport=54321, dport=21, flags="PA")/Raw(load=f"STOR secret_{encoded_flag}.txt\r\n"))
        wrpcap(PCAP_PATH, packets)
        return True
    except Exception:
        return False

def generate_log():
    """Fallback: generate a text-based network log if scapy not available"""
    log_path = os.path.join(os.path.dirname(__file__), "network_log.txt")
    if os.path.exists(log_path):
        return log_path
    encoded_flag = base64.b64encode(FLAG.encode()).decode()
    content = f"""=== Network Traffic Log ===
Captured: 2024-01-15 14:32:01 UTC
Interface: eth0

--- Packet #1 ---
Time: 14:32:01.001
Protocol: ICMP
Src: 192.168.1.100 -> Dst: 8.8.8.8
Type: Echo Request

--- Packet #2 ---
Time: 14:32:01.210
Protocol: DNS
Src: 192.168.1.100:52134 -> Dst: 1.1.1.1:53
Query: google.com (A)

--- Packet #3 ---
Time: 14:32:02.441
Protocol: HTTP
Src: 192.168.1.100:12345 -> Dst: 203.0.113.42:80
GET /api/data HTTP/1.1
Host: suspicious.example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 SecretData:{encoded_flag}
Accept: text/html,application/xhtml+xml
Connection: keep-alive

--- Packet #4 ---
Time: 14:32:02.553
Protocol: HTTP
Src: 203.0.113.42:80 -> Dst: 192.168.1.100:12345
HTTP/1.1 200 OK
Content-Type: application/json
{{"status":"success","message":"Data received"}}

--- Packet #5 ---
Time: 14:32:03.112
Protocol: TCP
Src: 192.168.1.100 -> Dst: github.com:443
Flags: SYN

--- Packet #6 ---
Time: 14:32:03.890
Protocol: FTP
Src: 192.168.1.100:54321 -> Dst: 192.168.1.50:21
Command: STOR secret_{encoded_flag}.txt

=== End of Capture ===
"""
    with open(log_path, 'w') as f:
        f.write(content)
    return log_path

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Packet Analysis Challenge</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Courier New', monospace; background: #0d1117; color: #c9d1d9; margin: 0; padding: 30px; }
        .container { max-width: 750px; margin: 0 auto; }
        h1 { color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
        .badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; margin-right: 6px; }
        .medium { background: #9e6a03; } .points { background: #388bfd22; border: 1px solid #388bfd; color: #58a6ff; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin: 20px 0; }
        a.btn { display: inline-block; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; margin: 5px 5px 0 0; }
        a.btn-blue { background: #1f6feb; } a.btn-blue:hover { background: #388bfd; }
        a.btn-green { background: #238636; } a.btn-green:hover { background: #2ea043; }
        button { background: #238636; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; margin-top: 8px; }
        button:hover { background: #2ea043; }
        input[type=text] { width: 100%; padding: 10px; background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; border-radius: 6px; font-family: monospace; font-size: 14px; }
        label { display: block; margin-bottom: 6px; color: #8b949e; }
        .success { color: #3fb950; background: #0d2b11; border: 1px solid #238636; padding: 15px; border-radius: 6px; font-size: 18px; text-align: center; }
        .error { color: #f85149; background: #2d0f0f; border: 1px solid #f85149; padding: 10px; border-radius: 6px; }
        code { background: #0d1117; padding: 2px 6px; border-radius: 4px; color: #f0883e; }
        pre { background: #0d1117; padding: 15px; border-radius: 6px; border: 1px solid #30363d; overflow-x: auto; color: #3fb950; font-size: 12px; }
        ul li { margin: 6px 0; }
    </style>
</head>
<body>
<div class="container">
    <h1>🌐 Network Packet Analysis</h1>
    <span class="badge medium">Medium</span>
    <span class="badge points">75 pts</span>

    <div class="card">
        <h3>Challenge</h3>
        <p>A network capture was taken during a suspected data exfiltration. Analyze the traffic to find the hidden flag.</p>
        <p>The flag was transmitted over the network encoded in <strong>base64</strong> and hidden inside a standard protocol.</p>
        {% if pcap_ready %}
        <a href="/download/pcap" class="btn btn-blue">⬇ Download network_capture.pcap</a>
        {% endif %}
        <a href="/download/log" class="btn btn-green">⬇ Download network_log.txt</a>
    </div>

    <div class="card">
        <h3>How to Analyze</h3>
        <p>Open the PCAP in <strong>Wireshark</strong> and look for suspicious HTTP headers. Or analyze the log file:</p>
        <pre>import base64

# Find lines with base64 encoded data and decode them
with open("network_log.txt") as f:
    for line in f:
        if "SecretData:" in line:
            encoded = line.split("SecretData:")[1].strip()
            print(base64.b64decode(encoded).decode())</pre>
        <p>Tools: <code>Wireshark</code>, <code>tshark</code>, <code>strings</code>, <code>base64</code></p>
    </div>

    <div class="card">
        <h3>Submit Flag</h3>
        <form method="POST" action="/submit">
            <label>Enter the flag (format: flag{...}):</label>
            <input type="text" name="flag" placeholder="flag{...}" value="{{ submitted or '' }}">
            <button type="submit">Submit</button>
        </form>
        {% if result %}
        <div class="{{ 'success' if correct else 'error' }}" style="margin-top:12px">{{ result }}</div>
        {% endif %}
    </div>
</div>
</body>
</html>
"""

pcap_ready = generate_pcap()
log_path = generate_log()

@app.route('/')
def index():
    return render_template_string(TEMPLATE, pcap_ready=pcap_ready)

@app.route('/download/pcap')
def download_pcap():
    if not os.path.exists(PCAP_PATH):
        return "PCAP not available. Install scapy: pip install scapy", 404
    return send_file(PCAP_PATH, as_attachment=True, download_name='network_capture.pcap')

@app.route('/download/log')
def download_log():
    if not log_path or not os.path.exists(log_path):
        return "Log not available", 404
    return send_file(log_path, as_attachment=True, download_name='network_log.txt')

@app.route('/submit', methods=['POST'])
def submit():
    submitted = request.form.get('flag', '').strip()
    if submitted.lower() == FLAG.lower():
        return render_template_string(TEMPLATE, pcap_ready=pcap_ready, submitted=submitted,
                                      result=f"Correct! Flag: {FLAG}", correct=True)
    return render_template_string(TEMPLATE, pcap_ready=pcap_ready, submitted=submitted,
                                  result="Wrong flag. Keep trying!", correct=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083, debug=False)
