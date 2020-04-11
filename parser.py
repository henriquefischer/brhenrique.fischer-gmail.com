import ply.yacc as yacc
import lexer as UCLexer 
tokens = UCLexer.UCLexer.tokens

class Parser(object):
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
    # Done
    def p_program(self,p):
        """ program  : global_declaration_list
        """
        p[0] = Program(p[1])

    # # Done
    def p_global_declaration_list(self,p):
        """ global_declaration_list : global_declaration
                                    | global_declaration_list global_declaration
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]
        

    def p_global_declaration(self,p):
        """ global_declaration  : function_definition
                                | declaration"""
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_function_definition(self,p):
        """ function_definition : declarator compound_statement
                                | declarator declaration_list compound_statement
                                | type_specifier declarator compound_statement
                                | type_specifier declarator declaration_list compound_statement
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_declaration_list(self,p):
        """ declaration_list    : declaration
                                | declaration_list declaration
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]
        
    def p_statement_list(self,p):
        """ statement_list  : statement
                            | statement_list statement
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_type_specifier(self,p):
        """ type_specifier  : VOID
                            | CHAR
                            | INT
                            | FLOAT
        """
        p[0] = type(p)

    def p_identifier(self,p):
        """ identifier : ID """
        p[0] = ID(p[1], lineno=p.lineno(1))

    def p_frase(self,p):
        """ frase : STRING """
        p[0] = STRING(p[1], lineno=p.lineno(1))

    def p_int_const(self,p):
        """ int_const : INT_CONST """
        p[0] = INT_CONST(p[1], lineno=p.lineno(1))

    def p_float_const(self,p):
        """ float_const : FLOAT_CONST """
        p[0] = FLOAT_CONST(p[1], lineno=p.lineno(1))

    # Talvez tenha que criar identifier_list
    def p_declarator(self,p):
        """ declarator  : identifier
                        | LPAREN declarator RPAREN
                        | declarator RBRACKET LBRACKET
                        | declarator RBRACKET constant_expression LBRACKET
                        | declarator LPAREN parameter_list RPAREN
                        | declarator LPAREN RPAREN
                        | declarator LPAREN identifier RPAREN
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_constant_expression(self,p):
        """ constant_expression : binary_expression
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_binary_expression(self,p):
        """ binary_expression   : cast_expression
                                | binary_expression TIMES binary_expression
                                | binary_expression DIVIDE binary_expression
                                | binary_expression MOD binary_expression
                                | binary_expression MINUS binary_expression
                                | binary_expression PLUS binary_expression
                                | binary_expression LT binary_expression
                                | binary_expression LE binary_expression
                                | binary_expression HT binary_expression
                                | binary_expression HE binary_expression
                                | binary_expression EQUALS binary_expression
                                | binary_expression DIFF binary_expression
                                | binary_expression AND binary_expression
                                | binary_expression OR binary_expression
        """
        if p[2] == '*':
            p[0] = p[1] * p[3]
        elif p[2] == '/':
            p[0] = p[1] / p[3]
        elif p[2] == '%':
            p[0] = p[1] % p[3]
        elif p[2] == '-':
            p[0] = p[1] - p[3]
        elif p[2] == '+':
            p[0] = p[1] + p[3]
        elif p[2] == '<':
            p[0] = p[1] < p[3]
        elif p[2] == '<=':
            p[0] = p[1] <= p[3]
        elif p[2] == '>':
            p[0] = p[1] > p[3]
        elif p[2] == '>=':
            p[0] = p[1] >= p[3]
        elif p[2] == '==':
            p[0] = p[1] == p[3]
        elif p[2] == '!=':
            p[0] = p[1] != p[3]
        elif p[2] == '&&':
            p[0] = p[1] and p[3]
        elif p[2] == '||':
            p[0] = p[1] or p[3]

    def p_cast_expression(self,p):
        """ cast_expression : unary_expression
                            | LPAREN type_specifier RPAREN cast_expression
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_unary_expression(self,p):
        """ unary_expression    : postfix_expression
                                | PLUSPLUS unary_expression
                                | MINUSMINUS unary_expression
                                | unary_operator cast_expression
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_postfix_expression(self,p):
        """ postfix_expression  : primary_expression
                                | postfix_expression LBRACKET expression RBRACKET
                                | postfix_expression LPAREN RPAREN
                                | postfix_expression LPAREN assignment_expression_list RPAREN
                                | postfix_expression PLUSPLUS
                                | postfix_expression MINUSMINUS
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]
        
    def p_primary_expression(self,p):
        """ primary_expression  : identifier
                                | int_const
                                | float_const
                                | frase
                                | LPAREN expression RPAREN
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_compound_statement(self,p):
        """ compound_statement  : LBRACE RBRACE
                                | LBRACE declaration_list RBRACE
                                | LBRACE statement_list RBRACE
                                | LBRACE declaration_list statement_list RBRACE
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]


    def p_assignment_expression_list(self,p):
        """ assignment_expression_list  : assignment_expression
                                        | assignment_expression_list assignment_expression
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_assignment_expression(self,p):
        """ assignment_expression   : binary_expression
                                    | unary_expression assignment_operator assignment_expression
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_expression(self,p):
        """ expression  : assignment_expression
                        | expression COMMA assignment_expression
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_assignment_operator(self,p):
        """ assignment_operator : EQ
                                | ASSIGN_TIMES
                                | ASSIGN_DIVIDE
                                | ASSIGN_MOD
                                | ASSIGN_PLUS
                                | ASSIGN_MINUS
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]
        
    def p_unary_operator(self,p):
        """ unary_operator  : ADDRESS
                            | TIMES
                            | PLUS
                            | MINUS
                            | NOT
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_parameter_list(self,p):
        """ parameter_list  : parameter_declaration
                            | parameter_list COMMA parameter_declaration
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_parameter_declaration(self,p):
        """ parameter_declaration   : type_specifier declarator
        """
        p[0] = type(p)

    def p_declaration(self,p):
        """ declaration : type_specifier SEMI
                        | type_specifier init_declarator SEMI
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_init_declarator(self,p):
        """ init_declarator : declarator
                            | declarator EQ initializer
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_initializer(self,p):
        """ initializer : assignment_expression
                        | LBRACE initializer_list RBRACE
                        | LBRACE initializer_list COMMA RBRACE
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_initializer_list(self,p):
        """ initializer_list    : initializer
                                | initializer_list COMMA initializer
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_statement(self,p):
        """statement    : expression_statement
                        | iteration_statement
                        | compound_statement
                        | jump_statement
                        | assert_statement
                        | print_statement
                        | selection_statement
                        | read_statement"""
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]
        # p[0] = p_selection_statement(self,p) if p[1] == 'if'
        # elif p[1] == 'while'
        #     p[0] = self.p_iteration_statement(self,p)
        # elif p[1] == 'break'
        #     p[0] = self.p_iteration_statement(self,p)
        # elif p[1] == 'assert'
        #     p[0] = self.p_iteration_statement(self,p)
        # elif p[1] == 'print'
        #     p[0] = self.p_iteration_statement(self,p)
        # elif p[1] == 'read'
        #     p[0] = self.p_iteration_statement(self,p)
        # elif
        
    def p_expression_statement(self,p):
        """ expression_statement    : SEMI
                                    | expression SEMI"""
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_selection_statement(self,p):
        """ selection_statement : IF LPAREN expression RPAREN statement
                            | IF LPAREN expression RPAREN statement ELSE statement
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_iteration_statement(self,p):
        """ iteration_statement : WHILE LPAREN expression RPAREN statement
                                | FOR LPAREN SEMI SEMI RPAREN statement
                                | FOR LPAREN expression SEMI SEMI RPAREN statement
                                | FOR LPAREN SEMI expression SEMI RPAREN statement
                                | FOR LPAREN SEMI SEMI expression RPAREN statement
                                | FOR LPAREN expression SEMI expression SEMI RPAREN statement
                                | FOR LPAREN expression SEMI SEMI expression RPAREN statement
                                | FOR LPAREN SEMI expression SEMI expression RPAREN statement
                                | FOR LPAREN expression SEMI expression SEMI expression RPAREN statement
        """
        p[0] = type(p)

    def p_jump_statement(self,p):
        """ jump_statement  : BREAK
                            | RETURN
                            | RETURN expression
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_error(self,p):
        """ID LPAREN error RPAREN"""
        print "Syntax error in arguments\n"

    def p_assert_statement(self,p):
        """ assert_statement : ASSERT expression SEMI
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_print_statement(self,p):
        """ print_statement : PRINT LPAREN expression RPAREN SEMI
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_read_statement(self,p):
        """ read_statement : READ LPAREN declarator_list RPAREN SEMI"""
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_declarator_list(self,p):
        """ declarator_list : declarator
                            | declarator_list declarator
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    # def scan(self, data):
    #     self.lexer.input(data)
    #     while True:
    #         tok = self.lexer.token()
    #         if not tok:
    #             break
    #         print(tok)

    def print_error(msg, x, y):
        print("Lexical error: %s at %d:%d" % (msg, x, y))

    def __init__(self):
        self.lexer = UCLexer.UCLexer(print_error)
        self.lexer.build()
        self.tokens = UCLexer.UCLexer.tokens
        self.parser = yacc.yacc(module=self)

    def parse(self):
        import sys
        msg = open(sys.argv[1]).read()
        token = self.lexer.scan(msg)
        print(token)    
        return  self.parser.parse(token)

if __name__ == '__main__':

    def print_error(msg, x, y):
        print("Lexical error: %s at %d:%d" % (msg, x, y))

    # lexer = UCLexer.UCLexer(print_error)
    parser = Parser()

    while True:
        try:
            text = input('Parse > ')
            result = parser.parse()
            print(result)
        except EOFError:
            break