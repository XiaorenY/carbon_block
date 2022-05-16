// contracts/Proposals.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";

contract Proposals is Ownable {
    string proposal = "No proposals Yet";

    // Emitted when a new proposal is created
    event ProposalChanged(string _newproposal);

    // Creates a proposal
    function getProposal() public view returns (string memory) {
        return proposal;
    }

    function setProposal(string memory _newproposal) public onlyOwner {
        proposal = _newproposal;
        emit ProposalChanged(_newproposal);
    }
}

