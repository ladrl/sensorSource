# SensorSource Demo Application

SensorSource is a demo application built from a SmartContract for Ethereum and a number of python scripts which allow the interaction with this smart contract. The goal of the application is to demonstate a way to collect sensor data for the use in other smart contracts.

**IMPORTANT:** This demo application is *not* tested with regards to security or upgrade-ability. *Never* use directly in production.

## SensorSource workflow

1. Register a sensor with their meta data stored on IPFS  
2. Subscribe to this sensor referencing the request list
3. Sensor receives the subscription, fetches the request from IPFS and collects the requested data
4. Sensor stores results in IPFS then publishes its hash
5. Data consumer receives the publication and accesses the data via IPFS

## File structure

* `./Readme.md`: This file
* `./testnet/`: Ethereum test network data
  * `./testnet/genesis.json`: A description of the first block of the Ethereum test network used for this demo
  * `./testnet/keystore/*`: A list of key files representing the accounts used by default by the python scripts. All keys are encrpyted, but use an empty password.
* `./python/`: Python scripts
  * `./python/requirements.txt`: Listing of required python packages. For setup, run `pip install -r requirements.txt`
  * `./python/sensorSource/__init__.py`: SensorSource library implementation
  * `./python/sensorSource/contracts/sensorSource.sol`: SensorSource SmartContract implementation
  * `./python/deployContract.py`: Bootstrap script to first deploy the SensorSource contract on the test net
  * `./python/registerSensor.py`: Register a sensor on an existing SensorSource contract
  * `./python/registeredSensors.py`: Show the existing sensors on a SensorSource contract, meant to illustrate the use of the event log as a registry
  * `./python/sensorDataConsumer.py`: Start a long-running consumer waiting for the data of a specific sensor to be published
  * `./python/sensor.py`: Start a long-running process emulating a sensor. It waits for subscriptions to itself and publishes sensor data
  * `./python/subscribeToSensor.py`: Generate a subscription to a sensor - this triggers the actual data collection on the sensor via the smart contract.
  * `./python/sensorDataPinning.py`: Demonstration of IPFS-based data replication. This is a long-running script waiting for the publication of any event including an IPFS hash and then pins this hash. Pinning a hash makes IPFS replicate this file to the local node.
  * 
* `./demo/`: Tmux-based demo script. See https://blog.dbi-services.com/using-tmux-for-semi-interactive-demos/
  * `./demo/setup-demo.sh`: Shell-script to set up a demo execution of the SensorSource system using tmux and alacritty on a mac.
  * `./demo/presentation.yml`: Alacritty configuration for the demo window - bigger font, fullscreen, etc.
  * `./demo/demo-script`: Sequence of tmux commands which are executed line-by-line during the demonstration

## Technical workflow - What happens when?

1. Deploy SensorSource Contract
2. Instantiate SensorSource Contract
3. Create SensorOwner address
4. Create sensor
   1. Create sensor address, aka sensorId
   2. Create & publish sensor meta data on IPFS, convert resulting hash to multi-hash (function, length, data) triple
   3. SensorOwner registers sensorId with meta data multi-hash on contract

5. Create sensor user for sensorId
   1. Requires user address aka SensorUser
   2. Create & publish sensor request list of length X data on IPFS, convert resulting hash to multi-hash triple
   3. SensorUser subscribes to sensorId with sensor request list multi-hash for X entries on contract

6. Activate sensor
   1. Sensor watches for subscription event of its id
   2. For each request, counting down:
      * acquire data
      * bundle into file & publish on IPFS (convert resulting hash to multi-hash triple)
      * SensorId publish result-multi hash with count down on contract

7. Consume data
   1. SensorUser watches for publication of result
   2. Pull result from IPFS

8. Replicate data
   1. Watch for any publication of result
   2. Pin hash on IPFS to replicate it
