from os.path import dirname
from ipfsApi import Client as IPFSClient
from base58 import b58decode, b58encode
from easysolc import Solc

import logging

def signWithPassword(keyFilePath, password):
    import web3
    account = web3.eth.Account()
    with open(keyFilePath) as keyfile:
        encrypted_key = keyfile.read()
        private_key = account.decrypt(encrypted_key, password)
        acc = account.privateKeyToAccount(private_key)
        def f(trx):
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

    def __str__(self):
        return str(encodeMultihash(self))

def deploy(web3, owner, signCallback): 
    trx = SensorSource._sensorSourceContract.constructor().buildTransaction({
            'nonce' : web3.eth.getTransactionCount(owner),
            'from' : owner
        })
    signedTrx = signCallback(trx)
    deployed = web3.eth.waitForTransactionReceipt(
        web3.eth.sendRawTransaction(signedTrx.rawTransaction)
    )
    return deployed

class SensorSource:

    _contractFile = dirname(__file__) + "/contracts/sensorSource.sol"
    _sensorSourceContract = Solc().get_contract_instance(
        source = _contractFile,
        contract_name = "SensorSource"
    )

    def __init__(self, web3, ipfs, contractAddress):
        self._log = logging.getLogger("SensorSource")
        self.__w3 = web3
        self.__ipfs = ipfs
        self._contract_address = contractAddress
        self.__contract = web3.eth.contract(
            address = self._contract_address, 
            abi = self._sensorSourceContract.abi
        )
        self._log.info("Sensor source @ " + self._contract_address)
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
        try:
            trx = self.__contract.functions.register_native(
                    sensorId, 
                    metaDataHash.function,
                    metaDataHash.length,
                    metaDataHash.hashData
                ).buildTransaction(self._trxDict(owner))
            signedTrx = signCallback(trx)
            result = self.__w3.eth.waitForTransactionReceipt(
                self.__w3.eth.sendRawTransaction(signedTrx.rawTransaction)
            )
            return dict(success=True, metaData = metaDataHash, result = result)
        except ValueError as e:
            return dict(success=False, error = e)

    def subscribe(self, sensorId, requestList, subscriber, signCallback): 
        self._log.info("Subscribe to sensor " + sensorId)
        count = len(requestList)
        reqListHash = self.ipfs_add_str("\n".join(requestList))
        try:
            trx = self.__contract.functions.subscribe_native(
                    sensorId,
                    reqListHash.function,
                    reqListHash.length,
                    reqListHash.hashData,
                    count
                ).buildTransaction(self._trxDict(subscriber))
            signedTrx = signCallback(trx)
            result = self.__w3.eth.waitForTransactionReceipt(
                self.__w3.eth.sendRawTransaction(signedTrx.rawTransaction)
            )
            return dict(success=True, result = result)
        except ValueError as e:
            return dict(success=False, error = e)

    def publish(self, sensorId, publicationNumber, publication, signCallback):
        self._log.info("Publish as " + sensorId)
        publicationHash = self.ipfs_add_str(publication)
        try:
            trx = self.__contract.functions.publish_native(
                    sensorId,
                    publicationHash.function,
                    publicationHash.length,
                    publicationHash.hashData,
                    publicationNumber
                ).buildTransaction(self._trxDict(sensorId))
            signedTrx = signCallback(trx)
            result = self.__w3.eth.waitForTransactionReceipt(
                self.__w3.eth.sendRawTransaction(signedTrx.rawTransaction)
            )
            return dict(success=True, result = result)
        except ValueError as e:
            return dict(success=False, error = e)


class SensorSourceEvents:


    def __init__(self, w3, contractAddress):
        self._log = logging.getLogger("SensorSourceEvents")
        self._contract_address = contractAddress
        self._contract = w3.eth.contract(address = self._contract_address, abi = SensorSource._sensorSourceContract.abi)
        self._log.info("Sensor source @ " + self._contract_address)
        self._filters = {
            'Registered' : self._contract.events.Registered.createFilter,
            'Subscribed': self._contract.events.Subscribed.createFilter,
            'Published' : self._contract.events.Published.createFilter
        }

    def history(self):
        return dict(
            [
                (name, [
                    (e.args.sensorId, dict(e.args)) for e in f(fromBlock = 0, toBlock = 'latest').get_all_entries()
                    ]) for (name, f) in self._filters.items()
                ]
            )

    def listen(self, handlers = {}, timeout = 1):
        from multiprocessing import Process
        import time
        def poll(): 
            filters = dict([(name, f(fromBlock='latest')) for (name, f) in self._filters.items()])
            while True:
                self._log.debug("Poll events")
                for (name, filter) in filters.items():
                    handler = handlers.get(name)
                    if(handler):
                        self._log.debug('Events for ' + name)
                        for event in filter.get_new_entries():
                            try:
                                handler(**dict(event.args))
                            except Exception as e:
                                self._log.error('Handler {} failed with args {}:\n{}'.format(handler, str(event.args), e))
                    time.sleep(timeout)
        self._poller = Process(target = poll)
        self._poller.start()

class Subscription:
    def __init__(self, sensorSource):
        pass


class Publisher:
    def __init__(self, sensorId):
        self.__id = sensorId
    