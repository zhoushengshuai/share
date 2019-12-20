# coding = utf-8

__author__ = 'Zhou Shengshuai'

import logging

import dns.resolver
import requests
from IPy import IP
from geopy.geocoders import Nominatim

IPSTACK_URL = 'http://api.ipstack.com/{ip}?access_key=ee2a84f55397f033d0ae1c106e7ebb34'
CONTENT_TYPE, USER_AGENT = 'application/json', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
HEADERS = {'Content-Type': CONTENT_TYPE, 'User-Agent': USER_AGENT}
PROXIES = {'http': 'http://xxx.xxx.xxx.xxx:8080/', 'https': 'https://xxx.xxx.xxx.xxx:8080/'}
TIMEOUT = 15


class CaptureIpLocation(object):
    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d]%(levelname)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.INFO)
        self.geolocator = Nominatim(user_agent=USER_AGENT, proxies=PROXIES, timeout=TIMEOUT)

    def capture_domain_ip(self, domain):
        try:
            cname_query = dns.resolver.query(domain, dns.rdatatype.CNAME)
            domain = [item.to_text() for record in cname_query.response.answer for item in record.items][0]
        except:
            pass
        a_query = dns.resolver.query(domain, dns.rdatatype.A)
        ip = [item.address for record in a_query.response.answer for item in record.items][0]
        logging.info('Domain & IP          : [{0}, {1}]'.format(domain, ip))
        return ip

    def capture_ip_coordinate(self, ip):
        IP(ip)
        response = requests.get(IPSTACK_URL.format(ip=ip), headers=HEADERS, proxies=PROXIES, timeout=TIMEOUT)
        data = response.json()
        latitude, longitude = data['latitude'], data['longitude']
        logging.info('Latitude & Longitude : [{0}, {1}]'.format(latitude, longitude))
        return latitude, longitude

    def capture_coordinate_location(self, latitude, longitude):
        coordinate = '{0}, {1}'.format(latitude, longitude)
        location = self.geolocator.reverse(coordinate)
        logging.info('Location & Post      : [{0}]'.format(location))
        return location


if __name__ == '__main__':
    captureIpLocation = CaptureIpLocation()
    ip = captureIpLocation.capture_domain_ip('www.cdjkyfsxx.net')
    latitude, longitude = captureIpLocation.capture_ip_coordinate(ip)
    captureIpLocation.capture_coordinate_location(latitude, longitude)
