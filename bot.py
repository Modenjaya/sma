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
███████╗ █████╗ ████████╗███████╗██╗   ██║███╗   ███╗ █████╗ 
██╔════╝██╔══██╗╚══██╔══╝██╔════╝██║   ██║████╗ ████║██╔══██╗
███████╗███████║   ██║   ███████╗██║   ██║██╔████╔██║███████║
╚════██║██╔══██║   ██║   ╚════██║██║   ██║██║╚██╔╝██║██╔══██║
███████║██║  ██║   ██║   ███████║╚██████╔╝██║ ╚═╝ ██║██║  ██║
╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝
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
        "3. Swap cBTC (Citrea Native) to NUSD (Satsuma)",
        "4. Swap USDC to SUMA (Satsuma) - Interactive",
        "5. Swap USDC to WCBTC (Satsuma) - Interactive",
        "6. Add Liquidity (WCBTC + USDC) (Satsuma)",
        "7. Convert SUMA to veSUMA (Satsuma)",
        "8. Stake veSUMA (Satsuma)",
        "9. Claim LP Reward (Satsuma)",
        "10. Run All Features",
        "11. Exit"
    ]
    
    for opt in options:
        table.add_row(opt)
    
    console.print(table)
    choice = console.input("[bold magenta]> Select option (1-11): [/bold magenta]")
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
        "rpc": "https://rpc.testnet.citrea.xyz",
        "chain_id": 5115,
        "symbol": "cBTC",
        "explorer": "https://explorer.testnet.citrea.xyz",
        # Satsuma Exchange Contracts (from previous script and user's new data)
        "satsuma_swap_router_address": Web3.to_checksum_address("0x3012e9049d05b4b5369d690114d5a5861ebb85cb"), # Contract for swaps
        "satsuma_lp_manager_address": Web3.to_checksum_address("0xcA3534C15Cc22535BF880Ba204c69340f813730b"), # Contract for adding LP
        "satsuma_lp_reward_contract_address": Web3.to_checksum_address("0x69D57B9D705eaD73a5d2f2476C30c55bD755cc2F"), # New LP Reward Contract
        # IMPORTANT: This is the address of the USDC/WCBTC pool. Please verify this address on Satsuma.exchange's liquidity page.
        # It was updated based on the URL you provided: https://www.satsuma.exchange/liquidity/0x9aa034631e14e2c7fc01890f8d7b19ab6aed1666/new-position
        "satsuma_pool_address": Web3.to_checksum_address("0x9aa034631e14e2c7fc01890f8d7b19ab6aed1666"), 

        # Nectra Contracts
        "nectra_borrow_contract_address": Web3.to_checksum_address("0x6cDC594d5A135d0307aee3449023A42385422355"),
        "nectra_deposit_contract_address": Web3.to_checksum_address("0x2e8ff07d4F29DA47209a58AD66845F7c290E78fD"),

        # Token Addresses (updated based on user's new data)
        "usdc_address": Web3.to_checksum_address("0x36c16eaC6B0Ba6c50f494914ff015fCa95B7835F"),
        "wcbtc_address": Web3.to_checksum_address("0x8d0c9d1c17ae5e40fff9be350f57840e9e66cd93"),
        "nusd_address": Web3.to_checksum_address("0x9B28B690550522608890C3C7e63c0b4A7eBab9AA"),
        "suma_address": Web3.to_checksum_address("0xdE4251dd68e1aD5865b14Dd527E54018767Af58a"), # CORRECTED SUMA ADDRESS
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

