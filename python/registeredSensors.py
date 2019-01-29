from web3.auto import w3
import ipfsApi 
import argparse
import logging
import textwrap

from sensorSource import (SensorSourceEvents,encodeMultihash, MultiHash)

def listSensors(args):
    print('Registered sensors on contract @ {}\n'.format(args.contractAddressFile))
    events = SensorSourceEvents(w3, open(args.contractAddressFile, 'r').read())
    ipfs = ipfsApi.Client()

    for sensorId, data in events.history()['Registered']:
        metaData = encodeMultihash(MultiHash(data['metaDataHashFunction'], data['metaDataHashLength'], data['metaDataHash']))
        print('Sensor {}:\n{}\n\n'.format(sensorId, 
            textwrap.indent(ipfs.cat(metaData), '|\t')))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='List the registered sensors')
    parser.add_argument(
        '--contractAddressFile',
        default='sensorSource.address'
    )
    args = parser.parse_args()

    listSensors(args)