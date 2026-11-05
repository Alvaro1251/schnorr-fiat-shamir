# Proyecto Final 11: Schnorr, Fiat–Shamir y firmas

## Ejecutar

En `python/`:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q tests
python demo.py
```

En `lean/`, con Lean instalado por `elan`:

```powershell
$env:MATHLIB_NO_CACHE_ON_UPDATE='1'
lake update
lake exe cache get Mathlib.Algebra.Field.ZMod Mathlib.Tactic.Ring
lake build
```

## Diseño y alcance

La implementación Python usa el subgrupo multiplicativo de orden primo
`q = 1019` en `Z_2039*`, generado por `g = 4`. La clave pública es
`Y = g^x mod p`. Una ronda interactiva verifica `g^s = R · Y^c mod p`.
La firma calcula `c = SHA-256(R || m) mod q`, con `R` codificado en una
cantidad fija de bytes. El nonce se elige con `secrets` salvo en pruebas y
en la demostración deliberada del ataque. **Estos parámetros pequeños son
solo didácticos; no proporcionan seguridad criptográfica real.**

Las pruebas de Python comprueban completitud en varios secretos, nonces y
desafíos; rechazo de respuestas, mensajes, claves y transcripciones alteradas;
y recuperación exacta de `x` cuando dos firmas válidas comparten `R` y tienen
desafíos distintos. Si los desafíos coinciden, el extractor rechaza porque
no existe inverso del denominador.

La formalización Lean trabaja en `ZMod q` con `q` primo y modela solamente
los exponentes. El compromiso es `R = k`, la clave pública en exponentes es
`Y = w` (generador representado por `1`) y una transcripción acepta cuando
`s = R + c · Y`. `schnorr_completeness` prueba la ecuación para la respuesta
honesta y `schnorr_special_soundness` prueba que el extractor
`(s₁-s₂)/(c₁-c₂)` recupera `w` si los compromisos coinciden y los desafíos
son distintos. Se incluyen `#print axioms` para ambos teoremas.

Lean no verifica el código Python ni modela SHA-256, aleatoriedad,
conocimiento cero, probabilidad de falsificación o seguridad del esquema de
firma. Fiat–Shamir se presenta aquí como transformación educativa; su
justificación criptográfica requiere supuestos adicionales, típicamente un
modelo de oráculo aleatorio.

