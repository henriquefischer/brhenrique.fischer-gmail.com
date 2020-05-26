import ply.lex as lex

class UCLexer:
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

    keywords = ('ASSERT', 'BREAK', 'PRINT', 'READ', 'FOR', 'RETURN', 'WHILE', 'IF', 'ELSE',
                'VOID', 'INT', 'FLOAT', 'CHAR')

    tokens = (
        # identifiers
        'ID', 
        
        # constant
        'INT_CONST', 'FLOAT_CONST', 'CHAR_CONST', 'STRING','ASSIGN_TIMES', 'PLUSPLUS', 'MINUSMINUS',
        'ASSIGN_DIVIDE', 'ASSIGN_MOD', 'ASSIGN_PLUS', 'ASSIGN_MINUS', 
        'DIFF', 'AND', 'OR', 'ADDRESS', 'NOT', 'EQUALS',
        'LT', 'HT', 'LE', 'HE', 'EQ',

        # operations
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE','MOD',

        #braces
        'LPAREN', 'RPAREN','LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET', 

        #punctuation
        'COMMA', 'SEMI',     
      ) + keywords

    keyword_map = {}
    for keyword in keywords:
        keyword_map[keyword.lower()] = keyword

    # Regular expression rules for simple tokens
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MOD = r'%'
    t_PLUSPLUS = r'\+\+'
    t_MINUSMINUS = r'--'
    t_ASSIGN_PLUS = r'\+='
    t_ASSIGN_MINUS = r'-='
    t_ASSIGN_TIMES = r'\*='
    t_ASSIGN_DIVIDE = r'\/='
    t_ASSIGN_MOD = r'%='
    t_EQUALS = r'='
    t_AND = r'\&\&'
    t_OR = r'\|\|'
    t_ADDRESS = r'\&'
    t_NOT = r'!'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_LBRACE = r'{'
    t_RBRACE = r'}'
    t_COMMA = r','
    t_SEMI = r';'
    t_LT = r'<'
    t_HT = r'>'
    t_LE = r'<='
    t_HE = r'>='
    t_EQ = r'=='
    t_DIFF = r'!='

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.keyword_map.get(t.value, "ID")
        return t

    def t_FLOAT_CONST(self, t):
        r'\d*\.\d*'
        t.type = self.keyword_map.get(t.value, "FLOAT_CONST")
        return t

    def t_INT_CONST(self, t):
        r'[0-9]+'
        t.type = self.keyword_map.get(t.value, "INT_CONST")
        return t

    def t_CHAR_CONST(self, t):
        r'\'.{1}\''
        t.type = self.keyword_map.get(t.value, "CHAR_CONST")
        return t

    def t_STRING(self, t):
        r'\"[^"]*\"'
        t.type = self.keyword_map.get(t.value, "STRING")
        return t

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_comment(self, t):
        r'(\/\*(.|\n)*?\*\/)|(\/\/.*)'
        pass

    # # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t'

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

'''
    def scan(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok) # Test print 
if __name__ == '__main__':
    import sys
    def print_error(msg, x, y):
        print("Lexical error: %s at %d:%d" % (msg, x, y))
    m = UCLexer(print_error)
    m.build()  # Build the lexer
    m.scan(open(sys.argv[1]).read())  # print tokens
'''