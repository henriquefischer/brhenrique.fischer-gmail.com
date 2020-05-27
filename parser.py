from ast import *
from lexer import UCLexer
import ply.yacc as yacc


class UCParser:
    def __init__(self):
        self.errors = 0
        self.warnings = 0

    def _token_coord(self, p, token_idx):
        last_cr = p.lexer.lexdata.rfind('\n', 0, p.lexpos(token_idx))
        if last_cr < 0:
            last_cr = -1
        column = (p.lexpos(token_idx) - (last_cr))
        return Coord(p.lineno(token_idx), column).__str__()

    def print_error(self, msg, x, y):
        print("Lexical error: %s at %d:%d" % (msg, x, y))

    def show(self, buf=None, showcoord=True):
        print("I'm on show")

    def _type_modify_decl(self, decl, modifier):
        modifier_head = modifier
        modifier_tail = modifier

        while modifier_tail.type:
            modifier_tail = modifier_tail.type

        if isinstance(decl, VarDecl):
            modifier_tail.type = decl
            return modifier
        else:
            decl_tail = decl

            while not isinstance(decl_tail.type, VarDecl):
                decl_tail = decl_tail.type

            modifier_tail.type = decl_tail.type
            decl_tail.type = modifier_head
            return decl

    def p_error(self, p):
        if p:
            print("Error near the symbol %s" % p.value)
        else:
            print("Error at the end of input")

    def _build_function_definition(self, spec, decl, param_decls, body):
        declaration = self._build_declarations(spec=spec, decls=[dict(decl=decl, init=None)])[0]

        return FuncDef(spec=spec, decl=declaration, param_decls=param_decls, body=body, coord=decl.coord)

    def _build_declarations(self, spec, decls):
        declarations = []

        for decl in decls:
            if self.debug:
                print(decl)
            assert decl['decl'] is not None
            declaration = Decl(name=None, type=decl['decl'], init=decl.get('init'), coord=decl.get('coord'))

            if isinstance(declaration.type, Type):
                fixed_decl = declaration
            else:
                fixed_decl = self._fix_decl_name_type(declaration, spec)

            declarations.append(fixed_decl)

        return declarations

    def _fix_decl_name_type(self, decl, typename):
        type = decl
        while not isinstance(type, VarDecl):
            if self.debug:
                print("no while")
                print(type)

            type = type.type

        decl.name = type.declname
        type.type = typename

        return decl

    def parse(self, code, filename='', debug=0):
        self.debug = debug

        if debug:
            print("Code: {0}".format(code))
            print("Filename: {0}".format(filename))

        self.lexer = UCLexer(self.print_error)
        self.lexer.build()

        self.tokens = self.lexer.tokens
        self.precedence = (
             ('left', 'EQUALS', 'DIFF', 'LT', 'HT', 'LE', 'HE'),
             ('left', 'OR'),
             ('left', 'AND'),
             ('left', 'PLUS', 'MINUS'),
             ('left', 'TIMES', 'DIVIDE', 'MOD'),
         )

        parser = yacc.yacc(module=self, write_tables=False)
        result = parser.parse(code, tracking=False)

        return result

    def p_program(self, p):
        ''' program : global_declaration_list
        '''
        p[0] = Program(p[1])

    def p_global_declaration_list(self, p):
        ''' global_declaration_list : global_declaration
                                    | global_declaration_list global_declaration
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1]+[p[2]]

    def p_declarator(self, p):
        ''' declarator : pointer direct_declarator
                       | direct_declarator
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = self._type_modify_decl(decl=p[2], modifier=p[1])

    def p_declaration(self, p):
        ''' declaration :  decl_body SEMI
        '''
        p[0] = p[1]

    def p_global_declaration1(self, p):
        ''' global_declaration : function_definition
        '''
        p[0] = p[1]

    def p_global_declaration2(self, p):
        ''' global_declaration : declaration
        '''
        p[0] = GlobalDecl(p[1])

    def p_declaration_list(self, p):
        ''' declaration_list : declaration
                            | declaration_list declaration
        '''
        if len(p) == 2:
            p[0] = DeclList(p[1])
        else:
            p[0] = p[1]+[p[2]]

    def p_declaration_list_opt(self, p):
        ''' declaration_list_opt : declaration_list
                                 | empty
        '''
        p[0] = p[1]

    def p_block_item_list_opt(self, p):
        ''' block_item_list_opt : block_item_list
                                | empty
        '''
        p[0] = p[1]

    def p_decl_body(self, p):
        ''' decl_body : type_specifier init_declarator_list_opt
        '''
        spec = p[1]
        if p[2] is not None:
            decls = self._build_declarations(spec=spec, decls=p[2])
        p[0] = decls

    def p_init_declarator(self, p):
        ''' init_declarator : declarator
                            | declarator EQUALS initializer
        '''
        if len(p) == 2:
            p[0] = dict(decl=p[1], init=None)
        else:
            p[0] = dict(decl=p[1], init=p[3])

    def p_init_declarator_list_opt(self, p):
        ''' init_declarator_list_opt : init_declarator_list
                                     | empty
        '''
        p[0] = p[1]

    def p_init_declarator_list1(self, p):
        ''' init_declarator_list : init_declarator
        '''
        p[0] = [p[1]]

    def p_init_declarator_list2(self, p):
        ''' init_declarator_list : init_declarator_list COMMA init_declarator
        '''
        p[0] = p[1] + [p[3]]

    def p_block_item_list(self, p):
        ''' block_item_list : block_item
                            | block_item_list block_item
        '''
        if len(p) == 2 or p[2] == [None]:
            p[0] = p[1]
        else:
            p[0] = p[1] + p[2]

    def p_block_item(self, p):
        ''' block_item : statement
                       | declaration
        '''
        if isinstance(p[1], list):
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_function_definition_1(self, p):
        ''' function_definition : type_specifier declarator declaration_list_opt compound_statement
        '''
        p[0] = self._build_function_definition(spec=p[1], decl=p[2], param_decls=p[3], body=p[4])

    def p_function_definition_2(self, p):
        ''' function_definition : declarator declaration_list_opt compound_statement
        '''
        p[0] = self._build_function_definition(spec=dict(type=[Type(['void'], coord=self._token_coord(p, 1))], function=[]),
                                               decl=p[1], param_decls=p[2], body=p[3])

    def p_direct_declarator1(self, p):
        ''' direct_declarator : identifier
        '''
        p[0] = VarDecl(p[1], type=None, coord=self._token_coord(p, 1))

    def p_direct_declarator2(self, p):
        ''' direct_declarator : LPAREN declarator RPAREN
        '''
        p[0] = p[2]

    def p_direct_declarator3(self, p):
        ''' direct_declarator : direct_declarator LPAREN parameter_list RPAREN
        '''
        func = FuncDecl(params=p[3], type=None, coord=p[1].coord)

        p[0] = self._type_modify_decl(decl=p[1], modifier=func)

    def p_direct_declarator4(self, p):
        ''' direct_declarator : direct_declarator LBRACKET constant_expression_opt RBRACKET
        '''
        arr = ArrayDecl(type=None, tam=p[3], coord=p[1].coord)
        p[0] = self._type_modify_decl(decl=p[1], modifier=arr)

    def p_direct_declarator5(self, p):
        ''' direct_declarator : direct_declarator LPAREN id_list_opt RPAREN
        '''

        func = FuncDecl(params=p[3], type=None, coord=p[1].coord)
        p[0] = self._type_modify_decl(decl=p[1], modifier=func)

    def p_initializer1(self, p):
        ''' initializer : assignment_expression
        '''
        p[0] = p[1]

    def p_initializer2(self, p):
        ''' initializer : LBRACE initializer_list RBRACE
                        | LBRACE initializer_list COMMA RBRACE
        '''
        if p[2] is None:
            p[0] = InitList([], self._token_coord(p, 1))
        else:
            p[0] = p[2]

    def p_initializer_list1(self, p):
        ''' initializer_list : initializer
        '''
        if len(p) == 2:
            p[0] = InitList([p[1]], p[1].coord)

    def p_initializer_list2(self, p):
        ''' initializer_list : initializer_list COMMA initializer
        '''
        p[1].expression.append(p[3])
        p[0] = p[1]

    def p_assert_statement(self, p):
        ''' assert_statement : ASSERT expression SEMI
        '''
        p[0] = Assert(p[2], self._token_coord(p, 1))

    def p_print_statement(self, p):
        ''' print_statement : PRINT LPAREN expression_opt RPAREN SEMI
        '''
        expression = None
        if len(p) == 6:
            expression = [p[3]]
        p[0] = Print(expression, self._token_coord(p, 1))

    def p_read_statement(self, p):
        ''' read_statement : READ LPAREN argument_expression_list RPAREN SEMI
        '''
        p[0] = Read([p[3]], self._token_coord(p, 1))

    def p_statement(self, p):
        ''' statement : expression_statement
                      | compound_statement
                      | selection_statement
                      | iteration_statement
                      | jump_statement
                      | assert_statement
                      | print_statement
                      | read_statement
        '''
        p[0] = p[1]

    def p_postfix_expression1(self, p):
        ''' postfix_expression : primary_expression
        '''
        p[0] = p[1]

    def p_postfix_expression2(self, p):
        ''' postfix_expression : postfix_expression PLUSPLUS
                               | postfix_expression MINUSMINUS
        '''
 
        p[0] = UnaryOp('p' + p[2], p[1], p[1].coord)

    def p_postfix_expression3(self, p):
        ''' postfix_expression : postfix_expression LBRACKET expression RBRACKET
        '''
        p[0] = ArrayRef(p[1], p[3], p[1].coord)

    def p_postfix_expression4(self, p):
        ''' postfix_expression : postfix_expression LPAREN argument_expression_opt RPAREN
        '''
        p[0] = FuncCall(p[1], p[3], p[1].coord)

    def p_cast_expression1(self, p):
        ''' cast_expression : unary_expression
        '''
        p[0] = p[1]

    def p_cast_expression2(self, p):
        ''' cast_expression : LPAREN type_specifier RPAREN cast_expression
        '''
        p[0] = Cast(p[2], p[4], self._token_coord(p, 1))

    def p_identifier(self, p):
        ''' identifier : ID
        '''
        p[0] = ID(p[1], coord=self._token_coord(p, 1))

    def p_unary_operator(self, p):
        ''' unary_operator : ADDRESS
                           | TIMES
                           | PLUS
                           | MINUS
                           | NOT
        '''
        p[0] = p[1]

    def p_unary_expression1(self, p):
        ''' unary_expression : postfix_expression
        '''
        p[0] = p[1]

    def p_unary_expression2(self, p):
        ''' unary_expression : PLUSPLUS unary_expression
                             | MINUSMINUS unary_expression
                             | unary_operator cast_expression
        '''
        p[0] = UnaryOp(p[1], p[2], p[2].coord)

    def p_constant_expression(self, p):
        ''' constant_expression : binary_expression
        '''
        p[0] = p[1]

    def p_constant_expression_opt(self, p):
        ''' constant_expression_opt : constant_expression
                                    | empty
        '''
        p[0] = p[1]

    def p_binary_expression1(self, p):
        ''' binary_expression : cast_expression
        '''
        p[0] = p[1]

    def p_binary_expression2(self, p):
        ''' binary_expression : binary_expression TIMES binary_expression
                              | binary_expression DIVIDE binary_expression
                              | binary_expression MOD binary_expression
                              | binary_expression PLUS binary_expression
                              | binary_expression MINUS binary_expression
                              | binary_expression LT binary_expression
                              | binary_expression LE binary_expression
                              | binary_expression HT binary_expression
                              | binary_expression HE binary_expression
                              | binary_expression EQ binary_expression
                              | binary_expression DIFF binary_expression
                              | binary_expression AND binary_expression
                              | binary_expression OR binary_expression
        '''

        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    def p_type_specifier(self, p):
        ''' type_specifier : VOID
                           | INT
                           | FLOAT
                           | CHAR
        '''
        p[0] = Type([p[1]], coord=self._token_coord(p, 1))

    def p_constant1(self, p):
        ''' constant : INT_CONST
        '''
        p[0] = Constant('int', p[1], self._token_coord(p, 1))

    def p_constant2(self, p):
        ''' constant : FLOAT_CONST
        '''
        p[0] = Constant('float', p[1], self._token_coord(p, 1))

    def p_constant3(self, p):
        ''' constant : CHAR_CONST
        '''
        p[0] = Constant('char', p[1], self._token_coord(p, 1))

    def p_selection_statement(self, p):
        ''' selection_statement : IF LPAREN expression RPAREN statement
                                | IF LPAREN expression RPAREN statement ELSE statement
        '''
        if len(p) == 6:
            p[0] = If(p[3], p[5], None, self._token_coord(p, 1))
        elif len(p) == 8:
            p[0] = If(p[3], p[5], p[7], self._token_coord(p, 1))

    def p_iteration_statement1(self, p):
        ''' iteration_statement : WHILE LPAREN expression RPAREN statement
        '''
        p[0] = While(p[3], p[5], self._token_coord(p, 1))

    def p_iteration_statement2(self, p):
        ''' iteration_statement : FOR LPAREN expression_opt SEMI expression_opt SEMI expression_opt RPAREN statement
        '''
        p[0] = For(p[3], p[5], p[7], p[9], self._token_coord(p, 1))

    def p_iteration_statement3(self, p):
        ''' iteration_statement : FOR LPAREN declaration expression_opt SEMI expression_opt RPAREN statement
        '''
        p[0] = For(DeclList(p[3], self._token_coord(p, 1)), p[4], p[6], p[8], self._token_coord(p, 1))

    def p_argument_expression_opt(self, p):
        ''' argument_expression_opt : argument_expression_list
                                    | empty
        '''
        if p[1] is not None:
            p[0] = p[1]

    def p_argument_expression_list(self, p):
        ''' argument_expression_list : assignment_expression
                                     | argument_expression_list COMMA assignment_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            if not isinstance(p[1], ExprList):
                p[1] = ExprList([p[1]], p[1].coord)

            p[1].expression.append(p[3])
            p[0] = p[1]

    def p_primary_expression1(self, p):
        ''' primary_expression : identifier
                               | constant
                               | string_literal
        '''
        p[0] = p[1]

    def p_primary_expression2(self, p):
        ''' primary_expression : LPAREN expression RPAREN
        '''
        p[0] = p[2]

    def p_assignment_operator(self, p):
        ''' assignment_operator : EQUALS
                               | ASSIGN_TIMES
                               | ASSIGN_DIVIDE
                               | ASSIGN_MOD
                               | ASSIGN_PLUS
                               | ASSIGN_MINUS
        '''
        p[0] = p[1]

    def p_assignment_expression1(self, p):
        ''' assignment_expression : binary_expression
        '''
        p[0] = p[1]

    def p_assignment_expression2(self, p):
        ''' assignment_expression : unary_expression assignment_operator assignment_expression
        '''
        p[0] = Assignment(p[2], p[1], p[3], p[1].coord)

    def p_jump_statement1(self, p):
        ''' jump_statement : BREAK SEMI
        '''
        p[0] = Break(self._token_coord(p, 1))

    def p_jump_statement2(self, p):
        ''' jump_statement : RETURN expression SEMI
        '''
        p[0] = Return(p[2], self._token_coord(p, 1))

    def p_jump_statement_3(self, p):
        ''' jump_statement : RETURN SEMI
        '''
        p[0] = Return(None, self._token_coord(p, 1))

    def p_parameter_list_1(self, p):
        ''' parameter_list : parameter_declaration
        '''
        p[0] = ParamList([p[1]], coord=self._token_coord(p, 1))

    def p_parameter_list_2(self, p):
        ''' parameter_list : parameter_list COMMA parameter_declaration
        '''
        p[1].params.append(p[3])
        p[0] = p[1]

    def p_id_list_opt(self, p):
        ''' id_list_opt : id_list
                        | empty
        '''
        p[0] = p[1]

    def p_id_list(self, p):
        ''' id_list : identifier
                    | id_list identifier
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_parameter_declaration(self, p):
        ''' parameter_declaration : type_specifier declarator
        '''
        spec = p[1]

        p[0] = self._build_declarations(spec=spec, decls=[dict(decl=p[2])])[0]

    def p_compound_statement(self, p):
        ''' compound_statement : LBRACE block_item_list_opt RBRACE
        '''
        p[0] = Compound(block_items=p[2], coord=self._token_coord(p, 1))

    def p_expression_statement(self, p):
        ''' expression_statement : expression_opt SEMI
        '''
        if p[1] is None:
            p[0] = EmptyStatement(self._token_coord(p, 2))
        else:
            p[0] = p[1]

    def p_expression_opt(self, p):
        ''' expression_opt : expression
                           | empty
        '''
        p[0] = p[1]

    def p_expression_1(self, p):
        ''' expression : assignment_expression
        '''
        if len(p) == 2:
            p[0] = p[1]

    def p_expression_2(self, p):
        ''' expression : expression COMMA assignment_expression
        '''
        if not isinstance(p[1], ExprList):
            p[1] = ExprList([p[1]], p[1].coord)

        p[1].expression.append(p[3])
        p[0] = p[1]

    def p_string_literal(self, p):
        ''' string_literal : STRING
        '''
        p[0] = Constant('string', p[1], self._token_coord(p, 1))

    def p_pointer_1(self, p):
        ''' pointer : TIMES pointer
        '''
        tail_type = p[3]
        while tail_type.type is not None:
            tail_type = tail_type.type
        tail_type.type = PtrDecl(type=None, coord=self._token_coord(p, 1))
        p[0] = p[2]

    def p_pointer_2(self, p):
        ''' pointer : TIMES
        '''
        p[0] = PtrDecl(type=None, coord=self._token_coord(p, 1))

    def p_empty(self, p):
        ''' empty :'''
        pass

