#!/bin/sh
# need root user run

cp iot_hub.service /etc/systemd/system
systemctl enable iot_hub
systemctl start iot_hub

