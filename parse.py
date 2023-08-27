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
        elif self.check_token(TokenType.IF):  # Branched statement
            # "IF" comparison "THEN" {statement} "ENDIF"
            print("STATEMENT-IF")
            self.next_token()
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()

            while not self.check_token(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)
        elif self.check_token(TokenType.WHILE):  # Branched statement
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

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        print("COMPARISON")

        self.expression()

        # Must be at least one comparison operator and another expression.
        if self.is_comparison_operator():
            self.next_token()
            self.expression()
        else:
            self.abort("Expected comparison operator at: " + self.cur_token.text)

        # Can have 0 or more comparison operator and expressions.
        while self.is_comparison_operator():
            self.next_token()
            self.expression()

    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        print("EXPRESSION")

        self.term()

        # Can have 0 or more +/- and expressions.
        while self.check_token(TokenType.MINUS) or self.check_token(TokenType.PLUS):
            self.next_token()
            self.term()

    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        print("TERM")

        self.unary()

        # Can have 0 or more *// and expressions.
        while self.check_token(TokenType.SLASH) or self.check_token(TokenType.ASTERISK):
            self.next_token()
            self.unary()

    # unary ::= ["+" | "-"] primary
    def unary(self):
        print("UNARY")

        # Optional unary +/-
        if self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.next_token()
        self.primary()

    # primary ::= number | ident
    def primary(self):
        print("PRIMARY (" + self.cur_token.text + ")")

        if self.check_token(TokenType.NUMBER):
            self.next_token()
        elif self.check_token(TokenType.IDENT):
            self.next_token()
        else:
            # Error!
            self.abort("Unexpected token at " + self.cur_token.text)

    # Return true if the current token is a comparison operator.
    def is_comparison_operator(self):
        return (
            self.check_token(TokenType.GT)
            or self.check_token(TokenType.GTEQ)
            or self.check_token(TokenType.LT)
            or self.check_token(TokenType.LTEQ)
            or self.check_token(TokenType.EQEQ)
            or self.check_token(TokenType.NOTEQ)
        )
