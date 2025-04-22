# T1 Protocol Devnet Bridge Menu Script

This Python script provides a text-based command-line menu interface to facilitate the bridging process between the Sepolia network (L1) and the T1 Protocol Devnet (L2).

## Key Features

* Interactive command-line menu.
* Supports bridging from Sepolia (L1) to T1 Protocol (L2).
* Placeholder for bridging from T1 Protocol (L2) to Sepolia (L1) (Coming Soon).
* Multi-language support: Indonesian (id) and English (en).
* Colored terminal output using `colorama` for better readability.
* Easy configuration via a `.env` file.
* Graceful program exit (including via `Ctrl+C`).

## Prerequisites

* Python 3.7 or higher.
* `pip` (Python package installer).

## Setup / Installation

1.  **Clone or Download:**
    * If this is a Git repository: `git clone https://github.com/ntfound-dev/t1protocol.git`

2.  **Navigate to Project Directory:**
    ```bash
    cd t1protocol
    ```

3.  **Install Dependencies:**
    Run the following command to install the required Python libraries from the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create and Configure `.env` File:**
    * Create a file named `.env` in the same directory as the Python script.
    * Copy the structure below and fill in your values. **WARNING:** Keep your `PRIVATE_KEY` secure! Never share it or commit it to a public repository.
    * You **must** find the values for `T1_L2_RPC_URL` and `L2_CONTRACT_ADDRESS` from the official T1 Protocol Devnet documentation.

    ```dotenv
    # --- General ---
    PRIVATE_KEY=PASTE_YOUR_PRIVATE_KEY_HERE_0x...

    # --- Configuration for L1 (Sepolia) -> L2 (T1) ---
    # Ensure variable names EXACTLY match below
    SEPOLIA_RPC_URL=[https://sepolia.infura.io/v3/YOUR_INFURA_ID_OR_OTHER_RPC](https://sepolia.infura.io/v3/YOUR_INFURA_ID_OR_OTHER_RPC)
    L1_CONTRACT_ADDRESS=0xAFdF5cb097D6FB2EB8B1FFbAB180e667458e18F4 # Bridge Contract on Sepolia
    T1_L2_CHAIN_ID_FOR_L1_TX=299792                             # T1 L2 Chain ID (as destination from L1)
    L2_RECIPIENT_ADDRESS=YOUR_RECIPIENT_ADDRESS_ON_T1_L2_0x...      # Your address on T1 L2

    # --- Configuration for L2 (T1) -> L1 (Sepolia) (Complete Later) ---
    T1_L2_RPC_URL=T1_L2_RPC_URL_FROM_DOCS             # <-- REQUIRED FROM T1 DOCS!
    T1_L2_CHAIN_ID=299792                            # T1 L2 Chain ID (as source from L2)
    L2_CONTRACT_ADDRESS=L2_CONTRACT_ADDRESS_FROM_DOCS # <-- REQUIRED FROM T1 DOCS!
    L1_RECIPIENT_ADDRESS=YOUR_RECIPIENT_ADDRESS_ON_SEPOLIA_0x...  # Your address on Sepolia
    ```

## Usage

1.  **Run the Script:** Open your terminal or command prompt in the project directory, then run:
    ```bash
    python main.py
    ```
    *(Replace `main_bridge_menu_final.py` if you named the Python file differently)*

2.  **Select Language:** The script will prompt you to select a language (`id` or `en`). Type your choice and press Enter.

3.  **Select Menu Option:** The main menu will be displayed. Enter the number of the option you want to execute:
    * `1`: Start the bridging process from Sepolia to T1 L2. You will be prompted to enter the amount of ETH to bridge.
    * `2`: (Coming Soon) Placeholder for bridging from T1 L2 to Sepolia.
    * `3`: (Coming Soon) Placeholder for other features.
    * `0`: Exit the script.

4.  **Follow Instructions:** The script will display process logs, including gas estimations, balance checks, transaction sending, and the transaction hash if successful.

5.  **Exit:** You can exit at any time by selecting option `0` or pressing `Ctrl+C`.

## Current Status (As of April 21, 2025)

* **Option 1 (Sepolia -> T1 L2):** Functional. Requires correct `.env` configuration for the L1->L2 section. Ensure the `gas_limit_l2` and `required_fee_eth` values within the code align with T1 Protocol recommendations.
* **Option 2 (T1 L2 -> Sepolia L1):** **Not Functional / Coming Soon.** You need to obtain the **L2 Contract ABI**, the **correct L2 function name**, and its **parameters** from the T1 Protocol documentation after their maintenance is complete. Afterward, you need to edit the `bridge_t1_to_sepolia()` function in the Python script and re-enable its call in the main menu.
* **Option 3:** Coming Soon.

## Disclaimer / Warning

* **Private Key Security:** Keep your `PRIVATE_KEY` confidential. You bear the risk of fund loss if this key is compromised. Consider using a dedicated wallet for development/testing.
* **Devnet Network:** This script interacts with a development network (Devnet). Do not use real assets or your main private keys. Functionality and contract addresses may change.
* **No Warranty:** This script is provided "as is" without any warranty. Use it at your own risk.
* **T1 Protocol Information:** Always refer to the official T1 Protocol documentation for the most accurate and up-to-date contract addresses, RPC URLs, ABIs, fees, and procedures.
