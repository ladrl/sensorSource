import web3
import logging

# Systems:
# brew install ipfs
# brew install geth
# brew install solidity
# 
# > geth account new
# > geth account new
# Add the created accounts to the genesis.json
# > geth removedb --datadir .
# > geth init --datadir . genesis.json
# > geth --identity "MyTestNetNode" --nodiscover --networkid 1999 --datadir . --mine --miner.threads 5  console --rpc --rpccorsdomain "*"
# On the console 
# $ personal.unlockAccount(eth.accounts[0], "", 30000)
# $ personal.unlockAccount(eth.accounts[1], "", 30000)


# Dependencies: 
# pip3 install web3
# pip3 install base58
# pip3 install ipfsApi
# pip3 install easysolc

import ipfsApi 
import base58
from web3.auto import w3
from easysolc import Solc

def sensorPrivateKey():
    with open( 'testnet/keystore/UTC--2019-01-17T09-23-30.699759000Z--b91df2b07643a88c323b7fcbad226b377a3fb857') as keyfile:
        encrypted_key = keyfile.read()
        private_key_sensorId = w3.eth.account.decrypt(encrypted_key, '')
        return private_key_sensorId

import os 
scriptDir = os.path.dirname(__file__)

logging.getLogger("web3.RequestManager").setLevel('DEBUG')

solc = Solc()
ipfs = ipfsApi.Client()
sensorId = w3.toChecksumAddress('0xb91df2b07643a88c323b7fcbad226b377a3fb857')    #w3.eth.accounts[1]
owner = w3.eth.accounts[0]

sensorSourceContract = solc.get_contract_instance(
    w3 = w3,
    source = scriptDir + '/sensorSource/contracts/sensorSource.sol',
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
    print("Publish for " + sensorId + " with " + str(publicationNumber) + ": " + publication)
    publicationHash = ipfs.add_str(publication)
    multiHash = decodeMultihash(publicationHash)
    trx = sensorSource.functions.publish_native(
            sensorId,
            multiHash['hashFunction'],
            multiHash['length'],
            multiHash['data'],
            publicationNumber
        ).buildTransaction({
            'from' : sensorId, 
            'gas': 100000,
            'gasPrice': w3.eth.gasPrice,
            'nonce' : w3.eth.getTransactionCount(sensorId),
            'chainId' : 15
        })
    signedTrx = w3.eth.account.signTransaction(
        trx,
        sensorPrivateKey()
    )
    tx_receipt = w3.eth.sendRawTransaction(signedTrx.rawTransaction)
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

def handleCount(filter_handler_pairs):
    def l(count): 
        actualCount = 0
        while actualCount < count:
            for (filter, handler) in filter_handler_pairs:
                for event in filter.get_new_entries():
                    handler(event)
                    actualCount += 1
    return l

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
    print("Sensor " + args.sensorId + " has published " + str(args) + ":")
    print(ipfs.cat(ipfsHash))

allEvents = handleCount([
    (sensorSource.events.Subscribed.createFilter(fromBlock = 'latest'), handle_subscription),
    (sensorSource.events.Registered.createFilter(fromBlock = 'latest'), handle_registration),
    (sensorSource.events.Published.createFilter(fromBlock = 'latest'), handle_publication)
])

print("register")
register(sensorId, "Some nice metadata")
print("registration done")

allEvents(1)

print("subscribe")
subscribe(sensorId, ["A", "B", "C"])
print("subscription done")

allEvents(1)

def nextPublishId(): 
    return sensorSource.functions.publication(sensorId).call()[4]

print("publishing")
publish(sensorId, nextPublishId(), "For C")
allEvents(1)
publish(sensorId, nextPublishId(), "For B")
allEvents(1)
publish(sensorId, nextPublishId(), "For A")
allEvents(1)
print("publishing done")