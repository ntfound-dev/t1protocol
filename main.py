import os
import re
import json
import sys
import traceback
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from web3.exceptions import TransactionNotFound, ContractLogicError
import time
import colorama
from colorama import Fore, Style, Back

# --- Impor Logo Kustom Anda ---
try:
    # Asumsikan DXJCOMMUNITY.py ada di direktori yang sama atau terinstal
    from DXJCOMMUNITY import print_logo
except ImportError:
    # Fallback jika modul tidak ditemukan
    def print_logo():
        print(Fore.MAGENTA + Style.BRIGHT + "=" * 40)
        print(Fore.MAGENTA + Style.BRIGHT + "===      LOGO ANDA DI SINI       ===")
        print(Fore.MAGENTA + Style.BRIGHT + "=" * 40)
        print(Fore.YELLOW + "Peringatan: Modul DXJCOMMUNITY tidak ditemukan.")

# --- Inisialisasi Colorama ---
colorama.init(autoreset=True)

# --- Definisi Warna ---
C_TITLE = Fore.CYAN + Style.BRIGHT
C_LOGO = Fore.MAGENTA + Style.BRIGHT # Warna khusus untuk logo jika fallback
C_MENU_OPTION = Fore.GREEN
C_COMING_SOON = Fore.YELLOW
C_EXIT_OPTION = Fore.YELLOW + Style.BRIGHT
C_SEPARATOR = Fore.WHITE + Style.DIM
C_PROMPT = Fore.WHITE + Style.BRIGHT
C_INPUT = Fore.WHITE
C_INFO = Fore.BLUE
C_SUCCESS = Fore.GREEN + Style.BRIGHT
C_WARNING = Fore.YELLOW + Style.BRIGHT
C_ERROR = Fore.RED + Style.BRIGHT
C_DISABLED = Fore.WHITE + Style.DIM
C_LINK = Fore.BLUE + Style.BRIGHT
C_RESET = Style.RESET_ALL

# --- Muat Variabel .env ---
load_dotenv()

# --- Variabel Global ---
RAW_PRIV_KEY = os.getenv("PRIVATE_KEY", "").strip()
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL", "").strip()
L1_CONTRACT_ADDR_STR = os.getenv("L1_CONTRACT_ADDRESS", "").strip()
DEST_CHAIN_ID_FOR_L1_TX = os.getenv("T1_L2_CHAIN_ID_FOR_L1_TX", "").strip()
L2_RECIPIENT_ADDR_STR = os.getenv("L2_RECIPIENT_ADDRESS", "").strip()
T1_L2_RPC_URL = os.getenv("T1_L2_RPC_URL", "").strip()
T1_L2_CHAIN_ID_STR = os.getenv("T1_L2_CHAIN_ID", "").strip()
L2_CONTRACT_ADDR_STR = os.getenv("L2_CONTRACT_ADDRESS", "").strip()
L1_RECIPIENT_ADDR_STR = os.getenv("L1_RECIPIENT_ADDRESS", "").strip()

# Kunci Privat disanitasi sekali di awal
PRIVATE_KEY_HEX = ""
if RAW_PRIV_KEY:
    hex_str = RAW_PRIV_KEY.lower().lstrip("0x")
    hex_str = re.sub(r"[^0-9a-f]", "", hex_str)
    if re.fullmatch(r"[0-9a-f]{64}", hex_str):
        PRIVATE_KEY_HEX = "0x" + hex_str

selected_lang = 'id' # Default

