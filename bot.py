from web3 import Web3
from dotenv import load_dotenv
import asyncio
import random
import time
import sys
import os
import json
from rich.console import Console
from rich.table import Table

# Initialize rich console
console = Console()

# Load environment variables
load_dotenv()

# File to store persistent transaction count (from previous script, kept for consistency)
CONFIG_FILE = "satsuma_config.json"

# === Animated Banner ===
def display_banner():
    banner_text = """
██╗  ██╗ ██████╗ ███╗   ██╗████████╗ ██████╗ ██╗     
██║ ██╔╝██╔═══██╗████╗  ██║╚══██╔══╝██╔═══██╗██║     
█████╔╝ ██║   ██║██╔██╗ ██║   ██║   ██║   ██║██║     
██╔═██╗ ██║   ██║██║╚██╗██║   ██║   ██║   ██║██║     
██║  ██╗╚██████╔╝██║ ╚████║   ██║   ╚██████╔╝███████╗
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚══════╝
    """
    console.print(f"[bold cyan]{banner_text}[/bold cyan]", justify="center")
    console.print(f"[bold green]L E T S - F U C K - T H I S - T E S T N E T [/bold green]", justify="center")
    console.print("-" * 50, style="green", justify="center")
    for _ in range(3):
        console.print(f"[yellow]> Initializing{'.' * (_ % 4)}[/yellow]", justify="center", end="\r")
        time.sleep(0.3)
    console.print(" " * 50, end="\r")
    console.print(f"[green]+ Satsuma & Nectra Bot - CREATED BY Alloidn[/green]", justify="center")
    console.print("-" * 50, style="green", justify="center")

# === CLI Menu ===
def display_menu():
    table = Table(title="[bold blue]Satsuma & Nectra Bot Menu[/bold blue]", style="green", title_justify="center", show_header=False, expand=True)
    table.add_column(justify="center", style="cyan")
    
    options = [
        "1. Borrow NUSD with cBTC (Nectra)",
        "2. Deposit NUSD (Nectra)",
        "3. Swap cBTC/WCBTC to NUSD (Satsuma)",
        "4. Add LP for USDC (Satsuma)",
        "5. Convert SUMA to veSUMA (Satsuma)",
        "6. Stake veSUMA (Satsuma)",
        "7. Claim LP Reward (Satsuma)", # New option
        "8. Run All Features",           # New option
        "9. Exit"
    ]
    
    for opt in options:
        table.add_row(opt)
    
    console.print(table)
    choice = console.input("[bold magenta]> Select option (1-9): [/bold magenta]")
    return choice

# Load or initialize user settings (from previous script, adapted)
def load_user_settings():
    user_settings = {
        "transaction_count": 0, # This was from the previous script's auto-swap. Not directly used for new functions.
        "current_round": 0
    }
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                user_settings["transaction_count"] = data.get("transaction_count", 0)
                # console.print(f"[green]+ Loaded saved transaction count: {user_settings['transaction_count']}[/green]")
    except Exception as e:
        console.print(f"[red]- Error loading settings: {str(e)}[/red]")
    return user_settings

# Save transaction count to file (from previous script, adapted)
def save_transaction_count(count):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"transaction_count": count}, f)
        console.print(f"[green]+ Transaction count {count} saved successfully[/green]")
    except Exception as e:
        console.print(f"[red]- Error saving transaction count: {str(e)}[/red]")

