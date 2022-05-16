from brownie import CarbonNFT, Settings, ERC721VaultFactory, accounts, network, config

def main():
    #acct = accounts.load('deployment_account')
    print("Active network:", network.show_active())
    CarbonNFT.deploy({'from': accounts[0]})
    fraction_num = 100
    collection = CarbonNFT[0].createCollectible(10000, 365, fraction_num)

    Settings.deploy({'from': accounts[0]})
    ERC721VaultFactory.deploy(Settings[0], {'from': accounts[0]})

    CarbonNFT[0].approve(ERC721VaultFactory[0], 0)
    tx = ERC721VaultFactory[0].mint('FractionToken', 'FT', CarbonNFT[0], 0, fraction_num, 50, 2, {'from': accounts[0]})
    print(tx.info())