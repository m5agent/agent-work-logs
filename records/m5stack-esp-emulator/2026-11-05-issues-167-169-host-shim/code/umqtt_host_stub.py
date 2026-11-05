"""Host-side umqtt / umqtt.simple / umqtt.robust stub for the EXTERNAL AIFlow eval simulator.

Drop this file into the AIFlow eval repo (e.g. `aiflow_eval/host_shims/umqtt_host_stub.py`)
and call ``install()`` from its host module table before the generated UIFlow2 program is
executed.  It is NOT part of m5stack-esp-emulator: this repository executes UIFlow2 programs
inside the QEMU/WASM MicroPython guest and does not provide a host Python executor.

Contract source of truth (official UIFlow2 `m5stack/libs/umqtt/`, see patch.md for hashes):

  * `umqtt/simple.py`:   MQTTException, MQTTClient(client_id, server, port=0, user=None,
                         password=None, keepalive=0, ssl=None, ssl_params={}),
                         set_callback, set_last_will, connect(clean_session=True, timeout=None),
                         disconnect, ping, isconnected, publish, subscribe, unsubscribe,
                         wait_msg, check_msg.
  * `umqtt/robust.py`:   MQTTClient(simple.MQTTClient) with DELAY=2, DEBUG=False,
                         delay, log, reconnect, publish, wait_msg, check_msg(attempts=2).
  * `umqtt/__init__.py`: MQTTClient(robust.MQTTClient) with subscribe(topic, handler, qos=0)
                         handler dispatch through `_topics` + `micropython.schedule`, and
                         unsubscribe cleanup.  `from umqtt import MQTTClient` is the official
                         UIFlow2 import form.

Host-stub rules implemented here:

  * NO sockets, no DNS, no TLS, no broker contact; every network operation is a recorded
    no-op with deterministic return values.
  * Every public call is appended to ``CALLS`` (JSON-adaptable dict) and, if a recorder hook
    was installed with ``set_recorder()``, passed to it as one dict argument.
  * The recorder event shape is::

        {"engine": "aiflow-eval-host-shim",
         "module": "umqtt" | "umqtt.simple" | "umqtt.robust",
         "op": "<public method name>",
         "client_id": <client_id>,
         "args": {...method-specific fields...}}

    Adapt it to the eval shim's existing schema, e.g.::

        umqtt_host_stub.set_recorder(
            lambda e: sim_runtime.record(e["module"], e["op"], e["client_id"], e["args"])
        )

Deterministic deviations from the frozen guest implementation (documented, intentional):

  * `connect()` returns `False` (session-present flag 0) and records the CONNECT.
  * `isconnected()` returns the recorded connection flag instead of writing a PINGREQ.
  * `disconnect()` is idempotent (official raises AttributeError when `sock` is None).
  * robust `delay()`/`log()` never sleep/print unless `DEBUG`; they only record.
  * no inbound broker traffic exists, so `wait_msg()`/`check_msg()` are no-ops returning None;
    the M5 wrapper's `_callback(topic, msg)` can be invoked directly by the eval to rehearse
    subscription dispatch.
"""

import binascii
import struct
import sys
import time
import types

ENGINE = "aiflow-eval-host-shim"

#: Recorded public calls, in order.  Reset with reset().
CALLS = []

_recorder = None
_scheduler = None


def set_recorder(recorder):
    """Install a callable receiving one event dict per recorded call (None detaches)."""
    global _recorder
    _recorder = recorder


def set_scheduler(scheduler):
    """Install a callable `scheduler(function, argument)` used for handler dispatch.

    Defaults to a direct call.  Use this if the eval shim already models
    `micropython.schedule` queueing; the official wrapper passes the handler a single
    `(topic, msg)` tuple argument.
    """
    global _scheduler
    _scheduler = scheduler


def reset():
    """Clear recorded calls (test helper); keeps hooks untouched."""
    del CALLS[:]


