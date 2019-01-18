import json
import web3

# Systems:
# brew install ipfs
# brew install geth
# brew install solidity
# 
# Dependencies: 
# pip3 install web3
# pip3 install base58
# pip3 install ipfsApi
# pip3 install easysolc

import ipfsApi 
import base58
from web3.auto import w3
from easysolc import Solc

import os 
scriptDir = os.path.dirname(__file__)

solc = Solc()
ipfs = ipfsApi.Client()
sensorId = w3.eth.accounts[1]
owner = w3.eth.accounts[0]

sensorSourceContract = solc.get_contract_instance(
    w3 = w3,
    source = scriptDir + '/../Off-Chain/contracts/sensorSource.sol',
    contract_name="SensorSource"
)

def register(sensorId, sensorMetaData):
    ipfsHash = ipfs.add_str(sensorMetaData)
    ipfsDecoded = base58.b58decode(ipfsHash)
    metaDataHash = {
            'hashFunction' : ipfsDecoded[0],
            'length' : ipfsDecoded[1],
            'data' : ipfsDecoded[2:]
    }
    register_receipt = w3.eth.waitForTransactionReceipt(
        sensorSource.functions.register_native(
            sensorId, 
            metaDataHash['hashFunction'],
            metaDataHash['length'],
            metaDataHash['data']
        ).transact({'from' : owner, 'gas': 100000})
    )

    return register_receipt

def deploy(): 
    tx_receipt = w3.eth.waitForTransactionReceipt(
        sensorSourceContract.constructor().transact({'from' : owner})
    )
    return tx_receipt.contractAddress

sensorSource = w3.eth.contract(
    address = deploy(), 
    abi = sensorSourceContract.abi
)

print("SensorSource contract @ " + sensorSource.address)

def listenTo(filter, handler):
    import multiprocessing
    import time
    def run():
        while True:
            for event in filter.get_new_entries():
                handler(event)
            time.sleep(1)
    proc = multiprocessing.Process(target = run)
    proc.start()
    return proc

def handle_registration(registration): 
    hashFunction = registration.args.metaDataHashFunction
    hashLength = registration.args.metaDataHashLength
    hash = registration.args.metaDataHash
    ipfsHash = base58.b58encode(bytes([hashFunction, hashLength]) + hash[:hashLength])
    print("Sensor has been registered:")
    print(" id:" + registration.args.sensorId)
    print(" meta:" + ipfs.cat(ipfsHash))

listenTo(sensorSource.events.Registered.createFilter(fromBlock = 'latest'), handle_registration)

register(sensorId, "Some nice metadata")

def subscribe(): 
    pass

subscribe()
