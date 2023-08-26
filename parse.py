import sys

from lex import Lexer
from lex_token import TokenType


# Parser object keeps track of current token and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer

        self.cur_token = None
        self.peek_token = None
        self.next_token()
        self.next_token()  # Call this twice to initialize current and peek.

    # Return true if the current token matches.
    def check_token(self, kind: TokenType):
        return kind == self.cur_token.kind

    # Return true if the next token matches.
    def check_peek(self, kind: TokenType):
        return kind == self.peek_token.kind

    # Try to match current token. If not, error. Advances the current token.
    def match(self, kind: TokenType):
        if not self.check_token(kind):
            self.abort("Expected " + kind.name + ", got " + self.cur_token.kind.name)
        self.next_token()

    # Advances the current token.
    def next_token(self):
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.get_token()
        # No need to worry about passing the EOF, lexer handles that.

    def abort(self, message):
        sys.exit("Error. " + message)

    # One of the following statements...
    # nl ::= '\n'+
    def nl(self):
        print("NEWLINE")

        # Require at least one newline.
        self.match(TokenType.NEWLINE)
        # But we will allow extra newlines too, of course.
        while self.check_token(TokenType.NEWLINE):
            self.next_token()

    def statement(self):
        # Check the first token to see what kind of statement this is.

        # "PRINT" (expression | string)
        if self.check_token(TokenType.PRINT):
            print("STATEMENT-PRINT")
            self.next_token()

            if self.check_token(TokenType.STRING):
                # Simple string.
                self.next_token()
            else:
                # Expect an expression.
                self.expression()

        self.nl()

    # program ::= {statement}
    def program(self):
        print("PROGRAM")

        # Parse all the statements in the program.
        while not self.check_token(TokenType.EOF):
            self.statement()
