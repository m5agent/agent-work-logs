import umqtt
import umqtt.simple
import umqtt.robust
from umqtt import MQTTClient
from umqtt.simple import MQTTException

print("ISSUE167_MODULES", type(umqtt).__name__, type(umqtt.simple).__name__,
      type(umqtt.robust).__name__)
client = MQTTClient("issue167-probe", "broker.invalid", port=1883)
print("ISSUE167_CLIENT", type(client).__name__, isinstance(client, umqtt.robust.MQTTClient))
surface = [name for name in ("connect", "publish", "subscribe", "unsubscribe",
                             "check_msg", "wait_msg", "disconnect", "ping",
                             "isconnected", "reconnect", "delay", "log",
                             "set_callback", "set_last_will")
           if callable(getattr(client, name, None))]
print("ISSUE167_SURFACE", ",".join(surface))
client.set_callback(lambda topic, msg: None)
client.set_last_will("m5/issue167", "offline", retain=False, qos=1)
try:
    raise MQTTException(5)
except MQTTException as error:
    print("ISSUE167_EXCEPTION_ARGS", error.args[0])
print("ISSUE167_MQTT_DONE")
