import enum


# Token contains the original text and the type of token.
class LexToken:
    def __init__(self, token_text, token_kind):
        self.text = token_text  # The token's actual text. Used for identifiers, strings, and numbers.
        self.kind = token_kind  # The TokenType that this token is classified as.

    @staticmethod
    def check_if_keyword(token_text):
        for kind in TokenType:
            # Relies on all keyword enum values being 1XX.
            if kind.name == token_text and 100 <= kind.value < 200:
                return kind
        return None


# TokenType is our enum for all the types of tokens.
class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    # Keywords.
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111
    # Operators.
    EQ = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211
