from netifaces import interfaces, ifaddresses, AF_INET


def get_cidr(netmask):
    return sum(bin(int(x)).count('1') for x in netmask.split('.'))


def get_ip4_addresses():
    ip_list = []
    for interface in interfaces():
        for link in ifaddresses(interface).get(AF_INET, ()):
            ip_list.append({'ip': link['addr'], 'mask': link['netmask'], 'cidr': get_cidr(link['netmask'])})
    return ip_list



