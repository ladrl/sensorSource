pragma solidity >=0.4.22 <0.6.0;
pragma experimental ABIEncoderV2;
contract SensorSource {

    constructor () public {
        owner = msg.sender;
    }
    address owner;

    struct MultiHash {
        uint8 hashFunction;
        uint8 lengh;
        bytes32 data;
    }

    struct Registration {
        address owner;
        MultiHash metaDataHash;
    }
    event Registered(
        address owner,
        address sensorId,
        uint8 metaDataHashFunction,
        uint8 metaDataHashLength,
        bytes32 metaDataHash
    );
    mapping(address => Registration) registrations;
    function register_native(address sensorId, uint8 hashFunction, uint8 hashLength, bytes32 hashData) public returns (bool) {
        register(sensorId, MultiHash(hashFunction, hashLength, hashData));
    }

    function register(address sensorId, MultiHash memory metaDataHash) public {
        //require(msg.sender == owner, "Only the owner of this sensor source may register sensors");
        //require(registrations[sensorId].owner == address(0), "Sensor is already registered");
        registrations[sensorId].owner = msg.sender;
        registrations[sensorId].metaDataHash = metaDataHash;
        emit Registered(
            msg.sender, 
            sensorId, 
            metaDataHash.hashFunction, 
            metaDataHash.lengh, 
            metaDataHash.data
        );        
    }
    

    struct Subscription {
        MultiHash requestListHash;
        uint256 resultCountDown;
    }
    event Subscribed (
        uint8 metaDataHashFunction,
        uint8 metaDataHashLength,
        bytes32 metaDataHash,
        address sensorId,
        uint256 requestCount
    );
    mapping(address => Subscription) subscriptions;
    function subscribe_native(address sensorId, uint8 hashFunction, uint8 hashLength, bytes32 hashData, uint256 requestCount) public {
        subscribe(sensorId, MultiHash(hashFunction, hashLength, hashData), requestCount);
    }
    // A subscription must pay for the sensor to actually publish the hashes + some benefit for it
    function subscribe(address sensorId, MultiHash memory requestListHash, uint256 requestCount) public {
        require(registrations[sensorId].owner != address(0), "Sensor is not registered");
        subscriptions[sensorId].requestListHash = requestListHash;
        subscriptions[sensorId].resultCountDown = requestCount;
        
        emit Subscribed(
            subscriptions[sensorId].requestListHash.hashFunction,
            subscriptions[sensorId].requestListHash.lengh,
            subscriptions[sensorId].requestListHash.data, 
            sensorId,
            requestCount
        );
    }
    
    event Published(
        address sensorId,
        uint8 metaDataHashFunction,
        uint8 metaDataHashLength,
        bytes32 metaDataHash,
        uint256 entryId
    );
    function publish_native(address sensorId, uint8 hashFunction, uint8 hashLength, bytes32 hashData, uint256 entryId) public {
        publish(sensorId, MultiHash(hashFunction, hashLength, hashData), entryId);
    }
    // Publication should benefit the sensor, eg. there should be money sent to the sensorId to sustain the actual publishing and 
    // maybe a final fulfilment payment
    function publish(address sensorId, MultiHash memory responseHash, uint256 entryId) public returns (bool) {
        require(registrations[sensorId].owner != address(0), "Sensor is not registered");
        bool publisherIsSensor = sensorId == msg.sender;
        bool currentCountDown = subscriptions[sensorId].resultCountDown == entryId;
        bool nonZeroCountDown = subscriptions[sensorId].resultCountDown > 0;
        
        if(publisherIsSensor && currentCountDown && nonZeroCountDown) {
            subscriptions[sensorId].resultCountDown -= 1;
            emit Published(
                sensorId, 
                responseHash.hashFunction,
                responseHash.lengh,
                responseHash.data,
                entryId
            );
            return true;
        } else {
            return false;
        }
    }

    function publication(address sensorId) public view returns (
        bool exists, 
        uint8 hashFunction, 
        uint8 hashLength, 
        bytes32 requestListHash, 
        uint256 nextRequestId
    ) {
        if (subscriptions[sensorId].requestListHash.data != 0) {
            exists = true;
            hashFunction = subscriptions[sensorId].requestListHash.hashFunction;
            hashLength = subscriptions[sensorId].requestListHash.lengh;
            requestListHash = subscriptions[sensorId].requestListHash.data;
            nextRequestId = subscriptions[sensorId].resultCountDown;
        } else {
            exists = false;
        }
    }
    
}