# --- Definisi Teks Multi-Bahasa ---
LANG_TEXT = {
    'id': {
        'lang_prompt': "Pilih bahasa (id/en): ",
        'invalid_lang': "Pilihan bahasa tidak valid.",
        'lang_selected': "Bahasa dipilih: {}",
        'menu_title': "===== DEVNET T1 PROTOCOL BRIDGE MENU =====",
        'menu_opt1': "1. Bridge Sepolia (L1) -> T1 Protokol (L2)",
        'menu_opt2': "2. Bridge T1 Protokol (L2) -> Sepolia (L1) (Segera Hadir)",
        'menu_opt3': "3. Opsi Lain (Segera Hadir)",
        'menu_opt0': "0. Keluar",
        'menu_separator': "------------------------------------------",
        'menu_footer': "==========================================",
        'enter_choice': "Masukkan pilihan Anda (0-3): ",
        'invalid_choice': "\nPilihan tidak valid, silakan coba lagi.",
        'coming_soon': "\nFitur ini belum tersedia...",
        'option_disabled': "Opsi ini sedang dinonaktifkan menunggu update.",
        'exiting': "\nTerima kasih! Keluar dari program.",
        'exit_interrupt': "\nProgram dihentikan oleh pengguna (Ctrl+C).",
        'press_enter': "\nTekan Enter untuk kembali ke menu...",
        'config_ok': "Konfigurasi awal dibaca...",
        'config_fail': "Error Fatal: PRIVATE_KEY tidak ada atau formatnya salah di .env",
        'validate_config': "== Memvalidasi Konfigurasi Awal ==",
        'pk_ok': "PRIVATE_KEY: OK (Format Valid)",
        'l1l2_title': "\n================================================\n  Memulai Bridge: Sepolia (L1) -> T1 L2\n================================================",
        'l1l2_validating': "\n== Memvalidasi Konfigurasi L1 -> L2 ==",
        'l1l2_env_error': "Error: Pastikan SEPOLIA_RPC_URL, L1_CONTRACT_ADDRESS, T1_L2_CHAIN_ID_FOR_L1_TX, L2_RECIPIENT_ADDRESS ada di .env",
        'l1l2_format_error': "Error: Format alamat L1/L2 atau chain ID L2 tujuan dari .env tidak valid.",
        'l1_contract_addr': "L1 Kontrak: {}",
        'l2_recipient_addr': "L2 Penerima: {}",
        'l2_dest_chain_id': "L2 Chain ID Tujuan: {}",
        'l1_connecting': "\n== Menghubungkan ke Node Sepolia L1 ==",
        'l1_connect_fail': "Gagal terkoneksi ke Sepolia RPC!",
        'l1_connect_ok': "Berhasil terkoneksi ke Sepolia (Chain ID: {})",
        'l1_connect_error': "Error saat menghubungkan ke Web3 L1:",
        'l1_account_prep': "\n== Menyiapkan Akun Pengirim di L1 ==",
        'l1_address': "Menggunakan alamat L1: {}",
        'l1_balance': "Saldo awal L1: {} Sepolia ETH",
        'l1_balance_warn': "Peringatan L1: Saldo Anda 0.",
        'l1_account_error': "Error saat menyiapkan akun L1 atau mendapatkan saldo:",
        'l1_abi_load_fail': "Error: Gagal memuat ABI kontrak L1:",
        'l1_instance_fail': "Error saat membuat instance kontrak L1:",
        'l1_contract_loaded': "Kontrak L1 dimuat dari alamat: {}",
        'l1l2_amount_prompt': "\n== Masukkan Jumlah Bridge L1 -> L2 == \nMasukkan jumlah ETH Sepolia yang ingin di-bridge ke L2 (0 jika hanya pesan): ",
        'l1l2_amount_neg_error': "[!] Jumlah tidak boleh negatif.",
        'l1l2_amount_invalid': "[!] Input tidak valid. Masukkan angka.",
        'l1l2_tx_prep': "\n== Mempersiapkan Transaksi sendMessage L1 -> L2 ==",
        'l1l2_param_title': "\nParameter Transaksi L1 -> L2:",
        'l1l2_param_bridge_amount': "  Jumlah Bridge: {} ETH",
        'l1l2_param_l2_gas': "  Gas Limit L2: {}",
        'l1l2_param_l2_fee': "  Fee Tambahan: {} ETH",
        'l1l2_param_total': "  TOTAL VALUE Tx L1: {} ETH",
        'l1_estimating_gas': "\nMemperkirakan gas L1...",
        'l1_gas_limit': "  Gas limit L1: {}",
        'l1_getting_gas_price': "\nMendapatkan harga gas L1...",
        'l1_checking_balance': "\nMengecek saldo L1...",
        'l1_balance_nok': "ERROR L1: Saldo tidak cukup! Perlu: ~{:.8f} ETH",
        'l1_balance_ok': "Saldo L1 cukup.",
        'l1_building_tx': "\nMembangun transaksi L1...",
        'l1_signing_tx': "Menandatangani transaksi L1...",
        'l1_sending_tx': "Mengirim transaksi ke Sepolia...",
        'l1_tx_sent': "\nTransaksi L1 DIKIRIM! Hash: {}",
        'l1_etherscan_link': "Lihat di Etherscan: {}",
        'l1_waiting_confirm': "\nMenunggu konfirmasi L1...",
        'l1_receipt_title': "\n--- Hasil Transaksi L1 ---",
        'receipt_status': "Status : {}",
        'receipt_status_ok': "Berhasil",
        'receipt_status_fail': "GAGAL",
        'l1l2_success': "\n== BERHASIL mengirim pesan/dana ke L2! ==",
        'l1l2_success_info': "   Proses selanjutnya terjadi di L2 dan memerlukan waktu.",
        'l1_fail': "\n== GAGAL! Transaksi L1 Reverted! ==",
        'l1_fail_info': "   Periksa Etherscan untuk detail error.",
        'l1_error_logic': "\nError Logika Kontrak L1 terdeteksi:",
        'l1_error_value': "\nValueError Transaksi L1:",
        'l1_error_unknown': "\nError Tak Terduga saat proses transaksi L1:",
        'separator_line': "------------------------------------------------\n",
        'l2l1_title': "\n================================================\n  Bridge: T1 L2 -> Sepolia (L1) - SEGERA HADIR\n================================================",
        'l2l1_disabled_info': "   Fungsi ini belum aktif karena menunggu update ABI/Info dari developer T1 Protocol.",
    },
    'en': {
        'lang_prompt': "Select language (id/en): ",
        'invalid_lang': "Invalid language selection.",
        'lang_selected': "Language set to: {}",
        'menu_title': "===== DEVNET T1 PROTOCOL BRIDGE MENU =====",
        'menu_opt1': "1. Bridge Sepolia (L1) -> T1 Protocol (L2)",
        'menu_opt2': "2. Bridge T1 Protocol (L2) -> Sepolia (L1) (Coming Soon)",
        'menu_opt3': "3. Other Options (Coming Soon)",
        'menu_opt0': "0. Exit",
        'menu_separator': "------------------------------------------",
        'menu_footer': "==========================================",
        'enter_choice': "Enter your choice (0-3): ",
        'invalid_choice': "\nInvalid choice, please try again.",
        'coming_soon': "\nThis feature is not available yet...",
        'option_disabled': "This option is currently disabled pending developer updates.",
        'exiting': "\nThank you! Exiting program.",
        'exit_interrupt': "\nProgram interrupted by user (Ctrl+C).",
        'press_enter': "\nPress Enter to return to the menu...",
        'config_ok': "Initial configuration read...",
        'config_fail': "Fatal Error: PRIVATE_KEY missing or invalid format in .env",
        'validate_config': "== Validating Initial Configuration ==",
        'pk_ok': "PRIVATE_KEY: OK (Valid Format)",
        'l1l2_title': "\n================================================\n  Starting Bridge: Sepolia (L1) -> T1 L2\n================================================",
        'l1l2_validating': "\n== Validating L1 -> L2 Configuration ==",
        'l1l2_env_error': "Error: Ensure SEPOLIA_RPC_URL, L1_CONTRACT_ADDRESS, T1_L2_CHAIN_ID_FOR_L1_TX, L2_RECIPIENT_ADDRESS are in .env",
        'l1l2_format_error': "Error: Invalid L1/L2 address or L2 destination chain ID format in .env.",
        'l1_contract_addr': "L1 Contract: {}",
        'l2_recipient_addr': "L2 Recipient: {}",
        'l2_dest_chain_id': "L2 Destination Chain ID: {}",
        'l1_connecting': "\n== Connecting to Sepolia L1 Node ==",
        'l1_connect_fail': "Failed to connect to Sepolia RPC!",
        'l1_connect_ok': "Successfully connected to Sepolia (Chain ID: {})",
        'l1_connect_error': "Error connecting to Web3 L1:",
        'l1_account_prep': "\n== Preparing Sender Account on L1 ==",
        'l1_address': "Using L1 address: {}",
        'l1_balance': "Initial L1 balance: {} Sepolia ETH",
        'l1_balance_warn': "L1 Warning: Your balance is 0.",
        'l1_account_error': "Error preparing L1 account or getting balance:",
        'l1_abi_load_fail': "Error: Failed to load L1 contract ABI:",
        'l1_instance_fail': "Error creating L1 contract instance:",
        'l1_contract_loaded': "L1 Contract loaded from address: {}",
        'l1l2_amount_prompt': "\n== Enter L1 -> L2 Bridge Amount ==\nEnter amount of Sepolia ETH to bridge to L2 (0 for message only): ",
        'l1l2_amount_neg_error': "[!] Amount cannot be negative.",
        'l1l2_amount_invalid': "[!] Invalid input. Please enter a number.",
        'l1l2_tx_prep': "\n== Preparing sendMessage Transaction L1 -> L2 ==",
        'l1l2_param_title': "\nL1 -> L2 Transaction Parameters:",
        'l1l2_param_bridge_amount': "  Bridge Amount: {} ETH",
        'l1l2_param_l2_gas': "  L2 Gas Limit: {}",
        'l1l2_param_l2_fee': "  Additional Fee: {} ETH",
        'l1l2_param_total': "  TOTAL L1 Tx VALUE: {} ETH",
        'l1_estimating_gas': "\nEstimating L1 gas...",
        'l1_gas_limit': "  L1 gas limit: {}",
        'l1_getting_gas_price': "\nGetting L1 gas price...",
        'l1_checking_balance': "\nChecking L1 balance...",
        'l1_balance_nok': "ERROR L1: Insufficient balance! Required: ~{:.8f} ETH",
        'l1_balance_ok': "L1 balance sufficient.",
        'l1_building_tx': "\nBuilding L1 transaction...",
        'l1_signing_tx': "Signing L1 transaction...",
        'l1_sending_tx': "Sending transaction to Sepolia...",
        'l1_tx_sent': "\nL1 Transaction SENT! Hash: {}",
        'l1_etherscan_link': "See on Etherscan: {}",
        'l1_waiting_confirm': "\nWaiting for L1 confirmation...",
        'l1_receipt_title': "\n--- L1 Transaction Result ---",
        'receipt_status': "Status : {}",
        'receipt_status_ok': "Success",
        'receipt_status_fail': "FAILED",
        'l1l2_success': "\n== Successfully sent message/funds to L2! ==",
        'l1l2_success_info': "   The next steps happen on L2 and take time.",
        'l1_fail': "\n== FAILED! L1 Transaction Reverted! ==",
        'l1_fail_info': "   Check Etherscan for error details.",
        'l1_error_logic': "\nL1 Contract Logic Error detected:",
        'l1_error_value': "\nL1 Transaction ValueError:",
        'l1_error_unknown': "\nUnexpected Error during L1 transaction process:",
        'separator_line': "------------------------------------------------\n",
        'l2l1_title': "\n================================================\n  Bridge: T1 L2 -> Sepolia (L1) - COMING SOON\n================================================",
        'l2l1_disabled_info': "   This function is not yet active, pending ABI/Info updates from T1 Protocol developers.",
    }
}

