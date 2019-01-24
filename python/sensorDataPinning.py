from web3.auto import w3
import ipfsApi 

from sensorSource import SensorSourceEvents

import logging

#logging.getLogger("web3.RequestManager").setLevel('DEBUG')
#logging.getLogger("SensorSourceRegistry").setLevel('DEBUG')

events = SensorSourceEvents(w3, handleRegistration = print)

events.start()