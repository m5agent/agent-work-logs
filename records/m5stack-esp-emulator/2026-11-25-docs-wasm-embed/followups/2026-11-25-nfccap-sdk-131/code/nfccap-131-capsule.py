from cap.cc1101 import M5, ST25R3916, _port_table, machine

def __init__(self):
    self._port = _port_table.get(M5.getBoard())
    if self._port is None:
        raise NotImplementedError("NFC CAP is not supported on this board")

    self._power_en = machine.Pin(self._port.power_en, machine.Pin.OUT, value=1)
    self._cc1101_cs = machine.Pin(self._port.spi_cs, machine.Pin.OUT, value=1)
    self._nfc_cs = machine.Pin(self._port.nfc_cs, machine.Pin.OUT, value=1)
    self._spi = machine.SPI(
        1,
        baudrate=2000000,
        polarity=0,
        phase=1,
        sck=machine.Pin(self._port.spi_sck),
        mosi=machine.Pin(self._port.spi_mosi),
        miso=machine.Pin(self._port.spi_miso),
    )
    self._chip = ST25R3916(
        spi=self._spi,
        cs=self._nfc_cs,
        irq=self._port.nfc_irq,
    )
    self.chip = self._chip
    if not self.chip.begin():
        raise RuntimeError("ST25R3916 initialization failed")
