import sys

from lex import Lexer
from parse import Parser


def main():
    print("Teeny Tiny Compiler")

    if len(sys.argv) != 2:
        sys.exit("Error: Compiler needs source file as argument.")
    with open(sys.argv[1], "r") as input_file:
        source = input_file.read()

    # Initialize the lexer and parser.
    lexer = Lexer(source)
    parser = Parser(lexer)

    parser.program()  # Start the parser.
    print("Parsing completed.")


if __name__ == "__main__":
    main()
