#!/bin/bash

mkdir -p /home/ubuntu/django_project/goaccess/geoip
cd /home/ubuntu/django_project/goaccess/geoip

wget -q "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=LICENSE_KEY&suffix=tar.gz" -O geoip.tar.gz

tar -xzf geoip.tar.gz
mv GeoLite2-City*/GeoLite2-City.mmdb .

docker restart verben_goaccess