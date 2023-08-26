import sys

from lex_token import LexToken, TokenType


class Lexer:
    def __init__(self, source):
        self.source = (
            source + "\n"
        )  # Source code to lex as a string. Append a newline to simplify lexing/parsing
        # the last token/statement.

        self.cur_char = ""  # Current character in the string.
        self.cur_pos = -1  # Current position in the string.
        self.next_char()

    # Process the next character.
    def next_char(self):
        self.cur_pos += 1
        if self.cur_pos >= len(self.source):
            self.cur_char = "\0"  # EOF
        else:
            self.cur_char = self.source[self.cur_pos]

    # Return the lookahead character.
    def peek(self):
        if self.cur_pos + 1 >= len(self.source):
            return "\0"
        return self.source[self.cur_pos + 1]

    # Invalid token found, print error message and exit.
    def abort(self, message):
        sys.exit("Lexing error. " + message)

    # Skip whitespace except newlines, which we will use to indicate the end of a statement.
    def skip_whitespace(self):
        while self.cur_char == " " or self.cur_char == "\t" or self.cur_char == "\r":
            self.next_char()

    # Skip comments in the code.
    def skip_comment(self):
        if self.cur_char == "#":
            while self.cur_char != "\n":
                self.next_char()

    # Return the next token.
    def get_token(self):
        self.skip_whitespace()
        self.skip_comment()
        token = None

        # Check the first character of this token to see if we can decide what it is. If it is a multiple
        # character operator (e.g., !=), number, identifier, or keyword then we will process the rest.
        if self.cur_char == "+":
            token = LexToken(self.cur_char, TokenType.PLUS)
        elif self.cur_char == "-":
            token = LexToken(self.cur_char, TokenType.MINUS)
        elif self.cur_char == "*":
            token = LexToken(self.cur_char, TokenType.ASTERISK)
        elif self.cur_char == "/":
            token = LexToken(self.cur_char, TokenType.SLASH)
        elif self.cur_char == "\n":
            token = LexToken(self.cur_char, TokenType.NEWLINE)
        elif self.cur_char == "\0":
            token = LexToken("", TokenType.EOF)
        elif self.cur_char == "=":
            # Check whether this token is = or ==
            if self.peek() == "=":
                last_char = self.cur_char
                self.next_char()
                token = LexToken(last_char + self.cur_char, TokenType.EQEQ)
            else:
                token = LexToken(self.cur_char, TokenType.EQ)
        elif self.cur_char == ">":
            # Check whether this token is > or >=
            if self.peek() == "=":
                last_char = self.cur_char
                self.next_char()
                token = LexToken(last_char + self.cur_char, TokenType.GTEQ)
            else:
                token = LexToken(self.cur_char, TokenType.GT)
        elif self.cur_char == "<":
            # Check whether this token is < or <=
            if self.peek() == "=":
                last_char = self.cur_char
                self.next_char()
                token = LexToken(last_char + self.cur_char, TokenType.LTEQ)
            else:
                token = LexToken(self.cur_char, TokenType.LT)
        elif self.cur_char == "!":
            # Check whether this token is ! or !=
            if self.peek() == "=":
                last_char = self.cur_char
                self.next_char()
                token = LexToken(last_char + self.cur_char, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got !" + self.peek())
        elif self.cur_char == '"':
            self.next_char()
            start_pos = self.cur_pos

            while self.cur_char != '"':
                # Don't allow special characters in the string. No escape characters, newlines, tabs, or %.
                # We will be using C's printf on this string.
                if (
                    self.cur_char == "\r"
                    or self.cur_char == "\n"
                    or self.cur_char == "\t"
                    or self.cur_char == "\\"
                    or self.cur_char == "%"
                ):
                    self.abort("Illegal character in string.")
                self.next_char()

            token_text = self.source[start_pos : self.cur_pos]  # Get the substring.
            token = LexToken(token_text, TokenType.STRING)
        elif self.cur_char.isdigit():
            # Leading character is a digit, so this must be a number.
            # Get all consecutive digits and decimal if there is one.
            start_pos = self.cur_pos
            while self.peek().isdigit():
                self.next_char()
            if self.peek() == ".":
                self.next_char()

                # Must have at least one digit after decimal.
                if not self.peek().isdigit():
                    # Error!
                    self.abort("Illegal character in number.")
                while self.peek().isdigit():
                    self.next_char()

            token_text = self.source[start_pos : self.cur_pos + 1]  # Get the substring.
            token = LexToken(token_text, TokenType.NUMBER)
        elif self.cur_char.isalpha():
            # Leading character is a letter, so this must be an identifier or a keyword.
            # Get all consecutive alphanumeric characters.
            start_pos = self.cur_pos
            while self.peek().isalnum():
                self.next_char()

            # Check if the token is in the list of keywords.
            token_text = self.source[start_pos : self.cur_pos + 1]  # Get the substring.
            keyword = LexToken.check_if_keyword(token_text)
            if keyword is None:  # Identifier
                token = LexToken(token_text, TokenType.IDENT)
            else:  # Keyword
                token = LexToken(token_text, keyword)
        else:
            # Unknown token!
            self.abort("Unknown token: " + self.cur_char)

        self.next_char()
        return token
