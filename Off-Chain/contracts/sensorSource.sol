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

    function register_native(address sensorId, uint8 hashFunction, uint8 hashLength, bytes32 hashData) public {
        register(sensorId, MultiHash(hashFunction, hashLength, hashData));
    }

    function register(address sensorId, MultiHash memory metaDataHash) public {
        require(msg.sender == owner);
        require(registrations[sensorId].owner == address(0));
        registrations[sensorId].owner = msg.sender;
        registrations[sensorId].metaDataHash = metaDataHash;
        emit Registered(msg.sender, sensorId, metaDataHash.hashFunction, metaDataHash.lengh, metaDataHash.data);        
    }
    
    function registration(address sensorId) public view returns (bool, bytes32) {
        return (registrations[sensorId].owner != address(0), registrations[sensorId].metaDataHash.data);
    }
    
    struct Subscription {
        MultiHash requestListHash;
        uint256 resultCountDown;
        address subscriber;
    }
    event Subscribed(
        MultiHash requestListHash,
        uint256 requestCount
    );
    mapping(address => Subscription) subscriptions;
    
    function subscribe(address sensorId, bytes32 requestListHash, uint256 requestCount) public {
        require(registrations[sensorId].owner != address(0));
        
        subscriptions[sensorId].requestListHash = MultiHash(0x12, 0x20, requestListHash);
        subscriptions[sensorId].resultCountDown = requestCount;
        subscriptions[sensorId].subscriber = msg.sender;
        
        emit Subscribed(subscriptions[sensorId].requestListHash, requestCount);
    }
    
    event Published(
        address sensorId,
        MultiHash responseHash
    );
    
    function publish(address sensorId, bytes32 responseHash, uint256 entryId) public returns (bool) {
        require(registrations[sensorId].owner != address(0));
        
        bool publisherIsSensor = sensorId == msg.sender;
        bool currentCountDown = subscriptions[sensorId].resultCountDown == entryId;
        bool nonZeroCountDown = subscriptions[sensorId].resultCountDown > 0;
        
        if(publisherIsSensor && currentCountDown && nonZeroCountDown) {
            subscriptions[sensorId].resultCountDown -= 1;
            emit Published(sensorId, MultiHash(0x12, 0x20, responseHash));
            return true;
        } else {
            return false;
        }
    }
    
}