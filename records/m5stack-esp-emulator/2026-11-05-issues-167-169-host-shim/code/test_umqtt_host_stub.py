"""Host-shim unit test for umqtt / umqtt.simple / umqtt.robust.

IMPORTANT: this is a HOST-SHIM unit test.  It proves the drop-in stub imports, dispatches
and records deterministically with no network; it is NOT guest/PASS evidence for the
firmware and it does not reproduce the failing eval run.

Copy together with `umqtt_host_stub.py` into the AIFlow eval repo, or adjust the import
line below to the module's installed path.  Runnable with pytest or `python3` directly.
"""

import importlib.util
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "umqtt_host_stub", HERE / "umqtt_host_stub.py"
)
stub = importlib.util.module_from_spec(_spec)
sys.modules["umqtt_host_stub"] = stub
_spec.loader.exec_module(stub)


def _fresh():
    """Reset shim state, drop previously installed umqtt modules, install fresh."""
    for name in [n for n in sys.modules if n == "umqtt" or n.startswith("umqtt.")]:
        del sys.modules[name]
    stub.reset()
    stub.set_recorder(None)
    stub.set_scheduler(None)
    return stub.install()


def _ops():
    return [event["op"] for event in stub.CALLS]


def test_import_surface():
    _fresh()
    from umqtt import MQTTClient

    from umqtt.simple import MQTTClient as SimpleClient
    from umqtt.simple import MQTTException
    from umqtt.robust import MQTTClient as RobustClient

    import umqtt
    import umqtt.robust
    import umqtt.simple

    assert "umqtt" in sys.modules
    assert "umqtt.simple" in sys.modules
    assert "umqtt.robust" in sys.modules
    assert umqtt.MQTTClient is MQTTClient
    assert umqtt.simple.MQTTClient is SimpleClient
    assert umqtt.robust.MQTTClient is RobustClient
    # official guest `dir(umqtt)` exports observed on real firmware
    for name in ("MQTTClient", "robust", "schedule", "simple"):
        assert hasattr(umqtt, name), name
    # official guest `dir(umqtt.simple)` re-exports
    for name in ("MQTTException", "MQTTClient", "hexlify", "socket", "struct"):
        assert hasattr(umqtt.simple, name), name
    # umqtt.MQTTClient is the M5 handler-subscribe wrapper (subclass of robust client)
    assert issubclass(MQTTClient, RobustClient)
    assert issubclass(RobustClient, SimpleClient)
    assert type(MQTTClient("cid", "broker")).__name__ == "MQTTClient"
    assert MQTTException is umqtt.simple.MQTTException


def test_constructor_defaults():
    _fresh()
    from umqtt import MQTTClient

    plain = MQTTClient("cid", "broker.example")
    assert plain.port == 1883  # port=0 and no ssl -> 1883
    assert plain.server == "broker.example"
    assert plain.client_id == "cid"
    assert plain.sock is None
    assert plain.pid == 0
    assert plain.user is None
    assert plain.pswd is None  # official state name for `password`
    assert plain.keepalive == 0
    assert plain.ssl is None
    assert plain.ssl_params == {}
    assert plain.lw_topic is None and plain.lw_retain is False
    assert callable(plain.cb)  # M5 wrapper installs _callback dispatch

    tls = MQTTClient("cid", "broker.example", port=0, ssl=True)
    assert tls.port == 8883  # port=0 and ssl -> 8883
    assert tls._topics == {}
    assert _ops() == ["init", "init"]


