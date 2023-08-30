from lex import Lexer
from lex_token import TokenType
from emit import Emitter


# Parser object keeps track of current token and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer: Lexer, emitter: Emitter):
        self.lexer = lexer
        self.emitter = emitter

        self.symbols = set()  # Variables declared so far.
        self.labels_declared = set()  # Labels declared so far.
        self.labels_gotoed = set()  # Labels goto'ed so far.

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
        raise Exception("Error! " + message)

    # One of the following statements...
    # nl ::= '\n'+
    def nl(self):
        # Require at least one newline.
        self.match(TokenType.NEWLINE)
        # But we will allow extra newlines too, of course.
        while self.check_token(TokenType.NEWLINE):
            self.next_token()

    def statement(self):
        # Check the first token to see what kind of statement this is.

        # "PRINT" (expression | string)
        if self.check_token(TokenType.PRINT):
            self.next_token()

            if self.check_token(TokenType.STRING):
                # Simple string, so print it.
                self.emitter.emit_line('printf("' + self.cur_token.text + '\\n");')
                self.next_token()
            else:
                # Expect an expression and print the result as a float.
                self.emitter.emit('printf("%' + '.2f\\n", (float)(')
                self.expression()
                self.emitter.emit_line("));")
        elif self.check_token(TokenType.IF):  # Branched statement
            # "IF" comparison "THEN" {statement} "ENDIF"
            self.next_token()
            self.emitter.emit("if(")
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()
            self.emitter.emit_line("){")

            while not self.check_token(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)
            self.emitter.emit_line("}")
        elif self.check_token(TokenType.WHILE):  # Branched statement
            self.next_token()
            self.emitter.emit("while(")
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()
            self.emitter.emit_line("){")

            while not self.check_token(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)
            self.emitter.emit_line("}")
        elif self.check_token(TokenType.LABEL):
            # "LABEL" ident
            self.next_token()

            # Make sure this label doesn't already exist.
            if self.cur_token.text in self.labels_declared:
                self.abort("Label already exists: " + self.cur_token.text)
            self.labels_declared.add(self.cur_token.text)

            self.emitter.emit_line(self.cur_token.text + ":")
            self.match(TokenType.IDENT)
        elif self.check_token(TokenType.GOTO):
            # "GOTO" ident
            self.next_token()

            self.labels_gotoed.add(self.cur_token.text)

            self.emitter.emit_line("goto " + self.cur_token.text + ";")
            self.match(TokenType.IDENT)
        elif self.check_token(TokenType.LET):
            # "LET" ident "=" expression
            self.next_token()

            #  Check if ident exists in symbol table. If not, declare it.
            if self.cur_token.text not in self.symbols:
                self.symbols.add(self.cur_token.text)
                self.emitter.header_line("float " + self.cur_token.text + ";")

            self.emitter.emit(self.cur_token.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression()
            self.emitter.emit_line(";")
        elif self.check_token(TokenType.INPUT):
            # "INPUT" ident
            self.next_token()

            # If variable doesn't already exist, declare it.
            if self.cur_token.text not in self.symbols:
                self.symbols.add(self.cur_token.text)
                self.emitter.header_line("float " + self.cur_token.text + ";")

            # Emit scanf but also validate the input. If invalid, set the variable to 0 and clear the input.
            self.emitter.emit_line(
                'if(0 == scanf("%' + 'f", &' + self.cur_token.text + ")) {"
            )
            self.emitter.emit_line(self.cur_token.text + " = 0;")
            self.emitter.emit('scanf("%')
            self.emitter.emit_line('*s");')
            self.emitter.emit_line("}")
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
        self.emitter.header_line("#include <stdio.h>")
        self.emitter.header_line("int main(void) {")

        # Since some newlines are required in our grammar, need to skip the excess.
        while self.check_token(TokenType.NEWLINE):
            self.next_token()

        # Parse all the statements in the program.
        while not self.check_token(TokenType.EOF):
            self.statement()

        # Wrap things up.
        self.emitter.emit_line("return 0;")
        self.emitter.emit_line("}")

        # Check that each label referenced in a GOTO is declared.
        for label in self.labels_gotoed:
            if label not in self.labels_declared:
                self.abort("Attempting to GOTO to undeclared label: " + label)

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        self.expression()

        # Must be at least one comparison operator and another expression.
        if self.is_comparison_operator():
            self.emitter.emit(self.cur_token.text)
            self.next_token()
            self.expression()
        else:
            self.abort("Expected comparison operator at: " + self.cur_token.text)

        # Can have 0 or more comparison operator and expressions.
        while self.is_comparison_operator():
            self.emitter.emit(self.cur_token.text)
            self.next_token()
            self.expression()

    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        self.term()

        # Can have 0 or more +/- and expressions.
        while self.check_token(TokenType.MINUS) or self.check_token(TokenType.PLUS):
            self.emitter.emit(self.cur_token.text)
            self.next_token()
            self.term()

    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        self.unary()

        # Can have 0 or more *// and expressions.
        while self.check_token(TokenType.SLASH) or self.check_token(TokenType.ASTERISK):
            self.emitter.emit(self.cur_token.text)
            self.next_token()
            self.unary()

    # unary ::= ["+" | "-"] primary
    def unary(self):
        # Optional unary +/-
        if self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.emitter.emit(self.cur_token.text)
            self.next_token()
        self.primary()

    # primary ::= number | ident
    def primary(self):
        if self.check_token(TokenType.NUMBER):
            self.emitter.emit(self.cur_token.text)
            self.next_token()
        elif self.check_token(TokenType.IDENT):
            # Ensure the variable already exists.
            if self.cur_token.text not in self.symbols:
                self.abort(
                    "Referencing variable before assignment: " + self.cur_token.text
                )

            self.emitter.emit(self.cur_token.text)
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
