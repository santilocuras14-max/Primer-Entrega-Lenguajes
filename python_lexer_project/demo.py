
import argparse, sys, json
from lexer import Lexer

def main():
    ap = argparse.ArgumentParser(description="Demo: Analizador Léxico (subset Python)")
    ap.add_argument("file", nargs="?", help="Ruta del archivo a tokenizar")
    ap.add_argument("-e", "--expr", help="Código directo a tokenizar")
    ap.add_argument("--json", action="store_true", help="Imprime tokens como JSON")
    args = ap.parse_args()

    if not args.file and not args.expr:
        print("Usa un archivo o -e 'codigo'")
        sys.exit(1)

    code = ""
    if args.expr is not None:
        code = args.expr
    else:
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()

    lex = Lexer()
    tokens = list(lex.tokenize(code))
    if args.json:
        as_list = [t.__dict__ for t in tokens]
        print(json.dumps(as_list, ensure_ascii=False, indent=2))
    else:
        for t in tokens:
            print(f"({t.type:8s}) {t.value!r}\t@ line {t.line}, col {t.column}")

if __name__ == "__main__":
    main()
