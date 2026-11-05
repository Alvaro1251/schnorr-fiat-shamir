"""Recover a teaching Schnorr secret when two signatures repeat a nonce."""

from __future__ import annotations

from fiat_shamir import Signature, challenge_for, verify_signature
from schnorr import G, P, Q


def extract_private_key(
    message1: bytes,
    signature1: Signature,
    message2: bytes,
    signature2: Signature,
    public_key_value: int,
) -> int:
    """Extract x = (s1-s2)/(c1-c2) mod Q from valid repeated-R signatures.

    Raises ValueError if the preconditions are not met, including a challenge
    collision (which makes the denominator non-invertible).
    """
    if message1 == message2:
        raise ValueError("messages must differ")
    if not (
        verify_signature(message1, public_key_value, signature1)
        and verify_signature(message2, public_key_value, signature2)
    ):
        raise ValueError("both signatures must verify")
    commitment1, response1 = signature1
    commitment2, response2 = signature2
    if commitment1 != commitment2:
        raise ValueError("signatures must reuse the same commitment")
    c1 = challenge_for(message1, commitment1)
    c2 = challenge_for(message2, commitment2)
    denominator = (c1 - c2) % Q
    if denominator == 0:
        raise ValueError("distinct messages produced the same challenge")
    secret = (response1 - response2) * pow(denominator, -1, Q) % Q
    if pow(G, secret, P) != public_key_value:
        raise ValueError("recovered secret does not match the public key")
    return secret
