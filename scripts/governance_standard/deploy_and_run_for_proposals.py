from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account
from brownie import (
    GovernorContract,
    CBlockToken,
    GovernanceTimeLock,
    Proposals,
    Contract,
    config,
    network,
    accounts,
    chain,
)
from web3 import Web3, constants

# Governor Contract
QUORUM_PERCENTAGE = 4
# VOTING_PERIOD = 45818  # 1 week - more traditional.
# You might have different periods for different kinds of proposals
VOTING_PERIOD = 5  # 5 blocks
VOTING_DELAY = 1  # 1 block

# Timelock
# MIN_DELAY = 3600  # 1 hour - more traditional
MIN_DELAY = 1  # 1 seconds


# New Proposal
PROPOSAL_DESCRIPTION = "Auditor 1: I am pushing a new lot, Vote for it!"
NEW_STORE_PROPOSAL = "Lot #1 is being pushed"


def deploy_governor():
    account = get_account()
    governance_token = (
        CBlockToken.deploy(
            {"from": account},
            publish_source=config["networks"][network.show_active()].get(
                "verify", False
            ),
        )
        if len(CBlockToken) <= 0
        else CBlockToken[-1]
    )
    governance_token.delegate(account, {"from": account})
    print(f"Checkpoints: {governance_token.numCheckpoints(account)}")
    ## typo?
    ##governance_time_lock = governance_time_lock = (
    governance_time_lock = (
        GovernanceTimeLock.deploy(
            MIN_DELAY,
            [],
            [],
            {"from": account},
            publish_source=config["networks"][network.show_active()].get(
                "verify", False
            ),
        )
        if len(GovernanceTimeLock) <= 0
        else GovernanceTimeLock[-1]
    )
    governor = GovernorContract.deploy(
        governance_token.address,
        governance_time_lock.address,
        QUORUM_PERCENTAGE,
        VOTING_PERIOD,
        VOTING_DELAY,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    # Now, we set the roles...
    # Multicall would be great here ;)
    proposer_role = governance_time_lock.PROPOSER_ROLE()
    executor_role = governance_time_lock.EXECUTOR_ROLE()
    timelock_admin_role = governance_time_lock.TIMELOCK_ADMIN_ROLE()
    governance_time_lock.grantRole(proposer_role, governor, {"from": account})
    governance_time_lock.grantRole(
        executor_role, constants.ADDRESS_ZERO, {"from": account}
    )
    tx = governance_time_lock.revokeRole(
        timelock_admin_role, account, {"from": account}
    )
    tx.wait(1)
    # Guess what? Now you can't do anything!
    # governance_time_lock.grantRole(timelock_admin_role, account, {"from": account})



# NEW FOR PORPOSAL:



def deploy_Proposals_to_be_governed():
    account = get_account()
    proposals = Proposals.deploy({"from": account})
    tx = proposals.transferOwnership(GovernanceTimeLock[-1], {"from": account})
    tx.wait(1)









# NEW FOR PORPOSAL:









def propose(issue_proposal):
    account = get_account()

    args = (issue_proposal,)

    encoded_function = Contract.from_abi("Proposals", Proposals[-1], Proposals.abi).setProposal.encode_input(
        *args
    )
    print(encoded_function)
    propose_tx = GovernorContract[-1].propose(
        [Proposals[-1].address],
        [0],
        [encoded_function],
        PROPOSAL_DESCRIPTION,
        {"from": account},
    )
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        tx = account.transfer(accounts[0], "0 ether")
        tx.wait(1)
    propose_tx.wait(2)  # We wait 2 blocks to include the voting delay
    # This will return the proposal ID, brownie.exceptions.EventLookupError will be 
    # thrown if ProposalCreated event is not emitted.
    proposal_id = propose_tx.events['ProposalCreated']['proposalId'] # you could also do `propose_tx.return_value` if your node allows
    print(f"Proposal state {GovernorContract[-1].state(proposal_id)}")
    print(
        f"Proposal snapshot {GovernorContract[-1].proposalSnapshot(proposal_id)}"
    )
    print(
        f"Proposal deadline {GovernorContract[-1].proposalDeadline(proposal_id)}"
    )
    return proposal_id


# Can be done through a UI
def vote(proposal_id: int, vote: int):
    # 0 = Against, 1 = For, 2 = Abstain for this example
    # you can all the #COUNTING_MODE() function to see how to vote otherwise
    print(f"voting yes on {proposal_id}")
    account = get_account()
    tx = GovernorContract[-1].castVoteWithReason(
        proposal_id, vote, "I am the auditor for this Lot. I am proposing this Lot for being listed on the Protocol.", {"from": account}
    )
    tx.wait(1)
    print(tx.events["VoteCast"])



def queue_and_execute(issue_proposal):
    print("queue_and_execute")
    account = get_account()
    # time.sleep(VOTING_PERIOD + 1)
    # we need to explicity give it everything, including the description hash
    # it gets the proposal id like so:
    # uint256 proposalId = hashProposal(targets, values, calldatas, descriptionHash);
    # It's nearlly exactly the same as the `propose` function, but we hash the description
    args = (issue_proposal,)
    encoded_function = Contract.from_abi("Proposals", Proposals[-1], Proposals.abi).setProposal.encode_input(
        *args
    )
    # this is the same as ethers.utils.id(description)
    description_hash = Web3.keccak(text=PROPOSAL_DESCRIPTION).hex()
    tx = GovernorContract[-1].queue(
        [Proposals[-1].address],
        [0],
        [encoded_function],
        description_hash,
        {"from": account},
    )
    print("before tx.wait 1")
    tx.wait(1)
    print("after tx.wait 1")
    tx = GovernorContract[-1].execute(
        [Proposals[-1].address],
        [0],
        [encoded_function],
        description_hash,
        {"from": account},
    )
    print("before second tx.wait 1")
    tx.wait(1)
    print("after second tx.wait 1")
    print(Proposals[-1].getProposal())


def move_blocks(amount):
    print("move_blocks", amount)
    for block in range(amount):
        get_account().transfer(get_account(), "0 ether")
    print(chain.height)









# NEW FOR Proposals









def main():
    deploy_governor()
    deploy_Proposals_to_be_governed()
    proposal_id = propose(NEW_STORE_PROPOSAL)
    print(f"Proposal ID {proposal_id}")
    # We do this just to move the blocks along
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        move_blocks(1)
    vote(proposal_id, 1)
    # Once the voting period is over,
    # if quorum was reached (enough voting power participated)
    # and the majority voted in favor, the proposal is
    # considered successful and can proceed to be executed.
    # To execute we must first `queue` it to pass the timelock
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        move_blocks(VOTING_PERIOD)
    # States: {Pending, Active, Canceled, Defeated, Succeeded, Queued, Expired, Executed }
    print(f" This proposal is currently {GovernorContract[-1].state(proposal_id)}")
    # comment out queue and execute for new proposal
    queue_and_execute(NEW_STORE_PROPOSAL)
