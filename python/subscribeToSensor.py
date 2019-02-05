from web3.auto import w3
from eth_utils import to_checksum_address
import argparse
import ipfsApi

from sensorSource import (SensorSource, signWithPassword, decodeMultihash)

def subscribeToSensor(subscriber, password, subscribersKeyFile, sensor, contractAddressFile, requestCount, readings):
    with open(contractAddressFile, 'r') as f: 
        contractAddress = f.read()

        source = SensorSource(w3, ipfsApi.Client(), contractAddress)

        subscriberId = to_checksum_address(subscriber)
        subscriberSigningCallback = signWithPassword(subscribersKeyFile, password)

        sensorId = to_checksum_address(sensor)

        requestEntries = [str(readings) for i in range(requestCount)]

        result = source.subscribe(
            sensorId, 
            requestEntries,
            subscriberId,
            subscriberSigningCallback
        )

        if result['success']: 
            print('Sensor {} has been subscribed to'.format(sensorId))
        else:
            print('Registration failed: {}', result['error'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='subscribe to a sensor on SensorSource')
    parser.add_argument(
        '--subscriber', 
        metavar='<subscriber account>', 
        type=str, 
        help="The sensor's subscribers account", 
        default='0xb7681870d74a882df35ca4e3712668fe8d24c146'
    )
    parser.add_argument(
        '--password',
        metavar='<subscribers password>',
        help='The subscribers password',
        default=''
    )    
    parser.add_argument(
        '--subscribersKeyFile',
        metavar='<owner-key-file>',
        default='../testnet/keystore/UTC--2019-01-29T12-01-37.019819000Z--b7681870d74a882df35ca4e3712668fe8d24c146'
    )
    parser.add_argument(
        '--sensor', 
        metavar='<sensor address>', 
        type=str, 
        help="The sensors' identity address", 
        default='0xb91df2b07643a88c323b7fcbad226b377a3fb857'
    )
    parser.add_argument(
        '--requestCount',
        metavar='<request count>',
        type=int,
        help='How many requests to subscribe for',
        default=20
    )
    parser.add_argument(
        '--readings',
        metavar='<readings per request>',
        type=int,
        help='How many readings to perform per request',
        default=10
    )
    parser.add_argument(
        '--contractAddressFile',
        default='sensorSource.address'
    )
    args = parser.parse_args()

    subscribeToSensor(**args.__dict__)