# Swap Router ABI (re-added)
SWAP_ROUTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"name": "tokenIn", "type": "address"},
                    {"name": "tokenOut", "type": "address"},
                    {"name": "deployer", "type": "address"},
                    {"name": "recipient", "type": "address"},
                    {"name": "deadline", "type": "uint256"},
                    {"name": "amountIn", "type": "uint256"},
                    {"name": "amountOutMinimum", "type": "uint256"},
                    {"name": "limitSqrtPrice", "type": "uint160"}
                ],
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "exactInputSingle",
        "outputs": [{"name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "tokenA", "type": "address"},
            {"name": "tokenB", "type": "address"},
            {"name": "deployer", "type": "address"},
            {"name": "recipient", "type": "address"},
            {"name": "amountADesired", "type": "uint256"},
            {"name": "amountBDesired", "type": "uint256"},
            {"name": "amountAMin", "type": "uint256"},
            {"name": "amountBMin", "type": "uint256"},
            {"name": "deadline", "type": "uint256"}
        ],
        "name": "addLiquidity",
        "outputs": [
            {"name": "amountA", "type": "uint256"},
            {"name": "amountB", "type": "uint256"},
            {"name": "liquidity", "type": "uint128"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Algebra Pool ABI (re-added)
ALGEBRA_POOL_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"name": "", "type": "uint128"},
            {"name": "", "type": "uint128"}
        ],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token0",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token1",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "factory",
        "outputs": [{"name": "", "type": "address"}],
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
        # Use 10**6 for USDC and 10**18 for other tokens for correct comparison
        token_decimals = 6 if token_address == config['usdc_address'] else 18
        if allowance >= amount:
            console.print(f"[green]+ Sufficient token allowance ({allowance / (10**token_decimals):.6f}) already exists for {token_address} to {spender_address}[/green]")
            return {"success": True}

        nonce = w3.eth.get_transaction_count(account.address)
        console.print(f"[yellow]> Approving {amount / (10**token_decimals):.6f} token {token_address} for {spender_address} with nonce {nonce}[/yellow]")

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
    console.print(f"\n[blue]=== Swapping cBTC (Citrea Native) to NUSD for: {account.address} ===[/blue]")

    # Transaction details from user's provided data
    to_address = config["satsuma_swap_router_address"]
    data_hex = "0xac9650d800000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000001041679c7920000000000000000000000008d0c9d1c17ae5e40fff9be350f57840e9e66cd930000000000000000000000009b28b690550522608890c3c7e63c0b4a7ebab9aa000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007f8ec2b79b7a1998fd0b21a4668b0cf1ca72c02000000000000000000000000000000000000000000000000000001981a0a6fd500000000000000000000000000000000000000000000000000005af3107a4000000000000000000000000000000000000000000000000000643cc1f269d293d9000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    value_wei = 0x5af3107a4000 # 0.0001 cBTC in wei (from user's data)
    gas_limit = 0x52a19 # from user's data
    gas_price_wei = 0xb71b78 # from user's data

    # No approval needed for native cBTC, it's sent via 'value'
    # The router contract is expected to handle the wrapping of cBTC to WCBTC internally.

    await send_custom_transaction(w3, config, account, to_address, data_hex, value_wei, gas_limit, gas_price_wei, "Swap cBTC to NUSD")

async def swap_usdc_to_suma_interactive(w3, config, private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        console.print(f"[blue]=== Processing interactive USDC to SUMA swap for address: {account.address} ===[/blue]")

        while True:
            try:
                usdc_amount_str = console.input("[bold magenta]> Enter the amount of USDC to swap (e.g., 10.5): [/bold magenta]")
                usdc_amount = float(usdc_amount_str)
                if usdc_amount <= 0:
                    console.print("[red]- Amount must be positive. Please enter a valid number.[/red]")
                    continue
                break
            except ValueError:
                console.print("[red]- Invalid input. Please enter a valid number.[/red]")

        console.print(f"[green]+ Amount to swap: {usdc_amount} USDC[/green]")

        usdc_contract = w3.eth.contract(address=config["usdc_address"], abi=ERC20_ABI)
        suma_contract = w3.eth.contract(address=config["suma_address"], abi=ERC20_ABI)

        usdc_balance = usdc_contract.functions.balanceOf(account.address).call()
        console.print(f"[green]+ Current USDC balance: {usdc_balance / 10**6:.6f} USDC[/green]")

        amount_in_usdc_wei = int(usdc_amount * 10**6) # USDC has 6 decimals
        if usdc_balance < amount_in_usdc_wei:
            console.print(f"[red]- Insufficient USDC balance. Needed: {usdc_amount} USDC, Available: {usdc_balance / 10**6:.6f} USDC[/red]")
            return

        # Approve USDC for the swap router
        approval_result = await approve_token(w3, config, account, config["usdc_address"], config["satsuma_swap_router_address"], amount_in_usdc_wei)
        if not approval_result["success"]:
            console.print("[red]- Skipping swap due to USDC approval failure[/red]")
            return

        swap_router = w3.eth.contract(address=config["satsuma_swap_router_address"], abi=SWAP_ROUTER_ABI)
        deadline = int(time.time()) + 20 * 60 # 20 minutes from now

        # Parameters for exactInputSingle (USDC to SUMA)
        # Using the structure from the provided transaction data, but with dynamic amountIn
        params_usdc_suma = (
            config["usdc_address"], # tokenIn
            config["suma_address"], # tokenOut
            Web3.to_checksum_address("0x0000000000000000000000000000000000000000"), # deployer (as per user's data)
            account.address, # recipient
            deadline,
            amount_in_usdc_wei, # dynamic amount from user input
            0, # amountOutMinimum (set to 0 for simplicity, consider adding slippage)
            0  # limitSqrtPrice (set to 0 for simplicity)
        )

        console.print("[yellow]> Sending USDC -> SUMA transaction...[/yellow]")
        usdc_suma_tx = swap_router.functions.exactInputSingle(params_usdc_suma).build_transaction({
            "from": account.address,
            "value": 0, # Value is 0x0 as per user's provided data
            "gas": 0x1e8480, # Fixed gas limit from user's provided data
            "gasPrice": 0xb71b78, # Fixed gas price from user's provided data
            "nonce": w3.eth.get_transaction_count(account.address),
            "chainId": config["chain_id"]
        })

        signed_tx = w3.eth.account.sign_transaction(usdc_suma_tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        console.print("[yellow]> Waiting for USDC -> SUMA transaction confirmation...[/yellow]")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt["status"] == 1:
            console.print(f"[green]+ USDC -> SUMA swap successful! Tx: {config['explorer']}/tx/{tx_hash.hex()}[/green]")
        else:
            console.print(f"[red]- USDC -> SUMA transaction failed! Tx: {config['explorer']}/tx/{tx_hash.hex()}[/red]")
            console.print(f"[cyan]Transaction receipt: {receipt}[/cyan]")
            return

        # Display SUMA received and veSUMA note
        suma_balance_after_swap = suma_contract.functions.balanceOf(account.address).call()
        console.print(f"[green]+ Current SUMA balance: {suma_balance_after_swap / 10**18:.6f} SUMA[/green]")
        console.print(f"[yellow]Note: To get veSUMA, you need to convert your SUMA using the 'Convert SUMA to veSUMA' option.[/yellow]")

    except Exception as e:
        console.print(f"[red]- Error during USDC to SUMA swap: {str(e)}[/red]")

async def swap_usdc_to_wcbtc_interactive(w3, config, private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        console.print(f"[blue]=== Processing interactive USDC to WCBTC swap for address: {account.address} ===[/blue]")

        while True:
            try:
                usdc_amount_str = console.input("[bold magenta]> Enter the amount of USDC to swap (e.g., 10.0): [/bold magenta]")
                usdc_amount = float(usdc_amount_str)
                if usdc_amount <= 0:
                    console.print("[red]- Amount must be positive. Please enter a valid number.[/red]")
                    continue
                break
            except ValueError:
                console.print("[red]- Invalid input. Please enter a valid number.[/red]")

        console.print(f"[green]+ Amount to swap: {usdc_amount} USDC[/green]")

        usdc_contract = w3.eth.contract(address=config["usdc_address"], abi=ERC20_ABI)
        wcbtc_contract = w3.eth.contract(address=config["wcbtc_address"], abi=ERC20_ABI)

        usdc_balance = usdc_contract.functions.balanceOf(account.address).call()
        console.print(f"[green]+ Current USDC balance: {usdc_balance / 10**6:.6f} USDC[/green]")

        amount_in_usdc_wei = int(usdc_amount * 10**6) # USDC has 6 decimals
        if usdc_balance < amount_in_usdc_wei:
            console.print(f"[red]- Insufficient USDC balance. Needed: {usdc_amount} USDC, Available: {usdc_balance / 10**6:.6f} USDC[/red]")
            return

        # Approve USDC for the swap router
        approval_result = await approve_token(w3, config, account, config["usdc_address"], config["satsuma_swap_router_address"], amount_in_usdc_wei)
        if not approval_result["success"]:
            console.print("[red]- Skipping swap due to USDC approval failure[/red]")
            return

        swap_router = w3.eth.contract(address=config["satsuma_swap_router_address"], abi=SWAP_ROUTER_ABI)
        deadline = int(time.time()) + 20 * 60 # 20 minutes from now

        # Parameters for exactInputSingle (USDC to WCBTC)
        params_usdc_wcbtc = (
            config["usdc_address"], # tokenIn
            config["wcbtc_address"], # tokenOut
            Web3.to_checksum_address("0x0000000000000000000000000000000000000000"), # deployer (as per user's data)
            account.address, # recipient
            deadline,
            amount_in_usdc_wei, # dynamic amount from user input
            0, # amountOutMinimum (set to 0 for simplicity, consider adding slippage)
            0  # limitSqrtPrice (set to 0 for simplicity)
        )

        console.print("[yellow]> Sending USDC -> WCBTC transaction...[/yellow]")
        usdc_wcbtc_tx = swap_router.functions.exactInputSingle(params_usdc_wcbtc).build_transaction({
            "from": account.address,
            "value": 0, # Value is 0x0 as per user's provided data
            "gas": 0x41dec, # Fixed gas limit from user's provided data
            "gasPrice": 0xb71b78, # Fixed gas price from user's provided data
            "nonce": w3.eth.get_transaction_count(account.address),
            "chainId": config["chain_id"]
        })

        signed_tx = w3.eth.account.sign_transaction(usdc_wcbtc_tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        console.print("[yellow]> Waiting for USDC -> WCBTC transaction confirmation...[/yellow]")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt["status"] == 1:
            console.print(f"[green]+ USDC -> WCBTC swap successful! Tx: {config['explorer']}/tx/{tx_hash.hex()}[/green]")
        else:
            console.print(f"[red]- USDC -> WCBTC transaction failed! Tx: {config['explorer']}/tx/{tx_hash.hex()}[/red]")
            console.print(f"[cyan]Transaction receipt: {receipt}[/cyan]")
            return

        # Display WCBTC received
        wcbtc_balance_after_swap = wcbtc_contract.functions.balanceOf(account.address).call()
        console.print(f"[green]+ Current WCBTC balance: {wcbtc_balance_after_swap / 10**18:.6f} WCBTC[/green]")

    except Exception as e:
        console.print(f"[red]- Error during USDC to WCBTC swap: {str(e)}[/red]")

async def wrap_cbtc(w3, config, account, amount_cbtc):
    """
    Wraps native cBTC to WCBTC.
    amount_cbtc: amount in cBTC (e.g., 0.0001)
    """
    try:
        amount_wei = w3.to_wei(amount_cbtc, 'ether') # cBTC has 18 decimals like ETH
        
        console.print(f"\n[blue]=== Wrapping {amount_cbtc} cBTC to WCBTC for: {account.address} ===[/blue]")

        to_address = config["wcbtc_address"] # WCBTC contract address
        data_hex = "0xd0e30db0" # Function selector for deposit() on WETH-like contracts
        value_wei = amount_wei
        gas_limit = 0x14a6f # from user's provided data for wrap
        gas_price_wei = 0xb71b78 # from user's provided data for wrap

        result = await send_custom_transaction(w3, config, account, to_address, data_hex, value_wei, gas_limit, gas_price_wei, "Wrap cBTC to WCBTC")
        return result
    except Exception as e:
        console.print(f"[red]- Error wrapping cBTC: {str(e)}[/red]")
        return {"success": False, "error": str(e)}

async def add_lp_satsuma(w3, config, private_key):
    try: # Outer try block for the entire function
        account = w3.eth.account.from_key(private_key)
        console.print(f"\n[blue]=== Adding Liquidity (WCBTC + USDC) for: {account.address} ===[/blue]")

        usdc_contract = w3.eth.contract(address=config["usdc_address"], abi=ERC20_ABI)
        wcbtc_contract = w3.eth.contract(address=config["wcbtc_address"], abi=ERC20_ABI)

        # Get current balances
        usdc_balance = usdc_contract.functions.balanceOf(account.address).call()
        wcbtc_balance = wcbtc_contract.functions.balanceOf(account.address).call()
        cbtc_native_balance = w3.eth.get_balance(account.address)

        console.print(f"[green]+ Current USDC Balance: {usdc_balance / 10**6:.6f} USDC[/green]")
        console.print(f"[green]+ Current WCBTC Balance: {wcbtc_balance / 10**18:.6f} WCBTC[/green]")
        console.print(f"[green]+ Current Native cBTC Balance: {cbtc_native_balance / 10**18:.6f} cBTC[/green]")

        while True:
            try:
                usdc_amount_to_add_str = console.input("[bold magenta]> Enter the amount of USDC to add to LP (e.g., 5.0): [/bold magenta]")
                usdc_amount_to_add = float(usdc_amount_to_add_str)
                if usdc_amount_to_add <= 0:
                    console.print("[red]- Amount must be positive. Please enter a valid number.[/red]")
                    continue
                break
            except ValueError:
                console.print("[red]- Invalid input. Please enter a valid number.[/red]")

        usdc_amount_to_add_wei = int(usdc_amount_to_add * 10**6) # USDC has 6 decimals

        if usdc_balance < usdc_amount_to_add_wei:
            console.print(f"[red]- Insufficient USDC balance. Needed: {usdc_amount_to_add} USDC, Have: {usdc_balance / 10**6:.6f} USDC[/red]")
            return

        # Fetch pool reserves to determine WCBTC amount
        try:
            pool_contract = w3.eth.contract(address=config["satsuma_pool_address"], abi=ALGEBRA_POOL_ABI)
            
            # Attempt to get token addresses from the pool contract
            token0_address = pool_contract.functions.token0().call()
            token1_address = pool_contract.functions.token1().call()
            
            # Attempt to get reserves from the pool contract
            reserves = pool_contract.functions.getReserves().call()

            # Determine which reserve corresponds to USDC and WCBTC
            if token0_address == config["usdc_address"] and token1_address == config["wcbtc_address"]:
                reserve_usdc = reserves[0]
                reserve_wcbtc = reserves[1]
            elif token0_address == config["wcbtc_address"] and token1_address == config["usdc_address"]:
                reserve_usdc = reserves[1]
                reserve_wcbtc = reserves[0]
            else:
                console.print(f"[red]- Pool tokens mismatch. Expected USDC ({config['usdc_address']}) and WCBTC ({config['wcbtc_address']}), but found Token0: {token0_address}, Token1: {token1_address}. Aborting LP add.[/red]")
                return

            # Calculate required WCBTC based on 50:50 ratio of current pool
            # Correct formula: Amount_WCBTC_wei = (Amount_USDC_wei * Reserve_WCBTC_wei) / Reserve_USDC_wei
            # This correctly handles the decimal differences because all values are in their respective wei units.
            
            # Use floating point for intermediate calculation to maintain precision
            # Ensure reserves are not zero to avoid division by zero
            if reserve_usdc == 0 or reserve_wcbtc == 0:
                console.print(f"[red]- One or both pool reserves are zero (USDC: {reserve_usdc}, WCBTC: {reserve_wcbtc}). Cannot calculate ratio. Aborting LP add.[/red]")
                return

            wcbtc_amount_to_add_float = (usdc_amount_to_add_wei * reserve_wcbtc) / reserve_usdc # FIX: Removed the extra *(10**12)
            wcbtc_amount_to_add_wei = int(wcbtc_amount_to_add_float)

            wcbtc_amount_to_add = wcbtc_amount_to_add_wei / 10**18

            console.print(f"[green]+ Raw Reserves: USDC={reserve_usdc}, WCBTC={reserve_wcbtc}[/green]")
            console.print(f"[green]+ Calculated WCBTC needed for {usdc_amount_to_add} USDC: {wcbtc_amount_to_add:.18f} WCBTC (raw wei: {wcbtc_amount_to_add_wei})[/green]")

            if wcbtc_amount_to_add_wei == 0:
                console.print("[red]- Calculated WCBTC amount is zero. This might happen if the pool ratio is extremely skewed or the USDC amount is too small. Aborting LP add.[/red]")
                return

        except Exception as e:
            console.print(f"[red]- Failed to fetch pool reserves or calculate ratio: {str(e)}. Please ensure 'satsuma_pool_address' is correct and the pool has liquidity. Aborting LP add.[/red]")
            return

        # Check WCBTC balance and offer to wrap cBTC
        if wcbtc_balance < wcbtc_amount_to_add_wei:
            missing_wcbtc = (wcbtc_amount_to_add_wei - wcbtc_balance) / 10**18
            console.print(f"[yellow]- Insufficient WCBTC balance. Missing: {missing_wcbtc:.10f} WCBTC[/yellow]")
            if cbtc_native_balance >= w3.to_wei(missing_wcbtc, 'ether'): # Check if native cBTC is enough
                wrap_choice = console.input(f"[bold magenta]> Do you want to wrap {missing_wcbtc:.10f} cBTC to WCBTC? (yes/no): [/bold magenta]").lower()
                if wrap_choice == 'yes':
                    wrap_result = await wrap_cbtc(w3, config, account, missing_wcbtc)
                    if not wrap_result["success"]:
                        console.print("[red]- Failed to wrap cBTC. Aborting LP add.[/red]")
                        return
                    # Update WCBTC balance after wrapping
                    wcbtc_balance = wcbtc_contract.functions.balanceOf(account.address).call()
                    console.print(f"[green]+ Updated WCBTC Balance after wrapping: {wcbtc_balance / 10**18:.6f} WCBTC[/green]")
                    if wcbtc_balance < wcbtc_amount_to_add_wei:
                        console.print("[red]- Still insufficient WCBTC after wrapping. Aborting LP add.[/red]")
                        return
                else:
                    console.print("[red]- Wrapping cBTC declined. Aborting LP add.[/red]")
                    return
            else:
                console.print(f"[red]- Insufficient cBTC native balance to wrap. Have: {cbtc_native_balance / 10**18:.6f} cBTC. Aborting LP add.[/red]")
                return

        # Approve tokens to the LP manager contract
        console.print("[yellow]> Approving USDC and WCBTC for LP manager...[/yellow]")
        usdc_approval = await approve_token(w3, config, account, config["usdc_address"], config["satsuma_lp_manager_address"], usdc_amount_to_add_wei)
        wcbtc_approval = await approve_token(w3, config, account, config["wcbtc_address"], config["satsuma_lp_manager_address"], wcbtc_amount_to_add_wei)
        
        if not usdc_approval["success"] or not wcbtc_approval["success"]:
            console.print("[red]- Token approval failed. Aborting liquidity add.[/red]")
            return
            
        # Get router contract (assuming LP manager has addLiquidity function from SWAP_ROUTER_ABI)
        router_contract = w3.eth.contract(address=config["satsuma_lp_manager_address"], abi=SWAP_ROUTER_ABI)
        deadline = int(time.time()) + 20 * 60 # 20 minutes

        # Define slippage tolerance (e.g., 0.5%)
        slippage_tolerance = 0.005
        amount_usdc_min = int(usdc_amount_to_add_wei * (1 - slippage_tolerance))
        amount_wcbtc_min = int(wcbtc_amount_to_add_wei * (1 - slippage_tolerance))

        console.print(f"[green]+ Adding {usdc_amount_to_add:.6f} USDC and {wcbtc_amount_to_add:.10f} WCBTC to LP.[/green]")
        console.print(f"[green]+ Minimum amounts (with {slippage_tolerance*100}% slippage): USDC={amount_usdc_min / 10**6:.6f}, WCBTC={amount_wcbtc_min / 10**18:.10f}[/green]")

        # Build add liquidity transaction
        add_liq_tx = router_contract.functions.addLiquidity(
            config["usdc_address"],
            config["wcbtc_address"],
            Web3.to_checksum_address("0x0000000000000000000000000000000000000000"), # deployer - often zero address for standard routers
            account.address,
            usdc_amount_to_add_wei,
            wcbtc_amount_to_add_wei,
            amount_usdc_min,
            amount_wcbtc_min,
            deadline
        ).build_transaction({
            "from": account.address,
            "gas": 800000, # Increased gas limit for addLiquidity
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(account.address),
            "chainId": config["chain_id"]
        })
                
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(add_liq_tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        console.print("[yellow]> Adding liquidity...[/yellow]")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                
        if receipt["status"] == 1:
            console.print(f"[green]+ Liquidity added successfully! Tx: {config['explorer']}/tx/{tx_hash.hex()}[/green]")
        else:
            console.print("[red]- Liquidity add transaction failed[/red]")
            try:
                # Attempt to decode revert reason
                tx = w3.eth.get_transaction(tx_hash)
                # This requires a local node or archive node to simulate call at previous block
                # For public RPCs, this might not work reliably.
                # result = w3.eth.call({
                #     'to': tx['to'],
                #     'from': tx['from'],
                #     'value': tx['value'],
                #     'data': tx['input'],
                #     'gas': tx['gas'],
                #     'gasPrice': tx['gasPrice'],
                #     'nonce': tx['nonce']
                # }, receipt['blockNumber'] - 1)
                # console.print(f"[red]- Transaction reverted: {result.hex()}[/red]")
                console.print(f"[cyan]Transaction receipt: {receipt}[/cyan]")
            except Exception as e:
                console.print(f"[red]- Error decoding revert reason: {str(e)}[/red]")
                
    except Exception as e: # Outer exception handler for add_lp_satsuma
        console.print(f"[red]- Error adding liquidity: {str(e)}[/red]")


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
    data_hex = "0xfc6f7865000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000038d7ea4c68000000000000000000000000000000000000000000000000002b5e3af16b188000000000000000000000000000000000000000000000000000000b1a2bc2ec5000000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000000"
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
        # Interactive swaps and LP add are not included in run_all_features
        await swap_cbtc_to_nusd(w3, config, private_key)
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
                if option == 11: # Updated exit option
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
                elif option == 4: # Interactive USDC to SUMA Swap
                    for private_key in private_keys:
                        await swap_usdc_to_suma_interactive(w3, config, private_key)
                        await asyncio.sleep(random.uniform(5, 10))
                elif option == 5: # New option for Interactive USDC to WCBTC Swap
                    for private_key in private_keys:
                        await swap_usdc_to_wcbtc_interactive(w3, config, private_key)
                        await asyncio.sleep(random.uniform(5, 10))
                elif option == 6: # Add Liquidity
                    for private_key in private_keys:
                        await add_lp_satsuma(w3, config, private_key)
                        await asyncio.sleep(random.uniform(5, 10))
                elif option == 7:
                    for private_key in private_keys:
                        await convert_suma_to_vesuma(w3, config, private_key)
                        await asyncio.sleep(random.uniform(5, 10))
                elif option == 8:
                    for private_key in private_keys:
                        await stake_vesuma(w3, config, private_key)
                        await asyncio.sleep(random.uniform(5, 10))
                elif option == 9: # Option for Claim LP Reward
                    for private_key in private_keys:
                        await claim_lp_reward(w3, config, private_key)
                        await asyncio.sleep(random.uniform(5, 10))
                elif option == 10: # Option for Run All Features
                    await run_all_features(w3, config, private_keys)
                else:
                    console.print("[red]- Invalid option. Please select 1-11.[/red]")
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
