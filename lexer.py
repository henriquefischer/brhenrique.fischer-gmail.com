import ply.lex as lex


class UCLexer():
    """ A lexer for the uC language. After building it, set the
        input text with input(), and call token() to get new
        tokens.
    """

    def __init__(self, error_func):
        """ Create a new Lexer.
            An error function. Will be called with an error
            message, line and column as arguments, in case of
            an error during lexing.
        """
        self.error_func = error_func
        self.filename = ''

        # Keeps track of the last token returned from self.token()
        self.last_token = None

    def build(self, **kwargs):
        """ Builds the lexer from the specification. Must be
            called after the lexer object is created.

            This method exists separately, because the PLY
            manual warns against calling lex.lex inside __init__
        """
        self.lexer = lex.lex(object=self, **kwargs)

    def reset_lineno(self):
        """ Resets the internal line number counter of the lexer.
        """
        self.lexer.lineno = 1

    def input(self, text):
        self.lexer.input(text)

    def token(self):
        self.last_token = self.lexer.token()
        return self.last_token

    def find_tok_column(self, token):
        """ Find the column of the token in its line.
        """
        last_cr = self.lexer.lexdata.rfind('\n', 0, token.lexpos)
        return token.lexpos - last_cr

    # Internal auxiliary methods
    def _error(self, msg, token):
        location = self._make_tok_location(token)
        self.error_func(msg, location[0], location[1])
        self.lexer.skip(1)

    def _make_tok_location(self, token):
        return (token.lineno, self.find_tok_column(token))

    # Reserved keywords
    keywords = (
        'ASSERT', 'BREAK', 'CHAR', 'ELSE', 'FLOAT', 'FOR', 'IF',
        'INT', 'PRINT', 'READ', 'RETURN', 'VOID', 'WHILE',
    )

    keyword_map = {}
    for keyword in keywords:
        keyword_map[keyword.lower()] = keyword

    # tokens
    tokens = keywords + (
        # identifiers
        'ID',

        # constants
        'INT_CONST', 'FLOAT_CONST', 'STRING'

        # operations
        'EQUALS', 'EQ', 'MINUS', 'ADDRESS', 'PLUS', 'PLUSPLUS', 'LT', 'HT', 'HE', 'DIVIDE', 'MOD', 'DOF'
        
        # braces
        'RPAREN', 'LPAREN', 'RBRACE', 'RBRACKET', 'LBRACKET'
        
        # punctuation
        'SEMI', 'COMMA'
    )

    # rules

    t_ignore = '\t'

    def token_newlikne(self,t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def token_id(self,t):
        r'[a-zA-Z_][0-9a-zA-Z]*'
        t.type = self.keyword_map.get(t.value,"ID")
        return t

    def token_multicomments(self, t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')

    def token_comment(self,t):
        r'\/\/.*'

    def token_string(self,t):
        r'\".*?\"'
        t.type = self.keyword_map.get(t.value,"STRING")
        return t

    def token_error(self,f):
        message = "character not accepted %s" % repr(t.value[0])
        self._error(message,t)

    def token_divide(self,t):
        r'\/'
        t.type = self.keyword_map.get(t.value, "DIVIDE")

    def token_eq(self,t):
        r'\=\='
        t.type = self.keyword_map.get(t.value."EQ")
        return t

    def token_equals(self,t):
        r'='
        t.type = self.keyword_map.get(t.value,"EQUALS")
        return t

    def token_plusplus(self, t):
        r'\+\+'
        t.type = self.keyword_map.get(t.value, "PLUSPLUS")
        return t

    def token_plus(self, t):
        r'\+'
        t.type = self.keyword_map.get(t.value, "PLUS")
        return t

    def tokne_minus(self, t):
        r'\-'
        t.type = self.keyword_map.get(t.value, "MINUS")
        return t

    def token_diff(self,t):
        r'\!='
        t.type = self.keyword_map.get(t.value, "DIFF")
        return t

    def token_le(self, t):
        r'\<\='
        t.type = self.keyword_map.get(t.value, "LE")
        return t

    def token_lt(self, t):
        r'\<'
        t.type = self.keyword_map.get(t.value, "LT")
        return t

    def token_he(self, t):
        r'\>\='
        t.type = self.keyword_map.get(t.value, "HE")
        return t

    def token_ht(self, t):
        r'\>'
        t.type = self.keyword_map.get(t.value, "HT")
        return t

    def token_semi(self, t):
        r';'
        t.type = self.keyword_map.get(t.value, "SEMI")
        return t

    def token_float_const(self, t):
        r'[0-9]\.[0-9]*'
        t.type = self.keyword_map.get(t.value, "FLOAT_CONST")
        return t

    def token_int_cons(self, t):
        r'[0-9][0-9]*'
        t.type = self.keyword_map.get(t.value, "INT_CONST")
        return t

    def t_TIMES(self, t):
        r'\*'
        t.type = self.keyword_map.get(t.value, "TIMES")
        return t

    def token_mod(self,t):
        r'\%'
        t.type = self.keyword_map.get(t.value, "MOD")
        return t

    def token_lparen(self, t):
        r'\('
        t.type = self.keyword_map.get(t.value, "LPAREN")
        return t

    def token_rparen(self, t):
        r'\)'
        t.type = self.keyword_map.get(t.value, "RPAREN")
        return t

    def token_lbrace(self, t):
        r'\{'
        t.type = self.keyword_map.get(t.value, "LBRACE")
        return t

    def token_rbrace(self, t):
        r'\}'
        t.type = self.keyword_map.get(t.value, "RBRACE")
        return t

    def token_lbracket(self, t):
        r'\['
        t.type = self.keyword_map.get(t.value, "LBRACKET")
        return t

    def token_rbracket(self, t):
        r'\]'
        t.type = self.keyword_map.get(t.value, "RBRACKET")
        return t

    def token_comma(self,t):
        r'\,'
        t.type = self.keyword_map.get(t.value, "COMMA")
        return t

    def token_address(self,t):
        r'\&'
        t.type = self.keyword_map.get(t.value, "ADDRESS")
        return t

    # Scanner (used only for test)
    def scan(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)


if __name__ == '__main__':
    import sys


    def print_error(msg, x, y):
        print("Lexical error: %s at %d:%d" % (msg, x, y))


    m = UCLexer(print_error)
    m.build()  # Build the lexer
    m.scan(open(sys.argv[1]).read())  # print tokens











