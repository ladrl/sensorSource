from sensorSource import (deploy)

from web3.auto import w3
from eth_utils import to_checksum_address

import web3
import ipfsApi 
import logging
import argparse


from sensorSource import (SensorSource, signWithPassword)

def deployContract(args):
    owner, ownerKeyFile, password, addressFile = args.owner, args.ownerKeyFile, args.password, args.contractAddressFile
    sourceOwner = to_checksum_address(owner)
    sourceOnwerSigningCallback = signWithPassword(ownerKeyFile, password)

    result = deploy(web3.auto.w3, sourceOwner, sourceOnwerSigningCallback)
    print('Deployed contract @ {}'.format(result.contractAddress))
    with open(addressFile, 'w') as f: 
            f.write(result.contractAddress)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Deploy a new SensorSource contract')
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
        default='./testnet/keystore/UTC--2019-01-17T09-04-39.652187000Z--92a793e3683de328c955eb1464aa9354833bfbe4'
    )
    parser.add_argument(
        '--contractAddressFile',
        default='sensorSource.address'
    )
    args = parser.parse_args()

    deployContract(args)