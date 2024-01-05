#!/usr/bin/python3
from scapy.all import *
import sys
import time
import math

def main(inputFile, serverip, serverport ):
    # make sure to load the HTTP layer
    percentiles = []
    latencies = []

    load_layer("http")
    pcap_filename = inputFile
    # example counters
    number_of_packets_total = 0
    number_of_tcp_packets = 0
    number_of_udp_packets = 0
    processed_file = rdpcap(pcap_filename)# read in the pcap file
    sessions = processed_file.sessions() #get the list of sessions/TCP connections
    latency = 0

    for session in sessions:
        first_request_time = None

        for packet in sessions[session]: # for each packet in each session
            #packet.show()
            number_of_packets_total = number_of_packets_total + 1 #increment total packet count

            if packet.haslayer(TCP): # check is the packet is a TCP packet
                number_of_tcp_packets = number_of_tcp_packets + 1 # count TCP packets
                source_ip = packet[IP].src # note that a packet is represented as a python hash table with keys corresponding to
                dest_ip = packet[IP].dst # layer field names and the values of the hash table as the packet field values

                if (packet.haslayer(HTTP)): # test for an HTTP packet
                    first_time = packet.time

                    if HTTPRequest in packet:
                        arrival_time = packet.time # get unix time of the packet
                        #new = arrival_time
                        if first_request_time is None:
                            first_request_time = arrival_time

                            # Record the HTTP request details
                            request_info = {
                                'arrival_time': arrival_time,
                                'source_ip': source_ip,
                                'dest_ip': dest_ip,
                                'port': packet[TCP].dport
                            }

                    elif HTTPResponse in packet:
                        # Calculate latency for this request-response pair
                        latency = arrival_time - first_request_time
                        latencies.append(latency)

                        print(f"Got an HTTP response at time: {arrival_time} for server IP {dest_ip}")
                        print(f"Round-trip latency: {latency:.6f} seconds")

                        print ("Got a TCP packet part of an HTTP request at time:%0.4f for server IP %s" % (arrival_time,dest_ip))

            else:
                if packet.haslayer(UDP):
                    number_of_udp_packets = number_of_udp_packets + 1

        if latencies:
            avg_latency = sum(latencies)/len(latencies)
            percentiles = calculate_percentiles(latencies)

            #print(f"\nStatistics for session {session}:")
            print(f"Average latency: {avg_latency:.6f}")
            print(f"Percentiles: {percentiles[0]:.6f}, {percentiles[1]:.6f} {percentiles[2]:.6f}"
                  f" {percentiles[3]:.6f} {percentiles[4]:.6f}\n")


    print("Got %d packets total, %d TCP packets, and %d UDP packets" %
          (number_of_packets_total, number_of_tcp_packets, number_of_udp_packets))

        

    print("Got %d packets total, %d TCP packets and %d UDP packets" %
    (number_of_packets_total, number_of_tcp_packets,number_of_udp_packets))

    #latency = float(latency / number_of_tcp_packets)
    #print(f"Website: {website}")
    #print(f"Destination Address: {dest_ip}")
    #print(f"Port Number: {serverport}")
    #print(f"AVERAGE LATENCY: {latency}")
    #print(f"PERCENTILES: {percentiles[0]} {percentiles[1]} {percentiles[2]} {percentiles[3]} {percentiles[4]} ")


def calculate_percentiles(latencies):
    latencies_sorted = sorted(latencies)
    n = len(latencies_sorted)
    percentiles = [latencies_sorted[int(n * p)] for p in [0.25, 0.5, 0.75, 0.95, 0.99]]
    return percentiles

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 measure-webserver.py <input-file> <server-ip> <server-port>")
        sys.exit()

    inputFile, serverip, serverport = sys.argv[1:4]
    
    main(inputFile, serverip, serverport)