# -*- coding: utf-8 -*-
"""
Example script reading measurement values from the EE894 sensor via E2 interface.

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
from e2_interface import E2Device
from ee894_e2_library import EE894E2

E2_SCL = 3
E2_SDA = 2
E2_DEV_ADDR = 0


def kelvin_to_celsius(kelvin):
    """Convert Kelvin to Celsius."""
    return kelvin - 273.15


# Definition
CSV_DELIMETER = ","


E2_DEVICE = E2Device(E2_SCL, E2_SDA, E2_DEV_ADDR)
EE894_DEVICE = EE894E2(E2_DEVICE)

# read device identification
try:
    print("Sensor type: " + str(EE894_DEVICE.read_sensortype()))
    print("Sensor sub-type: " + str(EE894_DEVICE.read_sensorsubtype()))
    print("Available measurands (bitmask): " + str(bin(EE894_DEVICE.read_available_measurands())))

except Warning as exception:
    print("Exception: " + str(exception))

# print csv header
print("temperature", CSV_DELIMETER,
      "relative humidity", CSV_DELIMETER,
      "co2", CSV_DELIMETER,
      "pressure")

for i in range(30):

    try:
        temperature = kelvin_to_celsius(EE894_DEVICE.read_temp())
        humidity = EE894_DEVICE.read_rh()
        co2 = EE894_DEVICE.read_co2_mean()
        pressure = EE894_DEVICE.read_pres()

        print('%0.2f °C' % temperature, CSV_DELIMETER,
              '%0.2f %%RH' % humidity, CSV_DELIMETER,
              '%0.0f ppm' % co2, CSV_DELIMETER,
              '%0.1f mbar' % pressure)

    except Warning as exception:
        print("Exception: " + str(exception))

    finally:
        time.sleep(0.5)
