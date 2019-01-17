# Off-Chain workflow

Need Ethereum Node and IPFS Node.

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