# --- Fungsi Helper untuk Mendapatkan Teks ---
def get_text(key, lang=None, default=""):
    """Mengambil teks berdasarkan kunci dan bahasa terpilih, dengan fallback."""
    lang_to_use = lang if lang else selected_lang
    try:
        return LANG_TEXT[lang_to_use].get(key, LANG_TEXT['en'].get(key, default if default else f"<{key}_NOT_FOUND>"))
    except KeyError:
        return LANG_TEXT['en'].get(key, default if default else f"<{key}_NOT_FOUND>")


# -----------------------------------------------------
#        FUNGSI UNTUK BRIDGE L1 (Sepolia) -> L2 (T1)
# -----------------------------------------------------
def bridge_sepolia_to_t1():
    """Menjalankan proses bridge dari Sepolia ke T1 L2."""
    print(C_TITLE + get_text('l1l2_title'))

    # --- Validasi Input Khusus L1->L2 ---
    print(C_INFO + get_text('l1l2_validating'))
    if not all([SEPOLIA_RPC_URL, L1_CONTRACT_ADDR_STR, DEST_CHAIN_ID_FOR_L1_TX, L2_RECIPIENT_ADDR_STR]):
        print(C_ERROR + get_text('l1l2_env_error'))
        return

    try:
        l1_contract_address = Web3.to_checksum_address(L1_CONTRACT_ADDR_STR)
        l2_recipient_address = Web3.to_checksum_address(L2_RECIPIENT_ADDR_STR)
        destination_chain_id = int(DEST_CHAIN_ID_FOR_L1_TX)
        print(f"  {get_text('l1_contract_addr').format(C_INFO + str(l1_contract_address))}")
        print(f"  {get_text('l2_recipient_addr').format(C_INFO + str(l2_recipient_address))}")
        print(f"  {get_text('l2_dest_chain_id').format(C_INFO + str(destination_chain_id))}")
    except ValueError as e:
        print(f"{C_ERROR}{get_text('l1l2_format_error')} {e}")
        return

    # --- Setup Web3 L1 ---
    print(C_INFO + get_text('l1_connecting'))
    try:
        w3_l1 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
        w3_l1.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        if not w3_l1.is_connected():
            print(C_ERROR + get_text('l1_connect_fail'))
            return
        print(C_SUCCESS + get_text('l1_connect_ok').format(w3_l1.eth.chain_id))
    except Exception as e:
        print(f"{C_ERROR}{get_text('l1_connect_error')} {e}")
        traceback.print_exc()
        return

    # --- Setup Akun L1 & Saldo ---
    print(C_INFO + get_text('l1_account_prep'))
    try:
        account_l1 = w3_l1.eth.account.from_key(PRIVATE_KEY_HEX)
        my_address_l1 = account_l1.address
        print(get_text('l1_address').format(C_INFO + my_address_l1))
        balance_l1_wei = w3_l1.eth.get_balance(my_address_l1)
        balance_l1_eth = w3_l1.from_wei(balance_l1_wei, "ether")
        print(get_text('l1_balance').format(f"{C_SUCCESS}{balance_l1_eth}"))
        if balance_l1_wei == 0:
            print(C_WARNING + get_text('l1_balance_warn'))
    except Exception as e:
        print(f"{C_ERROR}{get_text('l1_account_error')} {e}")
        traceback.print_exc()
        return

    # --- Load ABI Kontrak L1 ---
    l1_contract_abi_str = """
    [{"inputs":[{"internalType":"address","name":"_counterpart","type":"address"},{"internalType":"address","name":"_rollup","type":"address"},{"internalType":"address","name":"_messageQueue","type":"address"}],"stateMutability":"payable","type":"constructor"},{"inputs":[],"name":"ErrorZeroAddress","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"messageHash","type":"bytes32"}],"name":"FailedRelayedMessage","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint8","name":"version","type":"uint8"}],"name":"Initialized","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"messageHash","type":"bytes32"}],"name":"RelayedMessage","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":true,"internalType":"address","name":"target","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"messageNonce","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"gasLimit","type":"uint256"},{"indexed":false,"internalType":"bytes","name":"message","type":"bytes"},{"indexed":true,"internalType":"uint64","name":"destChainId","type":"uint64"},{"indexed":false,"internalType":"bytes32","name":"messageHash","type":"bytes32"}],"name":"SentMessage","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"_oldFeeVault","type":"address"},{"indexed":false,"internalType":"address","name":"_newFeeVault","type":"address"}],"name":"UpdateFeeVault","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"oldMaxReplayTimes","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"newMaxReplayTimes","type":"uint256"}],"name":"UpdateMaxReplayTimes","type":"event"},{"inputs":[],"name":"counterpart","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_from","type":"address"},{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_value","type":"uint256"},{"internalType":"uint256","name":"_messageNonce","type":"uint256"},{"internalType":"bytes","name":"_message","type":"bytes"}],"name":"dropMessage","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"feeVault","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_feeVault","type":"address"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"isL1MessageDropped","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"isL2MessageExecuted","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"maxReplayTimes","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"messageQueue","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"messageSendTimestamp","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"prevReplayIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_from","type":"address"},{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_value","type":"uint256"},{"internalType":"uint256","name":"_nonce","type":"uint256"},{"internalType":"bytes","name":"_message","type":"bytes"},{"components":[{"internalType":"uint256","name":"batchIndex","type":"uint256"},{"internalType":"bytes","name":"merkleProof","type":"bytes"}],"internalType":"struct IL1T1Messenger.L2MessageProof","name":"_proof","type":"tuple"}],"name":"relayMessageWithProof","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_from","type":"address"},{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_value","type":"uint256"},{"internalType":"uint256","name":"_messageNonce","type":"uint256"},{"internalType":"bytes","name":"_message","type":"bytes"},{"internalType":"uint32","name":"_newGasLimit","type":"uint32"},{"internalType":"address","name":"_refundAddress","type":"address"}],"name":"replayMessage","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"replayStates","outputs":[{"internalType":"uint128","name":"times","type":"uint128"},{"internalType":"uint128","name":"lastIndex","type":"uint128"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"rollup","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_value","type":"uint256"},{"internalType":"bytes","name":"_message","type":"bytes"},{"internalType":"uint256","name":"_gasLimit","type":"uint256"},{"internalType":"uint64","name":"_destChainId","type":"uint64"}],"name":"sendMessage","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_value","type":"uint256"},{"internalType":"bytes","name":"_message","type":"bytes"},{"internalType":"uint256","name":"_gasLimit","type":"uint256"},{"internalType":"uint64","name":"_destChainId","type":"uint64"},{"internalType":"address","name":"_callbackAddress","type":"address"}],"name":"sendMessage","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bool","name":"_status","type":"bool"}],"name":"setPause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_newFeeVault","type":"address"}],"name":"updateFeeVault","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_newMaxReplayTimes","type":"uint256"}],"name":"updateMaxReplayTimes","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"xDomainMessageSender","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"stateMutability":"payable","type":"receive"}]
    """
    try:
        l1_contract_abi = json.loads(l1_contract_abi_str)
        l1_contract = w3_l1.eth.contract(address=l1_contract_address, abi=l1_contract_abi)
        print(get_text('l1_contract_loaded').format(C_INFO + l1_contract.address))
    except json.JSONDecodeError as e:
        print(f"{C_ERROR}{get_text('l1_abi_load_fail')} {e}")
        return
    except Exception as e:
        print(f"{C_ERROR}{get_text('l1_instance_fail')} {e}")
        traceback.print_exc()
        return

    # --- Input Jumlah Bridge L1->L2 ---
    while True:
        amount_str = input(f"{C_PROMPT}{get_text('l1l2_amount_prompt')}{C_INPUT}")
        try:
            amount_to_bridge_decimal = Decimal(amount_str)
            if amount_to_bridge_decimal < 0: print(C_WARNING + get_text('l1l2_amount_neg_error'))
            else: break
        except InvalidOperation: print(C_ERROR + get_text('l1l2_amount_invalid'))
        except Exception as e: print(f"{C_ERROR}[!] Error: {e}")

    # --- Persiapan Transaksi sendMessage L1->L2 ---
    print(C_INFO + get_text('l1l2_tx_prep'))
    try:
        message_bytes = b''
        gas_limit_l2 = 500000 # VERIFIKASI DARI DOKS T1!
        required_fee_eth = 0.001 # VERIFIKASI DARI DOKS T1!
        required_fee_wei = w3_l1.to_wei(required_fee_eth, 'ether')
        amount_to_bridge_wei = w3_l1.to_wei(amount_to_bridge_decimal, 'ether')
        total_value_wei = amount_to_bridge_wei + required_fee_wei
        total_value_eth = w3_l1.from_wei(total_value_wei, 'ether')

        print(C_INFO + get_text('l1l2_param_title'))
        print(f"  {get_text('l2_recipient_addr').format(C_INFO + str(l2_recipient_address))}")
        print(f"  {get_text('l1l2_param_bridge_amount').format(C_INFO + str(amount_to_bridge_decimal))}")
        print(f"  {get_text('l1l2_param_l2_gas').format(C_INFO + str(gas_limit_l2))}")
        print(f"  {get_text('l2_dest_chain_id').format(C_INFO + str(destination_chain_id))}")
        print(f"  {get_text('l1l2_param_l2_fee').format(C_INFO + str(required_fee_eth))}")
        print(f"  {C_WARNING}{get_text('l1l2_param_total').format(str(total_value_eth))}")
        print(C_SEPARATOR + get_text('menu_separator'))

        func_call = l1_contract.functions.sendMessage(l2_recipient_address,amount_to_bridge_wei,message_bytes,gas_limit_l2,destination_chain_id)

        print(C_INFO + get_text('l1_estimating_gas'))
        estimated_gas_l1 = func_call.estimate_gas({'from': my_address_l1,'value': total_value_wei})
        gas_limit_l1 = int(estimated_gas_l1 * 1.3)
        print(f"  {get_text('l1_gas_limit').format(C_INFO + str(gas_limit_l1))}")

        print(C_INFO + get_text('l1_getting_gas_price'))
        gas_price_info = {}
        try:
             latest_block = w3_l1.eth.get_block('latest')
             base_fee = latest_block.get('baseFeePerGas')
             if base_fee is None: raise ValueError("baseFee missing")
             max_priority_fee_per_gas = w3_l1.to_wei(1.5, 'gwei')
             max_fee_per_gas = int(base_fee * 1.2) + max_priority_fee_per_gas
             gas_price_info = {'maxFeePerGas': max_fee_per_gas,'maxPriorityFeePerGas': max_priority_fee_per_gas}
             print(f"  {C_INFO}BaseFee: ~{w3_l1.from_wei(base_fee, 'gwei'):.2f} Gwei, MaxFee: ~{w3_l1.from_wei(max_fee_per_gas, 'gwei'):.2f} Gwei")
        except Exception as gas_err:
             print(f"{C_WARNING}  Gagal EIP-1559 ({gas_err}), mencoba legacy...")
             gas_price = w3_l1.eth.gas_price
             gas_price = int(gas_price * 1.1) # Buffer
             gas_price_info = {'gasPrice': gas_price}
             print(f"  {C_INFO}Legacy Gas Price: ~{w3_l1.from_wei(gas_price, 'gwei'):.2f} Gwei")


        print(C_INFO + get_text('l1_checking_balance'))
        current_gas_price = gas_price_info.get('maxFeePerGas', gas_price_info.get('gasPrice'))
        estimated_l1_gas_cost_wei = gas_limit_l1 * current_gas_price
        total_estimated_cost_wei = total_value_wei + estimated_l1_gas_cost_wei
        if balance_l1_wei < total_estimated_cost_wei:
             print(f"{C_ERROR}{get_text('l1_balance_nok').format(w3_l1.from_wei(total_estimated_cost_wei, 'ether'))}")
             return
        else: print(C_SUCCESS + get_text('l1_balance_ok'))

        print(C_INFO + get_text('l1_building_tx'))
        nonce = w3_l1.eth.get_transaction_count(my_address_l1)
        tx_params = {'from':my_address_l1,'chainId':w3_l1.eth.chain_id,'value':total_value_wei,'gas':gas_limit_l1,'nonce':nonce,**gas_price_info}
        built_tx = func_call.build_transaction(tx_params)

        print(C_INFO + get_text('l1_signing_tx'))
        signed_tx = w3_l1.eth.account.sign_transaction(built_tx, PRIVATE_KEY_HEX)

        print(C_INFO + get_text('l1_sending_tx'))
        tx_hash = w3_l1.eth.send_raw_transaction(signed_tx.raw_transaction)
        hex_tx_hash = tx_hash.hex()
        etherscan_link = f"https://sepolia.etherscan.io/tx/{hex_tx_hash}"
        print(f"{C_SUCCESS}{get_text('l1_tx_sent').format(hex_tx_hash)}")
        print(f"  {get_text('l1_etherscan_link').format(C_LINK + etherscan_link)}")

        print(C_INFO + get_text('l1_waiting_confirm'))
        receipt = w3_l1.eth.wait_for_transaction_receipt(tx_hash, timeout=300)

        print(C_INFO + get_text('l1_receipt_title'))
        status_text = get_text('receipt_status_ok') if receipt.status == 1 else get_text('receipt_status_fail')
        status_color = C_SUCCESS if receipt.status == 1 else C_ERROR
        print(get_text('receipt_status').format(status_color + status_text))
        print(f"  Block: {C_INFO}{receipt.blockNumber}")
        print(f"  Gas Used: {C_INFO}{receipt.gasUsed}")

        if receipt.status == 1:
            print(C_SUCCESS + get_text('l1l2_success'))
            print(C_INFO + get_text('l1l2_success_info'))
        else:
            print(C_ERROR + get_text('l1_fail'))
            print(C_INFO + get_text('l1_fail_info'))

    except ContractLogicError as cle:
        print(f"{C_ERROR}{get_text('l1_error_logic')} {cle}")
        traceback.print_exc()
    except ValueError as ve:
        print(f"{C_ERROR}{get_text('l1_error_value')} {ve}")
        traceback.print_exc()
    except TransactionNotFound:
        print(f"{C_ERROR}Error: L1 Transaction with hash {hex_tx_hash} not found after timeout.")
    except Exception as e:
        print(C_ERROR + get_text('l1_error_unknown'))
        traceback.print_exc()

    print(C_SEPARATOR + get_text('separator_line'))


