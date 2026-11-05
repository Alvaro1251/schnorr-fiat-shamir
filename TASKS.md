# Backlog de Implementación Autónoma

## Reglas de Ejecución para el Agente
1. Resuelve las tareas en orden secuencial[cite: 65].
2. Tras completar una tarea, ejecuta su suite de pruebas (pytest en Python o lake build en Lean 4)[cite: 1, 65].
3. Si ocurre algún error o fallo de táctica, corrígelo iterativamente antes de avanzar[cite: 65].
4. Marca la tarea con [x] y realiza un commit en git con mensaje descriptivo[cite: 65].

---

### Fase 1: Entorno y Core Criptográfico en Python[cite: 65]
- [x] Tarea 1.1: Configuración de Dependencias y Modelos[cite: 65]
  - Crear python/requirements.txt (pytest, cryptography)[cite: 65].
  - Crear estructura base de módulos y pruebas[cite: 65].
- [x] Tarea 1.2: Implementación de Schnorr Interactivo[cite: 5, 65]
  - Implementar en python/schnorr.py las clases SchnorrProver y SchnorrVerifier sobre Z_p* con subgrupo de orden q[cite: 5, 65].
  - Escribir pruebas unitarias en python/tests/test_crypto.py verificando completitud con probadores honestos y rechazo de probadores deshonestos[cite: 5, 41, 65].
- [x] Tarea 1.3: Transformación de Fiat–Shamir y Firmas[cite: 5, 65]
  - Implementar en python/fiat_shamir.py las funciones sign_message(m, x) y verify_signature(m, Y, sig)[cite: 5, 65].
  - Agregar tests unitarios verificando firma legítima, alteración de mensaje y alteración de clave pública[cite: 65].
- [x] Tarea 1.4: Script de Ataque por Reutilización de Nonce[cite: 5, 65]
  - Implementar en python/nonce_attack.py la función extract_private_key(m1, sig1, m2, sig2, Y)[cite: 5, 65].
  - Crear prueba unitaria que firme dos mensajes distintos con un mismo nonce fijo k, ejecute el ataque y verifique que la clave privada extraída coincide exactamente con la original[cite: 5, 65].

---

### Fase 2: Formalización y Demostraciones en Lean 4[cite: 5, 65]
- [x] Tarea 2.1: Configuración del Paquete Lake[cite: 65]
  - Crear lean/lakefile.lean y lean/lean-toolchain[cite: 65].
  - Verificar que lake build compile sin advertencias un archivo vacío.
- [x] Tarea 2.2: Definición de Tipos y Predicados Algebraicos
  - En lean/Schnorr.lean, definir el contexto con variable q prima (ZMod q)[cite: 5].
  - Formalizar la relación de clave pública Y = g * w.
  - Formalizar el predicado de transcripción válida.
- [x] Tarea 2.3: Teorema de Completitud[cite: 5]
  - Demostrar el lema schnorr_completeness formalizando que la respuesta honesta s = k + c * w satisface la ecuación de verificación[cite: 5].
  - Asegurar cero usos de sorry[cite: 1].
- [x] Tarea 2.4: Teorema de Special Soundness (Extractor)[cite: 5]
  - Definir la función extractora ext(t1, t2) = (s1 - s2) * (c1 - c2)^(-1)[cite: 5].
  - Demostrar el teorema schnorr_special_soundness: si c1 != c2 y ambas transcripciones son válidas para el mismo compromiso R, entonces ext(t1, t2) es exactamente igual al testigo secreto w[cite: 5].
  - Añadir #print axioms schnorr_completeness y #print axioms schnorr_special_soundness[cite: 1].
