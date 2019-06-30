# -*- coding: utf-8 -*-
# Author: matthewliu
# Created: 2019/6/30
#
# send iot voltage to aliyun iot-hub every 60 seconds
#

import hmac
import json
import sys
import time
from hashlib import sha1
from uuid import getnode as get_mac

import brickpi3
import paho.mqtt.client as mqtt

from iot_properties import *


# The callback for when the client receives a CONNACK response from the server.
def on_connect(mqttc, userdata, flags, rc):
    logging.info("on_connect, Connected with result code %s" % str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    if rc == 0:
        result = client.subscribe(TOPIC_DOWNSTREAM)
        logging.info("on_connect, subscribe result: %s" % str(result))


def on_publish(mqttc, obj, mid):
    logging.info("on_publish, mid: %s" % str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    logging.info("on_subscribe, Subscribed: %s %s" % (str(mid), str(granted_qos)))


def on_message(mqttc, userdata, msg):
    logging.info("on_message, topic: %s payload: %s" % (msg.topic, str(msg.payload)))


def on_log(mqttc, obj, level, string):
    logging.debug("paho %s %s" % (level, string))


def gen_sign_4aliyun(key, params):
    """
    https://help.aliyun.com/document_detail/63656.html?spm=a2c4g.11186623.6.651.2a531cb6z5PwI3
    :param key:
    :param params:
    :return:
    """

    sorted_params = sorted(params.items(), key=lambda x: x[0])
    content = ""
    for k, v in sorted_params:
        content += str(k) + str(v)

    logging.debug("hmacsha1: %s %s" % (key, content))
    hmac_code = hmac.new(key.encode(encoding="utf-8"), content.encode(encoding="utf-8"), sha1)
    return hmac_code.hexdigest()


def connect_ailyun(client, username, password):
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_log = on_log

    client.username_pw_set(username, password)
    # blocking
    client.connect(MQTT_URL, MQTT_PORT, MQTT_KEEPALIVE)

    # loop in background thread to get subscribe
    client.loop_start()
    return client


def send_ailyun(client, params, rpc_id):
    js = {
        "id": rpc_id,
        "version": "1.0",
        "params": params,
        "method": "user.update"
    }
    payload = json.dumps(js, ensure_ascii=False, sort_keys=True, indent=2)
    logging.info("publish to aliyun, topic: %s payload: %s" % (TOPIC_UPSTREAM, payload))

    info = client.publish(TOPIC_UPSTREAM, payload)
    info.wait_for_publish()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.info("Usage: %s ${device_secret}" % sys.argv[0])
        exit(1)
    device_secret = sys.argv[1]

    logging.basicConfig(format='%(asctime)s %(process)d-%(thread)d [%(levelname)s] %(pathname)s:%(lineno)d %(message)s',
                        level=LOG_LEVEL)

    logging.info("iot hub daemon enter")

    username = "%s&%s" % (DEVICE_NAME, PRODUCT_KEY)
    sign_content = {"clientId": get_mac(),
                    "productKey": PRODUCT_KEY,
                    "deviceName": DEVICE_NAME,
                    "timestamp": int(time.time())}
    password = gen_sign_4aliyun(device_secret, sign_content)
    # securemode=3 meanings ws; 2 wss
    client_id = "%s|securemode=3,signmethod=hmacsha1,timestamp=%s|" % (
        sign_content["clientId"], sign_content["timestamp"])

    logging.info("device_secret: " + device_secret)
    logging.info("username: " + username)
    logging.info("password: " + password)
    logging.info("client_id: " + client_id)

    client = mqtt.Client(client_id, True, None, mqtt.MQTTv311, "websockets")
    connect_ailyun(client, username, password)

    bp = brickpi3.BrickPi3()
    rpc_id = 0
    try:
        while True:
            # read the current voltages
            params = {"voltage_battery": bp.get_voltage_battery(),
                      "voltage_9v": bp.get_voltage_9v(),
                      "voltage_5v": bp.get_voltage_5v(),
                      "voltage_3.3v": bp.get_voltage_3v3()}

            rpc_id += 1
            send_ailyun(client, params, rpc_id)

            time.sleep(60)
    finally:
        bp.reset_all()
        client.disconnect()
        logging.info("iot hub daemon exit")
