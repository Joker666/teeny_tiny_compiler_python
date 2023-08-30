import sys

from lex import Lexer
from parse import Parser
from emit import Emitter


def main():
    print("Teeny Tiny Compiler")

    if len(sys.argv) != 2:
        sys.exit("Error: Compiler needs source file as argument.")
    with open(sys.argv[1], "r") as input_file:
        source = input_file.read()

    # Initialize the lexer and parser.
    lexer = Lexer(source)
    emitter = Emitter("out.c")
    parser = Parser(lexer, emitter)

    parser.program()  # Start the parser.
    emitter.write_file()  # Write the output to file.
    print("Compiling completed.")


if __name__ == "__main__":
    main()
