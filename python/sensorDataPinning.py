from web3.auto import w3
import ipfsApi 
import argparse
import logging

from sensorSource import (SensorSourceEvents, encodeMultihash, MultiHash)

def pinPublishedHashes(contractAddressFile):

    client = ipfsApi.Client()

    def pinRegistered(owner, sensorId, metaDataHashFunction, metaDataHashLength, metaDataHash):
        dataHash = encodeMultihash(MultiHash(metaDataHashFunction, metaDataHashLength, metaDataHash))
        client.pin_add(dataHash)
        print("Pinning registration data of {}".format(sensorId))
        print(client.cat(dataHash))

    def pinSubscribed(requestCount, sensorId, metaDataHashFunction, metaDataHashLength, metaDataHash):
        dataHash = encodeMultihash(MultiHash(metaDataHashFunction, metaDataHashLength, metaDataHash))
        client.pin_add(dataHash)
        print("Pinning subscription data of {}".format(sensorId))
        print(client.cat(dataHash))

    def pinPublished(entryId, sensorId, metaDataHashFunction, metaDataHashLength, metaDataHash):
        dataHash = encodeMultihash(MultiHash(metaDataHashFunction, metaDataHashLength, metaDataHash))
        client.pin_add(dataHash)
        print("Pinning publication data of {}".format(sensorId))
        print(client.cat(dataHash))

    events = SensorSourceEvents(w3, open(contractAddressFile).read())
    events.listen(dict(Registered = pinRegistered, Subscribed = pinSubscribed, Published = pinPublished))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pin all published hashes of a SensorSource')
    parser.add_argument(
        '--contractAddressFile',
        default='sensorSource.address'
    )
    args = parser.parse_args()

    pinPublishedHashes(**args.__dict__)

