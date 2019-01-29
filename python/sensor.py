from web3.auto import w3
from eth_utils import to_checksum_address

import ipfsApi 
import argparse
import logging

logging.getLogger("SensorSourceEvents").setLevel('DEBUG')

from sensorSource import (SensorSource, SensorSourceEvents, signWithPassword)

def handleSubscription(args):

    #source = SensorSource(w3, ipfsApi.Client(), contractAddress)
    #sourceOnwerSigningCallback = signWithPassword(keyFile, password)
    #result = source.publish(
    #        sensorId, 
    #        "Sensor meta data, for real!", 
    #        sourceOwner,
    #        sourceOnwerSigningCallback
    #)
    #if result['success']: 
    #    print('Sensor {} has been registered with meta-data {}'.format(sensorId, result['metaData']))
    #else:
    #    print('Registration failed: {}', result['error'])
    print('Got subscription ' + str(args))

def sensor(args):
    sensor, keyFile, password, addressFile = args.sensor, args.sensorKeyFile, args.password, args.contractAddressFile
    with open(addressFile, 'r') as f: 
        contractAddress = f.read()

        sensorId = to_checksum_address(sensor)
        events = SensorSourceEvents(w3, contractAddress)

        def filterForId(id, args):
            if(id == sensorId):
                handleSubscription(args)
        print('Waiting for subscription to sensor @ {} on sensorSource @ {}'.format(sensorId, contractAddress))
        events.listen(handlers=dict(Subscribed = filterForId))


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
        default='./testnet/keystore/UTC--2019-01-17T09-23-30.699759000Z--b91df2b07643a88c323b7fcbad226b377a3fb857'
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
    sensor(args)