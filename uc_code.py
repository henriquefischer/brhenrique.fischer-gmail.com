from uc_sema import *
from ast import *


class GenerateCode(NodeVisitor):
    '''
    Node visitor class that creates 3-address encoded instruction sequences.
    '''

    def __init__(self):
        super(GenerateCode, self).__init__()

        # version dictionary for temporaries
        self.fname = 'main'  # We use the function name as a key
        self.versions = {self.fname: 0}
        # The generated code (list of tuples)
        self.text = []
        self.code = []
        '''
        self.binary_opcodes = {"+": "add", "-": "sub", "*": "mul", "/": "div", "%": "mod",
        "==": "eq", "!=": "ne", "<": "lt", ">": "ht", "<=": "le", ">=": "he", "&&": "and",
        "||": "or"}
        '''
        self.binary_opcodes = {"+": "add", "-": "sub", "*": "mul", "/": "div", "%": "mod",
                               "==": "eq", "!=": "ne", "<": "lt", ">": "gt", "<=": "le", ">=": "ge", "&&": "and",
                               "||": "or"}
        self.unary_opcodes = {"-": "sub", "+": "", "--": "sub", "++":"add", "!": "not",
                              "*": "", "&": ""}
        self.assign_opcodes = {"+=": "add", "-=": "sub", "*=": "mul", "/=": "div", "%=": "mod"}
      
        self.allocation_step = None
        self.return_location = None
        self.return_label = None
        self.items = []

    def clean(self):
        self.items = []

    def enqueue(self, item):
        self.items.insert(0, item)

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
        self.versions['main'] += 1
        return name

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        # ~ print('generic:', type(node))
        if node is None:
            return ''
        else:
            return ''.join(self.visit(c) for c_name, c in node.children())

    def _loadRefer(self, node):
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
            self._loadRefer(source)
        self.code.append(('store_' + typename, target, source.gen_location))

    def _globalLocal(self, node, decl, tam):
        type_var = node.type.names[-1].typename
        if tam is not None:
            type_var += tam
        var_name = "@" + node.declname.name
        if decl.init is None:
            self.text.append(('global_' + type_var, var_name))
        elif isinstance(decl.init, Constant):
            self.text.append(('global_' + type_var, var_name, decl.init.value))
        elif isinstance(decl.init, InitList):
            self.visit(decl.init)
            self.text.append(('global_' + type_var, var_name, decl.init.value))
        node.declname.gen_location = var_name

    def _loadLocal(self, node):
        var_name = self.new_temp()
        typename = node.type.names[-1].typename
        if isinstance(node, ArrayRef):
            typename += '_*'
        elif isinstance(node.bind, ArrayDecl):
            typename += '_' + str(node.bind.tam.value)
        inst = ('load_' + typename, node.gen_location, var_name)
        self.code.append(inst)
        node.gen_location = var_name

    def _storeLocal(self, typename, init, target):
        self.visit(init)
        if isinstance(init, ID) or isinstance(init, ArrayRef):
            self._loadLocal(init)
        elif isinstance(init, UnaryOp) and init.op == '*':
            self._loadRefer(init)
        inst = ('store_' + typename, init.gen_location, target)
        self.code.append(inst)

    def visit_Program(self, node):
        for i in node.gdecls:
            self.visit(i)

    def visit_GlobalDecl(self, node):
        for i in node.decls:
            if not isinstance(i.type, FuncDecl):
                self.visit(i)

    def visit_Constant(self, node):
        if node.rawtype == 'string':
            target = self.new_text()
            inst = ('global_string', target, node.value)
            self.text.append(inst)
        else:
            target = self.new_temp()
            inst = ('literal_' + node.rawtype, node.value, target)
            self.code.append(inst)
        node.gen_location = target

    def visit_Cast(self, node):
        self.visit(node.expression)
        if isinstance(node.expression, ID) or isinstance(node.expression, ArrayRef):
            self._loadLocal(node.expression)
        temporary = self.new_temp()
        if node.to_type.names[-1].typename == IntType.typename:
            inst = ('fptosi', node.expression.gen_location, temporary)
        else:
            inst = ('sitofp', node.expression.gen_location, temporary)
        self.code.append(inst)
        node.gen_location = temporary

    def visit_Type(self, node):
        pass

    def visit_ID(self, node):
        if node.gen_location is None:
            type_var = node.bind
            while not isinstance(type_var, VarDecl):
                type_var = type_var.type
            if type_var.declname.gen_location is None:
                if node.model == 'func' and node.scope == 1:
                    node.gen_location = '@' + node.name
            else:
                node.gen_location = type_var.declname.gen_location

    def visit_UnaryOp(self, node):
        self.visit(node.expression)
        source = node.expression.gen_location

        if node.op == '&' or node.op == '*':
            node.gen_location = node.expression.gen_location
        elif node.op == '!':
            if isinstance(node.expression, ID) or isinstance(node.expression, ArrayRef):
                self._loadLocal(node.expression)
            node.gen_location = self.new_temp()
            self.code.append(('not_bool', source, node.gen_location))
        else:
            if isinstance(node.expression, ID) or isinstance(node.expression, ArrayRef):
                self._loadLocal(node.expression)
            if node.op == '+':
                node.gen_location = node.expression.gen_location

            elif node.op == '-':
                typename = node.expression.type.names[-1].typename
                opcode = self.unary_opcodes[node.op] + "_" + typename
                aux = self.new_temp()
                self.code.append(('literal_' + typename, 0, aux))
                node.gen_location = self.new_temp()
                inst = (opcode, aux, node.expression.gen_location, node.gen_location)
                self.code.append(inst)

            elif node.op in ["++", "--"]:
                if node.op == "++":
                    value = 1
                else:
                    value = -1
                var = self.new_temp()
                self.code.append(('literal_int', value, var))
                opcode = self.unary_opcodes[node.op] + "_" + node.expression.type.names[-1].typename
                node.gen_location = self.new_temp()
                inst = (opcode, node.expression.gen_location, var, node.gen_location)
                self.code.append(inst)
                opcode = 'store_' + node.expression.type.names[-1].typename
                inst = (opcode, node.gen_location, source)
                self.code.append(inst)
                if node.op in ["p++", "p--"]:
                    node.gen_location = node.expression.gen_location

    def visit_BinaryOp(self, node):
        self.visit(node.left_val)
        self.visit(node.right_val)

        if isinstance(node.left_val, ID) or isinstance(node.left_val, ArrayRef):
            self._loadLocal(node.left_val)
        elif isinstance(node.left_val, UnaryOp) and node.left_val.op == '*':
            self._loadRefer(node.left_val)

        if isinstance(node.right_val, ID) or isinstance(node.right_val, ArrayRef):
            self._loadLocal(node.right_val)
        elif isinstance(node.right_val, UnaryOp) and node.right_val.op == '*':
            self._loadRefer(node.right_val)

        target = self.new_temp()

        opcode = self.binary_opcodes[node.op] + "_" + node.left_val.type.names[-1].typename
        inst = (opcode, node.left_val.gen_location, node.right_val.gen_location, target)
        self.code.append(inst)

        node.gen_location = target

    def visit_If(self, node):
        label_true = self.new_temp()
        label_false = self.new_temp()
        label_exit = self.new_temp()

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

    def visit_Break(self, node):
        self.code.append(('jump', node.bind.exit_label))

    def visit_Print(self, node):
        if node.expression is not None:
            if isinstance(node.expression[0], ExprList):
                for var in node.expression[0].exprs:
                    self.visit(var)
                    if isinstance(var, ID) or isinstance(var, ArrayRef):
                        self._loadLocal(var)
                    elif isinstance(var, UnaryOp) and var.op == "*":
                        self._loadRefer(var)
                    inst = ('print_' + var.type.names[-1].typename, var.gen_location)
                    self.code.append(inst)
        else:
            inst = ('print_void',)
            self.code.append(inst)

    def visit_Return(self, node):
        if node.expression is not None:
            self.visit(node.expression)
            if isinstance(node.expression, ID) or isinstance(node.expression, ArrayRef):
                self._loadLocal(node.expression)
            inst = ('store_' + node.expression.type.names[-1].typename, node.expression.gen_location, self.return_location)
            self.code.append(inst)

        self.code.append(('jump', self.return_label))

    def visit_Assert(self, node):
        i = node.expression
        self.visit(i)

        label_true = self.new_temp()
        label_false = self.new_temp()
        label_exit = self.new_temp()

        inst = ('cbranch', i.gen_location, label_true, label_false)
        self.code.append(inst)

        self.code.append((label_true[1:],))
        self.code.append(('jump', label_exit))
        self.code.append((label_false[1:],))

        target = self.new_text()
        expressionTemporary = i.coord.split('@')
        temporaryCoord = expressionTemporary[1].split(':')
        inst = ('global_string', target, "assertion_fail on " + f"{temporaryCoord[0]}:{temporaryCoord[1]}")
        self.text.append(inst)

        inst = ('print_string', target)
        self.code.append(inst)
        self.code.append(('jump', self.return_label))

        self.code.append((label_exit[1:],))

    def visit_Assignment(self, node):
        right_val = node.value1
        self.visit(right_val)
        if isinstance(right_val, ID) or isinstance(right_val, ArrayRef):
            self._loadLocal(right_val)
        elif isinstance(right_val, UnaryOp) and right_val.op == "*":
            self._loadRefer(right_val)
        left_val = node.value2
        self.visit(left_val)
        if node.op in self.assign_opcodes:
            left_val = self.new_temp()
            target = self.new_temp()
            typename = left_val.type.names[-1].typename
            if isinstance(node.value1, ArrayRef):
                typename += "_*"
            inst = ('load_' + typename, left_val.gen_location, left_val)
            self.code.append(inst)
            inst = (self.assign_opcodes[node.op] + '_' + left_val.type.names[-1].typename,
                    node.value1.gen_location, left_val, target)
            self.code.append(inst)
            inst = ('store_' + left_val.type.names[-1].typename, target, left_val.gen_location)
            self.code.append(inst)
        else:
            if isinstance(left_val, ID) or isinstance(left_val, ArrayRef):
                typename = left_val.type.names[-1].typename
                if isinstance(left_val, ArrayRef):
                    typename += '_*'
                elif isinstance(left_val.bind, ArrayDecl):
                    typename += '_' + str(left_val.bind.tam.value)
                elif left_val.type.names[0] == PtrType:
                    if left_val.model == 'func':
                        left_val.bind.type.gen_location = left_val.gen_location
                    typename += '_*'
                    inst = ('get_' + typename, node.value1.gen_location, left_val.gen_location)
                    self.code.append(inst)
                    return
                inst = ('store_' + typename, node.value1.gen_location, left_val.gen_location)
                self.code.append(inst)
            else:
                typename = left_val.type.names[-1].typename
                if isinstance(left_val, UnaryOp):
                    if left_val.op == '*':
                        typename += '_*'
                    inst = ('store_' + typename, node.value1.gen_location, left_val.gen_location)
                    self.code.append(inst)

    def visit_Read(self, node):
        for i in node.names:
            self.visit(i)

            if isinstance(i, ID) or isinstance(i, ArrayRef):
                self._readLocal(i)

            elif isinstance(i, ExprList):
                for j in i.exprs:
                    self.visit(j)
                    self._readLocal(j)

    def visit_Compound(self, node):
        for i in node.block_items:
            self.visit(i)

    def visit_EmptyStatement(self, node):
        pass

    def visit_VarDecl(self, node, decl, tam):
        if node.declname.scope == 1:
            self._globalLocal(node, decl, tam)
        else:
            typename = node.type.names[-1].typename + tam
            if self.allocation_step == 'argument_declaration' or self.allocation_step == 'variable_declartion':
                var_name = self.new_temp()
                inst = ('alloc_' + typename, var_name)
                self.code.append(inst)
                node.declname.gen_location = var_name
                decl.name.gen_location = var_name
            elif self.allocation_step == 'argument_initalize':
                inst = ('store_' + typename, self.dequeue(), node.declname.gen_location)
                self.code.append(inst)
            elif self.allocation_step == 'variable_initalize':
                if decl.init is not None:
                    self._storeLocal(typename, decl.init, node.declname.gen_location)

    def visit_Decl(self, node):
        type_var = node.type
        tam = ""
        if isinstance(type_var, VarDecl):
            self.visit_VarDecl(type_var, node, tam)
        elif isinstance(type_var, ArrayDecl):
            self.visit_ArrayDecl(type_var, node, tam)
        elif isinstance(type_var, PtrDecl):
            self.visit_PtrDecl(type_var, node, tam)
        elif isinstance(type_var, FuncDecl):
            self.visit_FuncDecl(type_var)

    def visit_DeclList(self, node):
        for i in node.decls:
            self.visit(i)

    def visit_ParamList(self, node):
        for i in node.params:
            self.visit(i)

    def visit_ExprList(self, node):
        pass

    def visit_InitList(self, node):
        node.value = []
        for i in node.expressions:
            if isinstance(i, InitList):
                self.visit(i)
            node.value.append(i.value)

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

    def visit_ArrayRef(self, node):
        subscript_a = node.subscript
        self.visit(subscript_a)
        if isinstance(node.name, ArrayRef):
            subscript_b = node.name.subscript
            self.visit(subscript_b)
            tam = node.name.name.bind.type.tam
            self.visit(tam)
            if isinstance(subscript_b, ID) or isinstance(subscript_b, ArrayRef):
                self._loadLocal(subscript_b)
            target = self.new_temp()
            self.code.append(('mul_' + node.type.names[-1].typename, tam.gen_location,
                              subscript_b.gen_location, target))
            if isinstance(subscript_a, ID) or isinstance(subscript_a, ArrayRef):
                self._loadLocal(subscript_a)
            indice = self.new_temp()
            self.code.append(('add_' + node.type.names[-1].typename, target,
                              subscript_a.gen_location, indice))
            var = node.name.name.bind.type.type.declname.gen_location
            node.gen_location = self.new_temp()
            self.code.append(('elem_' + node.type.names[-1].typename, var, indice,
                              node.gen_location))

        else:
            if isinstance(subscript_a, ID) or isinstance(subscript_a, ArrayRef):
                self._loadLocal(subscript_a)
            var = node.name.bind.type.declname.gen_location
            indice = subscript_a.gen_location
            target = self.new_temp()
            node.gen_location = target
            inst = ('elem_' + node.type.names[-1].typename, var, indice, target)
            self.code.append(inst)

    def visit_FuncDef(self, node):
        self.allocation_step = None
        self.visit(node.decl)

        if node.param_decls is not None:
            for i in node.param_decls:
                self.visit(i)

        if node.body is not None:
            self.allocation_step = 'variable_declartion'
            for i in node.body:
                if isinstance(i, Decl):
                    self.visit(i)
            for _decl in node.decls:
                self.visit(_decl)

            self.allocation_step = 'variable_initalize'
            for i in node.body:
                self.visit(i)

        self.code.append((self.return_label[1:],))
        if node.spec.names[-1].typename == 'void':
            self.code.append(('return_void',))
        else:
            right_value = self.new_temp()
            inst = ('load_' + node.spec.names[-1].typename, self.return_location, right_value)
            self.code.append(inst)
            self.code.append(('return_' + node.spec.names[-1].typename, right_value))

    def visit_FuncDecl(self, node):
        self.fname = "@" + node.type.declname.name

        inst = ('define', self.fname)
        self.code.append(inst)
        node.type.declname.gen_location = self.fname

        if node.params is not None:
            self.clean()
            for _ in node.params.params:
                self.enqueue(self.new_temp())

        self.return_location = self.new_temp()
        self.allocation_step = 'argument_declaration'
        if node.params is not None:
            for i in node.params:
                self.visit(i)

        self.return_label = self.new_temp()

        self.allocation_step = 'argument_initalize'
        if node.params is not None:
            for i in node.params:
                self.visit(i)

    def visit_FuncCall(self, node):
        if node.params is not None:
            if isinstance(node.params, ExprList):
                tam_code = []
                for i in node.params.expression:
                    self.visit(i)
                    if isinstance(i, ID) or isinstance(i, ArrayRef):
                        self._loadLocal(i)
                    inst = ('param_' + i.type.names[-1].typename, i.gen_location)
                    tam_code.append(inst)
                for i_inst in tam_code:
                    self.code.append(i_inst)

            else:
                self.visit(node.params)
                if isinstance(node.params, ID) or isinstance(node.params, ArrayRef):
                    self._loadLocal(node.params)
                inst = ('param_' + node.params.type.names[-1].typename, node.params.gen_location)
                self.code.append(inst)

        if isinstance(node.name.bind, PtrDecl):
            target = self.new_temp()
            self.code.append(('load_' + node.type.names[-1].typename + '_*',
                              node.name.bind.type.gen_location, target))
            node.gen_location = self.new_temp()
            self.code.append(('call', target, node.gen_location))
        else:
            node.gen_location = self.new_temp()
            self.visit(node.name)
            inst = ('call', '@' + node.name.name, node.gen_location)
            self.code.append(inst)

    def visit_PtrDecl(self, node, decl, tam):
        type_var = node
        tam += "_*"
        while not isinstance(type_var, VarDecl):
            type_var = type_var.type
            if isinstance(type_var, PtrDecl):
                tam += "_*"
            elif isinstance(type_var, ArrayDecl):
                tam += "_" + str(type_var.tam.value)
        self.visit_VarDecl(type_var, decl, tam)
