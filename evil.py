#!/usr/bin/python
# codigo 3.3

'''@author: Ramon Fontes
   @email: ramon.fontes@imd.ufrn.br'''

import os

from containernet.net import Containernet
from containernet.node import DockerSta
from containernet.cli import CLI
from containernet.term import makeTerm
from mininet.log import info, setLogLevel


def topology():
    "Create a network."
    net = Containernet(ipBase='10.200.0.0/24')

    os.system('sudo xhost +local:docker')
    os.system('export DISPLAY=:1')

    info("*** Creating nodes\n")
    ap1 = net.addAccessPoint('ap1', ssid="simplewifi", mode="g", channel="1",
                             passwd='123456789a', encrypt='wpa2',
                             failMode="standalone", datapath='user',
                             mac='00:00:00:00:00:01')
    ap2 = net.addStation('ap2', cls=DockerSta, dimage="ramonfontes/rogue-ap", cpu_shares=20,
                         mac='00:00:00:00:00:02')
    alice1 = net.addStation('alice', dimage="ramonfontes/seguranca", cpu_shares=20,
                            volumes=['/tmp/.X11-unix:/tmp/.X11-unix:rw'],
                            environment={'DISPLAY':":1"}, passwd='123456789a', 
                            encrypt='wpa2', cls=DockerSta, mac='00:00:00:00:00:03',
                            ip='10.200.0.2/24')
    chuck1 = net.addStation('chuck', dimage="ramonfontes/seguranca", cpu_shares=20,
                            volumes=['/tmp/.X11-unix:/tmp/.X11-unix:rw'],
                            environment={'DISPLAY':":1"}, passwd='123456789a', 
                            encrypt='wpa2', cls=DockerSta, mac='00:00:00:00:00:04',
                            ip='10.200.0.3/24')
    
    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Associating Stations\n")
    net.addLink(alice1, ap1)

    info("*** Starting network\n")
    net.build()
    ap1.start([])

    ap1.cmd("ifconfig ap1-wlan1 up 10.200.0.10 netmask 255.255.255.0")
    ap2.cmd("ifconfig ap2-wlan0 up 10.200.0.1 netmask 255.255.255.0")
    ap2.cmd("echo \'10.200.0.1 ap2\' > /etc/hosts")
    ap2.cmd("service apache2 start")
    ap2.cmd("service mysql start")

    alice1.cmd('route add default gw 10.200.0.1') 
    chuck1.cmd('route add default gw 10.200.0.1')    

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
