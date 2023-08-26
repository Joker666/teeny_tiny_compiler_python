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

        elif self.check_token(TokenType.IF):
            # "IF" comparison "THEN" {statement} "ENDIF"
            print("STATEMENT-IF")
            self.next_token()
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()

            while not self.check_token(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)

        elif self.check_token(TokenType.WHILE):
            print("STATEMENT-WHILE")
            self.next_token()
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()

            while not self.check_token(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)

        elif self.check_token(TokenType.LABEL):
            # "LABEL" ident
            print("STATEMENT-LABEL")
            self.next_token()
            self.match(TokenType.IDENT)

        elif self.check_token(TokenType.GOTO):
            # "GOTO" ident
            print("STATEMENT-GOTO")
            self.next_token()
            self.match(TokenType.IDENT)

        elif self.check_token(TokenType.LET):
            # "LET" ident "=" expression
            print("STATEMENT-LET")
            self.next_token()
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression()

        elif self.check_token(TokenType.INPUT):
            # "INPUT" ident
            print("STATEMENT-INPUT")
            self.next_token()
            self.match(TokenType.IDENT)

        else:
            # This is not a valid statement. Error!
            self.abort(
                "Invalid statement at "
                + self.cur_token.text
                + " ("
                + self.cur_token.kind.name
                + ")"
            )

        self.nl()

    # program ::= {statement}
    def program(self):
        print("PROGRAM")

        # Since some newlines are required in our grammar, need to skip the excess.
        while self.check_token(TokenType.NEWLINE):
            self.next_token()

        # Parse all the statements in the program.
        while not self.check_token(TokenType.EOF):
            self.statement()

    def expression(self):
        pass

    def comparison(self):
        pass
