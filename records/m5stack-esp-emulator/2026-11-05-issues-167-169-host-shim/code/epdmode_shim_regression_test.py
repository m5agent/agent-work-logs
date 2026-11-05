#!/usr/bin/env python3
"""Reference host-shim unit test for issue #169 (M5.Display.EPDMode).

This exercises the drop-in ``EPDMode`` / ``Screen`` contract for the EXTERNAL
``aiflow_eval/sim_runtime.py`` host shim. It is a host-shim unit test only:
it is NOT guest/firmware evidence and grants no eval PASS.

Run: python3 epdmode_shim_regression_test.py
"""

# --------------------------------------------------------------------------
# Reference shim (drop into aiflow_eval/sim_runtime.py)
# --------------------------------------------------------------------------


class EPDMode:
    """M5GFX epd_mode_t namespace.

    Source of truth (official UIFlow2 2.5.3 tag 50e44078, M5GFX 9bcedf4e):
      m5stack/cmodules/m5unified/m5unified_gfx.c:313-335 (sha256 9e869e68...)
      m5stack/components/M5Unified/M5GFX/src/lgfx/v1/misc/enum.hpp:42-52
      (sha256 0e8aac59...)
    """

    EPD_QUALITY = 1
    EPD_TEXT = 2
    EPD_FAST = 3
    EPD_FASTEST = 4


# Start value for devices that are EPD after firmware init; coreink is the
# device from the reported failing case, paper* are this repo's EPD lanes.
EPD_DEVICE_IDS = frozenset(("coreink", "papercolor", "papermono"))


class Screen:
    # 1) Class attribute, not an instance/__getattr__ fallback: normal attribute
    #    lookup finds this before __getattr__ is consulted. This is the fix for
    #    "'function' object has no attribute 'EPD_QUALITY'".
    EPDMode = EPDMode

    def __init__(self, device="coreink", is_epd=None):
        if is_epd is None:
            is_epd = device in EPD_DEVICE_IDS
        self.device = device
        self._is_epd = bool(is_epd)
        # Panel.hpp:79 base default is 0 (non-EPD). EPD panel constructors set
        # epd_quality=1 (Panel_ED2208.cpp:242, Panel_SSD1677.cpp:188,
        # Panel_GDEW0154M09.cpp:39). Model the post-init state.
        self._epd_mode = EPDMode.EPD_QUALITY if self._is_epd else 0
        self.api_calls = []
        self.draw_calls = 0

    # Existing generic fallback: unknown attributes become recording callables.
    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)

        def _virtual(*args, **kwargs):
            self.api_calls.append(
                {"name": name, "args": list(args), "kwargs": dict(kwargs),
                 "result": None, "virtual": True}
            )
            return None

        return _virtual

    # ---- EPD API (define on the class so __getattr__ never sees them) ----

    def _record(self, name, args=(), kwargs=None, result=None):
        self.api_calls.append(
            {"name": name, "args": list(args), "kwargs": dict(kwargs or {}),
             "result": result, "virtual": False}
        )

    def isEPD(self):
        result = self._is_epd
        self._record("isEPD", result=result)
        return result

    def setEpdMode(self, epd_mode):
        # MicroPython gfx_setEpdMode: MP_ARG_INT | MP_ARG_REQUIRED -> one
        # int-convertible argument; bool converts (True=1, False=0); float,
        # str, None raise TypeError from mp_obj_get_int.
        if isinstance(epd_mode, bool):
            epd_mode = int(epd_mode)
        elif not isinstance(epd_mode, int):
            raise TypeError(
                "can't convert {} to int".format(type(epd_mode).__name__))
        # Panel.hpp:98: ignored when current or new mode is 0. Firmware does
        # not range-check 1..4; nonzero values are stored on EPD panels.
        if self._epd_mode and epd_mode:
            self._epd_mode = epd_mode
        self._record("setEpdMode", (epd_mode,), result=None)
        return None

    def getEpdMode(self):
        result = self._epd_mode
        self._record("getEpdMode", result=result)
        return result


class _M5:
    def __init__(self, display):
        self.Display = display
        self.Lcd = display  # same object on firmware (inventory: same member set)


# --------------------------------------------------------------------------
# Minimal test harness (stdlib only; intentionally no pytest dependency)
# --------------------------------------------------------------------------

_CHECKS = []


def check(name, condition, detail=""):
    _CHECKS.append((name, bool(condition), detail))


def expect_raises(name, exc_type, fn):
    try:
        fn()
    except exc_type as exc:
        check(name, True, "{}: {}".format(type(exc).__name__, exc))
    except Exception as exc:  # noqa: BLE001 - recorded as mismatch
        check(name, False, "unexpected {}: {}".format(type(exc).__name__, exc))
    else:
        check(name, False, "no exception raised")