def test_m5_wrapper_lifecycle_recorded_sequence():
    _fresh()
    from umqtt import MQTTClient

    client = MQTTClient("cid-1", "broker.example", port=1883, keepalive=30)
    assert client.connect(clean_session=True) in (0, False)
    assert client.isconnected() is True
    client.publish("testtopic/test", "hello", qos=0)
    client.publish(b"testtopic/test", b"qos-one", qos=1)
    assert client.pid == 1  # only qos>0 publication allocates a packet id

    handled = []
    client.subscribe("testtopic/test", lambda data: handled.append(data), qos=0)
    assert "testtopic/test" in client._topics
    client._callback(b"testtopic/test", b"payload")
    assert handled == [(b"testtopic/test", b"payload")]  # single (topic, msg) arg
    client.unsubscribe("testtopic/test")
    assert client._topics == {}

    client.check_msg()
    client.wait_msg()
    client.set_last_will("will/topic", b"gone", retain=True, qos=1)
    client.ping()
    client.disconnect()
    assert client.isconnected() is False
    assert client.reconnect() in (0, False)
    assert client.isconnected() is True

    assert _ops() == [
        "init", "connect", "isconnected", "publish", "publish", "subscribe",
        "dispatch", "unsubscribe", "check_msg", "wait_msg", "set_last_will",
        "ping", "disconnect", "isconnected", "reconnect", "isconnected",
    ]
    publish_events = [e for e in stub.CALLS if e["op"] == "publish"]
    assert publish_events[1]["args"]["qos"] == 1
    assert publish_events[1]["args"]["topic"] == b"testtopic/test"
    assert publish_events[0]["args"]["retain"] is False
    dispatch = [e for e in stub.CALLS if e["op"] == "dispatch"][0]
    assert dispatch["module"] == "umqtt"
    assert dispatch["args"]["scheduled"] is True
    will = [e for e in stub.CALLS if e["op"] == "set_last_will"][0]
    assert will["args"] == {"topic": "will/topic", "msg": b"gone", "retain": True, "qos": 1}


def test_m5_wrapper_handler_dispatch_variants():
    _fresh()
    from umqtt import MQTTClient

    client = MQTTClient("cid", "broker")
    client.connect()
    seen = []
    client.subscribe(b"bytes/topic", lambda data: seen.append(("bytes", data)))
    client.subscribe("str/topic", lambda data: seen.append(("str", data)))
    client._callback(b"bytes/topic", b"m1")
    client._callback("str/topic", b"m2")
    client._callback("unknown/topic", b"m3")  # no handler: recorded, no exception
    assert seen == [
        ("bytes", (b"bytes/topic", b"m1")),
        ("str", ("str/topic", b"m2")),
    ]
    dispatches = [e for e in stub.CALLS if e["op"] == "dispatch"]
    assert [e["args"]["scheduled"] for e in dispatches] == [True, True, False]
    assert len(seen) == 2  # unknown topic neither dispatched nor raised

    # Scheduler hook: the eval shim can defer/queue dispatch instead of direct call.
    queued = []
    stub.set_scheduler(lambda function, argument: queued.append((function, argument)))
    client._callback(b"bytes/topic", b"deferred")
    assert len(seen) == 2  # not yet called: dispatch is queued in the host scheduler
    function, argument = queued.pop()
    function(argument)
    assert seen[-1] == ("bytes", (b"bytes/topic", b"deferred"))


def test_simple_client_surface():
    _fresh()
    from umqtt.simple import MQTTClient, MQTTException

    assert str(MQTTException(5).args[0]) == "5"
    try:
        raise MQTTException(5)
    except MQTTException as error:  # public exception keeps the protocol error code
        assert error.args[0] == 5

    client = MQTTClient("sid", "broker", port=1883, keepalive=30)
    try:
        client.subscribe("t", qos=0)
        raise AssertionError("subscribe without callback must assert")
    except AssertionError:
        pass
    for bad in (3, -1):
        try:
            client.set_last_will("will", b"m", qos=bad)
            raise AssertionError("set_last_will qos=%d must assert" % bad)
        except AssertionError:
            pass
    try:
        client.set_last_will("", b"m")
        raise AssertionError("empty will topic must assert")
    except AssertionError:
        pass

    received = []
    client.set_callback(lambda topic, msg: received.append((topic, msg)))
    assert client.connect(timeout=5) in (0, False)
    assert client.isconnected() is True
    client.set_last_will("will/topic", b"offline", retain=True, qos=1)
    client.subscribe("topic", qos=0)
    client.publish("topic", b"qos-zero", qos=0)
    client.publish("topic", b"qos-one", qos=1)
    assert client.pid == 2  # subscribe + qos1 publish
    client.wait_msg()
    client.check_msg()
    client.unsubscribe("topic")
    client.disconnect()
    assert client.isconnected() is False
    assert received == []  # host shim has no inbound broker traffic

    assert _ops() == [
        "init", "set_callback", "connect", "isconnected", "set_last_will",
        "subscribe", "publish", "publish", "wait_msg", "check_msg",
        "unsubscribe", "disconnect", "isconnected",
    ]