def _record(module, op, client, **args):
    event = {
        "engine": ENGINE,
        "module": module,
        "op": op,
        "client_id": getattr(client, "client_id", None),
        "args": args,
    }
    CALLS.append(event)
    if _recorder is not None:
        _recorder(event)
    return event


def _record_self(client, op, **args):
    return _record(getattr(client, "_shim_module", "umqtt.simple"), op, client, **args)


class _NoNetworkSocketModule:
    """Placeholder for the module attribute `socket` in umqtt.simple.

    The guest module does `import socket`; the host stub never creates a socket.  Any
    accidental network use fails loudly instead of touching the machine network.
    """

    SOCK_STREAM = 1
    SOCK_DGRAM = 2
    AF_INET = 2

    def __getattr__(self, name):
        def _blocked(*args, **kwargs):
            raise RuntimeError(
                "umqtt host shim: network access is disabled (attribute %r)" % (name,)
            )

        return _blocked


_NO_NETWORK = _NoNetworkSocketModule()


class _HostSocket:
    """Stand-in for `simple.MQTTClient.sock`; records writes, never networks.

    After `disconnect()` the placeholder is marked closed, so `sock.send()` raises
    OSError exactly like the frozen guest client after its socket is closed.
    """

    def __init__(self, client):
        self._client = client
        self.closed = False

    def settimeout(self, value):
        _record_self(self._client, "sock.settimeout", value=value)

    def setblocking(self, flag):
        _record_self(self._client, "sock.setblocking", flag=bool(flag))

    def write(self, data):
        if self.closed:
            raise OSError("host shim socket is closed")
        _record_self(self._client, "sock.write", bytes=len(data))
        return len(data) if hasattr(data, "__len__") else 2

    def read(self, size=-1):
        if self.closed:
            raise OSError("host shim socket is closed")
        return b""

    def send(self, data):
        if self.closed:
            raise OSError("host shim socket is closed")
        _record_self(self._client, "sock.send", bytes=len(data))
        return len(data) if hasattr(data, "__len__") else 0

    def close(self):
        _record_self(self._client, "sock.close")
        self.closed = True


class MQTTException(Exception):
    """Public exception from umqtt.simple; protocol error code is preserved in args."""


