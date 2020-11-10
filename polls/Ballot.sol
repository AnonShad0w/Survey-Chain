// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.5.10;

/** 
 * @title Ballot
 * @dev Implements voting process
 */
 
contract Ballot {
     
    uint256 totalBallots = 0;
     
    mapping(uint256 => Survey) public surveys;
     
    struct Survey {
        uint256 id;
        string choice;
    }
     
    function addBallot(string memory _choice) public {
        incrementBallot();
        surveys[totalBallots] = Survey(totalBallots, _choice);
    }
     
    function incrementBallot() internal {
        totalBallots += 1;
    }
}
