# -*- coding: utf-8 -*-
"""
Read functions for measurement values of the EE894 Sensor via E2 interface.

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

from e2_interface import E2StatusCode
from e2_interface import get_status_string

# constant definition
# -----------------------------------------------------------------------------
CB_TYPELO = 0x11      # controlbyte for reading sensortype low-byte
CB_TYPESUB = 0x21     # controlbyte for reading sensor-subtype
CB_AVPHMES = 0x31     # controlbyte for reading available physical measurements
CB_TYPEHI = 0x41      # controlbyte for reading sensortype high-byte
CB_STATUS = 0x71      # controlbyte for reading statusbyte
CB_MV1LO = 0x81       # controlbyte for reading measurement value 1 low-byte
CB_MV1HI = 0x91       # controlbyte for reading measurement value 1 high-byte
CB_MV2LO = 0xA1       # controlbyte for reading measurement value 2 low-byte
CB_MV2HI = 0xB1       # controlbyte for reading measurement value 2 high-byte
CB_MV3LO = 0xC1       # controlbyte for reading measurement value 3 low-byte
CB_MV3HI = 0xD1       # controlbyte for reading measurement value 3 high-byte
CB_MV4LO = 0xE1       # controlbyte for reading measurement value 4 low-byte
CB_MV4HI = 0xF1       # controlbyte for reading measurement value 4 high-byte


class EE894E2():
    """Implements communication with EE894 over E2."""

    def __init__(self, e2_device):
        self.e2_device = e2_device

    def read_meas_value(self, control_bytes, scale_factor):
        """Read two bytes and treat them as measurement values."""
        status = self.read_status()
        if status == E2StatusCode.E2_OK:
            value, status = self.e2_device.read_word_from_slave(control_bytes)

        if status != E2StatusCode.E2_OK:
            raise Warning(get_status_string(status))

        return float(value / scale_factor)

    def read_rh(self):
        """Read relative humidity [%]."""
        return self.read_meas_value([CB_MV1LO, CB_MV1HI], 100)

    def read_temp(self):
        """Read temperature [K]."""
        return self.read_meas_value([CB_MV2LO, CB_MV2HI], 100)

    def read_pres(self):
        """Read air pressure [mbar]."""
        return self.read_meas_value([CB_MV3LO, CB_MV3HI], 10)

    def read_co2_mean(self):
        """CO2 mean [ppm]."""
        return self.read_meas_value([CB_MV4LO, CB_MV4HI], 1)

    def read_status(self):
        """Read status byte."""
        data_byte, status = self.e2_device.read_byte_from_slave(CB_STATUS)
        if status == E2StatusCode.E2_OK:  # data transmittion was ok
            if data_byte != 0:
                return E2StatusCode.E2_ERR_MEAS
        return status

    def read_sensortype(self):
        """Read sensor type."""
        sensor_type, status = self.e2_device.read_word_from_slave([CB_TYPELO, CB_TYPEHI])

        if status != E2StatusCode.E2_OK:
            raise Warning(get_status_string(status))
        return sensor_type

    def read_sensorsubtype(self):
        """Read sensor subtype."""
        subtype, status = self.e2_device.read_byte_from_slave(CB_TYPESUB)

        if status != E2StatusCode.E2_OK:
            raise Warning(get_status_string(status))
        return subtype

    def read_available_measurands(self):
        """Read available measurands."""
        measurands, status = self.e2_device.read_byte_from_slave(CB_AVPHMES)

        if status != E2StatusCode.E2_OK:
            raise Warning(get_status_string(status))
        return measurands
