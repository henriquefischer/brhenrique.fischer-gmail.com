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

    # Test function get
    def get__item(self):
      return self

    # Reserved keywords
    keywords = (
        'ASSERT', 'BREAK', 'CHAR', 'ELSE', 'FLOAT', 'FOR', 'IF',
        'INT', 'PRINT', 'READ', 'RETURN', 'VOID', 'WHILE',
    )

    keyword_map = {}
    for keyword in keywords:
        keyword_map[keyword.lower()] = keyword

    #
    # All the tokens recognized by the lexer
    #
    tokens = keywords + (
        # Identifiers
        'ID',

        # constants
        'FLOAT_CONST', 'INT_CONST', 'STRING',


        # operations
        'PLUS', 'PLUSPLUS', 'MINUS', 'MINUSMINUS', 'TIMES', 'DIVIDE', 'ADDRESS', 'OR', 'AND', 'NOT', 'DIFF', 
        'EQUALS', 'LT', 'LE', 'HT', 'HE', 'EQ', 'ASSIGN_TIMES', 'ASSIGN_DIVIDE', 'ASSIGN_MOD', 'ASSIGN_PLUS', 'ASSIGN_MINUS',  'MOD', 

        # braces
        'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE', 

        # punctuation
        'SEMI', 'COMMA',
    )


    # Rules
    t_ignore = ' \t'

    def t_ASSIGN_PLUS(self, t):
      r'\+='
      t.type = self.keyword_map.get(t.value, "ASSIGN_PLUS")
      return t

    def t_PLUSPLUS(self, t):
      r'\+\+'
      t.type = self.keyword_map.get(t.value, "PLUSPLUS")
      return t

    def t_PLUS(self, t):
      r'\+'
      t.type = self.keyword_map.get(t.value, "PLUS")
      return t

    def t_ASSIGN_MINUS(self, t):
      r'-='
      t.type = self.keyword_map.get(t.value, "ASSIGN_MINUS")
      return t

    def t_MINUSMINUS(self,t):
      r'\-\-'
      t.type = self.keyword_map.get(t.value,"MINUSMINUS")
      return t

    def t_MINUS(self, t):
      r'\-'
      t.type = self.keyword_map.get(t.value, "MINUS")
      return t

    def t_ASSIGN_TIMES(self, t):
      r'\*='
      t.type = self.keyword_map.get(t.value,"ASSIGN_TIMES")
      return t

    def t_TIMES(self, t):
      r'\*'
      t.type = self.keyword_map.get(t.value, "TIMES")
      return t

    def t_ASSIGN_DIVIDE(self, t):
      r'/='
      t.type = self.keyword_map.get(t.value, "ASSIGN_DIVIDE")
      return t

    def t_DIVIDE(self,t):
      r'\/'
      t.type = self.keyword_map.get(t.value, "DIVIDE")
      return t

    def t_SEMI(self, t):
      r';'
      t.type = self.keyword_map.get(t.value, "SEMI")
      return t

    def t_COMMA(self,t):
      r'\,'
      t.type = self.keyword_map.get(t.value, "COMMA")
      return t

    def t_ADDRESS(self,t):
      r'\&'
      t.type = self.keyword_map.get(t.value, "ADDRESS")
      return t

    def t_OR(self, t):
      r'\|\|'
      t.type = self.keyword_map.get(t.value,"OR")
      return t

    def t_AND(self, t):
      r'\&\&'
      t.type = self.keyword_map.get(t.value,"AND")
      return t

    def t_NOT(self, t):
      r'!'
      t.type = self.keyword_map.get(t.value,"NOT")
      return t

    def t_DIFF(self,t):
      r'\!='
      t.type = self.keyword_map.get(t.value, "DIFF")
      return t

    def t_EQUALS(self, t):
      r'=='
      t.type = self.keyword_map.get(t.value, "EQUALS")
      return t

    def t_LT(self, t):
      r'\<'
      t.type = self.keyword_map.get(t.value, "LT")
      return t

    def t_LE(self, t):
      r'\<\='
      t.type = self.keyword_map.get(t.value, "LE")
      return t

    def t_HT(self, t):
      r'\>'
      t.type = self.keyword_map.get(t.value, "HT")
      return t

    def t_HE(self, t):
      r'\>\='
      t.type = self.keyword_map.get(t.value, "HE")
      return t

    def t_EQ(self, t):
      r'\='
      t.type = self.keyword_map.get(t.value, "EQ")
      return t

    def t_ASSIGN_MOD(self, t):
      r'%='
      t.type = self.keyword_map.get(t.value, "ASSIGN_MOD")
      return t

    def t_LPAREN(self, t):
      r'\('
      t.type = self.keyword_map.get(t.value, "LPAREN")
      return t

    def t_RPAREN(self, t):
      r'\)'
      t.type = self.keyword_map.get(t.value, "RPAREN")
      return t

    def t_LBRACKET(self, t):
      r'\['
      t.type = self.keyword_map.get(t.value, "LBRACKET")
      return t

    def t_RBRACKET(self, t):
      r'\]'
      t.type = self.keyword_map.get(t.value, "RBRACKET")
      return t

    def t_LBRACE(self, t):
      r'\{'
      t.type = self.keyword_map.get(t.value, "LBRACE")
      return t

    def t_RBRACE(self, t):
      r'\}'
      t.type = self.keyword_map.get(t.value, "RBRACE")
      return t

    def t_FLOAT_CONST(self, t):
      r'[0-9]\.[0-9]*'
      t.type = self.keyword_map.get(t.value, "FLOAT_CONST")
      return t

    def t_INT_CONST(self, t):
      r'[0-9][0-9]*'
      t.type = self.keyword_map.get(t.value, "INT_CONST")
      return t

    def t_MOD(self,t):
      r'\%'
      t.type = self.keyword_map.get(t.value, "MOD")
      return t

    def t_NEWLINE(self, t):
      r'\n+'
      t.lexer.lineno += t.value.count("\n")

    def t_ID(self, t):
      r'[a-zA-Z_][0-9a-zA-Z_]*'
      t.type = self.keyword_map.get(t.value, "ID")
      return t

    def t_multilinecomment(self, t):
      r'/\*(.|\n)*?\*/'
      t.lexer.lineno += t.value.count('\n')

    def t_comment(self,t):
      r'\/\/.*'

    def t_string(self,t):
      r'\".*?\"'
      t.type = self.keyword_map.get(t.value, "STRING")
      return t

    def t_error(self, t):
      msg = "Illegal character %s" % repr(t.value[0])
      self._error(msg, t)

    def scan(self, data):
        self.lexer.input(data)
        self.all = []
        while True:
            tok = self.lexer.token()
            if not tok:
              break
            self.all.append(tok)
        return self.all


if __name__ == '__main__':
    import sys


    def print_error(msg, x, y):
        print("Lexical error: %s at %d:%d" % (msg, x, y))


    m = UCLexer(print_error)
    m.build()  # Build the lexer
    m.scan(open(sys.argv[1]).read())  # print tokens

