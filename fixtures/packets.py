from scapy.all import *
import subprocess
import random

class Sniff:
    """For sniff traffic"""

    def __init__(self, number_link:int):
        self.process_list: list[subprocess.Popen] = []
        self.number_link = number_link

    def run(self, router_name: str, expression: str = None):
        exp = expression if expression else ""
        for i in range(1, self.number_link+1):
            command = f"ip netns exec {router_name} tcpdump -i output{i} {exp} -w /tmp/output{i}.pcap"
            self.process_list.append(subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True))
    
    def stop(self):
        for proc in self.process_list:
            proc.terminate()

class TraffGenerate:
    """For generator packet with Scapy"""

    def __init__(self):
        self.packet_db = []

    def packet_append(self, ip_src: str, ip_dst: str, port_src: int| None = None, port_dst: int | None = None):
        sport = port_src if port_src else random.randint(1, 65535)
        dport = port_dst if port_dst else random.randint(1, 65535)
        pack = Ether()/IP(src=ip_src, dst=ip_dst)/TCP(sport=sport, dport=dport)
        self.packet_db.append(pack)
    
    def get_pcap(self):
        return self.packet_db