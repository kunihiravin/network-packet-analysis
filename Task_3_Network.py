import subprocess
import re
import pandas as pd
from scapy.all import rdpcap, IP, IPv6, TCP, UDP, ICMP, DNS


# ==========================================
# 1. LIVE PING ANALYSIS
# ==========================================

def analyze_ping(destination="8.8.8.8", count=20):

    result = subprocess.run(
        ["ping", "-n", str(count), destination],
        capture_output=True,
        text=True
    )

    # Extract ping response times
    times = re.findall(
        r"time[=<]\s*(\d+)\s*ms",
        result.stdout,
        re.IGNORECASE
    )

    rtt = [int(t) for t in times]

    received = len(rtt)
    sent = count
    lost = sent - received

    if received > 0:

        average_latency = sum(rtt) / received
        minimum_latency = min(rtt)
        maximum_latency = max(rtt)

        differences = [
            abs(rtt[i] - rtt[i - 1])
            for i in range(1, len(rtt))
        ]

        jitter = (
            sum(differences) / len(differences)
            if differences else 0
        )

    else:

        average_latency = 0
        minimum_latency = 0
        maximum_latency = 0
        jitter = 0

    packet_loss = (lost / sent) * 100

    return {
        "sent": sent,
        "received": received,
        "lost": lost,
        "packet_loss": packet_loss,
        "average_latency": average_latency,
        "minimum_latency": minimum_latency,
        "maximum_latency": maximum_latency,
        "jitter": jitter,
        "rtt_values": rtt
    }


# ==========================================
# 2. WIRESHARK CAPTURE ANALYSIS
# ==========================================

def analyze_capture(filename="Packets.pcapng"):

    packets = rdpcap(filename)

    data = []
    requests = {}
    rtt_values = []

    sent = 0
    received = 0

    timestamps = []

    for packet in packets:

        protocol = "Other"
        source = "Unknown"
        destination = "Unknown"

        timestamp = float(packet.time)
        timestamps.append(timestamp)

        if IP in packet:
            source = packet[IP].src
            destination = packet[IP].dst

        elif IPv6 in packet:
            source = packet[IPv6].src
            destination = packet[IPv6].dst

        if TCP in packet:
            protocol = "TCP"

        elif UDP in packet:
            protocol = "UDP"

        elif ICMP in packet:
            protocol = "ICMP"

        data.append({
            "Protocol": protocol,
            "Source": source,
            "Destination": destination,
            "Size": len(packet),
            "Time": timestamp,
            "DNS": DNS in packet
        })

        # Match ICMP echo requests and replies
        if IP in packet and ICMP in packet:

            icmp = packet[ICMP]

            if icmp.type == 8:

                sent += 1

                key = (
                    packet[IP].src,
                    packet[IP].dst,
                    icmp.id,
                    icmp.seq
                )

                requests.setdefault(key, []).append(timestamp)

            elif icmp.type == 0:

                key = (
                    packet[IP].dst,
                    packet[IP].src,
                    icmp.id,
                    icmp.seq
                )

                if key in requests and requests[key]:

                    start_time = requests[key].pop(0)

                    rtt = (timestamp - start_time) * 1000

                    rtt_values.append(rtt)
                    received += 1

    df = pd.DataFrame(data)

    total_packets = len(df)
    total_bytes = int(df["Size"].sum()) if total_packets else 0

    if rtt_values:

        average_latency = sum(rtt_values) / len(rtt_values)
        minimum_latency = min(rtt_values)
        maximum_latency = max(rtt_values)

    else:

        average_latency = 0
        minimum_latency = 0
        maximum_latency = 0

    if len(rtt_values) > 1:

        differences = [
            abs(rtt_values[i] - rtt_values[i - 1])
            for i in range(1, len(rtt_values))
        ]

        jitter = sum(differences) / len(differences)

    else:

        jitter = 0

    lost = sent - received

    packet_loss = (
        (lost / sent) * 100 if sent > 0 else 0
    )

    duration = (
        max(timestamps) - min(timestamps)
        if len(timestamps) > 1 else 0
    )

    throughput_mbps = (
        (total_bytes * 8) / duration / 1_000_000
        if duration > 0 else 0
    )

    results = {

        "total_packets": total_packets,
        "total_bytes": total_bytes,

        "tcp_count": int((df["Protocol"] == "TCP").sum()),
        "udp_count": int((df["Protocol"] == "UDP").sum()),
        "icmp_count": int((df["Protocol"] == "ICMP").sum()),
        "dns_count": int(df["DNS"].sum()),

        "average_packet_size": (
            df["Size"].mean() if total_packets else 0
        ),

        "average_latency": average_latency,
        "minimum_latency": minimum_latency,
        "maximum_latency": maximum_latency,
        "jitter": jitter,

        "sent": sent,
        "received": received,
        "lost": lost,
        "packet_loss": packet_loss,

        "duration": duration,
        "throughput_mbps": throughput_mbps,

        "rtt_values": rtt_values
    }

    return df, results

