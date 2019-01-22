import web3
import logging

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

#logging.getLogger("web3.RequestManager").setLevel('DEBUG')

solc = Solc()
ipfs = ipfsApi.Client()
sensorId = w3.eth.accounts[1]
owner = w3.eth.accounts[0]

sensorSourceContract = solc.get_contract_instance(
    w3 = w3,
    source = scriptDir + '/../Off-Chain/contracts/sensorSource.sol',
    contract_name="SensorSource"
)

def decodeMultihash(ipfsHash):
    decoded = base58.b58decode(ipfsHash)
    return {
        'hashFunction' : decoded[0],
        'length' : decoded[1],
        'data' : decoded[2:]
    }

def encodeMultihash(hashFunction, hashLength, hash):
    return base58.b58encode(bytes([hashFunction, hashLength]) + hash[:hashLength])

def register(sensorId, sensorMetaData):
    ipfsHash = ipfs.add_str(sensorMetaData)
    metaDataHash = decodeMultihash(ipfsHash)
    return w3.eth.waitForTransactionReceipt(
        sensorSource.functions.register_native(
            sensorId, 
            metaDataHash['hashFunction'],
            metaDataHash['length'],
            metaDataHash['data']
        ).transact({'from' : owner, 'gas': 100000})
    )

def subscribe(sensorId, requestList): 
    count = len(requestList)
    reqListHash = ipfs.add_str("\n".join(requestList))
    multiHash = decodeMultihash(reqListHash)
    tx_receipt = sensorSource.functions.subscribe_native(
            sensorId,
            multiHash['hashFunction'],
            multiHash['length'],
            multiHash['data'],
            count
        ).transact({'from' : owner, 'gas': 100000})
    return w3.eth.waitForTransactionReceipt(tx_receipt)

def publish(sensorId, publicationNumber, publication):
    publicationHash = ipfs.add_str(publication)
    print(publicationHash)
    multiHash = decodeMultihash(publicationHash)
    print(multiHash)
    tx_receipt = sensorSource.functions.publish_native(
            sensorId,
            multiHash['hashFunction'],
            multiHash['length'],
            multiHash['data'],
            publicationNumber
        ).transact({'from' : sensorId, 'gas': 100000})
    return w3.eth.waitForTransactionReceipt(tx_receipt)

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

def listenTo(filter_handler_pairs):
    import multiprocessing
    import time
    def run():
        while True:
            try:
                for (filter, handler) in filter_handler_pairs:
                    for event in filter.get_new_entries():
                        handler(event)
            except ValueError:
                print("ignore error")
            time.sleep(1)
    proc = multiprocessing.Process(target = run)
    proc.start()
    return proc

def handle_registration(registration):
    args = registration.args
    ipfsHash =  encodeMultihash(args.metaDataHashFunction, args.metaDataHashLength, args.metaDataHash)
    print("Sensor " + args.sensorId + " has been registered:")
    print(" id:" + registration.args.sensorId)
    print(" meta:" + ipfs.cat(ipfsHash))

def handle_subscription(subscription):
    args = subscription.args
    ipfsHash = encodeMultihash(args.metaDataHashFunction, args.metaDataHashLength, args.metaDataHash)
    print("Sensor " + args.sensorId + " has been subscribed to for " + str(args.requestCount) + " requests")
    print(" requests:" + ipfs.cat(ipfsHash))

def handle_publication(publication):
    args = publication.args
    ipfsHash = encodeMultihash(args.metaDataHashFunction, args.metaDataHashLength, args.metaDataHash)
    print("Sensor " + args.sensorId + " has published " + str(args.requestCount) + ":")
    print(ipfs.cat(ipfsHash))

listenTo([
    (sensorSource.events.Subscribed.createFilter(fromBlock = 'latest'), handle_subscription),
    (sensorSource.events.Registered.createFilter(fromBlock = 'latest'), handle_registration),
    (sensorSource.events.Published.createFilter(fromBlock = 'latest'), handle_publication)
])

print("register")
register(sensorId, "Some nice metadata")
print("registration done")

print("subscribe")
subscribe(sensorId, ["A", "B", "C"])
print("subscription done")

print("publishing")
import time
time.sleep(5)
publish(sensorId, 2, "For C")
time.sleep(5)
publish(sensorId, 1, "For B")
time.sleep(5)
publish(sensorId, 0, "For A")
print("publishing done")