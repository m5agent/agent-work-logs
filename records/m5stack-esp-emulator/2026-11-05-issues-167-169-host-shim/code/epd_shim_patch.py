"""Reference host-shim patch for UIFlow2 ``M5.Display.EPDMode`` (external AIFlow eval).

The failing external component (``aiflow_eval/sim_runtime.py``) is not in this
workspace. This file is therefore a drop-in reference patch for its ``Screen``
class. It is derived from the pinned official UIFlow2 source:

* ``m5stack/cmodules/m5unified/m5unified_gfx.c`` (sha256
  9e869e68eb99706e46855858e72a213db66e65e0e83a56ad155ab5238bac9a4e, candidate commit
  3a86d8f611b3639cca755a933e01a5a829771ef1), lines 313-318:
  EPD_QUALITY=1, EPD_TEXT=2, EPD_FAST=3, EPD_FASTEST=4.
* ``m5stack/components/M5Unified/mpy_m5gfx.cpp``: ``gfx_setEpdMode`` takes one
  required int argument (MP_ARG_INT), ``gfx_getEpdMode`` returns the current
  int, ``gfx_isEPD`` returns ``bool(gfx->isEPD())``.
* ``m5stack/components/M5Unified/M5GFX/src/lgfx/v1/Panel.hpp``: ``_epd_mode``
  starts at 0 (non-EPD), ``setEpdMode`` only updates when the panel is EPD and
  the argument is non-zero, ``getEpdMode`` returns the stored value.
* ``.../LGFXBase.hpp``: ``isEPD()`` delegates to the panel.

Integration: paste the two marked blocks into the external shim, REPLACING the
``# ADAPT`` call-recorder line with the shim's existing api/draw recorder. The
rest of this file is a self-contained regression that also proves the original
``AttributeError`` mode is fixed; it is a host-shim unit test, not guest
firmware evidence.
"""


# --- BLOCK 1: add beside the other UIFlow2 enums in the external shim ---------
class EPDMode:
    EPD_QUALITY = 1
    EPD_TEXT = 2
    EPD_FAST = 3
    EPD_FASTEST = 4


# --- BLOCK 2: add to the external shim's Screen class ------------------------
# class Screen:
#     EPDMode = EPDMode      # class attribute wins normal lookup -> __getattr__
#                            # is never consulted for M5.Display.EPDMode
#     _is_epd = False        # True only for EPD boards (PaperColor/PaperMono)
#     _epd_mode = 0          # same initial value as the official Panel
#
#     def isEPD(self):
#         self._record_api("Display.isEPD")          # ADAPT: existing recorder
#         return self._is_epd
#
#     def setEpdMode(self, epd_mode):
#         if not isinstance(epd_mode, int) or isinstance(epd_mode, bool):
#             # MP_ARG_INT rejection in the official binding
#             raise TypeError("setEpdMode() argument 'epd_mode' must be int")
#         self._record_api("Display.setEpdMode", epd_mode)  # ADAPT
#         if self._is_epd and epd_mode:
#             self._epd_mode = epd_mode               # official Panel semantics
#         return None
#
#     def getEpdMode(self):
#         self._record_api("Display.getEpdMode")     # ADAPT
#         return self._epd_mode
# ---------------------------------------------------------------------------

import builtins


class DemoShimScreen:
    """Minimal stand-in for the external ``Screen`` to prove the patch."""

    EPDMode = EPDMode
    _is_epd = False
    _epd_mode = 0

    def __init__(self, epd=False):
        self._is_epd = bool(epd)
        self._epd_mode = 0
        self.calls = []

    # The external shim's documented failure mode: unknown attributes return a
    # callable stub, so ``M5.Display.EPDMode`` used to be a function.
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return lambda *args, **kwargs: self._record_api(f"draw.{name}", *args)

    def _record_api(self, name, *args):
        self.calls.append((name, args))
        return None

    def isEPD(self):
        self._record_api("Display.isEPD")
        return self._is_epd

    def setEpdMode(self, epd_mode):
        if not isinstance(epd_mode, int) or isinstance(epd_mode, bool):
            raise TypeError("setEpdMode() argument 'epd_mode' must be int")
        self._record_api("Display.setEpdMode", epd_mode)
        if self._is_epd and epd_mode:
            self._epd_mode = epd_mode
        return None

    def getEpdMode(self):
        self._record_api("Display.getEpdMode")
        return self._epd_mode


def main():
    # Enum identity: official numeric values (1..4), not the stale 0..3 docs.
    assert (EPDMode.EPD_QUALITY, EPDMode.EPD_TEXT, EPDMode.EPD_FAST, EPDMode.EPD_FASTEST) == (1, 2, 3, 4)
    assert DemoShimScreen.EPDMode is EPDMode

    # Reported failure: named constants on the display object are attributes,
    # not the dynamic callable fallback.
    epd = DemoShimScreen(epd=True)
    assert epd.EPDMode.EPD_QUALITY == 1
    assert callable(epd.EPDMode.EPD_QUALITY) is False

    # Official forms from the issue / upstream test.
    assert epd.isEPD() is True
    assert epd.getEpdMode() == 0
    epd.setEpdMode(epd.EPDMode.EPD_QUALITY)
    assert epd.getEpdMode() == 1
    epd.setEpdMode(epd.EPDMode.EPD_FASTEST)
    assert epd.getEpdMode() == 4
    epd.setEpdMode(2)  # plain documented int form
    assert epd.getEpdMode() == 2
    epd.setEpdMode(0)  # official Panel ignores zero
    assert epd.getEpdMode() == 2
    try:
        epd.setEpdMode("EPD_FAST")
    except TypeError as error:
        assert "epd_mode" in str(error)
    else:
        raise AssertionError("non-int EPD mode must be rejected like MP_ARG_INT")
    assert ("Display.setEpdMode", (1,)) in epd.calls
    assert ("Display.isEPD", ()) in epd.calls

    # Non-EPD boards: API exists, isEPD() False, getEpdMode() 0, calls recorded
    # but state ignored (official Panel semantics).
    lcd = DemoShimScreen(epd=False)
    assert lcd.isEPD() is False
    lcd.setEpdMode(lcd.EPDMode.EPD_FAST)
    assert lcd.getEpdMode() == 0
    assert ("Display.setEpdMode", (3,)) in lcd.calls

    # The eval shim must mark PaperColor/PaperMono as EPD in its device table;
    # for every other board isEPD() stays False.
    print("EPD_HOST_SHIM_PATCH_PASS", len(epd.calls), len(lcd.calls))


if __name__ == "__main__":
    main()
