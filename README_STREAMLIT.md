# Streamlit deployment add-on

This package adds a Streamlit UI to the existing certificate project. It is an add-on, not a complete copy of the repository: merge these files into the root of the original repository, where the `backend/app/...` modules already exist.

## Local run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

For local development, create a root `.env` file with:

```env
GANACHE_RPC_URL=http://127.0.0.1:7545
CONTRACT_ADDRESS=YOUR_DEPLOYED_CONTRACT_ADDRESS
BLOCKCHAIN_PRIVATE_KEY=YOUR_LOCAL_TEST_ACCOUNT_PRIVATE_KEY
ADMIN_PASSWORD=CHOOSE_A_STRONG_ADMIN_PASSWORD
```

Never commit `.env` or real private keys.

## Streamlit Community Cloud

1. Merge `streamlit_app.py` and `requirements.txt` into the repository root.
2. Deploy `streamlit_app.py` from that repository on Streamlit Community Cloud.
3. Add these keys under the app's **Settings → Secrets**:

```toml
GANACHE_RPC_URL = "https://YOUR_CLOUD_REACHABLE_RPC_ENDPOINT"
CONTRACT_ADDRESS = "YOUR_DEPLOYED_CONTRACT_ADDRESS"
BLOCKCHAIN_PRIVATE_KEY = "YOUR_ADMIN_WALLET_PRIVATE_KEY"
ADMIN_PASSWORD = "A_STRONG_UNIQUE_PASSWORD"
```

The app gates the dashboard, issue, and revoke pages behind `ADMIN_PASSWORD`. The account configured by `BLOCKCHAIN_PRIVATE_KEY` can issue and revoke certificates, so use a dedicated wallet with limited funds/permissions. Public verification/details pages remain accessible.

A local Ganache endpoint such as `127.0.0.1:7545` is not reachable from Streamlit Cloud. Deploy the contract to an RPC endpoint reachable by the cloud app and use its matching contract address and chain configuration. Check that the backend's `blockchain_service.py` reads the configured RPC and contract values from environment variables.

The repository's backend code and contract are required. This package alone will not run without them. Review the deployment and access-control model before making the app public.
