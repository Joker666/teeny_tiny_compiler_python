from lex import Lexer
from lex_token import TokenType


def main():
    source = "IF+-123 foo*THEN/"
    lexer = Lexer(source)

    token = lexer.get_token()
    while token.kind != TokenType.EOF:
        print(token.text, " => ", token.kind)
        token = lexer.get_token()


if __name__ == "__main__":
    main()
