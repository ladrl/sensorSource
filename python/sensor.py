from web3.auto import w3
from eth_utils import to_checksum_address

import ipfsApi 
import argparse
import logging

#logging.getLogger("SensorSourceEvents").setLevel('DEBUG')

from sensorSource import (SensorSource, SensorSourceEvents, signWithPassword, encodeMultihash, MultiHash)

def sensor(password, sensorKeyFile, sensor, contractAddressFile):
    with open(contractAddressFile, 'r') as f: 
        contractAddress = f.read()

        sensorId = to_checksum_address(sensor)
        events = SensorSourceEvents(w3, contractAddress)

        def handleSubscription(metaDataHashFunction, metaDataHashLength, metaDataHash, requestCount, sensorId):
            if to_checksum_address(sensor) == sensorId:
                source = SensorSource(w3, ipfsApi.Client(), contractAddress)
                sourceOnwerSigningCallback = signWithPassword(sensorKeyFile, password)

                requests = ipfsApi.Client().cat(encodeMultihash(MultiHash(metaDataHashFunction, metaDataHashLength, metaDataHash)))

                publicationId = requestCount
                for pendingRequest in requests.splitlines():
                    #values = [input('Publication #{} reading #{}: '.format(publicationId, i)) for i in range(int(pendingRequest))]
                    values = ['Sensor {}, publication #{}, reading #{}'.format(sensorId, publicationId, i) for i in range(int(pendingRequest))]
                    result = source.publish(
                            sensorId,
                            publicationId,
                            '\n'.join(values),
                            sourceOnwerSigningCallback
                    )
                    if result['success']:
                        print('Sensor values published as id {}'.format(publicationId))
                        publicationId -= 1 
                    else:
                        print('Registration failed: {}', result['error'])

        print('Waiting for subscription to sensor @ {} on sensorSource @ {}'.format(sensorId, contractAddress))
        events.listen(handlers=dict(Subscribed = handleSubscription))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run as a sensor')
    parser.add_argument(
        '--password',
        metavar='<sensor address password>',
        help='The sensors password',
        default=''
    )    
    parser.add_argument(
        '--sensorKeyFile',
        metavar='<sensor-key-file>',
        default='../testnet/keystore/UTC--2019-01-17T09-23-30.699759000Z--b91df2b07643a88c323b7fcbad226b377a3fb857'
    )
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
    sensor(**args.__dict__)