class _SimpleMQTTClient:
    #: Recorded as the event's "module"; overridden by the robust and M5 wrapper classes.
    _shim_module = "umqtt.simple"

    def __init__(
        self,
        client_id,
        server,
        port=0,
        user=None,
        password=None,
        keepalive=0,
        ssl=None,
        ssl_params={},
    ):
        # Literal official default: port 0 resolves to 8883 with ssl, else 1883.
        if port == 0:
            port = 8883 if ssl else 1883
        self.client_id = client_id
        self.sock = None
        self.server = server
        self.port = port
        self.ssl = ssl
        self.ssl_params = ssl_params
        self.pid = 0
        self.cb = None
        self.user = user
        self.pswd = password
        self.keepalive = keepalive
        self.lw_topic = None
        self.lw_msg = None
        self.lw_qos = 0
        self.lw_retain = False
        self._connected = False
        _record_self(
            self,
            "init",
            server=server,
            port=port,
            user=user,
            keepalive=keepalive,
            ssl=bool(ssl),
        )

    def set_callback(self, f):
        self.cb = f
        _record_self(self, "set_callback", callback=_callable_name(f))
        return None

    def set_last_will(self, topic, msg, retain=False, qos=0):
        assert 0 <= qos <= 2
        assert topic
        self.lw_topic = topic
        self.lw_msg = msg
        self.lw_qos = qos
        self.lw_retain = retain
        _record_self(
            self,
            "set_last_will",
            topic=topic,
            msg=msg,
            retain=bool(retain),
            qos=qos,
        )
        return None

    def connect(self, clean_session=True, timeout=None):
        self.sock = _HostSocket(self)
        self._connected = True
        _record_self(
            self,
            "connect",
            clean_session=bool(clean_session),
            timeout=timeout,
            server=self.server,
            port=self.port,
        )
        # Session-present flag of a clean CONNACK is 0, matching the frozen client's
        # `return resp[2] & 1` against a broker without a stored session.
        return False

    def disconnect(self):
        if self.sock is not None:
            # Close quietly; only the public disconnect() is a recorded user call.
            self.sock.closed = True
        self._connected = False
        _record_self(self, "disconnect")
        return None

    def ping(self):
        _record_self(self, "ping")
        return None

    def isconnected(self):
        result = bool(self._connected)
        _record_self(self, "isconnected", result=result)
        return result

    def publish(self, topic, msg, retain=False, qos=0):
        self._publish(topic, msg, retain, qos)
        _record_self(
            self, "publish", topic=topic, msg=msg, retain=bool(retain), qos=qos
        )
        return None

    def subscribe(self, topic, qos=0):
        assert self.cb is not None, "Subscribe callback is not set"
        self._subscribe(topic, qos)
        _record_self(self, "subscribe", topic=topic, qos=qos)
        return None

    def unsubscribe(self, topic):
        self._unsubscribe(topic)
        _record_self(self, "unsubscribe", topic=topic)
        return None

    def wait_msg(self):
        _record_self(self, "wait_msg")
        return None

    def check_msg(self):
        _record_self(self, "check_msg")
        return None

    # --- internals (single recorded event per public call) -------------------------

    def _publish(self, topic, msg, retain, qos):
        if qos > 0:
            self.pid += 1
        return None

    def _subscribe(self, topic, qos):
        self.pid += 1

    def _unsubscribe(self, topic):
        self.pid += 1

    def _connect_impl(self, clean_session):
        self.sock = _HostSocket(self)
        self._connected = True
        return False

    def _wait_msg_impl(self):
        return None


class _RobustMQTTClient(_SimpleMQTTClient):
    _shim_module = "umqtt.robust"

    DELAY = 2
    DEBUG = False

    def delay(self, i):
        # Official sleeps time.sleep(self.DELAY); the host shim must stay deterministic.
        _record_self(self, "delay", attempt=i, seconds=self.DELAY)
        return None

    def log(self, in_reconnect, e):
        if self.DEBUG:
            if in_reconnect:
                print("mqtt reconnect: %r" % e)
            else:
                print("mqtt: %r" % e)
        _record_self(self, "log", in_reconnect=bool(in_reconnect), error=repr(e))
        return None

    def reconnect(self):
        connected = self._connect_impl(False)
        _record_self(self, "reconnect", server=self.server, port=self.port)
        return connected

    def publish(self, topic, msg, retain=False, qos=0):
        self._publish(topic, msg, retain, qos)
        _record_self(
            self, "publish", topic=topic, msg=msg, retain=bool(retain), qos=qos
        )
        return None

    def wait_msg(self):
        _record_self(self, "wait_msg")
        return self._wait_msg_impl()

    def check_msg(self, attempts=2):
        _record_self(self, "check_msg", attempts=attempts)
        remaining = attempts
        while remaining:
            remaining -= 1
            return self._wait_msg_impl()
        return None


def _callable_name(f):
    return getattr(f, "__name__", repr(f))


def _schedule(function, argument):
    """`micropython.schedule` equivalent used by the M5 wrapper dispatch."""
    if _scheduler is not None:
        return _scheduler(function, argument)
    return function(argument)


