import json
import os
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()


GANACHE_RPC_URL = os.getenv(
    "GANACHE_RPC_URL",
    "http://127.0.0.1:7545"
)

CONTRACT_ADDRESS = os.getenv(
    "CONTRACT_ADDRESS"
)

PRIVATE_KEY = os.getenv(
    "BLOCKCHAIN_PRIVATE_KEY"
)


# --------------------------------------------------
# Validate configuration
# --------------------------------------------------

if not CONTRACT_ADDRESS:
    raise RuntimeError(
        "CONTRACT_ADDRESS is missing from .env"
    )

if not PRIVATE_KEY:
    raise RuntimeError(
        "BLOCKCHAIN_PRIVATE_KEY is missing from .env"
    )


# --------------------------------------------------
# Connect to Ganache
# --------------------------------------------------

web3 = Web3(
    Web3.HTTPProvider(GANACHE_RPC_URL)
)


if not web3.is_connected():
    raise RuntimeError(
        "Could not connect to Ganache at "
        f"{GANACHE_RPC_URL}"
    )


# --------------------------------------------------
# Load contract ABI
# --------------------------------------------------

# Project root:
# CertificateVerificationSystem/
PROJECT_ROOT = Path(__file__).resolve().parents[3]

ABI_PATH = (
    PROJECT_ROOT
    / "blockchain"
    / "abi"
    / "CertificateVerification.json"
)


if not ABI_PATH.exists():
    raise RuntimeError(
        f"Contract ABI not found at: {ABI_PATH}"
    )


with open(
    ABI_PATH,
    "r",
    encoding="utf-8"
) as file:
    CONTRACT_ABI = json.load(file)


# --------------------------------------------------
# Contract
# --------------------------------------------------

contract = web3.eth.contract(
    address=Web3.to_checksum_address(
        CONTRACT_ADDRESS
    ),
    abi=CONTRACT_ABI
)


# --------------------------------------------------
# Account
# --------------------------------------------------

account = web3.eth.account.from_key(
    PRIVATE_KEY
)

ACCOUNT_ADDRESS = account.address


# --------------------------------------------------
# Issue Certificate
# --------------------------------------------------

def issue_certificate_on_blockchain(
    certificate_id: str,
    student_name: str,
    course: str,
    institution: str,
    certificate_hash: str,
    issue_date: int
):
    """
    Issues a certificate on the blockchain.

    Returns:
        transaction_hash
        block_number
    """

    nonce = web3.eth.get_transaction_count(
        ACCOUNT_ADDRESS
    )

    transaction = contract.functions.issueCertificate(
        certificate_id,
        student_name,
        course,
        institution,
        certificate_hash,
        issue_date
    ).build_transaction(
        {
            "from": ACCOUNT_ADDRESS,
            "nonce": nonce,
            "gas": 500000,
            "gasPrice": web3.eth.gas_price,
        }
    )

    signed_transaction = web3.eth.account.sign_transaction(
        transaction,
        private_key=PRIVATE_KEY
    )

    transaction_hash = web3.eth.send_raw_transaction(
        signed_transaction.raw_transaction
    )

    receipt = web3.eth.wait_for_transaction_receipt(
        transaction_hash
    )

    return {
        "transaction_hash": transaction_hash.hex(),
        "block_number": receipt["blockNumber"]
    }


# --------------------------------------------------
# Verify Certificate
# --------------------------------------------------

def verify_certificate_on_blockchain(
    certificate_id: str,
    certificate_hash: str
):
    """
    Verifies a certificate against
    the blockchain record.
    """

    result = contract.functions.verifyCertificate(
        certificate_id,
        certificate_hash
    ).call()

    return {
        "is_valid": result[0],
        "is_revoked": result[1]
    }


# --------------------------------------------------
# Get Certificate
# --------------------------------------------------

def get_certificate_from_blockchain(
    certificate_id: str
):
    """
    Returns complete certificate information
    stored on the blockchain.
    """

    result = contract.functions.getCertificate(
        certificate_id
    ).call()

    return {
        "certificate_id": result[0],
        "student_name": result[1],
        "course": result[2],
        "institution": result[3],
        "certificate_hash": result[4],
        "issue_date": result[5],
        "issuer": result[6],
        "revoked": result[7]
    }


# --------------------------------------------------
# Revoke Certificate
# --------------------------------------------------

def revoke_certificate_on_blockchain(
    certificate_id: str
):
    """
    Revokes a certificate on the blockchain.
    """

    nonce = web3.eth.get_transaction_count(
        ACCOUNT_ADDRESS
    )

    transaction = contract.functions.revokeCertificate(
        certificate_id
    ).build_transaction(
        {
            "from": ACCOUNT_ADDRESS,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": web3.eth.gas_price,
        }
    )

    signed_transaction = web3.eth.account.sign_transaction(
        transaction,
        private_key=PRIVATE_KEY
    )

    transaction_hash = web3.eth.send_raw_transaction(
        signed_transaction.raw_transaction
    )

    receipt = web3.eth.wait_for_transaction_receipt(
        transaction_hash
    )

    return {
        "transaction_hash": transaction_hash.hex(),
        "block_number": receipt["blockNumber"]
    }