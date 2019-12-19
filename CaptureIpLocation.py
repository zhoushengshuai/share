# coding = utf-8

__author__ = 'Zhou Shengshuai'
__version__ = '1.0'

import json
import logging
from urllib import request

import geoip2.database
from IPy import IP

GEOIP_READER = geoip2.database.Reader('C:/study/GeoLite2-City/GeoLite2-City.mmdb')


class CaptureIpLocation(object):
    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d]%(levelname)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.INFO)

    def verify_ip(self, ip):
        try:
            IP(ip)
        except:
            raise ValueError('Invalid IP {0}'.format(ip))

    def capture_ip_address(self, ip):
        response = GEOIP_READER.city(ip)

        # 读取国家代码
        country_iso_code = response.country.iso_code
        # 读取国家名称
        country_name = response.country.name
        # 读取国家名称(中文显示)
        country_cn_name = response.country.names['zh-CN']

        # 读取州(国外)/省(国内)名称
        country_specific_name = response.subdivisions.most_specific.name
        # 读取州(国外)/省(国内)代码
        country_specific_iso_code = response.subdivisions.most_specific.iso_code

        # 读取城市名称
        city_name = response.city.name
        # 读取邮政编码
        city_postal_code = response.postal.code

        # 获取纬度
        location_latitude = response.location.latitude
        # 获取经度
        location_longitude = response.location.longitude

        logging.info('Target IP                 : {0}'.format(ip))
        logging.info('Country ISO Code          : {0}'.format(country_iso_code))
        logging.info('Country Name              : {0}'.format(country_name))
        logging.info('Country CN Name           : {0}'.format(country_cn_name))
        logging.info('Country Specific Name     : {0}'.format(country_specific_name))
        logging.info('Country Specific ISO Code : {0}'.format(country_specific_iso_code))
        logging.info('City Name                 : {0}'.format(city_name))
        if city_postal_code != None:
            logging.info('City Postal Code          : {0}'.format(city_postal_code))
        logging.info('Location Latitude         : {0}'.format(str(location_latitude)))
        logging.info('Location Longitude        : {0}'.format(str(location_longitude)))

    def capture_ip_location(self, ip):
        url = 'http://api.ipstack.com/{ip}?access_key=ee2a84f55397f033d0ae1c106e7ebb34'.format(ip=ip)
        response = request.urlopen(url)

        data = json.load(response)
        latitude = data['latitude']
        longitude = data['longitude']

        logging.info('Target IP                 : {0}'.format(ip))
        logging.info('Location Latitude         : {0}'.format(latitude))
        logging.info('Location Longitude        : {0}'.format(longitude))
        return latitude, longitude


if __name__ == '__main__':
    captureIpLocation = CaptureIpLocation()
    captureIpLocation.verify_ip('119.108.116.209')
    captureIpLocation.capture_ip_address('119.108.116.209')
    captureIpLocation.capture_ip_location('119.108.116.209')
