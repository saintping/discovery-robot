# -*- coding: utf-8 -*-
# Author: matthewliu
# Created: 2019/6/30
#

import logging

LOG_LEVEL = logging.INFO

PRODUCT_KEY = "a1fHGn1zEtm"
DEVICE_NAME = "7AL7DptYafJU0FvjtMH5"

TOPIC_UPSTREAM = "/%s/%s/user/update" % (PRODUCT_KEY, DEVICE_NAME)
TOPIC_UPSTREAM_ERROR = "/%s/%s/user/update/error" % (PRODUCT_KEY, DEVICE_NAME)
TOPIC_DOWNSTREAM = "/%s/%s/user/get" % (PRODUCT_KEY, DEVICE_NAME)

MQTT_URL = "%s.iot-as-mqtt.cn-shanghai.aliyuncs.com" % PRODUCT_KEY
MQTT_PORT = 443
MQTT_KEEPALIVE = 60
