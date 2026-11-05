"""Behavioral tests for the interactive protocol, signatures, and attack."""

import hashlib

import pytest

from fiat_shamir import challenge_for, sign_message, verify_signature
from nonce_attack import extract_private_key
from schnorr import G, P, Q, SchnorrProver, SchnorrVerifier, generate_keypair, public_key


def test_group_parameters_and_key_generation():
    assert P == 2 * Q + 1
    assert pow(G, Q, P) == 1
    assert G != 1
    for _ in range(20):
        secret, public = generate_keypair()
        assert 1 <= secret < Q
        assert public == pow(G, secret, P)


@pytest.mark.parametrize("secret", [1, 2, 17, Q - 1])
@pytest.mark.parametrize("nonce", [1, 7, Q - 1])
@pytest.mark.parametrize("challenge", [0, 1, 53, Q - 1])
def test_honest_interactive_round(secret, nonce, challenge):
    prover = SchnorrProver(secret, nonce=nonce)
    verifier = SchnorrVerifier(prover.public_key)
    commitment = prover.commit()
    response = prover.respond(challenge)
    assert commitment == pow(G, nonce, P)
    assert response == (nonce + challenge * secret) % Q
    assert verifier.verify(commitment, challenge, response)


def test_interactive_rejects_dishonest_response_and_wrong_key():
    prover = SchnorrProver(19, nonce=37)
    verifier = SchnorrVerifier(prover.public_key)
    commitment = prover.commit()
    response = prover.respond(77)
    assert not verifier.verify(commitment, 77, (response + 1) % Q)
    assert not SchnorrVerifier(public_key(20)).verify(commitment, 77, response)
    assert not verifier.verify(commitment, 78, response)


def test_interactive_state_and_input_validation():
    prover = SchnorrProver(19, nonce=37)
    with pytest.raises(RuntimeError):
        prover.respond(1)
    prover.commit()
    with pytest.raises(ValueError):
        prover.respond(Q)
    assert SchnorrVerifier(prover.public_key).verify(pow(G, 37, P), 1, prover.respond(1))
    with pytest.raises(RuntimeError):
        prover.respond(1)
    for bad in [0, Q, True, -1]:
        with pytest.raises(ValueError):
            SchnorrProver(bad)
    with pytest.raises(ValueError):
        SchnorrVerifier(1)
    assert not SchnorrVerifier(prover.public_key).verify(0, 1, 1)
    assert not SchnorrVerifier(prover.public_key).verify(2, 1, 1)  # outside subgroup
    assert not SchnorrVerifier(prover.public_key).verify(1, Q, 1)
    assert not SchnorrVerifier(prover.public_key).verify(1, 1, Q)


def test_challenge_uses_fixed_width_commitment_then_message():
    message = b"\x00binary\xff"
    commitment = 7
    width = (P.bit_length() + 7) // 8
    expected = int.from_bytes(
        hashlib.sha256(commitment.to_bytes(width, "big") + message).digest(), "big"
    ) % Q
    assert challenge_for(message, commitment) == expected


@pytest.mark.parametrize("message", [b"", b"hello", b"\x00\xff", "á".encode()])
def test_signature_accepts_original_and_rejects_tampering(message):
    secret = 19
    public = public_key(secret)
    signature = sign_message(message, secret, nonce=53)
    assert verify_signature(message, public, signature)
    assert not verify_signature(message + b"!", public, signature)
    assert not verify_signature(message, public_key(secret + 1), signature)
    assert not verify_signature(message, public, (signature[0], (signature[1] + 1) % Q))


@pytest.mark.parametrize("bad_signature", [(0, 1), (P, 1), (2, 1), (4, Q), (True, 1), (), [4, 1]])
def test_signature_rejects_malformed_transcripts(bad_signature):
    assert not verify_signature(b"m", public_key(19), bad_signature)


def test_signer_rejects_bad_secret_nonce_and_message():
    with pytest.raises(ValueError):
        sign_message(b"m", 0)
    with pytest.raises(ValueError):
        sign_message(b"m", 19, nonce=0)
    with pytest.raises(TypeError):
        sign_message("m", 19)
    assert not verify_signature("m", public_key(19), (4, 2))


def distinct_challenge_message(first: bytes, commitment: int) -> bytes:
    first_challenge = challenge_for(first, commitment)
    return next(
        candidate
        for i in range(Q + 1)
        if (candidate := f"other-{i}".encode()) != first
        and challenge_for(candidate, commitment) != first_challenge
    )


@pytest.mark.parametrize("secret,nonce", [(1, 1), (19, 37), (Q - 1, Q - 1)])
def test_nonce_reuse_recovers_exact_private_key(secret, nonce):
    public = public_key(secret)
    first_message = b"pay Alice"
    first_signature = sign_message(first_message, secret, nonce=nonce)
    second_message = distinct_challenge_message(first_message, first_signature[0])
    second_signature = sign_message(second_message, secret, nonce=nonce)
    assert first_signature[0] == second_signature[0]
    assert extract_private_key(
        first_message, first_signature, second_message, second_signature, public
    ) == secret


def test_nonce_attack_rejects_bad_preconditions():
    secret = 19
    public = public_key(secret)
    first = sign_message(b"one", secret, nonce=7)
    second = sign_message(b"two", secret, nonce=8)
    with pytest.raises(ValueError, match="same commitment"):
        extract_private_key(b"one", first, b"two", second, public)
    with pytest.raises(ValueError, match="messages must differ"):
        extract_private_key(b"one", first, b"one", first, public)
    with pytest.raises(ValueError, match="both signatures must verify"):
        extract_private_key(b"one", first, b"two", (first[0], first[1]), public)

    # In this tiny teaching group, distinct messages can collide modulo Q.
    first_challenge = challenge_for(b"one", first[0])
    collision = next(
        candidate
        for i in range(10_000)
        if (candidate := f"collision-{i}".encode()) != b"one"
        and challenge_for(candidate, first[0]) == first_challenge
    )
    colliding_signature = sign_message(collision, secret, nonce=7)
    with pytest.raises(ValueError, match="same challenge"):
        extract_private_key(b"one", first, collision, colliding_signature, public)
