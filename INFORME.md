# Informe: Proyecto Final 11

## 1. Protocolo interactivo de Schnorr

Se trabaja en el subgrupo de orden primo `q = 1019` generado por `g = 4`
en `Z_2039*`. Como `p = 2039` y `q = 1019` son primos y `g^q = 1 (mod p)`
con `g ≠ 1`, el orden de `g` es exactamente `q`. El probador elige una
clave privada `x ∈ {1, …, q−1}` y publica `Y = g^x (mod p)`.

Para identificarse, el probador toma un nonce `k`, envía `R = g^k`, recibe
un desafío `c ∈ Z_q` y responde `s = k + cx (mod q)`. El verificador acepta
si `g^s = RY^c (mod p)`. La completitud se deduce directamente:

```text
g^s = g^(k+cx) = g^k (g^x)^c = R Y^c  (mod p).
```

La elección aleatoria del desafío después del compromiso es esencial para
la interpretación interactiva. La comprobación de una sola ecuación por
sí misma no prueba conocimiento del secreto.

## 2. Fiat–Shamir y firma

Para eliminar la interacción, el desafío se calcula como
`c = SHA-256(encode(R) || m) mod q`. `encode(R)` usa el ancho fijo
determinado por `p`; la firma es `(R, s)`. El verificador recalcula `c` a
partir del mensaje recibido y luego comprueba la ecuación de Schnorr.
Por eso, cambiar `m`, `R`, `s` o la clave pública invalida la firma en los
casos comprobados por la suite de pruebas.

Fiat–Shamir se analiza usualmente en el modelo de oráculo aleatorio. El
grupo del programa es intencionalmente pequeño y permite buscar logaritmos
discretos; esta implementación es una demostración académica, no una firma
apta para producción.

## 3. Reutilización del nonce

Si dos firmas de mensajes distintos tienen el mismo `k`, comparten el
compromiso `R` y sus respuestas satisfacen
`s₁ = k + c₁x` y `s₂ = k + c₂x` en `Z_q`. Al restar:

```text
s₁ − s₂ = (c₁ − c₂)x,
x = (s₁ − s₂)(c₁ − c₂)⁻¹ mod q,  si c₁ ≠ c₂.
```

El programa verifica primero las dos firmas, exige el mismo `R`, comprueba
que los desafíos difieran y contrasta el resultado con `Y`. En un grupo
pequeño puede ocurrir una colisión de desafíos aunque los mensajes sean
distintos; en ese caso el denominador es cero y el extractor rechaza.

## 4. Qué demuestra Lean

La prueba formal abstrae los exponentes como elementos de `ZMod q` bajo
la hipótesis `Fact (Nat.Prime q)`. El generador en este sistema de
coordenadas es `1`, de modo que la relación de clave pública es
`Y = generator · w = w`. La transcripción tiene compromiso `R`, desafío
`c` y respuesta `s`, y es válida cuando `s = R + cY`.

`schnorr_completeness` certifica que la respuesta honesta `k + cw` es
válida. `schnorr_special_soundness` supone dos transcripciones válidas con
igual `R` y distintos `c`; tras restar las ecuaciones, demuestra que
`ext(t₁,t₂) = (s₁−s₂)(c₁−c₂)⁻¹ = w`. Los comandos `#print axioms` en el
archivo Lean permiten inspeccionar los axiomas utilizados por cada prueba.

Esta formalización verifica el álgebra del protocolo. No demuestra que el
código Python implemente exactamente ese modelo, ni propiedades
probabilísticas, conocimiento cero, resistencia a falsificaciones, seguridad
del hash o seguridad frente a canales laterales.

## 5. Validación

La suite `pytest` cubre 68 casos: claves y parámetros, completitud
interactiva para distintos secretos, nonces y desafíos, rechazo de
transcripciones alteradas, firmas válidas e inválidas, entradas malformadas,
ataque exitoso y rechazo de precondiciones incumplidas. La comprobación
formal requerida es `lake build` en el directorio `lean/`. En la carpeta
de entrega, `python -m pytest -q` terminó con **68 passed** y `lake build`
terminó con **Build completed successfully** (1203 jobs), sin advertencias.
`#print axioms` informó `propext` y `Quot.sound` para completitud, y
`propext`, `Classical.choice` y `Quot.sound` para special soundness;
ninguna prueba depende de `sorryAx`.
