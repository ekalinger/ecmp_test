import collections
from functools import total_ordering
import allure
import pytest
import time
from fixtures.packets import TraffGenerate, Sniff
from scapy.all import sendp, rdpcap
import subprocess

INPUT_IFACE = "input"
num_paths = 3  # Количество путей ECMP

# Инициализация счетчиков путей
path_counts_traffic = collections.defaultdict(int)

def test_with_one_target(pcaps: TraffGenerate, sniff: Sniff):
    ip_dst = "172.172.174.1"
    total_ips = 0
    with allure.step("Генерируем IP-пакеты, а также подсчитываем распределение этих пакетов по линкам"):
        for octet in range(1, 254):
            ip_str = f"10.10.10.{octet}"
            pcaps.packet_append(ip_src=ip_str, ip_dst=ip_dst)
            total_ips += 1
        packet_distribution = total_ips // num_paths
        allure.attach(f"\nНа каждом интерфейсе ожидаем количество пакетов: {packet_distribution}", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Отправляем сгенерированные пакеты на входящий интерфейс стенда"):
        sniff.run("r2", "net 10.10.10.0/24")
        time.sleep(2)
        sendp(pcaps.get_pcap(), iface=INPUT_IFACE, return_packets=True)
        time.sleep(5)
    
    with allure.step("Подсчет количества пакетов, полученных с выходных интерфейсов"):
        recieved_packets = 0
        for i in range(1, num_paths+1):
            pcap_path = f"/tmp/output{i}.pcap"
            file = rdpcap(pcap_path)
            path_counts_traffic[i] = len(file)
            recieved_packets +=len(file)
            allure.attach.file(
                pcap_path, 
                name=f"from_interface_output{i}.pcap", 
                attachment_type="application/octet-stream", 
                extension="pcap"
            )
        assert recieved_packets == total_ips, pytest.fail(f"Количество отправленных{total_ips} не равно количеству принятых{recieved_packets}")

    with allure.step("Анализ соотношений ожидаемых и полученных пакетов по путям"):
        out_str = f"Анализ ECMP для {total_ips} источников по {num_paths} путям:\n"
        out_str += f"{'Path':<10} | {'Expected packets':<10} | {'Received packets':<10}\n"
        out_str += "--------------------------------------------------------\n"
        for path in range(num_paths):
            rec_count = path_counts_traffic[path]
            out_str += f"{path:<10} | {packet_distribution:<16} | {rec_count:<10}\n"
        allure.attach(f"\n{out_str}Большая разница между ожидаемым и полученным сообщает о некорректности работы", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Расчет равномерности (Variance) полученного траффика"):
        counts = list(path_counts_traffic.values())
        if len(counts) > 0:
            variance = max(counts) - min(counts)
            allure.attach(f"\nРазница между макс/мин путем: {variance} (меньше = лучше)", attachment_type=allure.attachment_type.TEXT)

def test_with_link_down(pcaps: TraffGenerate, sniff: Sniff):
    ip_dst = "172.172.174.1"
    total_ips = 0
    with allure.step("Деактивируем один порт"):
        subprocess.run("ip netns exec r1 ip link set veth-r1-l2 down", shell=True)
    with allure.step("Генерируем IP-пакеты, а также подсчитываем распределение этих пакетов по линкам"):
        for octet in range(1, 254):
            ip_str = f"10.10.10.{octet}"
            pcaps.packet_append(ip_src=ip_str, ip_dst=ip_dst)
            total_ips += 1
        packet_distribution = total_ips // num_paths - 1
        allure.attach(f"\nНа каждом интерфейсе ожидаем количество пакетов: {packet_distribution}", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Отправляем сгенерированные пакеты на входящий интерфейс стенда"):
        sniff.run("r2", "net 10.10.10.0/24")
        time.sleep(2)
        sendp(pcaps.get_pcap(), iface=INPUT_IFACE, return_packets=True)
        time.sleep(5)
    
    with allure.step("Подсчет количества пакетов, полученных с выходных интерфейсов"):
        recieved_packets = 0
        for i in range(1, num_paths+1):
            pcap_path = f"/tmp/output{i}.pcap"
            file = rdpcap(pcap_path)
            path_counts_traffic[i] = len(file)
            recieved_packets +=len(file)
            allure.attach.file(
                pcap_path, 
                name=f"from_interface_output{i}.pcap", 
                attachment_type="application/octet-stream", 
                extension="pcap"
            )
        assert recieved_packets == total_ips, pytest.fail("Количество отправленных не равно количеству принятых")

    with allure.step("Анализ соотношений ожидаемых и полученных пакетов по путям"):
        out_str = f"Анализ ECMP для {total_ips} источников по {num_paths} путям:\n"
        out_str += f"{'Path':<10} | {'Expected packets':<10} | {'Received packets':<10}\n"
        out_str += "--------------------------------------------------------\n"
        for path in range(num_paths):
            rec_count = path_counts_traffic[path]
            out_str += f"{path:<10} | {packet_distribution:<16} | {rec_count:<10}\n"
        allure.attach(f"\n{out_str}Большая разница между ожидаемым и полученным сообщает о некорректности работы", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Расчет равномерности (Variance) полученного траффика"):
        counts = list(path_counts_traffic.values())
        if len(counts) > 0:
            variance = max(counts) - min(counts)
            allure.attach(f"\nРазница между макс/мин путем: {variance} (меньше = лучше)", attachment_type=allure.attachment_type.TEXT)
