from web3.auto import w3
from eth_utils import to_checksum_address

import ipfsApi 

from sensorSource import (SensorSource, signWithPassword)

source = SensorSource(w3, ipfsApi.Client())

sourceOwner = to_checksum_address('0x92a793e3683de328c955eb1464aa9354833bfbe4')
sourceOnwerSigningCallback = signWithPassword('/Users/lla/Documents/Talks/BETH/testnet/keystore/UTC--2019-01-17T09-04-39.652187000Z--92a793e3683de328c955eb1464aa9354833bfbe4', '')

sensorId = to_checksum_address('0xb91df2b07643a88c323b7fcbad226b377a3fb857')

result = source.register(
    sensorId, 
    "Sensor meta data, for real!", 
    sourceOwner, 
    sourceOnwerSigningCallback
)

print("Registration: " + str(result))
