# Streamlit interface

The repository now has a Streamlit UI design for the existing blockchain certificate system.

## Run

From the repository root:

```bash
pip install -r requirements-streamlit.txt
streamlit run streamlit_app.py
```

Create `.env` in the repository root:

```env
GANACHE_RPC_URL=http://127.0.0.1:7545
CONTRACT_ADDRESS=YOUR_DEPLOYED_CONTRACT_ADDRESS
BLOCKCHAIN_PRIVATE_KEY=YOUR_GANACHE_ACCOUNT_PRIVATE_KEY
```

The Streamlit app reuses the existing SQLite database, PDF generator, SHA-256 hashing service, Web3 service, and Solidity contract.

Do not commit real private keys to GitHub.
