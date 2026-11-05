"""Run ``python demo.py`` to see one protocol round and the nonce attack."""

from fiat_shamir import challenge_for, sign_message, verify_signature
from nonce_attack import extract_private_key
from schnorr import Q, SchnorrProver, SchnorrVerifier, generate_keypair


def main() -> None:
    secret, public = generate_keypair()
    prover = SchnorrProver(secret)
    verifier = SchnorrVerifier(public)
    commitment = prover.commit()
    challenge = verifier.challenge()
    response = prover.respond(challenge)
    print(f"Schnorr interactive accepted: {verifier.verify(commitment, challenge, response)}")

    message = b"Proyecto Final 11"
    signature = sign_message(message, secret)
    print(f"Fiat-Shamir signature accepted: {verify_signature(message, public, signature)}")

    # Deliberate nonce reuse is only for demonstrating the vulnerability.
    first = sign_message(b"first", secret, nonce=7)
    second_message = next(
        b"second-" + str(i).encode()
        for i in range(Q)
        if challenge_for(b"first", first[0])
        != challenge_for(b"second-" + str(i).encode(), first[0])
    )
    second = sign_message(second_message, secret, nonce=7)
    recovered = extract_private_key(b"first", first, second_message, second, public)
    print(f"Repeated nonce recovered original secret: {recovered == secret}")


if __name__ == "__main__":
    main()