# Load configuration from .env and add new contract addresses
def load_config():
    display_banner()
    console.print("[yellow]> Loading configuration...[/yellow]", justify="center")
    
    config = {
        "rpc": "[https://rpc.testnet.citrea.xyz](https://rpc.testnet.citrea.xyz)",
        "chain_id": 5115,
        "symbol": "cBTC",
        "explorer": "[https://explorer.testnet.citrea.xyz](https://explorer.testnet.citrea.xyz)",
        # Satsuma Exchange Contracts (from previous script and user's new data)
        "satsuma_swap_router_address": Web3.to_checksum_address("0x3012e9049d05b4b5369d690114d5a5861ebb85cb"), # Contract for swaps
        "satsuma_lp_manager_address": Web3.to_checksum_address("0xcA3534C15Cc22535BF880Ba204c69340f813730b"), # Contract for adding LP
        "satsuma_lp_reward_contract_address": Web3.to_checksum_address("0x69D57B9D705eaD73a5d2f2476C30c55bD755cc2F"), # New LP Reward Contract
        "satsuma_pool_address": Web3.to_checksum_address("0x080c376e6aB309fF1a861e1c3F91F27b8D4f1443"), # Example pool address (from previous script)

        # Nectra Contracts
        "nectra_borrow_contract_address": Web3.to_checksum_address("0x6cDC594d5A135d0307aee3449023A42385422355"),
        "nectra_deposit_contract_address": Web3.to_checksum_address("0x2e8ff07d4F29DA47209a58AD66845F7c290E78fD"),

        # Token Addresses (updated based on user's new data)
        "usdc_address": Web3.to_checksum_address("0x36c16eaC6B0Ba6c50f494914ff015fCa95B7835F"),
        "wcbtc_address": Web3.to_checksum_address("0x8d0c9d1c17ae5e40fff9be350f57840e9e66cd93"),
        "nusd_address": Web3.to_checksum_address("0x9B28B690550522608890C3C7e63c0b4A7eBab9AA"),
        "suma_address": Web3.to_checksum_address("0xdE4251dd68e1aD5865b14Dd527E54018767Af58a"), # Using address from previous script due to user's provided SUMA address being same as USDC.
        "vesuma_address": Web3.to_checksum_address("0x97a4f684620D578312Dc9fFBc4b0EbD8E804ab4a"),
        
        # Staking and Voting Contracts (updated based on user's new data)
        "staking_contract_address": Web3.to_checksum_address("0x22625aDDDcD0e6D981312f6c6E2DBb0003863A90"),
        "voting_contract_address": Web3.to_checksum_address("0x1234567890123456789012345678901234567890"), # Placeholder, user didn't provide new voting contract
        "gauge_address": Web3.to_checksum_address("0x1234567890123456789012345678901234567890") # Placeholder, user didn't provide new gauge address
    }

    return config

# Initialize Web3 provider
def initialize_provider(config):
    try:
        w3 = Web3(Web3.HTTPProvider(config["rpc"]))
        if not w3.is_connected():
            raise Exception("Failed to connect to RPC")
        console.print(f"[green]+ Connected to {config['rpc']} (Chain ID: {config['chain_id']})[/green]")
        return w3
    except Exception as e:
        console.print(f"[red]- Provider initialization error: {str(e)}[/red]")
        sys.exit(1)

# Load private keys from environment variables
def get_private_keys():
    private_keys = []
    i = 1
    while True:
        key_name = f"PRIVATE_KEY_{i}"
        key = os.getenv(key_name)
        if key:
            try:
                Web3().eth.account.from_key(key)
                private_keys.append(key)
                console.print(f"[green]+ Loaded private key for {key_name}[/green]")
            except Exception as e:
                console.print(f"[red]- Invalid private key for {key_name}: {str(e)}[/red]")
        else:
            break
        i += 1

    if not private_keys:
        console.print("[red]- No private keys found in .env file (e.g., PRIVATE_KEY_1, PRIVATE_KEY_2, ...)[/red]")
        sys.exit(1)
        
    console.print(f"[green]+ Successfully loaded {len(private_keys)} private key(s)[/green]")
    return private_keys

# ERC20 ABI (minimal for approve and balanceOf)
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    }
]

# veSUMA ABI (from previous script)
VESUMA_ABI = [
    {
        "name": "create_lock",
        "inputs": [
            {"name": "_value", "type": "uint256"},
            {"name": "_unlock_time", "type": "uint256"}
        ],
        "outputs": [],
        "type": "function"
    },
    {
        "name": "increase_amount",
        "inputs": [
            {"name": "_value", "type": "uint256"}
        ],
        "outputs": [],
        "type": "function"
    },
    {
        "name": "increase_unlock_time",
        "inputs": [
            {"name": "_unlock_time", "type": "uint256"}
        ],
        "outputs": [],
        "type": "function"
    }
]

