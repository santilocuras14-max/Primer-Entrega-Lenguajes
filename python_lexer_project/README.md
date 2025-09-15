# Analizador Léxico de Python (subset, con INDENT/DEDENT)

Implementa un **lexer** de un subconjunto amplio de Python 3:
- `NEWLINE`, `INDENT`, `DEDENT` con reglas de indentación (tab = siguiente múltiplo de 8).
- Identificadores, **palabras clave**, **números** (dec, bin, oct, hex, float con exp), **strings** simples y **triple-strings** multi-línea.
- **Comentarios** `# ...`, **operadores** y **delimitadores** comunes.

## Uso
```bash
python demo.py tests/sample.py
python demo.py -e "def f(x):\n    return x+1\n"
python demo.py tests/sample.py --json
```