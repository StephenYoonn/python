#!/usr/bin/env python

'''
CS352 Assignment 1: Network Time Protocol
You can work with 1 other CS352 student

DO NOT CHANGE ANY OF THE FUNCTION SIGNATURES BELOW
'''

#from socket import socket, AF_INET, 
import socket
import struct
from datetime import datetime


def getNTPTimeValue(server="time.apple.com", port=123) -> (bytes, float, float):
    # add your code here 
    #header remains constant, take timestamp(reference)/ keep other fields same and make ntp packet to send to server
    #int packet_size = bytes.size

    #unpack 1 byte(beginning 8 bits), then 47 more bytes(until transmit timestamp)
    fs = "!1B"  + 47 * "B"

    #set the first 8 bits to 00, 011, 011 then 47 other bits
    sendpkt = struct.pack(fs, 0x1B, *([0] * 47))

    #timestamp1
    time_difference = datetime.utcnow() - datetime(1970, 1, 1, 0, 0, 0)
    secs = time_difference.days*24.0*60.0*60.0 + time_difference.seconds
    T1 = secs + float(time_difference.microseconds / 1000000.0)


    #open client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #send client pkt with server port
    client_socket.sendto(sendpkt, (server, port))

    #recv packt
    pkt = client_socket.recv(100)

    #close socket
    client_socket.close()
    
    #print(pkt)

    #timestamp2
    time_difference = datetime.utcnow() - datetime(1970, 1, 1, 0, 0, 0)
    secs = time_difference.days*24.0*60.0*60.0 + time_difference.seconds
    T4 = secs + float(time_difference.microseconds / 1000000.0)

    return (pkt, T1, T4)

def ntpPktToRTTandOffset(pkt: bytes, T1: float, T4: float) -> (float, float):
    # add your code here 

    #fs = "!48B" #48 bytes unpack
    
    #arr = struct.unpack(fs,pkt)

    modified_packet = bytearray(pkt)

    #change first bits to 00, 011, 011
    modified_packet[0] = 0
    modified_packet[1] = 0
    modified_packet[2] = 0
    modified_packet[3] = 1
    modified_packet[4] = 1
    modified_packet[5] = 0
    modified_packet[6] = 1
    modified_packet[7] = 1
    
    #5,6 reference time
    #7,8 origin
    #9,10 receive - T2
    #11,12 transmit - T3

    #t2 : byte (32-40) -> 31-39
    T2start = 32
    T2end = 40

    #t3: byte (41-48) -> 40- 47
    T3start = 40
    T3end = 48

    #startbit2 = T2end - T2start + 1
    #startbit3 = T3end - T3start + 1

   
    data2 = modified_packet[T2start:T2end]
    data3 = modified_packet[T3start:T3end]
    #print(len(data2))
    #print(len(data3))
    

    T2result = bin(struct.unpack('>Q', data2)[0])[2:]
    T2seconds = (T2result[:32])
    T2fraction = T2result[32:]

    #num2 = hex(int(T2seconds, 2))
    T2secondfloat = int(T2seconds, 2)
    #print(T2secondfloat)

    T2fractionfloat = int(T2fraction, 2) / (2 ** len(T2fraction))
    #print(T2fractionfloat)

    T2 = T2secondfloat + T2fractionfloat - 2208988800.0
    

    T3result = bin(struct.unpack('>Q', data3)[0])[2:]
    T3seconds = (T3result[:32])
    T3fraction = T3result[32:]

    T3secondfloat = int(T3seconds, 2)
    #print(T3secondfloat)

    T3fractionfloat = int(T3fraction, 2) / (2 ** len(T3fraction))
    #print(T3fractionfloat)

    T3 = T3secondfloat + T3fractionfloat - 2208988800.0
    
    #print(datetime(1970, 1, 1, 0, 0, 0))

    RTT = (T4- T1) - (T3- T4)
    offset = ((T2 - T1) + (T3 - T4))/2.0
    
    return (RTT, offset)

def getCurrentTime(server="time.apple.com", port=123, iters=20) -> float:
    # add your code here
    offsets = []

    for time in range(iters):
        (pkt, T1, T4) = getNTPTimeValue(server, port)
        (RTT, offset) = ntpPktToRTTandOffset(pkt, T1, T4)
        offsets.append(offset)

    average = 0.0
    for number in offsets:
        average = average + number

    average = average /20.0

    #currentTime = average + current time with microsecond granularity
    
    time_difference = datetime.utcnow() - datetime(1970, 1, 1, 0, 0, 0)
    secs = time_difference.days*24.0*60.0*60.0 + time_difference.seconds

    tfinal = secs + float(time_difference.microseconds / 1000000.0)

    currentTime = average + tfinal

    return currentTime


if __name__ == "__main__":

    print(getCurrentTime())