# Staking ABI (from previous script)
STAKING_ABI = [
    {
        "name": "stake",
        "inputs": [
            {"name": "_amount", "type": "uint256"}
        ],
        "outputs": [],
        "type": "function"
    },
    {
        "name": "withdraw",
        "inputs": [
            {"name": "_amount", "type": "uint256"}
        ],
        "outputs": [],
        "type": "function"
    }
]

# === Helper Function to Send Custom Raw Transactions ===
async def send_custom_transaction(w3, config, account, to_address, data_hex, value_wei, gas_limit, gas_price_wei, description="Transaction"):
    try:
        nonce = w3.eth.get_transaction_count(account.address)
        console.print(f"[yellow]> Preparing {description} for {account.address} with nonce {nonce}[/yellow]")

        tx = {
            "from": account.address,
            "to": to_address,
            "data": data_hex,
            "value": value_wei,
            "gas": gas_limit,
            "gasPrice": gas_price_wei,
            "nonce": nonce,
            "chainId": config["chain_id"]
        }

        console.print(f"[yellow]> Signing {description} transaction...[/yellow]")
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=account.key)
        
        console.print(f"[yellow]> Sending {description} transaction...[/yellow]")
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        console.print(f"[yellow]> Waiting for {description} confirmation... Tx Hash: {tx_hash.hex()}[/yellow]")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt["status"] == 1:
            console.print(f"[green]+ {description} successful! Tx: {config['explorer']}/tx/{tx_hash.hex()}[/green]")
            return {"success": True, "tx_hash": tx_hash.hex()}
        else:
            console.print(f"[red]- {description} failed! Tx: {config['explorer']}/tx/{tx_hash.hex()}[/red]")
            console.print(f"[cyan]Transaction receipt: {receipt}[/cyan]")
            return {"success": False, "tx_hash": tx_hash.hex(), "receipt": receipt}
    except Exception as e:
        console.print(f"[red]- Error during {description} for {account.address}: {str(e)}[/red]")
        return {"success": False, "error": str(e)}

