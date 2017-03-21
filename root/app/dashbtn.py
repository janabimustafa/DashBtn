#!/usr/bin/python

import sys
import time
import socket
import struct
import logging
import binascii
import subprocess

logging.basicConfig(filename='/var/log/dashbtn.log',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S -- ')

discover_mode=False

if len(sys.argv) > 1:
    if sys.argv[1] == "discover": discover_mode=True

rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
buttons={"a002dc61b924_192.168.1.1":["Bdrm Light - Goldfish",0,["/config/goldfish.sh"]],
         "74c2469ad556_192.168.1.1":["TV - Tide",0,["/config/tide.sh"]],
         "f0272d22edd0_192.168.1.1":["Mickey Mouse - Glad",0,["/config/glad.sh"]]}

logging.info(' ### DashBtn Service Started ### ')
while True:
    packet = rawSocket.recvfrom(2048)
    ethernet_header = packet[0][0:14]
    ethernet_detailed = struct.unpack('!6s6s2s', ethernet_header)
    arp_header = packet[0][14:42]
    arp_detailed = struct.unpack('2s2s1s1s2s6s4s6s4s', arp_header)
    # skip non-ARP packets
    ethertype = ethernet_detailed[2]
    if ethertype != '\x08\x06':
        continue
    source_mac = binascii.hexlify(arp_detailed[5])
    dest_ip = socket.inet_ntoa(arp_detailed[8])
    identifier=source_mac+"_"+str(dest_ip)

    if discover_mode:
        logging.info("We saw an arp from MAC: " + str(source_mac) + " ip: " + str(dest_ip)+ "\n")
        continue

    if identifier in buttons:
        buttons[identifier][1] += 1  #iterate the count of button presses
        logging.info(buttons[identifier][0] + " Pressed  " + str(buttons[identifier][1]) + " times.\n")
        subprocess.Popen(buttons[identifier][2],stdout=subprocess.PIPE).communicate()[0]
