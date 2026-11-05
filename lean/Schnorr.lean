module

public import Mathlib.Algebra.Field.ZMod
import Mathlib.Tactic.Ring

/-!
# Algebraic Schnorr transcripts

This formalizes the exponent equations of Schnorr over `ZMod q`, with `q`
prime.  It proves algebraic completeness and special soundness.  It does not
model the multiplicative implementation, Fiat--Shamir hash, randomness, or
the zero-knowledge/security properties of a deployment.
-/

public section

namespace Schnorr

variable {q : ℕ}

/-- The generator in the additive exponent model. -/
def generator : ZMod q := 1

/-- Public-key relation `Y = g * w`, with `g = 1` in exponent coordinates. -/
def publicKey (w : ZMod q) : ZMod q := generator * w

/-- Commitment, challenge and response in the order-`q` exponent group. -/
structure Transcript (q : ℕ) where
  R : ZMod q
  c : ZMod q
  s : ZMod q

/-- The verifier's exponent equation `s = R + c * Y`. -/
def isValidTranscript (Y : ZMod q) (t : Transcript q) : Prop :=
  t.s = t.R + t.c * Y

/-- An honest response always verifies for its public key. -/
theorem schnorr_completeness (w k c : ZMod q) :
    isValidTranscript (publicKey w) { R := k, c := c, s := k + c * w } := by
  simp [isValidTranscript, publicKey, generator]

/-- The special-soundness extractor from two accepting responses. -/
def ext (t₁ t₂ : Transcript q) : ZMod q :=
  (t₁.s - t₂.s) * (t₁.c - t₂.c)⁻¹

variable [Fact (Nat.Prime q)]

/-- Two accepting transcripts with the same commitment and different
challenges determine the witness exactly. -/
theorem schnorr_special_soundness
    (w : ZMod q) (t₁ t₂ : Transcript q)
    (hR : t₁.R = t₂.R)
    (hc : t₁.c ≠ t₂.c)
    (h₁ : isValidTranscript (publicKey w) t₁)
    (h₂ : isValidTranscript (publicKey w) t₂) :
    ext t₁ t₂ = w := by
  simp only [isValidTranscript, publicKey, generator, one_mul] at h₁ h₂
  have hdiff : t₁.c - t₂.c ≠ 0 := sub_ne_zero.mpr hc
  have hs : t₁.s - t₂.s = (t₁.c - t₂.c) * w := by
    calc
      t₁.s - t₂.s = (t₁.R + t₁.c * w) - (t₂.R + t₂.c * w) := by rw [h₁, h₂]
      _ = (t₁.c - t₂.c) * w := by rw [hR]; ring
  simp only [ext, hs]
  calc
    ((t₁.c - t₂.c) * w) * (t₁.c - t₂.c)⁻¹ =
        (t₁.c - t₂.c) * ((t₁.c - t₂.c)⁻¹ * w) := by ring
    _ = w := mul_inv_cancel_left₀ hdiff w

#print axioms schnorr_completeness
#print axioms schnorr_special_soundness

end Schnorr
