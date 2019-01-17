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
    hash = registration.args.metaDataHash
    ipfsHash = base58.b58encode(b'\x12\x20' + hash)
    print("Sensor has been registered:")
    print(" id:" + registration.args.sensorId)
    print(" meta:" + ipfs.cat(ipfsHash))

listenTo(sensorSource.events.Registered.createFilter(fromBlock = 'latest'), handle_registration)

def register(sensorId, sensorMetaData):
    ipfsHash = ipfs.add_str(sensorMetaData)
    #print(ipfsHash)
    metaDataHash = base58.b58decode(ipfsHash)[2:] # cut off the first 2 bytes indicating sha256 (0x12) and length (0x20)
    #print(metaDataHash)
    register_receipt = w3.eth.waitForTransactionReceipt(
        sensorSource.functions.register(
            sensorId, 
            metaDataHash
        ).transact({'from' : owner, 'gas': 100000})
    )

    return register_receipt

register(sensorId, "Some nice metadata")