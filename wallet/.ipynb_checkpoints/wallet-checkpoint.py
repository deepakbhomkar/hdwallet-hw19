import subprocess
import json

from dotenv import load_dotenv
import os

from constants import *

from web3 import Web3
import web3

from eth_account import Account

import bit
from bit.network import NetworkAPI

#from web3.middleware import geth_poa_middleware
#w3.middleware_onion.inject(geth_poa_middleware, layer=0)

load_dotenv()

#mnemonic = "neutral canal release coral negative depth hamster total arm session forget father"
mnemonic = os.getenv("MNEMONIC", 'online screen patch leaf unfold sunset forest beyond infant galaxy swarm swarm weekend elephant again')

#for windows users
#command = 'php derive -g --mnemonic="neutral canal release coral negative depth hamster total arm session forget father" --cols=path,address,privkey,pubkey --format=json'
# for mac users
#command = './derive -g --mnemonic="neutral canal release coral negative depth hamster total arm session forget father" --cols=path,address,privkey,pubkey --format=json'

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

def derive_wallets(mnemonic, coin, numderive):
    command = f'php derive -g --mnemonic="{mnemonic}" --cols=path,address,privkey,pubkey --coin="{coin}" --numderive={numderive} --format=json'

#    print(command)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    accounts = json.loads(output)
    return(accounts)

coins = {
    'btc-test': derive_wallets(mnemonic, BTCTEST, '3'), 
    'eth': derive_wallets(mnemonic, ETH, '3')
}

def priv_key_to_account(coin, priv_key):
    if coin == 'btc-test':
        return bit.PrivateKeyTestnet(priv_key)
    if coin == 'eth':
        return Account.privateKeyToAccount(priv_key)
    
def create_tx(coin, account, to, amount):
    if coin == 'eth':
        gasEstimate = w3.eth.estimateGas({"from": account.address, "to": to, "value": amount})
        return {
        "to": to,
        "from": account.address,
        "value": amount,
        "gas": gasEstimate,            
        "gasPrice": w3.eth.gasPrice,
        "nonce": w3.eth.getTransactionCount(account.address),
        "chainId": w3.eth.chainId
        }
    if coin == 'btc-test':
        return bit.PrivateKeyTestnet.prepare_transaction(account.address, [(to.address, amount, BTC)])

def send_tx(coin, account, to, amount):
    raw_tx=create_tx(coin, account, to, amount)
    if coin == 'eth':
        signed = account.sign_transaction(raw_tx)
        return w3.eth.sendRawTransaction(signed.rawTransaction)
    if coin == 'btc-test':
        signed = account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed)    

#BTC TEST send transaction
account_one = priv_key_to_account(BTCTEST, coins[BTCTEST][0]['privkey'])
account_two = priv_key_to_account(BTCTEST, coins[BTCTEST][1]['privkey'])

#ETH TEST send transcation
account_one = priv_key_to_account(ETH, coins[ETH][0]['privkey'])
account_two = priv_key_to_account(ETH, coins[ETH][1]['privkey'])

#send_tx(BTCTEST, account_one, account_two, 0.00001)
send_tx(ETH, account_one, '0x12f9d4Eda8980421f96985456b5DeA6b9eDFB069', 1000000000000000000)

#print(send_tx(ETH, eth_accounts["account_01"], eth_accounts["account_02"], 200000000000000))