class _M5MQTTClient(_RobustMQTTClient):
    _shim_module = "umqtt"

    def __init__(
        self,
        client_id,
        server,
        port=0,
        user=None,
        password=None,
        keepalive=0,
        ssl=None,
        ssl_params={},
    ):
        super().__init__(
            client_id, server, port, user, password, keepalive, ssl, ssl_params
        )
        # Official __init__ calls self.set_callback(self._callback); assign directly so
        # the recorder sees only user-issued set_callback calls.
        self.cb = self._callback
        self._topics = {}

    def _callback(self, topic, msg):
        handler = None
        if isinstance(topic, bytes):
            handler = self._topics.get(topic.decode())
            if handler is None:
                handler = self._topics.get(topic)
        elif isinstance(topic, str):
            handler = self._topics.get(topic)
            if handler is None:
                handler = self._topics.get(topic.encode())
        _record_self(
            self,
            "dispatch",
            topic=topic,
            msg=msg,
            handler=_callable_name(handler) if handler is not None else None,
            scheduled=handler is not None,
        )
        if handler is not None:
            return _schedule(handler, (topic, msg))
        return None

    def subscribe(self, topic, handler, qos=0):
        self._topics[topic] = handler
        self._subscribe(topic, qos)
        _record_self(
            self,
            "subscribe",
            topic=topic,
            qos=qos,
            handler=_callable_name(handler),
        )
        return None

    def unsubscribe(self, topic):
        if topic in self._topics:
            del self._topics[topic]
        self._unsubscribe(topic)
        _record_self(self, "unsubscribe", topic=topic)
        return None


# Class names must match the guest module surface (`type(x).__name__ == "MQTTClient"`).
_SimpleMQTTClient.__name__ = "MQTTClient"
_SimpleMQTTClient.__qualname__ = "MQTTClient"
_RobustMQTTClient.__name__ = "MQTTClient"
_RobustMQTTClient.__qualname__ = "MQTTClient"
_M5MQTTClient.__name__ = "MQTTClient"
_M5MQTTClient.__qualname__ = "MQTTClient"

# ---------------------------------------------------------------------------
# Module objects mirroring the frozen guest layout.
# ---------------------------------------------------------------------------

simple = types.ModuleType("umqtt.simple")
simple.__doc__ = "Host-shim equivalent of UIFlow2 m5stack/libs/umqtt/simple.py"
simple.MQTTException = MQTTException
simple.MQTTClient = _SimpleMQTTClient
# Guest module attributes observed by `dir(umqtt.simple)` on real firmware:
simple.hexlify = binascii.hexlify
simple.struct = struct
simple.socket = _NO_NETWORK

robust = types.ModuleType("umqtt.robust")
robust.__doc__ = "Host-shim equivalent of UIFlow2 m5stack/libs/umqtt/robust.py"
robust.MQTTClient = _RobustMQTTClient
robust.simple = simple
robust.time = time

package = types.ModuleType("umqtt")
package.__doc__ = (
    "Host-shim equivalent of UIFlow2 m5stack/libs/umqtt/__init__.py "
    "(M5 handler-subscribe wrapper)"
)
package.MQTTClient = _M5MQTTClient
package.robust = robust
package.simple = simple
package.schedule = _schedule
package.__path__ = []  # package-like so `import umqtt.simple` resolution is deterministic

#: name -> module mapping for eval shims that keep an explicit module table.
MODULES = {
    "umqtt": package,
    "umqtt.simple": simple,
    "umqtt.robust": robust,
}


def install(module_table=None, sys_modules=None):
    """Register the stub modules so generated UIFlow2 code imports them.

    Call once from the eval host-shim bootstrap, BEFORE executing the generated
    program, and keep the shim's own recorder wiring:

        import umqtt_host_stub
        umqtt_host_stub.set_recorder(sim_runtime.record)
        umqtt_host_stub.install(SHIM_MODULE_TABLE)

    * `sys_modules` defaults to the real `sys.modules` (pass a dict in unit tests).
    * `module_table` is any dict-like registry (`update()` support): it receives the same
      three entries.  If the eval shim consults only `sys.modules`, omit it.
    * Idempotent: re-calling re-registers the same module objects and keeps recorded state.

    Returns the registered `umqtt` package module.
    """
    if sys_modules is None:
        sys_modules = sys.modules
    if module_table is not None:
        module_table.update(MODULES)
    for name in ("umqtt.simple", "umqtt.robust", "umqtt"):
        sys_modules[name] = MODULES[name]
    return package
