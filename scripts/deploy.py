from brownie import CarbonNFT, accounts, network, config

def main():
    acct = accounts.load('deployment_account')
    print(network.show_active())
    CarbonNFT.deploy({"from": acct})