import yacc as yacc
import lexer as UCLexer 
tokens = UCLexer.UCLexer.tokens

class UCParser():
    def __init__(self, error_func):
        """ Create a new Parser.
            An error function. Will be called with an error
            message, line and column as arguments, in case of
            an error during lexing.
        """
        yacc.yacc()
        data = "x = 3*4+5*6"
        yacc.parse(data)

    def build(self):
        yacc.yacc()
        data = "x = 3*4+5*6"
        yacc.parse(data)

    def p_type_specifier(self,p):
        """ type_specifier  : VOID
                            | CHAR
                            | INT
                            | FLOAT
        """
        p[0] = type(self,p)

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
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_constant_expression(self,p):
        """ constant_expression : binary_expression
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

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
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_cast_expression(self,p):
        """ cast_expression : unary_expression
                            | LPAREN type_specifier RPAREN cast_expression
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_unary_expression(self,p):
        """ unary_expression    : postfix_expression
                                | PLUSPLUS unary_expression
                                | MINUSMINUS unary_expression
                                | unary_operator cast_expression
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_postfix_expression(self,p):
        """ postfix_expression  : primary_expression
                                | postfix_expression LBRACKET expression RBRACKET
                                | postfix_expression LPAREN RPAREN
                                | postfix_expression LPAREN assignment_expression_list RPAREN
                                | postfix_expression PLUSPLUS
                                | postfix_expression MINUSMINUS
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]
        
    def p_primary_expression(self,p):
        """ primary_expression  : identifier
                                | int_const
                                | float_const
                                | frase
                                | LPAREN expression RPAREN
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_assignment_expression_list(self,p):
        """ assignment_expression_list  : assignment_expression
                                        | assignment_expression_list assignment_expression
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_assignment_expression(self,p):
        """ assignment_expression   : binary_expression
                                    | unary_expression assignment_operator assignment_expression
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_expression(self,p):
        """ expression  : assignment_expression
                        | expression COMMA assignment_expression
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_assignment_operator(self,p):
        """ assignment_operator : EQ
                                | ASSIGN_TIMES
                                | ASSIGN_DIVIDE
                                | ASSIGN_MOD
                                | ASSIGN_PLUS
                                | ASSIGN_MINUS
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]
        
    def p_unary_operator(self,p):
        """ unary_operator  : ADDRESS
                            | TIMES
                            | PLUS
                            | MINUS
                            | NOT
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_parameter_list(self,p):
        """ parameter_list  : parameter_declaration
                            | parameter_list COMMA parameter_declaration
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_parameter_declaration(self,p):
        """ parameter_declaration   : type_specifier declarator
        """
        p[0] = type(self,p)

    def p_declaration(self,p):
        """ declaration : type_specifier SEMI
                        | type_specifier init_declarator SEMI
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_init_declarator(self,p):
        """ init_declarator : declarator
                            | declarator EQ initializer
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_initializer(self,p):
        """ initializer : assignment_expression
                        | LBRACE initializer_list RBRACE
                        | LBRACE initializer_list COMMA RBRACE
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_initializer_list(self,p):
        """ initializer_list    : initializer
                                | initializer_list COMMA initializer
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_jump_statement(self,p):
        """ jump_statement  : BREAK
                            | RETURN
                            | RETURN expression
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_error(self,p):
        """ID LPAREN error RPAREN"""
        print "Syntax error in arguments\n"

    def p_assert_statement(self,p):
        """ assert_statement : ASSERT expression SEMI
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_print_statement(self,p):
        """ print_statement : PRINT LPAREN expression RPAREN SEMI
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_read_statement(self,p):
        """ read_statement : READ LPAREN declarator_list RPAREN """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]

    def p_declarator_list(self,p):
        """ declarator_list : declarator_list
                            | declarator_list declarator
        """
        p[0] = [p[1]] if len(self,p) == 2 else p[1] + [p[2]]



if __name__ == '__main__':
    import sys

    def print_error(msg, x, y):
        print("Error: %s at %d:%d" % (msg, x, y))

    m = UCParser(print_error)
    m.build()  # Build the lexer
    m.scan(open(sys.argv[1]).read())  # print tokens