pragma solidity ^0.5.2;
// these imports are automatically injected by Remix.
import "remix_tests.sol"; 

import "./SensorSource.sol";

contract registrationTest {
   
    SensorSource sut;
    
    
    bytes32 sensorMetadataHash = bytes32(hex"deadbeef");
    
    function beforeAll () public {
       sut = new SensorSource();
    }
    
    function check1_Registration() public {
        address sensorId = address(0x42);
        
        // registration
        sut.register(sensorId, sensorMetadataHash);
        
        (bool registered, bytes32 hash) = sut.registration(sensorId);
        Assert.ok(registered, "Must be registered");
        Assert.equal(hash, sensorMetadataHash, "Correct meta data hash");
    }
    
    function check2_Subscription() public {
        address sensorId = address(0x43);

        // registration
        sut.register(sensorId, sensorMetadataHash);
        // subscription
        bytes32 requestListHash = bytes32(hex"decafbad");
        uint256 requestCount = uint256(2);
        sut.subscribe(sensorId, requestListHash, requestCount);

        Assert.ok(true, "");
    }
    
    function check3_RejectNonSensorIdPublication() public {
        address sensorId = address(0x44); 
        
        // registration
        sut.register(sensorId, sensorMetadataHash);
        
        // subscription
        bytes32 requestListHash = bytes32(hex"decafbad");
        uint256 requestCount = uint256(2);
        sut.subscribe(sensorId, requestListHash, requestCount);
        
        // publication should fail
        Assert.ok(!sut.publish(sensorId, bytes32(hex"d0d0"), 2), "Contract address should not be able to publish as sensorId");
    }

    function check4_MainFlow() public {
        address sensorId = address(this); 
        
        // registration
        sut.register(sensorId, sensorMetadataHash);
        
        // subscription
        bytes32 requestListHash = bytes32(hex"decafbad");
        uint256 requestCount = uint256(2);
        sut.subscribe(sensorId, requestListHash, requestCount);

        // publication 1 succeeds
        Assert.ok(sut.publish(sensorId, bytes32(hex"d0d0"), 2), "Publication");
        
        // publication 2 succeeds
        Assert.ok(sut.publish(sensorId, bytes32(hex"d1d1"), 1), "Last publication");
        
        // publication 3 failes
        Assert.ok(!sut.publish(sensorId, bytes32(hex"d2d2"), 0), "No more publications");
    }
}
