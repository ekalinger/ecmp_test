from scapy.all import *
import subprocess

class Sniff:
    """For sniff traffic"""

    def __init__(self, number_link:int):
        self.process_list: list[subprocess.Popen] = []
        self.number_link = number_link

    def run(self, router_name: str):
        for i in self.number_link:
            command = f"ip netns exec {router_name} tcpdump -i output{i} -w output{i}.pcap"
            self.process_list.append(subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
    
    def stop(self):
        for proc in self.process_list:
            proc.terminate()

class TraffGenerate:
    """For generator packet with Scapy"""

    def __init__(self):
        self.packet_db = []

    def packet_append(self, ip_src: str, ip_dst: str):
        pack = Ether()/IP(src=ip_src, dst=ip_dst)/TCP()
        self.packet_db.append(pack)
    
    def get_pcap(self):
        return wrpcap(self.packet_db)