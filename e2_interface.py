# -*- coding: utf-8 -*-
"""
Implementation of E2 interface via bitbanging GPIO.

Copyright 2021 E+E Elektronik Ges.m.b.H.

Disclaimer:
This application example is non-binding and does not claim to be complete with regard
to configuration and equipment as well as all eventualities. The application example
is intended to provide assistance with the EE894 sensor module design-in and is provided "as is".
You yourself are responsible for the proper operation of the products described.
This application example does not release you from the obligation to handle the product safely
during application, installation, operation and maintenance. By using this application example,
you acknowledge that we cannot be held liable for any damage beyond the liability regulations
described.

We reserve the right to make changes to this application example at any time without notice.
In case of discrepancies between the suggestions in this application example and other E+E
publications, such as catalogues, the content of the other documentation takes precedence.
We assume no liability for the information contained in this document.
"""

import time
from enum import Enum

# pylint: disable=E0401
import RPi.GPIO as GPIO
# pylint: enable=E0401


ACK = 1
NAK = 0


class E2StatusCode(Enum):
    """E2 status codes."""

    E2_OK = 0
    E2_ERR_NAK = 1
    E2_ERR_CKSUM = 2
    E2_ERR_MEAS = 3


def get_status_string(status_code):
    """Return string from status_code."""
    status_string = {
        E2StatusCode.E2_OK: "Success",
        E2StatusCode.E2_ERR_NAK: "Not acknowledge error",
        E2StatusCode.E2_ERR_CKSUM: "Checksum error",
        E2StatusCode.E2_ERR_MEAS: "Measurement error",
    }

    if isinstance(status_code, E2StatusCode) and status_code.value < len(status_string):
        return status_string[status_code]

    return "Unknown error"


class E2Device():
    """Class for interfacing with an E2 device."""

    def __init__(self, e2_scl_gpio, e2_sda_gpio, e2_dev_addr):

        self.scl = e2_scl_gpio
        self.sda = e2_sda_gpio

        self.dev_addr = e2_dev_addr

        # init GPIOs
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.sda, GPIO.IN)
        GPIO.setup(self.scl, GPIO.IN)

    def read_word_from_slave(self, control_bytes):
        """Read word from slave."""
        result = 0
        low_byte, status = self.read_byte_from_slave(control_bytes[0])

        if status == E2StatusCode.E2_OK:
            high_byte, status = self.read_byte_from_slave(control_bytes[1])

        if status == E2StatusCode.E2_OK:
            result = low_byte + high_byte * 256

        return result, status  # return tuple with data_byte and status

    def read_byte_from_slave(self, control_byte):
        """Read byte from slave."""
        data_byte = 0x00
        status = E2StatusCode.E2_OK
        ctrl_byte_addr = control_byte | (self.dev_addr << 1)

        self.start()
        self.send_byte(ctrl_byte_addr)
        if self.check_ack() == ACK:
            data_byte = self.read_byte()
            self.send_ack()
            checksum = self.read_byte()
            self.send_nak()
            if ((ctrl_byte_addr + data_byte) % 0x100) != checksum:
                status = E2StatusCode.E2_ERR_CKSUM
        else:
            status = E2StatusCode.E2_ERR_NAK
        self.stop()
        return data_byte, status  # return tuple with data_byte and status

    def start(self):
        """Issue start condition on bus lines."""
        self.sda_output()
        self.set_sda()
        self.set_scl()
        time.sleep(30/100000)
        self.clear_sda()
        time.sleep(30/100000)

    def stop(self):
        """Issue stop condition on bus lines."""
        self.sda_output()
        self.clear_scl()
        time.sleep(20/100000)
        self.clear_sda()
        time.sleep(20/100000)
        self.set_scl()
        time.sleep(20/100000)
        self.set_sda()

    def send_byte(self, value):
        """Send byte."""
        self.sda_output()
        mask = 0x80
        while mask > 0:
            self.clear_scl()
            time.sleep(10/100000)
            if (value & mask) != 0:
                self.set_sda()
            else:
                self.clear_sda()
            time.sleep(20/100000)
            self.set_scl()
            time.sleep(30/100000)
            self.clear_scl()
            mask >>= 1
        self.set_sda()

    def read_byte(self):
        """Read byte."""
        self.sda_input()
        data_in = 0x00
        mask = 0x80
        i = 0
        while mask > 0:
            self.clear_scl()
            time.sleep(30/100000)
            self.set_scl()
            time.sleep(15/100000)
            if self.read_sda():
                data_in |= mask
            time.sleep(15/100000)
            self.clear_scl()
            mask >>= 1
            i += 1
        return data_in

    def check_ack(self):
        """Check for acknowledge."""
        self.sda_input()
        self.clear_scl()
        time.sleep(30/100000)
        self.set_scl()
        time.sleep(15/100000)
        data = self.read_sda()
        time.sleep(15/100000)

        if data == 1:  # SDA = LOW ==> ACK, SDA = HIGH ==> NAK
            return NAK

        return ACK

    def send_ack(self):
        """Send acknowledge (ACK)."""
        self.sda_output()
        self.clear_scl()
        time.sleep(15/100000)
        self.clear_sda()
        time.sleep(15/100000)
        self.set_scl()
        time.sleep(28/100000)
        self.clear_scl()
        time.sleep(2/100000)
        self.set_sda()

    def send_nak(self):
        """Send not acknowledge (NAK)."""
        self.sda_output()
        self.clear_scl()
        time.sleep(15/100000)
        self.set_sda()
        time.sleep(15/100000)
        self.set_scl()
        time.sleep(30/100000)
        self.set_scl()

    def sda_input(self):
        """Change SDA direction to input."""
        GPIO.setup(self.sda, GPIO.IN)

    def sda_output(self):
        """Change SDA direction to output."""
        GPIO.setup(self.sda, GPIO.OUT)

    def set_sda(self):
        """Set SDA."""
        GPIO.output(self.sda, GPIO.HIGH)

    def clear_sda(self):
        """Clear SDA."""
        GPIO.output(self.sda, GPIO.LOW)

    def read_sda(self):
        """Read SDA-pin."""
        return GPIO.input(self.sda)

    def set_scl(self):
        """Set SCL."""
        GPIO.setup(self.scl, GPIO.IN)  # "High-Z"

        # consider clock stretching (wait for slave to release SCL, if necessary)
        while GPIO.input(self.scl) == 0:
            time.sleep(10e-6)

    def clear_scl(self):
        """Clear SCL."""
        GPIO.setup(self.scl, GPIO.OUT)
        GPIO.output(self.scl, GPIO.LOW)
