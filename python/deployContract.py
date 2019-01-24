from sensorSource import (deploy)

from web3.auto import w3
from eth_utils import to_checksum_address

import web3
import ipfsApi 
import logging
#logging.getLogger("web3.RequestManager").setLevel('DEBUG')


from sensorSource import (SensorSource, signWithPassword)

sourceOwner = to_checksum_address('0x92a793e3683de328c955eb1464aa9354833bfbe4')
sourceOnwerSigningCallback = signWithPassword('/Users/lla/Documents/Talks/BETH/testnet/keystore/UTC--2019-01-17T09-04-39.652187000Z--92a793e3683de328c955eb1464aa9354833bfbe4', '')

result = deploy(web3.auto.w3, sourceOwner, sourceOnwerSigningCallback)
print("Deployment: " + str(result))