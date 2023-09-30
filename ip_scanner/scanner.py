# from libraries.my_networkscan import Networkscan
import time
#
from libnmap.parser import NmapParser
from libnmap.process import NmapProcess
from libnmap.reportjson import ReportEncoder

from ip_scanner.networks import get_ip4_addresses
from ipaddress import IPv4Interface
from threading import Thread
from utils.utils import get_main_logger, get_project_root, dmsg
import nmap3
import json
import os

log = get_main_logger('scanner.py')


class IPScanner:
    def __init__(self, _net='0.0.0.0', _sub='255.255.255.255', _cidr='0'):
        self.network = _net
        self.subnet = _sub
        self.cidr = _cidr

    def set_network(self, _net):
        self.network = _net
        return self.network

    def set_subnet(self, _sub):
        self.subnet = _sub
        return self.subnet

    def set_cidr(self, _cidr):
        self.cidr = _cidr
        return self.cidr

    def write_to_file(self, file_name: str, content: dict):
        try:
            with open(file_name, 'w') as file:
                file.write(json.dumps(content, indent=4))
        except Exception as e:
            log.exception(e.__str__())

    def scan_network(self, _net):
        try:
            # my_scan = Networkscan(_net)
            my_scan = nmap3.NmapHostDiscovery()
            # Display information
            # log.debug("Network to scan: " + str(my_scan.network))
            log.debug("Network to scan: " + str(_net))
            # log.debug(("Prefix to scan: " + str(my_scan.network.prefixlen)))
            # log.debug(("Number of hosts to scan: " + str(my_scan.nbr_host)))
            # Run the network scan
            log.debug("Scanning hosts...")
            # Run the scan of hosts using pings
            beg_ts = time.time()
            # my_scan.run()
            res = my_scan.nmap_no_portscan(_net, '-n -PR -T5 --min-parallelism 100')
            # proc = NmapProcess(targets=str(_net), options='-sn -T5')
            # proc.run()
            # parsed = NmapParser.parse(proc.stdout)
            # res = json.dumps(parsed, cls=ReportEncoder, indent=4)
            # res = my_scan.scan_command(_net, arg='-sn -T5')
            end_ts = time.time()
            log.debug(f'DONE for network: {_net}! elapsed time: {end_ts - beg_ts}')
            # Display information
            # Display information
            # log.debug("Number of hosts found: " + str(my_scan.nbr_host_found))
            # Write the file on disk
            # res = my_scan.write_file(file_type=0, filename='./scan_results/' + str(_net).replace('/', '_') + ".yaml")
            path = str(os.path.join(str(get_project_root()), 'scan_results'))
            log.debug(dmsg('') + f'saving results to path: {path}')
            self.write_to_file(str(os.path.join(path, str(_net).replace('/', '_') + ".json")), res)
        except Exception as e:
            log.exception(e.__str__())

    def scan_all(self, scan_threshold=16):
        # self.scan_network('10.0.100.0/24')
        # t = Thread(target=self.scan_network, args=('10.0.100.0/24',))
        # t.start()
        networks = get_ip4_addresses()
        for n in networks:
            ifc = IPv4Interface(str(n['ip']) + '/' + str(n['cidr']))
            # ifc = IPv4Interface(str(n['ip']) + '/24')
            if int(n['cidr']) >= scan_threshold \
                    and str(ifc.network) != '127.0.0.0/16' \
                    and str(ifc.network) != "169.254.0.0/16":
                self.scan_network(ifc.network)
                # print(ifc.network.__str__())
                # t = Thread(target=self.scan_network, args=(ifc.network,))
                # t.start()
            else:
                log.debug('skipping network: ' + str(ifc.network))

# s = IPScanner()
# s.scan_network('10.0.100.0/24')
