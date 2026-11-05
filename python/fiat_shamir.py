"""Fiat--Shamir Schnorr signatures for the small teaching group."""

from __future__ import annotations

import hashlib
import secrets

from schnorr import G, P, Q, SchnorrVerifier, _scalar, public_key

Signature = tuple[int, int]  # (commitment R, response s)


def challenge_for(message: bytes, commitment: int) -> int:
    """Compute SHA-256(R || message) mod Q using a fixed-width R encoding."""
    if not isinstance(message, bytes):
        raise TypeError("message must be bytes")
    if type(commitment) is not int or not 1 <= commitment < P:
        raise ValueError("commitment is out of range")
    width = (P.bit_length() + 7) // 8
    digest = hashlib.sha256(commitment.to_bytes(width, "big") + message).digest()
    return int.from_bytes(digest, "big") % Q


def sign_message(message: bytes, secret: int, *, nonce: int | None = None) -> Signature:
    """Sign a message; ``nonce`` exists solely for reproducible attack tests."""
    public_key(secret)  # Validate the private key.
    if not isinstance(message, bytes):
        raise TypeError("message must be bytes")
    if nonce is not None and not _scalar(nonce, nonzero=True):
        raise ValueError("nonce must be in 1..Q-1")
    k = nonce if nonce is not None else secrets.randbelow(Q - 1) + 1
    commitment = pow(G, k, P)
    challenge = challenge_for(message, commitment)
    return commitment, (k + challenge * secret) % Q


def verify_signature(message: bytes, public_key_value: int, signature: Signature) -> bool:
    """Reject malformed inputs and accept exactly valid Schnorr transcripts."""
    if not isinstance(message, bytes):
        return False
    if not isinstance(signature, tuple) or len(signature) != 2:
        return False
    commitment, response = signature
    try:
        verifier = SchnorrVerifier(public_key_value)
        challenge = challenge_for(message, commitment)
    except (TypeError, ValueError):
        return False
    return verifier.verify(commitment, challenge, response)
