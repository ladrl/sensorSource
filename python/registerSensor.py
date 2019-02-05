from web3.auto import w3
from eth_utils import to_checksum_address

import ipfsApi 
import argparse

from sensorSource import (SensorSource, signWithPassword)

def registerSensor(args):
    owner, ownerKeyFile, sensorId, addressFile = args.owner, args.ownerKeyFile, args.sensor, args.contractAddressFile
    with open(addressFile, 'r') as f: 
        contractAddress = f.read()

        source = SensorSource(w3, ipfsApi.Client(), contractAddress)

        sourceOwner = to_checksum_address(owner)
        sourceOnwerSigningCallback = signWithPassword(ownerKeyFile, '')

        sensorId = to_checksum_address(sensorId)

        result = source.register(
            sensorId, 
            "Sensor meta data, for real!", 
            sourceOwner, 
            sourceOnwerSigningCallback
        )
        if result['success']: 
            print('Sensor {} has been registered with meta-data {}'.format(sensorId, result['metaData']))
        else:
            print('Registration failed: {}', result['error'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='register a sensor on SensorSource')
    parser.add_argument(
        '--owner', 
        metavar='<owner address>', 
        type=str, 
        help="The sensor's owners address", 
        default='0x92a793e3683de328c955eb1464aa9354833bfbe4'
    )
    parser.add_argument(
        '--password',
        metavar='<owner address password>',
        help='The owners password',
        default=''
    )    
    parser.add_argument(
        '--ownerKeyFile',
        metavar='<owner-key-file>',
        default='../testnet/keystore/UTC--2019-01-17T09-04-39.652187000Z--92a793e3683de328c955eb1464aa9354833bfbe4'
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

    registerSensor(args)

