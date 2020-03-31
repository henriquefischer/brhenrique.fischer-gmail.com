import yacc as yacc
import lexer as UCLexer 
tokens = UCLexer.UCLexer.tokens

# Done
def p_program(p):
    """ program  : global_declaration_list
    """
    p[0] = Program(p[1])

# Done
def p_global_declaration_list(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_function_definition(p):
    """ <function_definition> ::= {<type_specifier>}? <declarator> {<declaration>}* <compound-statement>"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_type_specifier(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = type(p)

def p_declarator(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_constant_expression(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def binary_expression(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_cast_expression(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_unary_expression(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_postfix_expression(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]
    
def p_primar_expression(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_constant(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_type_specifier(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = type(p)

def p_declarator(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_constant_expression(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_binary_expression(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_cast_expression(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_assignment_expression(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_assignment_operator(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]
    
def p_unary_operator(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_parameter_list(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_parameter_declaration(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = type(p)

def p_declaration(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_init_declarator(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_initializer(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_initializer_list(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_compound_statement(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

# TODO expression and compound
def p_statement(p):
    """<statement> ::= <expression_statement>
        | <compound_statement>
        | <selection_statement>
        | <iteration_statement>
        | <jump_statement>
        | <assert_statement>
        | <print_statement>
        | <read_statement>"""
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
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_selection_statement(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_iteration_statement(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = type(p)

def p_jump_statement(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_assert_statement(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def print_statement(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_read_statement(p):
    """ global_declaration_list : global_declaration
                                | global_declaration_list global_declaration
    """
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

yacc.yacc()
data = "x = 3*4+5*6"
yacc.parse(data)