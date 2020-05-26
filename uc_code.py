from ast import *
from uc_sema import *


class GenerateCode(NodeVisitor):
    '''
    Node visitor class that creates 3-address encoded instruction sequences.
    '''
    def __init__(self):
        super(GenerateCode, self).__init__()

        # version dictionary for temporaries
        self.fname = 'main'  # We use the function name as a key
        self.versions = {self.fname:0}

        # The generated code (list of tuples)
        self.code = []
        self.text = []

        self.assign_op = {"+=":"ASSIGN_PLUS", "-=":"ASSIGN_MINUS", "*=":"ASSIGN_TIMES", "/=":"ASSIGN_DIVIDE", "%=":"ASSIGN_MOD"}
        self.unary_op = {"-":"MINUS", "--":"MINUSMINUS", "+":"PLUS", "++":"PLUSPLUS", "p++":"PLUS", "p--": "MINUS","!":"NOT"}
        self.binary_op = {"+":"PLUS", "-":"MINUS", "*":"TIMES", "/":"DIVIDE", "%":"MOD", "==":"EQ", "!=":"DIFF",
                                "<":"LT", ">":"HT", "<=":"LE", ">=":"HE","&&":"AND", "||":"OR"}

        self.return_location = None
        self.return_label = None
        self.items = []
        self.step_allocation = None

    def clean(self):
        self.items = []
    
    def enqueue(self, item):
        self.items.insert(0,item)
    
    def dequeue(self):
        return self.items.pop()

    def new_temp(self):
        '''
        Create a new temporary variable of a given scope (function name).
        '''
        if self.fname not in self.versions:
            self.versions[self.fname] = 0
        name = "%" + "%d" % (self.versions[self.fname])
        self.versions[self.fname] += 1
        return name

    def new_text(self):
        name = "@.str." + "%d" % (self.versions['main'])
        self.versions['main'] +=1
        return name

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        if node is None:
            return 'void'
        else:
            return ''.join(self.visit(c) for c_name, c in node.children())

    # You must implement visit_Nodename methods for all of the other
    # AST nodes.  In your code, you will need to make instructions
    # and append them to the self.code list.
    #
    # A few sample methods follow.  You may have to adjust depending
    # on the names of the AST nodes you've defined.

    def __loadRefer(self, node):
        node.gen_location = self.new_temp()
        inst = ('load_' + node.expression.type.names[-1].typename + "_*", 
                node.expression.gen_location, node.gen_location)
        self.code.append(inst)

    
    def _readLocal(self, source):
        target = self.new_temp()
        typename = source.type.names[-1].typename
        self.code.append(('read_' + typename, target))
        if isinstance(source, ArrayRef):
            typename += "_*"
        if isinstance(source, UnaryOp) and source.op == "*":
            self.__loadRefer(source)
        self.code.append(('store_'+ typename, target, source.gen_location))


    def _storeLocation(self, typename, init, target):
        self.visit(init)
        if isinstance(init, ID) or isinstance(init, ArrayRef):
            self.visit_LoadLocation(init)
        elif isinstance(init, UnaryOp) and init.op == '*':
            self.__loadRefer(init)
        inst = ('store_' + typename, init.gen_location, target)
        self.code.append(inst)


    def visit_LoadLocation(self, node):
        target = self.new_temp()
        typename = node.type.names[-1].typename
        if isinstance(node, ArrayRef):
            typename += '_*'
        elif isinstance(node.bind, ArrayDecl):
            typename += '_' + str(node.bind.tam.value)
        inst = ('load_' + typename, node.gen_location, target)
        self.code.append(inst)
        node.gen_location = target


    def visit_globalLocation(self, node, decl, tam):
        type_var = node.type.names[-1].typename
        if tam is not None:
            type_var += tam
        var = "@" + node.declname.name
        if decl.init is None:
            self.text.append(('global_'+ type_var, var))
        elif isinstance(decl.init, Constant):
            self.text.append(('global_' + type_var, var, decl.init.value))
        elif isinstance(decl.init, InitList):
            self.visit(decl.init)
            self.text.append(('global_' + type_var, var, dec.init.value))
        node.declname.gen_location = var


    def visit_UnaryOp(self, node):
        self.visit(node.expression)
        source = node.expression.gen_location

        if node.op == '&' or node.op == '*':
            node.gen_location = node.expression.gen_location
        elif node.op == '!':
            if isinstance(node.expression, ID) or isinstance(node.expression, ArrayRef):
                self.visit_LoadLocation(node.expression)
            node.gen_location = self.new_temp()
            self.code.append(('bool_not', source, node.gen_location))
        else:
            if isinstance(node.expression, ID) or isinstance(node.expression, ArrayRef):
                self.visit_LoadLocation(node.expression)
            if node.op == '+':
                node.gen_location = node.expression.gen_location
            elif node.op == '-':
                typename = node.expression.type.names[-1].typename
                opcode = self.unary_op[node.op] + "_" + typename
                aux - self.new_temp()
                self.code.append(('literal_' + typename,0,aux))
                node.gen_location = self.new_temp()
                inst = (opcode, aux, node.expression.gen_location, node.gen_location)
                self.code.append(inst)
            elif node.op in ["++", "--","p++","p--"]:
                if node.op == "++" or node.op == "p++":
                    val = 1
                else:
                    val = -1
                value = self.new_temp()
                self.code.append('int_literal', val, value)
                opcode = self.unary_op[node.op] + "_" + node.expression.type.names[-1].typename
                node.gen_location = self.new_temp()
                inst = (opcode, node.expression.gen_location, value, node.gen_location)
                self.code.append(inst)
                opcode = 'store_' + node.expression.type.names[-1].typename
                inst = (opcode, node.gen_location, source)
                self.code.append(inst)
                if node.op in ["p++", "p--"]:
                    node.gen_location = node.expression.gen_location


    def visit_BinaryOp(self, node):
        # Visit the left and right expressions
        self.visit(node.left_val)
        self.visit(node.right_val)

        if isinstance(node.left_val, ID) or isinstance(node.left_val, ArrayRef):
            self.visit_LoadLocation(node.left_val)
        elif isinstance(node.left_val, UnaryOp) and node.left_val.op == '*':
            self.__loadRefer(node.left_val)

        if isinstance(node.right_val, ID) or isinstance(node.right_val, ArrayRef):
            self.visit_LoadLocation(node.right_val)
        elif isinstance(node.right_val, UnaryOp) and node.right_val.op == '*':
            self.__loadRefer(node.right_val)

        # Make a new temporary for storing the result
        target = self.new_temp()

        # Create the opcode and append to list
        opcode = self.binary_op[node.op] + "_" + node.left_val.type.names[-1].typename
        inst = (opcode, node.left_val.gen_location, node.right_val.gen_location, target)
        self.code.append(inst)

        # Store location of the result on the node
        node.gen_location = target


    def visit_Type(self, node):
        pass


    def visit_Return(self, node):
        if node.expression is not None:
            self.visit(node.expression)
            if isinstance(node.expression, ID) or isinstance(node.expression, ArrayRef):
                self.visit_LoadLocation(node.expression)
            inst = ('store_' + node.expression.type.names[-1].typename, node.expression.gen_location,
                    self.return_location)
            self.code.append(inst)
        self.code.append(('jump', self.return_label))


    def visit_Cast(self, node):
        self.visit(node.expression)
        if isinstance(node.expression, ID) or isinstance(node.expression, ArrayRef):
            self.visit_LoadLocation(node.expression)
        temporary = self.new_temp()
        if node.cast.names[-1].typename == IntType.typename:
            inst = ('fptosi', node.expression.gen_location, temporary)
        else:
            inst = ('sitofp', node.expression.gen_location, temporary)
        self.code.append(inst)
        node.gen_location = temporary


    def visit_EmptyStatement(self, node):
        pass


    def visit_Compound(self, node):
        for i in node.block_items:
            self.visit(i)


    def visit_Break(self, node):
        self.code.append(('jump', node.bind.label_exit))


    def visit_While(self, node):
        label_start = self.new_temp()
        label_true = self.new_temp()
        label_exit = self.new_temp()
        node.label_exit = label_exit
        self.code.append((label_start[1:],))
        self.visit(node.cond)
        inst = ('cbranch', node.cond.gen_location, label_true, label_exit)
        self.code.append(inst)
        self.code.append((label_true[1:],))
        if node.statement is not None:
            self.visit(node.statement)
        self.code.append(('jump', label_start))
        self.code.append((label_exit[1:],))


    def visit_For(self, node):
        label_start = self.new_temp()
        label_body = self.new_temp()
        label_exit = self.new_temp()
        node.label_exit = label_exit

        self.visit(node.initial)
        self.code.append((label_start[1:],))

        self.visit(node.cond)
        inst = ('cbranch', node.cond.gen_location, label_body, label_exit)
        self.code.append(inst)

        self.code.append((label_body[1:],))
        self.visit(node.statement)
        self.visit(node.next)
        self.code.append(('jump', label_start))
        self.code.append((label_exit[1:],))


    def visit_If(self, node):
        label_exit = self.new_temp()
        label_false = self.new_temp()
        label_true = self.new_temp()

        self.visit(node.cond)
        inst = ('cbranch', node.cond.gen_location, label_true, label_false)
        self.code.append(inst)

        self.code.append((label_true[1:],))
        self.visit(node.true)

        if node.false is not None:
            self.code.append(('jump', label_exit))
            self.code.append((label_false[1:],))
            self.visit(node.false)
            self.code.append((label_exit[1:],))
        else:
            self.code.append((label_false[1:],))


    def visit_Assignment(self, node):
        right_value = node.value1
        self.visit(right_value)
        if isinstance(right_value,ID) or isinstance(right_value, ArrayRef):
            self.visit_LoadLocation(right_value)
        elif isinstance(right_value, UnaryOp) and right_value.op == "*":
            self.__loadRefer(right_value)
        
        left_value = node.value2
        self.visit(left_value)
        if node.op in self.assign_op:
            left_value = self.new_temp()
            target = self.new_temp()
            typename = left_value.type.names[-1].typename
            if isinstance(node.value1, ArrayRef):
                typename +="_*"
            inst = ('load_' + typename, left_value.gen_location, left_value)
            self.code.append(inst)
            inst = (self.assign_op[node.op] + '_' + left_value.type.names[-1].typename, 
                    node.right_value.gen_location, left_value, target)
            self.code.append(inst)
            inst = ('store_' + left_value.type.names[-1].typename, target, left_value.gen_location)
            self.code.append(inst)
        else:
            if isinstance(left_value, ID) or isinstance (left_value, ArrayRef):
                typename = left_value.type.names[-1].typename
                if isinstance(left_value, ArrayRef):
                    typename += '_*'
                elif isinstance(left_value.bind, ArrayDecl):
                    typename += '_' + str(left_value.bind.tam.value)
                elif left_value.type.names[0] == PtrType:
                    if left_value.model == 'func':
                        left_value.bind.type.gen_location = left_value.gen_location
                    typename += '_*'
                    inst = ('get_' + typename, node.value1.gen_location, left_value.gen_location)
                    self.code.append(inst)
                    return 
                inst = ('store_' + typename, node.value1.gen_location, left_value.gen_location)
                self.code.append(inst)
            else:
                typename = left_value.type.names[-1].typename
                if isinstance(left_value, UnaryOp):
                    if left_value.op == '*':
                        typename += '_*'
                    inst = ('store_' + typename, node.value1.gen_location, left_value.gen_location)
                    self.code.append(inst)


    def visit_Assert(self, node):
        var = node.expression 
        self.visit(var)
        label_true = self.new_temp()
        label_false = self.new_temp()
        label_exit = self.new_temp()

        inst = ('cbranch', var.gen_location, label_true, label_false)
        self.code.append(inst)

        self.code.append((label_true[1:],))
        self.code.append(('jump', label_exit))
        self.code.append((label_false[1:],))

        target = self.new_temp()
        expressionTemp = var.coord.split('@')
        expressionCoord = expressionTemp[1].split(':')
        inst = ('global_string', target, "assertion_fail on" + f"{expressionCoord[0]}:{expressionCoord[1]}")
        self.text.append(inst)

        inst = ('print_string', target)
        self.code.append(inst)
        self.code.append(('jump', self.return_label))
        self.code.append((label_exit[1:],))


    def visit_Print(self, node):
        if node.expression is not None:
            if isinstance(node.expression[0], ExprList):
                for i in node.expression[0].expression:
                    self.visit(i)
                    if isinstance(i, ID) or isinstance(i, ArrayRef):
                        self.visit_LoadLocation(i)
                    elif isinstance(i, UnaryOp) and i.op == "*":
                        self.__loadRefer(i)
                    inst = ('print_'+ i.type.names[-1].typename, i.gen_location)
                    self.code.append(inst)
        else:
            inst = ('print_void',)
            self.code.append(inst)


    def visit_VarDecl(self, node, var, tam):
        if node.declname.scope == 1:
            self.visit_globalLocation(node, var, tam)
        else:
            typename = node.type.names[-1].typename + tam
            if self.step_allocation == 'declaration_arguments' or self.step_allocation == 'declaration_variable':
                varname = self.new_temp()
                inst = ('allocation_' + typename, varname)
                self.code.append(inst)
                node.declname.gen_location = varname
                var.name.gen_location = varname
            elif self.step_allocation == 'initialize_arguments':
                inst = ('store_' + typename, self.dequeue(), node.declname.gen_location)
                self.code.append(inst)
            elif self.step_allocation == 'initialize_variable':
                if var.init is not None:
                    self._storeLocation(typename, var.init, node.declname.gen_location)


    def visit_DeclList(self,node):
        for i in node.decls:
            self.visit(i)
    

    def visit_Decl(self, node):
        type_var = node.type
        tam_var = ""
        if isinstance(type_var, VarDecl):
            self.visit_VarDecl(type_var, node, tam_var)
        elif isinstance(type_var, ArrayDecl):
            self.visit_ArrayDecl(type_var, node, tam_var)
        elif isinstance(type_var, PtrDecl):
            self.visit_PtrDecl(type_var, node, tam_var)
        elif isinstance(type_var, FuncDecl):
            self.visit_FuncDecl(type_var)


    def visit_PtrDecl(self, node, decl, tam):
        type_var = node
        tam += "_*"
        while not isinstance(type_var, VarDecl):
            type_var = type_var.type
            if isinstance(type_var, PtrDecl):
                tam += "_*"
            if isinstance(type_var, ArrayDecl):
                tam += "_" + str(type_var.tam.value)
        self.visit_VarDecl(type_var, decl, tam)


    def visit_ArrayDecl(self, node, decl, tam):
        type_var = node
        tam += "_" + str(node.tam.value)
        while not isinstance(type_var, VarDecl):
            type_var = type_var.type
            if isinstance(type_var, ArrayDecl):
                tam += "_" + str(type_var.tam.value)
            elif isinstance(type_var, PtrDecl):
                tam += "_*"
        self.visit_VarDecl(type_var, decl, tam) 


    def visit_FuncDecl(self, node):
        self.fname = "@" + node.type.declname.name
        inst = ('define', self.fname)
        self.code.append(inst)
        node.type.declname.gen_location = self.fname
        if node.params is not None:
            self.clean()
            for i in node.params.params:
                self.enqueue(self.new_temp())

        self.return_location = self.new_temp()
        self.step_allocation = 'declaration_arguments'
        if node.params is not None:
            for i in node.params:
                self.visit(i)
        
        self.return_label = self.new_temp()

        self.step_allocation = 'initialize_arguments'
        if node.params is not None:
            for i in node.params:
                self.visit(i)


    def visit_Read(self, node):
        for i in node.names:
            self.visit(i)

            if isinstance(i, ID) or isinstance(i, ArrayRef):
                self._readLocal(i)
            elif isinstance(i, ExprList):
                for var in i.expression:
                    self.visit(var)
                    self._readLocal(var)


    def visit_InitList(self, node):
        node.value = []
        for i in node.expression:
            if isinstance(i, InitList):
                self.visit(i)
            node.value.append(i.value)
    

    def visit_ExprList(self, node):
        pass


    def visit_ParamList(self, node):
        for i in node.params:
            self.visit(i)
    

    def visit_FuncDef(self, node):
        self.step_allocation = None
        self.visit(node.decl)
        if node.param_decls is not None:
            for i in node.param_decls:
                self.visit(i)

        if node.body is not None:
            self.step_allocation = 'declaration_variable'
            for bod in node.body:
                if isinstance(bod, Decl):
                    self.visit(bod)
            for dcl in node.decls:
                self.visit(dcl)

            self.step_allocation = 'initialize_variable'
            for bod in node.body:
                self.visit(bod)

        self.code.append((self.return_label[1:],))
        if node.spec.names[-1].typename == 'void':
            self.code.append(('return_void'))
        else:
            value = self.new_temp()
            inst = ('load_'+ node.spec.names[-1].typename, self.return_location, value)
            self.code.append(inst)
            self.code.append(('return_' + node.spec.names[-1].typename, value))


    def visit_Constant(self,node):
        if node.rawtype == 'string':
            target = self.new_text()
            inst =('global_string', target, node.value)
            self.text.append(inst)
        else:
            target = self.new_temp()
            inst=('literal_' + node.rawtype, node.value, target)
            self.code.append(inst)
        node.gen_location = target


    def visit_ID(self,node):
        if node.gen_location is None:
            type_var = node.bind 
            while not isinstance(type_var, VarDecl):
                type_var = type_var.type
            if type_var.declname.gen_location is None:
                if node.model == 'func' and node.scope == 1:
                    node.gen_location = '@' + node.name 
                else:
                    node.gen_location = type_var.declname.gen_location


    def visit_Program(self,node):
        for i in node.gdecls:
            self.visit(i)

    
    def visit_ArrayRef(self,node):
        subscript_a = node.subscript
        self.visit(subscript_a)
        if isinstance(node.name, ArrayRef):
            subscript_b = node.name.subscript
            self.visit(subscript_b)
            tam_var = node.name.name.bind.type.tam 
            self.visit(tam_var)
            if isinstance(subscript_b, ID) or isinstance(subscript_b, ArrayRef):
                self.visit_LoadLocation(subscript_b)
            target = self.new_temp() 
            self.code.append(('times_' + node.type.names[-1].typename, tam_var.gen_location, 
                             subscript_b.gen_location, target))
            if isinstance(subscript_a, ID) or isinstance(subscript_a, ArrayRef):
                self.visit_LoadLocation(subscript_a)
            index = self.new_temp()
            self.code.append(('plus_' + node.type.names[-1].typename, target, subscript_a.gen_location, index))
            var = node.name.name.bind.type.type.declname.gen_location
            node.gen_location = self.new_temp()
            self.code.append(('elem_' + node.type.names[-1].typename, var, index, node.gen_location))
        else:
            if isinstance(subscript_a, ID) or isinstance(subscript_a, ArrayRef):
                self.visit_LoadLocation(subscript_a)
            var = node.name.bind.type.declname.gen_location 
            index = subscript_a.gen_location
            target = self.new_temp()
            node.gen_location = target 
            inst = ('elem_' + node.type.names[-1].typename, var, index, target)
            self.code.append(inst)


    def visit_FuncCall(self,node):
        if node.params is not None:
            if isinstance(node.params, ExprList):
                listcode = []   
                for params_var in node.params.expression:
                    self.visit(params_var)
                    if isinstance(params_var, ID) or isinstance(params_var, ArrayRef):
                        self.visit_LoadLocation(params_var)
                    inst = ('params_' + params_var.type.names[-1].typename, params_var.gen_location)
                    listcode.append(inst)
                for i in listcode:
                    self.code.append(i)
            else:
                self.visit(node.params)
                if isinstance(node.params, ID) or isinstance(node.params, ArrayRef):
                    self.visit_LoadLocation(node.params)
                inst = ('params_' + node.params.type.names[-1].typename, node.params.gen_location)
                self.code.append(inst)
        if isinstance(node.name.bind, PtrDecl):
            target = self.new_temp()
            self.code.append('load_' + node.type.names[-1].typename + '_*', 
                              node.name.bind.type.gen_location, target)
            node.gen_location = self.new_temp()
            self.code.append(('call', target, node.gen_location))
        else:
            node.gen_location = self.new_temp()
            self.visit(node.name)
            inst = ('call', '@' + node.name.name, node.gen_location)
            self.code.append(inst)


    def visit_GlobalDecl(self,node):
        for i in node.decls:
            if not isinstance(i.type , FuncDecl):
                self.visit(i)


    


