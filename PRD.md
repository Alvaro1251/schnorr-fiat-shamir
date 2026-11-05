# Product Requirements Document (PRD)
## Proyecto Final: Protocolos Σ, Transformación Fiat–Shamir y Firmas Digitales
**Cátedra:** Lenguajes, Computabilidad y Aplicaciones Modernas (UTN FRD)

### 1. Objetivo General
Implementar y formalizar un esquema de identificación de conocimiento cero (Schnorr), su derivación a firma digital no interactiva mediante la heurística de Fiat–Shamir, la demostración práctica del ataque por reutilización de nonce, y la verificación formal de sus propiedades algebraicas en Lean 4.

### 2. Estructura del Proyecto
El proyecto se divide estrictamente en dos entornos desacoplados:
- python/: Implementación ejecutable, CLI demostrativo, suite de ataques y tests unitarios.
- lean/: Formalización matemática en Lean 4 de las propiedades de Completitud y Special Soundness.

Archivos esperados en el repositorio:
- PRD.md
- TASKS.md
- python/requirements.txt
- python/schnorr.py
- python/fiat_shamir.py
- python/nonce_attack.py
- python/tests/test_crypto.py
- lean/lakefile.lean
- lean/lean-toolchain
- lean/Schnorr.lean

### 3. Requerimientos Técnicos: Componente Python
1. Grupo Cíclico / Aritmética Modular:
   - Implementar operaciones sobre un grupo multiplicativo Z_p* con generador g de orden primo q, o sobre curva elíptica estándar si se prefiere.
   - Definir formalmente: Par de claves (x, Y) donde Y = g^x (mod p).
2. Protocolo Interactivo de Schnorr:
   - Prover genera secreto efímero k, envía compromiso R = g^k (mod p).
   - Verifier emite desafío aleatorio c en Z_q.
   - Prover responde s = (k + c * x) (mod q).
   - Verifier valida g^s = R * (Y^c) (mod p).
3. Transformación de Fiat–Shamir (Firma Digital):
   - Reemplazar el desafío interactivo por c = SHA256(R || m) (mod q).
   - Funciones sign(m, x) que devuelve (R, s) y verify(m, Y, (R, s)) que retorna booleano.
4. Script de Ataque (Nonce Reuse):
   - Dadas dos firmas (R, s1) para m1 y (R, s2) para m2 generadas con el mismo k:
     - Calcular x = (s1 - s2) * (c1 - c2)^(-1) (mod q).
     - Comprobar que g^x = Y (mod p).
5. Criterio de Validación: Todos los tests deben ejecutarse con pytest y pasar al 100%.

### 4. Requerimientos Técnicos: Componente Lean 4
1. Espacio de Trabajo:
   - Definir el esquema algebraico sobre ZMod q asumiendo q primo ([Fact (Nat.Prime q)]).
2. Estructuras Formales:
   - Transcript: compromiso R, desafío c, respuesta s.
   - Predicado de validez isValidTranscript (w : ZMod q) (t : Transcript) : Prop.
3. Teoremas Obligatorios:
   - Completitud (completeness): Para todo secreto w, si el probador computa s = k + c * w, la transcripción resultante es válida.
   - Special Soundness (special_soundness): Dadas dos transcripciones válidas (R, c1, s1) y (R, c2, s2) con c1 != c2, existe un extractor que calcula un valor w' tal que w' = w (o recupera el testigo del sistema de ecuaciones).
4. Reglas de Calificación Cátedra:
   - Prohibido el uso de sorry.
   - Incluir #print axioms al pie de cada teorema principal para certificar ausencia de axiomas no estándar.