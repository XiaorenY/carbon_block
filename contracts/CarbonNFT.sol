// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract CarbonNFT is ERC721, Ownable, ERC721Burnable {
    uint256 public tokenCounter;

    mapping (uint256 => uint256) public tokenIdToExpectedCarbonCredit;
    // for each token id, burn at expire time
    mapping(uint256 => uint) public tokenIdToExpireTime;
    mapping(uint256 => uint256) public tokenIdToFractionalToken;

    constructor () public ERC721 ("CarbonNFT", "Carbon") {}

    function createCollectible(uint256 expectedCarbondCredit, uint period, uint256 fractionalTokenNumber, string memory tokenURI) public returns (uint256) {
        uint256 newItemId = tokenCounter;
        _safeMint(msg.sender, newItemId);
        //_setTokenURI(newItemId, tokenURI);
        tokenIdToExpectedCarbonCredit[newItemId] = expectedCarbondCredit;
        tokenIdToExpireTime[newItemId] = block.timestamp + period;
        tokenIdToFractionalToken[newItemId] = fractionalTokenNumber;
        tokenCounter = tokenCounter + 1;
        return newItemId;
    }
}