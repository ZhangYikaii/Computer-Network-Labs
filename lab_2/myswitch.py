# -*- coding: utf-8 -*-

'''
Ethernet learning switch in Python.

Note that this file currently has the code to implement a "hub"
in it, not a learning switch.  (I.e., it's currently a switch
that doesn't learn.)
'''
from switchyard.lib.userlib import *
import time

def main(net):
    my_interfaces = net.interfaces() 
    mymacs = [intf.ethaddr for intf in my_interfaces]

    log_info("My Interfaces: {}".format([intf.name for intf in my_interfaces]))

    forwTable = {} # 转发表.
    while True:
        try:
            timestamp,input_port,packet = net.recv_packet()
        except NoPackets:
            log_info("Hit except NoPackets.")
            continue
        except Shutdown:
            log_info("Hit except Shutdown.")
            return

        log_info("In ({}) received packet ({}) on ({})".format(net.name, packet, input_port))
        
        # 加入转发表，self-learning
        if packet[0].src not in forwTable.keys():
            forwTable[packet[0].src] = input_port

        if packet[0].dst in mymacs:
            log_info("Packet intended for me")
        else:
            # 广播
            if packet[0].dst not in forwTable.keys():
                for intf in my_interfaces:
                    if input_port != intf.name:
                        log_info("(broadcast) Flooding packet ({}) to ({})\n".format(packet, intf.name))
                        net.send_packet(intf.name, packet)

            else:
                # 在转发表中，直接发送
                log_info("(self-learning) Sending packet ({}) to ({})\n".format(packet, forwTable[packet[0].dst]))
                net.send_packet(forwTable[packet[0].dst], packet)


    net.shutdown()
