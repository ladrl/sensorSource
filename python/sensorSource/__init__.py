from os.path import dirname
from ipfsApi import Client as IPFSClient
from base58 import b58decode, b58encode
from easysolc import Solc

import logging

_contractFile = dirname(__file__) + "/contracts/sensorSource.sol"
_contractAddressFile = dirname(__file__) + "/adddress.bin"
_sensorSourceContract = Solc().get_contract_instance(
    source = _contractFile,
    contract_name = "SensorSource"
)

def signWithPassword(keyFilePath, password):
    import web3
    account = web3.eth.Account()
    with open(keyFilePath) as keyfile:
        encrypted_key = keyfile.read()
        private_key = account.decrypt(encrypted_key, password)
        acc = account.privateKeyToAccount(private_key)
        print('Key file ' + keyFilePath)
        print('Using account with adress ' + acc._address)
        def f(trx):
            print("Signing transaction " + str(trx))
            return acc.signTransaction(transaction_dict = trx)
        return f

def decodeMultihash(hashStr):
    decoded = b58decode(hashStr)
    return MultiHash(decoded[0],decoded[1], decoded[2:])

def encodeMultihash(multiHash):
    return b58encode(bytes([multiHash.function, multiHash.length]) + multiHash.hashData)

class MultiHash:
    def __init__(self, function, length, hashData):
        self.function = function
        self.length = length
        self.hashData = hashData

def deploy(web3, owner, signCallback): 
    trx = _sensorSourceContract.constructor().buildTransaction({
            'nonce' : web3.eth.getTransactionCount(owner),
            'from' : owner
        })
    signedTrx = signCallback(trx)
    deployed = web3.eth.waitForTransactionReceipt(
        web3.eth.sendRawTransaction(signedTrx.rawTransaction)
    )
    with open(_contractAddressFile, 'w') as addressFile: 
        addressFile.write(deployed.contractAddress)
    return deployed

class SensorSource:

    def __init__(self, web3, ipfs):
        self._log = logging.getLogger("SensorSource")
        self.__w3 = web3
        self.__ipfs = ipfs
        with open(_contractAddressFile) as addressFile:
            contract_address = addressFile.read()
            self.__contract = web3.eth.contract(address = contract_address, abi = _sensorSourceContract.abi)
            self._log.info("Sensor source @ " + contract_address)
        self.ipfs_add_str = self.decodeAsMultiHash(self.__ipfs.add_str)

    def _trxDict(self, sender):
        return {
            'nonce' : self.__w3.eth.getTransactionCount(sender),
            'from' : sender
        }

    def decodeAsMultiHash(self, f):
        def f_(*args, **kwargs): 
            return decodeMultihash(f(*args, **kwargs))
        return f_

    def register(self, sensorId, sensorMetaData, owner, signCallback):
        self._log.info("Register sensor " + sensorId)
        metaDataHash = self.ipfs_add_str(sensorMetaData)
        trx = self.__contract.functions.register_native(
                sensorId, 
                metaDataHash.function,
                metaDataHash.length,
                metaDataHash.hashData
            ).buildTransaction(self._trxDict(owner))
        signedTrx = signCallback(trx)
        return self.__w3.eth.waitForTransactionReceipt(
            self.__w3.eth.sendRawTransaction(signedTrx.rawTransaction)
        )

    def subscribe(self, sensorId, requestList, subscriber, signCallback): 
        self._log.info("Subscribe to sensor " + sensorId)
        count = len(requestList)
        reqListHash = self.ipfs_add_str("\n".join(requestList))
        trx = self.__contract.functions.subscribe_native(
                sensorId,
                reqListHash.function,
                reqListHash.length,
                reqListHash.hashData,
                count
            ).buildTransaction(self._trxDict(subscriber))
        signedTrx = signCallback(trx)
        return self.__w3.eth.waitForTransactionReceipt(
            self.__w3.eth.sendRawTransaction(signedTrx.rawTransaction)
        )

    def publish(self, sensorId, publicationNumber, publication, signCallback):
        self._log.info("Publish as " + sensorId)
        publicationHash = self.ipfs_add_str(publication)
        trx = self.__contract.functions.publish_native(
                sensorId,
                publicationHash.function,
                publicationHash.length,
                publicationHash.hashData,
                publicationNumber
            ).buildTransaction(self._trxDict(sensorId))
        signedTrx = signCallback(trx)
        return self.__w3.eth.waitForTransactionReceipt(
            self.__w3.eth.sendRawTransaction(signedTrx.rawTransaction)
        )


class SensorSourceEvents:

    def __init__(self, w3, handleRegistration = lambda evt: None, handleSubscription = lambda evt: None, handlePublication = lambda evt: None, timeout = 1):
        from multiprocessing import Process
        import time
        with open(_contractAddressFile) as addressFile:
            contract_address = addressFile.read()
            self._log = logging.getLogger("SensorSourceEvents")
            self.__contract = w3.eth.contract(address = contract_address, abi = _sensorSourceContract.abi)
            self._log.info("Sensor source @ " + contract_address)


        filters = [
            (self.__contract.events.Registered.createFilter(fromBlock = 'latest'), handleRegistration),
            (self.__contract.events.Subscribed.createFilter(fromBlock = 'latest'), handleSubscription),
            (self.__contract.events.Published.createFilter(fromBlock = 'latest'), handlePublication)
        ]

        def poll(): 
            while True:
                self._log.debug("Poll events")
                for (filter, handler) in filters:
                    for event in filter.get_new_entries():
                        handler(event)
                    time.sleep(timeout)
        self._poller = Process(target = poll)

    def start(self):
        self._poller.start()

class Subscription:
    def __init__(self, sensorSource):
        pass


class Publisher:
    def __init__(self, sensorId):
        self.__id = sensorId
    