def test_robust_client_surface():
    _fresh()
    from umqtt.robust import MQTTClient

    client = MQTTClient("rid", "broker", port=1883)
    assert client.DELAY == 2
    assert client.DEBUG is False
    assert client.connect(clean_session=False) in (0, False)
    client.publish("t", b"m", qos=0)
    client.publish("t", b"m1", qos=1)
    client.set_last_will("will", b"m")
    client.set_callback(lambda topic, msg: None)
    client.subscribe("t", qos=0)
    client.wait_msg()
    client.check_msg(attempts=2)
    assert client.delay(1) is None  # records; never sleeps 2s
    assert client.log(False, RuntimeError("fixture")) is None
    assert client.reconnect() in (0, False)
    client.unsubscribe("t")
    client.disconnect()

    assert _ops() == [
        "init", "connect", "publish", "publish", "set_last_will", "set_callback",
        "subscribe", "wait_msg", "check_msg", "delay", "log", "reconnect",
        "unsubscribe", "disconnect",
    ]
    delay = [e for e in stub.CALLS if e["op"] == "delay"][0]
    assert delay["module"] == "umqtt.robust"
    assert delay["args"] == {"attempt": 1, "seconds": 2}
    check = [e for e in stub.CALLS if e["op"] == "check_msg"][0]
    assert check["args"] == {"attempts": 2}
    log = [e for e in stub.CALLS if e["op"] == "log"][0]
    assert log["args"]["in_reconnect"] is False
    assert "fixture" in log["args"]["error"]


def test_no_network_guard():
    _fresh()
    import umqtt.simple
    from umqtt import MQTTClient

    # umqtt.simple.socket matches the guest reflection surface but cannot network.
    for name in ("socket", "getaddrinfo", "create_connection"):
        try:
            getattr(umqtt.simple.socket, name)()
            raise AssertionError("socket.%s must be blocked in the host shim" % name)
        except RuntimeError:
            pass
    # The stub module itself never imports Python's socket module.
    source = (HERE / "umqtt_host_stub.py").read_text(encoding="utf-8")
    assert re.search(r"^(?:import socket|from socket)", source, re.MULTILINE) is None
    client = MQTTClient("cid", "broker")
    client.connect()
    client.disconnect()
    try:
        client.sock.send(b"x")
        raise AssertionError("closed host-shim socket must reject further writes")
    except OSError:
        pass


def test_recorder_hook_and_module_table():
    _fresh()
    events = []
    table = {}
    stub.set_recorder(events.append)
    stub.install(module_table=table)  # idempotent re-install with explicit registry
    assert set(table) == {"umqtt", "umqtt.simple", "umqtt.robust"}
    assert table["umqtt"] is sys.modules["umqtt"]
    from umqtt import MQTTClient

    client = MQTTClient("cid", "broker")
    client.connect()
    client.publish("t", b"m")
    assert [event["op"] for event in events] == ["init", "connect", "publish"]
    assert all(event["engine"] == stub.ENGINE for event in events)
    assert events[2]["module"] == "umqtt"
    assert events[2]["client_id"] == "cid"
    assert events[2]["args"]["topic"] == "t"
    assert stub.CALLS == events  # CALLS keeps the same order


def test_uiflow2_program_start_pattern():
    """A generated-UIFlow2-shaped MQTT program must import and start under the stub."""
    _fresh()
    program = """
from umqtt import MQTTClient
from umqtt.simple import MQTTException

mqtt_client = None
messages = []


def on_message(data):
    messages.append(data)


def setup():
    global mqtt_client
    mqtt_client = MQTTClient(
        "uiflow", "broker.emqx.io", port=1883, user="test", password="test", keepalive=0
    )
    mqtt_client.connect(clean_session=True)
    mqtt_client.subscribe("testtopic/test", on_message, qos=0)


def loop():
    mqtt_client.check_msg()


setup()
for _ in range(3):
    loop()
mqtt_client._callback("testtopic/test", "hello")
mqtt_client.publish("testtopic/test", "from-button", qos=0)
mqtt_client.disconnect()
assert messages == [("testtopic/test", "hello")], messages
"""
    exec(compile(program, "generated_main.py", "exec"), {})
    assert "init" in _ops() and "connect" in _ops()
    assert _ops().count("check_msg") == 3  # program loop executed
    assert "disconnect" in _ops()

TESTS = [value for name, value in sorted(globals().items()) if name.startswith("test_")]


if __name__ == "__main__":
    for test in TESTS:
        _fresh()
        test()
        print("PASS", test.__name__)
    print("UMQTT_HOST_STUB_TESTS_DONE", len(TESTS))
