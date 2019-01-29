from web3.auto import w3
import ipfsApi 

from sensorSource import (SensorSourceEvents, encodeMultihash, MultiHash)

import logging

def pinRegistered(sensorId, args):
    dataHash = encodeMultihash(MultiHash(args['metaDataHashFunction'], args['metaDataHashLength'], args['metaDataHash']))
    ipfsApi.Client().pin_add(dataHash)
    print("Pinning data for sensor " + sensorId)

events = SensorSourceEvents(w3)
events.listen(dict(Registered = pinRegistered))