from web3.auto import w3
from eth_utils import to_checksum_address

import ipfsApi 
import argparse
import logging
import textwrap

from sensorSource import (SensorSourceEvents, encodeMultihash, MultiHash)

def consumeSensorData(contractAddressFile, sensor):

    client = ipfsApi.Client()

    def processPublished(entryId, sensorId, metaDataHashFunction, metaDataHashLength, metaDataHash):
        if(sensorId == to_checksum_address(sensor)):
            dataHash = encodeMultihash(MultiHash(metaDataHashFunction, metaDataHashLength, metaDataHash))
            print("Sensor data from {}\n{}\n".format(sensorId, textwrap.indent(client.cat(dataHash), '|\t')))
        else: 
            print('{} vs {}'.format(sensorId, sensor))

    events = SensorSourceEvents(w3, open(contractAddressFile).read())
    events.listen(dict(Published = processPublished))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process the data of a single sensor from SensorSource')
    parser.add_argument(
        '--sensor', 
        metavar='<sensor address>', 
        type=str, 
        help="The sensors' identity address", 
        default='0xb91df2b07643a88c323b7fcbad226b377a3fb857'
    )
    parser.add_argument(
        '--contractAddressFile',
        default='sensorSource.address'
    )
    args = parser.parse_args()

    consumeSensorData(**args.__dict__)