def main():
    # 0. Reproduce the reported failure mode with a shim that lacks EPDMode.
    class BrokenScreen:
        def __getattr__(self, name):
            def _fn(*args, **kwargs):
                return None

            return _fn

    try:
        BrokenScreen().EPDMode.EPD_QUALITY
    except AttributeError as exc:
        check("root-cause-reproduced",
              "'function' object has no attribute 'EPD_QUALITY'" in str(exc),
              str(exc))
    else:
        check("root-cause-reproduced", False, "unexpectedly resolved")

    # 1. Namespace values are plain ints, exactly as the binding exposes them.
    for name, value in (("EPD_QUALITY", 1), ("EPD_TEXT", 2),
                        ("EPD_FAST", 3), ("EPD_FASTEST", 4)):
        check("EPDMode." + name, getattr(EPDMode, name) == value,
              repr(getattr(EPDMode, name)))

    # 2. EPD device: official forms from the issue and the upstream test.
    epd = Screen("coreink")
    m5 = _M5(epd)
    check("EPDMode-class-attribute",
          m5.Display.EPDMode is EPDMode
          and not callable(getattr(EPDMode, "EPD_QUALITY")),
          repr(m5.Display.EPDMode))
    m5.Display.setEpdMode(m5.Display.EPDMode.EPD_QUALITY)
    mode = m5.Display.getEpdMode()
    check("official-form-EPD_QUALITY-pass", mode == EPDMode.EPD_QUALITY, mode)
    m5.Display.setEpdMode(m5.Display.EPDMode.EPD_FASTEST)
    mode = m5.Display.getEpdMode()
    check("upstream-form-EPD_FASTEST-pass", mode == EPDMode.EPD_FASTEST, mode)
    check("isEPD-true-on-epd-device", m5.Display.isEPD() is True)
    check("epd-initial-mode-quality",
          Screen("coreink").getEpdMode() == EPDMode.EPD_QUALITY, "1")
    check("EPD-calls-recorded",
          [c["name"] for c in epd.api_calls] ==
          ["setEpdMode", "getEpdMode", "setEpdMode", "getEpdMode", "isEPD"],
          [c["name"] for c in epd.api_calls])
    check("draw_calls-unaffected", epd.draw_calls == 0)

    # 3. Keyword form is accepted by the firmware binding (MP_ARG_INT + kw).
    epd.setEpdMode(epd_mode=EPDMode.EPD_TEXT)
    check("keyword-arg-accepted",
          epd.getEpdMode() == EPDMode.EPD_TEXT, epd.getEpdMode())

    # 4. setEpdMode(0) is a silent no-op (Panel.hpp:98), not an exception.
    before = epd.getEpdMode()
    epd.setEpdMode(0)
    check("set-zero-ignored",
          epd.getEpdMode() == before and before == EPDMode.EPD_TEXT,
          epd.getEpdMode())

    # 5. Firmware does not range-check: nonzero undefined values are stored.
    epd.setEpdMode(5)
    check("out-of-range-nonzero-stored", epd.getEpdMode() == 5,
          epd.getEpdMode())
    epd.setEpdMode(EPDMode.EPD_QUALITY)  # restore

    # 6. Non-EPD device: getter 0, setter silently ignored but recorded.
    lcd = Screen("cores3")
    check("isEPD-false-on-lcd", lcd.isEPD() is False)
    check("lcd-initial-mode-zero", lcd.getEpdMode() == 0)
    lcd.setEpdMode(EPDMode.EPD_FAST)
    check("lcd-set-ignored", lcd.getEpdMode() == 0, lcd.getEpdMode())
    check("lcd-set-recorded",
          any(c["name"] == "setEpdMode" and not c["virtual"]
              for c in lcd.api_calls))
    check("bool-true-converts-to-1",
          Screen("cores3").setEpdMode(True) is None)

    # 7. Argument validation mirrors MP_ARG_INT | MP_ARG_REQUIRED.
    expect_raises("str-raises-TypeError", TypeError,
                  lambda: epd.setEpdMode("EPD_FAST"))
    expect_raises("float-raises-TypeError", TypeError,
                  lambda: epd.setEpdMode(3.0))
    expect_raises("none-raises-TypeError", TypeError,
                  lambda: epd.setEpdMode(None))
    expect_raises("missing-arg-TypeError", TypeError,
                  lambda: epd.setEpdMode())
    expect_raises("extra-arg-TypeError", TypeError,
                  lambda: epd.setEpdMode(1, 2))

    # 8. The pre-existing __getattr__ fallback still works for other APIs.
    check("fallback-preserved",
          lcd.someUnimplementedApi(7) is None
          and lcd.api_calls[-1]["virtual"] is True,
          lcd.api_calls[-1]["name"])

    failed = [name for name, ok, _ in _CHECKS if not ok]
    for name, ok, detail in _CHECKS:
        print("{} {}{}".format("PASS" if ok else "FAIL", name,
                               "" if not detail else "  [" + str(detail) + "]"))
    print("\n{}/{} checks passed".format(len(_CHECKS) - len(failed),
                                         len(_CHECKS)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