async def approve_token(w3, config, account, token_address, spender_address, amount):
    try:
        token_contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
        
        allowance = token_contract.functions.allowance(account.address, spender_address).call()
        if allowance >= amount:
            console.print(f"[green]+ Sufficient token allowance ({allowance / (10**18 if token_address != config['usdc_address'] else 10**6):.6f}) already exists for {token_address} to {spender_address}[/green]")
            return {"success": True}

        nonce = w3.eth.get_transaction_count(account.address)
        console.print(f"[yellow]> Approving {amount / (10**18 if token_address != config['usdc_address'] else 10**6):.6f} token {token_address} for {spender_address} with nonce {nonce}[/yellow]")

        approve_tx = token_contract.functions.approve(spender_address, amount).build_transaction({
            "from": account.address,
            "gas": 100000, # Standard gas limit for approval
            "gasPrice": w3.eth.gas_price, # Use dynamic gas price
            "nonce": nonce,
            "chainId": config["chain_id"]
        })

        signed_tx = w3.eth.account.sign_transaction(approve_tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        console.print("[yellow]> Waiting for approval transaction confirmation...[/yellow]")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt["status"] == 1:
            console.print(f"[green]+ Token approval successful! Tx: {config['explorer']}/tx/{tx_hash.hex()}[/green]")
            return {"success": True}
        else:
            console.print(f"[red]- Token approval transaction failed! Tx: {config['explorer']}/tx/{tx_hash.hex()}[/red]")
            return {"success": False}
    except Exception as e:
        console.print(f"[red]- Token approval error for {account.address}: {str(e)}[/red]")
        return {"success": False, "error": str(e)}

# === Nectra Functions ===
async def borrow_nusd_with_cbtc(w3, config, private_key):
    account = w3.eth.account.from_key(private_key)
    console.print(f"\n[blue]=== Borrowing NUSD with cBTC for: {account.address} ===[/blue]")

    # Transaction details from user's provided data
    to_address = config["nectra_borrow_contract_address"]
    data_hex = "0xc5dbe83f000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000038d7ea4c68000000000000000000000000000000000000000000000000002b5e3af16b188000000000000000000000000000000000000000000000000000000b1a2bc2ec5000000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000000"
    value_wei = 0x38d7ea4c68000 # 0.0001 cBTC in wei (from user's data)
    gas_limit = 0xa85af # from user's data
    gas_price_wei = 0xb71b78 # from user's data

    await send_custom_transaction(w3, config, account, to_address, data_hex, value_wei, gas_limit, gas_price_wei, "Borrow NUSD")

async def deposit_nusd(w3, config, private_key):
    account = w3.eth.account.from_key(private_key)
    console.print(f"\n[blue]=== Depositing NUSD for: {account.address} ===[/blue]")

    # Transaction details from user's provided data
    to_address = config["nectra_deposit_contract_address"]
    data_hex = "0xb6b55f25000000000000000000000000000000000000000000000002b5e3af16b1880000" # 500 NUSD (500 * 10**18)
    value_wei = 0x0
    gas_limit = 0x493e0 # from user's data
    gas_price_wei = 0xb71b78 # from user's data

    # NUSD approval for the deposit contract
    deposit_amount_wei = 0x2b5e3af16b1880000 # 500 NUSD
    approval_result = await approve_token(w3, config, account, config["nusd_address"], to_address, deposit_amount_wei)
    if not approval_result["success"]:
        console.print("[red]- NUSD approval failed. Aborting NUSD deposit.[/red]")
        return

    await send_custom_transaction(w3, config, account, to_address, data_hex, value_wei, gas_limit, gas_price_wei, "Deposit NUSD")

# === Satsuma Functions ===
async def swap_cbtc_to_nusd(w3, config, private_key):
    account = w3.eth.account.from_key(private_key)
    console.print(f"\n[blue]=== Swapping cBTC/WCBTC to NUSD for: {account.address} ===[/blue]")

    # Transaction details from user's provided data
    to_address = config["satsuma_swap_router_address"]
    data_hex = "0xac9650d800000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000001041679c7920000000000000000000000008d0c9d1c17ae5e40fff9be350f57840e9e66cd930000000000000000000000009b28b690550522608890c3c7e63c0b4a7ebab9aa000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007f8ec2b79b7a1998fd0b21a4668b0cf1ca72c02000000000000000000000000000000000000000000000000000001981a0a6fd500000000000000000000000000000000000000000000000000005af3107a4000000000000000000000000000000000000000000000000000643cc1f269d293d9000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    value_wei = 0x5af3107a4000 # 0.0001 cBTC in wei (from user's data)
    gas_limit = 0x52a19 # from user's data
    gas_price_wei = 0xb71b78 # from user's data

    # The data implies a WCBTC -> NUSD swap. Need to approve WCBTC for the router.
    # The amount to approve is 0.1 WCBTC (from the data: 0x1981a0a6fd5)
    wcbtc_amount_in_data = 0x1981a0a6fd5
    approval_result = await approve_token(w3, config, account, config["wcbtc_address"], to_address, wcbtc_amount_in_data)
    if not approval_result["success"]:
        console.print("[red]- WCBTC approval failed. Aborting swap.[/red]")
        return

    await send_custom_transaction(w3, config, account, to_address, data_hex, value_wei, gas_limit, gas_price_wei, "Swap cBTC/WCBTC to NUSD")

async def add_lp_satsuma(w3, config, private_key):
    account = w3.eth.account.from_key(private_key)
    console.print(f"\n[blue]=== Adding LP for USDC on Satsuma for: {account.address} ===[/blue]")

    # Transaction details from user's provided data
    to_address = config["satsuma_lp_manager_address"]
    data_hex = "0x5d123e3f00000000000000000000000037b9f4994928ca0a4a98c85ed5ad5335b2c47b330000000000000000000000005b4b1f40cea75f3b7e4df178ad1b1804d82491d900000000000000000000000036c16eac6b0ba6c50f494914ff015fca95b7835f000000000000000000000000000000000000000000000000000000000098968000000000000000000000000000000000000000000000000001b3c23249b2617f00000000000000000000000007f8ec2b79b7a1998fd0b21a4668b0cf1ca72c02"
    value_wei = 0x0
    gas_limit = 0x89030 # from user's data
    gas_price_wei = 0xb71b78 # from user's data

    # The data implies adding 10 USDC (0x989680)
    usdc_amount_in_data = 0x989680 # 10 USDC (10 * 10**6)
    approval_result = await approve_token(w3, config, account, config["usdc_address"], to_address, usdc_amount_in_data)
    if not approval_result["success"]:
        console.print("[red]- USDC approval failed. Aborting LP add.[/red]")
        return

    await send_custom_transaction(w3, config, account, to_address, data_hex, value_wei, gas_limit, gas_price_wei, "Add LP")

async def convert_suma_to_vesuma(w3, config, private_key):
    account = w3.eth.account.from_key(private_key)
    console.print(f"\n[blue]=== Converting SUMA to veSUMA for: {account.address} ===[/blue]")

    # Transaction details from user's provided data
    to_address = config["vesuma_address"]
    data_hex = "0x12e82674000000000000000000000000000000000000000000000000016345785d8a0000" # 0.1 SUMA (0.1 * 10**18)
    value_wei = 0x0
    gas_limit = 0x241f8 # from user's data
    gas_price_wei = 0xb71b78 # from user's data

    # Amount to convert is 0.1 SUMA
    suma_amount_in_data = 0x16345785d8a0000 # 0.1 SUMA (0.1 * 10**18)
    approval_result = await approve_token(w3, config, account, config["suma_address"], to_address, suma_amount_in_data)
    if not approval_result["success"]:
        console.print("[red]- SUMA approval failed. Aborting conversion to veSUMA.[/red]")
        return

    await send_custom_transaction(w3, config, account, to_address, data_hex, value_wei, gas_limit, gas_price_wei, "Convert SUMA to veSUMA")

async def stake_vesuma(w3, config, private_key):
    account = w3.eth.account.from_key(private_key)
    console.print(f"\n[blue]=== Staking veSUMA for: {account.address} ===[/blue]")

    # Transaction details from user's provided data
    to_address = config["staking_contract_address"]
    data_hex = "0xb6b55f25000000000000000000000000000000000000000000000000016345785d8a0000" # 0.1 veSUMA (0.1 * 10**18)
    value_wei = 0x0
    gas_limit = 0x38eb6 # from user's data
    gas_price_wei = 0xb71b78 # from user's data

    # Amount to stake is 0.1 veSUMA
    vesuma_amount_in_data = 0x16345785d8a0000 # 0.1 veSUMA (0.1 * 10**18)
    approval_result = await approve_token(w3, config, account, config["vesuma_address"], to_address, vesuma_amount_in_data)
    if not approval_result["success"]:
        console.print("[red]- veSUMA approval failed. Aborting staking.[/red]")
        return

    await send_custom_transaction(w3, config, account, to_address, data_hex, value_wei, gas_limit, gas_price_wei, "Stake veSUMA")

async def claim_lp_reward(w3, config, private_key):
    account = w3.eth.account.from_key(private_key)
    console.print(f"\n[blue]=== Claiming LP Reward for: {account.address} ===[/blue]")

    # Transaction details from user's provided data
    to_address = config["satsuma_lp_reward_contract_address"]
    data_hex = "0xfc6f7865000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007f8ec2b79b7a1998fd0b21a4668b0cf1ca72c0200000000000000000000000000000000ffffffffffffffffffffffffffffffff00000000000000000000000000000000ffffffffffffffffffffffffffffffff"
    value_wei = 0x0
    gas_limit = 0x1e8480 # from user's data
    gas_price_wei = 0xb71b78 # from user's data

    await send_custom_transaction(w3, config, account, to_address, data_hex, value_wei, gas_limit, gas_price_wei, "Claim LP Reward")

async def run_all_features(w3, config, private_keys):
    console.print(f"\n[bold green]=== Running All Features for All Accounts ===[/bold green]")
    for i, private_key in enumerate(private_keys):
        account = w3.eth.account.from_key(private_key)
        console.print(f"\n[bold cyan]--- Processing all features for Account {i+1}: {account.address} ---[/bold cyan]")

        # Nectra Actions
        await borrow_nusd_with_cbtc(w3, config, private_key)
        await asyncio.sleep(random.uniform(10, 20)) # Delay between actions
        await deposit_nusd(w3, config, private_key)
        await asyncio.sleep(random.uniform(10, 20))

        # Satsuma Actions
        await swap_cbtc_to_nusd(w3, config, private_key)
        await asyncio.sleep(random.uniform(10, 20))
        await add_lp_satsuma(w3, config, private_key)
        await asyncio.sleep(random.uniform(10, 20))
        await convert_suma_to_vesuma(w3, config, private_key)
        await asyncio.sleep(random.uniform(10, 20))
        await stake_vesuma(w3, config, private_key)
        await asyncio.sleep(random.uniform(10, 20))
        await claim_lp_reward(w3, config, private_key)
        await asyncio.sleep(random.uniform(10, 20)) # Delay after last action for this account

        console.print(f"\n[bold green]--- Finished all features for Account {i+1} ---[/bold green]")
        if i < len(private_keys) - 1:
            console.print("[yellow]> Waiting 60 seconds before processing next account...[/yellow]")
            await asyncio.sleep(60) # Longer delay between different accounts

    console.print(f"\n[bold green]=== All Features Run Completed for All Accounts! ===[/bold green]")


async def main():
    try:
        config = load_config()
        w3 = initialize_provider(config)
        private_keys = get_private_keys()
        user_settings = load_user_settings() # Not directly used for new functions, but kept for consistency

        while True:
            choice = display_menu()
            try:
                option = int(choice)
                if option == 9: # Updated exit option
                    console.print("[yellow]> Exiting Satsuma & Nectra Bot...[/yellow]")
                    sys.exit(0)
                elif option == 1:
                    for private_key in private_keys:
                        await borrow_nusd_with_cbtc(w3, config, private_key)
                        await asyncio.sleep(random.uniform(5, 10)) # Small delay between accounts
                elif option == 2:
                    for private_key in private_keys:
                        await deposit_nusd(w3, config, private_key)
                        await asyncio.sleep(random.uniform(5, 10))
                elif option == 3:
                    for private_key in private_keys:
                        await swap_cbtc_to_nusd(w3, config, private_key)
                        await asyncio.sleep(random.uniform(5, 10))
                elif option == 4:
                    for private_key in private_keys:
                        await add_lp_satsuma(w3, config, private_key)
                        await asyncio.sleep(random.uniform(5, 10))
                elif option == 5:
                    for private_key in private_keys:
                        await convert_suma_to_vesuma(w3, config, private_key)
                        await asyncio.sleep(random.uniform(5, 10))
                elif option == 6:
                    for private_key in private_keys:
                        await stake_vesuma(w3, config, private_key)
                        await asyncio.sleep(random.uniform(5, 10))
                elif option == 7: # New option for Claim LP Reward
                    for private_key in private_keys:
                        await claim_lp_reward(w3, config, private_key)
                        await asyncio.sleep(random.uniform(5, 10))
                elif option == 8: # New option for Run All Features
                    await run_all_features(w3, config, private_keys)
                else:
                    console.print("[red]- Invalid option. Please select 1-9.[/red]")
            except ValueError:
                console.print("[red]- Invalid input. Please enter a number.[/red]")
            except Exception as e:
                console.print(f"[red]- Error in main loop: {str(e)}[/red]")
                console.print("[yellow]> Waiting 30 seconds before retry...[/yellow]")
                await asyncio.sleep(30)

    except Exception as e:
        console.print(f"[red]- Main execution error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("[yellow]> Program interrupted. Exiting...[/yellow]")
        sys.exit(0)
