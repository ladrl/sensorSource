from web3.auto import w3
import ipfsApi 

from sensorSource import SensorSourceEvents

import logging

registry = {}

events = SensorSourceEvents(w3)

print(events.history())