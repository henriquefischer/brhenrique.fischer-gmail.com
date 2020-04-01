import yacc as yacc
import lexer as UCLexer 
tokens = UCLexer.UCLexer.tokens

# Done
def p_program(p):
    """ program  : global_declaration_list
    """
    p[0] = Program(p[1])

# # Done
def p_global_declaration_list(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]
    

def p_global_declaration(p):
    """ global_declaration  : function_definition
                            | declaration"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_function_definition(p):
    """ function_definition : declarator compound_statement
                            | declarator declaration_list compound_statement
                            | type_specifier declarator compound_statement
                            | type_specifier declarator declaration_list compound_statement
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_declaration_list(p):
    """ declaration_list    : declaration
                            | declaration_list declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]
    
def p_statement_list(p):
    """ statement_list  : statement_list
                        | statement_list statement
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_type_specifier(p):
    """ type_specifier  : VOID
                        | CHAR
                        | INT
                        | FLOAT
    """
    p[0] = type(p)

def p_identifier(p):
    """ identifier : ID """
    p[0] = ID(p[1], lineno=p.lineno(1))

def p_frase(p):
    """ frase : STRING """
    p[0] = ID(p[1], lineno=p.lineno(1))

def p_int_const(p):
    """ int_const : INT_CONST """
    p[0] = INT_CONST(p[1], lineno=p.lineno(1))

def p_float_const(p):
    """ float_const : FLOAT_CONST """
    p[0] = FLOAT_CONST(p[1], lineno=p.lineno(1))

# Talvez tenha que criar identifier_list
def p_declarator(p):
    """ declarator  : identifier
                    | LPAREN declarator RPAREN
                    | declarator RBRACKET LBRACKET
                    | declarator RBRACKET constant_expression LBRACKET
                    | declarator LPAREN parameter_list RPAREN
                    | declarator LPAREN RPAREN
                    | declarator LPAREN identifier RPAREN
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_constant_expression(p):
    """ constant_expression : binary_expression
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_binary_expression(p):
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
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_cast_expression(p):
    """ cast_expression : unary_expression
                        | LPAREN type_specifier RPAREN cast_expression
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_unary_expression(p):
    """ unary_expression    : postfix_expression
                            | PLUSPLUS unary_expression
                            | MINUSMINUS unary_expression
                            | unary_operator cast_expression
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_postfix_expression(p):
    """ postfix_expression  : primary_expression
                            | postfix_expression LBRACKET expression RBRACKET
                            | postfix_expression LPAREN RPAREN
                            | postfix_expression LPAREN assignment_expression_list RPAREN
                            | postfix_expression PLUSPLUS
                            | postfix_expression MINUSMINUS
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]
    
def p_primary_expression(p):
    """ primary_expression  : identifier
                            | int_const
                            | float_const
                            | frase
                            | LPAREN expression RPAREN
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_compound_statement(p):
    """ compound_statement  : LBRACE RBRACE
                            | LBRACE declaration_list RBRACE
                            | LBRACE statement_list RBRACE
                            | LBRACE declaration_list statement_list RBRACE
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]


def p_assignment_expression_list(p):
    """ assignment_expression_list  : assignment_expression
                                    | assignment_expression_list assignment_expression
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_assignment_expression(p):
    """ assignment_expression   : binary_expression
                                | unary_expression assignment_operator assignment_expression
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_expression(p):
    """ expression  : assignment_expression
                    | expression COMMA assignment_expression
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_assignment_operator(p):
    """ assignment_operator : EQ
                            | ASSIGN_TIMES
                            | ASSIGN_DIVIDE
                            | ASSIGN_MOD
                            | ASSIGN_PLUS
                            | ASSIGN_MINUS
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]
    
def p_unary_operator(p):
    """ unary_operator  : ADDRESS
                        | TIMES
                        | PLUS
                        | MINUS
                        | NOT
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_parameter_list(p):
    """ parameter_list  : parameter_declaration
                        | parameter_list COMMA parameter_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_parameter_declaration(p):
    """ parameter_declaration   : type_specifier declarator
    """
    p[0] = type(p)

def p_declaration(p):
    """ declaration : type_specifier SEMI
                    | type_specifier init_declarator SEMI
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_init_declarator(p):
    """ init_declarator : declarator
                        | declarator EQ initializer
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_initializer(p):
    """ initializer : assignment_expression
                    | LBRACE initializer_list RBRACE
                    | LBRACE initializer_list COMMA RBRACE
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_initializer_list(p):
    """ initializer_list    : initializer
                            | initializer_list COMMA initializer
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

# # TODO expression and compound
                    # | compound_statement
                    # | selection_statement
                    # | iteration_statement
def p_statement(p):
    """statement    : expression_statement
                    | jump_statement
                    | assert_statement
                    | print_statement
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
    
def p_expression_statement(p):
    """ expression_statement    : SEMI
                                | expression SEMI"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

# def p_selection_statement(p):
#     """ global_declaration_list : global_declaration
#                                 | global_declaration_list global_declaration
#     """
#     p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

# def p_iteration_statement(p):
#     """ global_declaration_list : global_declaration
#                                 | global_declaration_list global_declaration
#     """
#     p[0] = type(p)

def p_jump_statement(p):
    """ jump_statement  : BREAK
                        | RETURN
                        | RETURN expression
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_error(p):
    """ID LPAREN error RPAREN"""
    print "Syntax error in arguments\n"

def p_assert_statement(p):
    """ assert_statement : ASSERT expression SEMI
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_print_statement(p):
    """ print_statement : PRINT LPAREN expression RPAREN SEMI
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_read_statement(p):
    """ read_statement : READ LPAREN declarator_list RPAREN """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_declarator_list(p):
    """ declarator_list : declarator_list
                        | declarator_list declarator
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

yacc.yacc()
data = "x = 3*4*6"
yacc.parse(data)