# -----------------------------------------------------
#        FUNGSI UNTUK BRIDGE L2 (T1) -> L1 (Sepolia) (Placeholder)
# -----------------------------------------------------
def bridge_t1_to_sepolia():
    """Menjalankan proses bridge dari T1 L2 ke Sepolia (Saat ini Dinonaktifkan)."""
    print(C_TITLE + get_text('l2l1_title'))
    print(C_DISABLED + get_text('l2l1_disabled_info'))
    print(C_SEPARATOR + get_text('separator_line'))
    # --- Tempat Anda memasukkan logika L2->L1 nanti ---
    # 1. Validasi .env L2->L1
    # 2. Connect Web3 ke T1_L2_RPC_URL
    # 3. Setup Akun L2
    # 4. Load ABI Kontrak L2 (l2_contract_abi_str)
    # 5. Input jumlah penarikan
    # 6. Persiapan parameter (sesuai fungsi L2 yang benar)
    # 7. Estimasi gas L2, cek saldo L2
    # 8. Build, sign, send Tx L2
    # 9. Tunggu receipt L2
    # 10. Beri info tentang masa tunggu & klaim L1


# -----------------------------------------------------
#                 TAMPILAN MENU UTAMA
# -----------------------------------------------------
def display_menu():
    """Menampilkan menu pilihan kepada pengguna."""
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        print_logo() # Panggil logo kustom Anda
    except NameError:
        print(f"{C_ERROR}Error: Fungsi 'print_logo' tidak ditemukan.")
    except Exception as logo_err:
        print(f"{C_ERROR}Error saat mencetak logo: {logo_err}")

    print(f"\n{C_TITLE}{get_text('menu_title')}")
    print(f"  {C_MENU_OPTION}{get_text('menu_opt1')}")
    print(f"  {C_COMING_SOON}{get_text('menu_opt2')}")
    print(f"  {C_COMING_SOON}{get_text('menu_opt3')}")
    print(C_SEPARATOR + get_text('menu_separator'))
    print(f"  {C_EXIT_OPTION}{get_text('menu_opt0')}")
    print(C_TITLE + get_text('menu_footer'))

# -----------------------------------------------------
#                PILIHAN BAHASA
# -----------------------------------------------------
def select_language():
    """Meminta pengguna memilih bahasa."""
    global selected_lang
    print(f"{C_PROMPT}Select language (id/en):{C_RESET} ", end='')
    while True:
        choice = input().lower().strip()
        if choice in ['id', 'en']:
            selected_lang = choice
            print(f"{C_SUCCESS}{get_text('lang_selected', lang=selected_lang).format(selected_lang.upper())}")
            time.sleep(1)
            break
        else:
            print(C_ERROR + LANG_TEXT['id']['invalid_lang'] + " / " + LANG_TEXT['en']['invalid_lang'])
            print(f"{C_PROMPT}Select language (id/en):{C_RESET} ", end='')


# -----------------------------------------------------
#                     LOOP UTAMA
# -----------------------------------------------------
def main():
    """Fungsi utama untuk menjalankan menu."""
    select_language()

    while True:
        # Pindah clear screen ke display_menu
        display_menu()
        choice = input(f"{C_PROMPT}{get_text('enter_choice')}{C_INPUT}")

        if choice == '1':
            bridge_sepolia_to_t1()
        elif choice == '2':
            print(C_COMING_SOON + get_text('coming_soon')) # Opsi 2 dinonaktifkan
            # bridge_t1_to_sepolia() # Aktifkan ini jika sudah siap
        elif choice == '3':
            print(C_COMING_SOON + get_text('coming_soon'))
        elif choice == '0':
            print(C_EXIT_OPTION + get_text('exiting'))
            break
        else:
            print(C_ERROR + get_text('invalid_choice'))

        # Beri jeda agar pengguna bisa membaca output
        input(f"\n{C_PROMPT}{get_text('press_enter')}{C_RESET}")

# -----------------------------------------------------
#                  ENTRY POINT & EXIT HANDLER
# -----------------------------------------------------
if __name__ == "__main__":
    # Validasi awal yang krusial
    if not RAW_PRIV_KEY or len(PRIVATE_KEY_HEX) != 66:
         print(C_ERROR + get_text('config_fail', lang='en')) # Error fatal pakai English
         exit(1)
    print(C_INFO + get_text('config_ok', lang='en')) # Pesan awal pakai English

    try:
        main() # Jalankan loop utama
    except KeyboardInterrupt:
        # Tangkap Ctrl+C
        print("\n" + C_WARNING + get_text('exit_interrupt'))
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except Exception as e:
        # Tangkap error tak terduga lainnya
        print(f"\n{C_ERROR}An unexpected fatal error occurred:")
        traceback.print_exc()
        sys.exit(1)
