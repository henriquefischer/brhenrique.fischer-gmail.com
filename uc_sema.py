from ast import *


class UCType(object):
    '''
    Class that represents a type in the uC language.  Types
    are declared as singleton instances of this type.
    '''

    def __init__(self, typename, binary_ops=set(), unary_ops=set(), rel_ops=set(), assign_ops=set()):
        '''
        You must implement yourself and figure out what to store.
        '''
        self.typename = typename
        self.unary_ops = unary_ops or set()
        self.binary_ops = binary_ops or set()
        self.rel_ops = rel_ops or set()
        self.assign_ops = assign_ops or set()

    def __str__(self):
        return str(self.typename)


IntType = UCType("int",
                 unary_ops={"-", "+", "--", "++", "p--", "p++", "*", "&"},
                 binary_ops={"+", "-", "*", "/", "%"},
                 rel_ops={"==", "!=", "<", ">", "<=", ">=", "||", "&&"},
                 assign_ops={"=", "+=", "-=", "*=", "/=", "%="}
                 )

FloatType = UCType("float",
                   unary_ops={"-", "*", "&"},
                   binary_ops={"+", "-", "*", "/", "%"},
                   rel_ops={"==", "!=", "<", ">", "<=", ">=", "||", "&&"},
                   assign_ops={"=", "+=", "-=", "*=", "/=", "%="}
                   )
CharType = UCType("char",
                  unary_ops={"*", "&"},
                  binary_ops={"+"},
                  rel_ops={"==", "!=", "<", ">", "<=", ">=", "||", "&&"},
                  assign_ops={"="}
                  )
ArrayType = UCType("array",
                   unary_ops={"*", "&"},
                   rel_ops={"==", "!="},
                   assign_ops={"="}
                   )

StringType = UCType("string",
                    binary_ops={"+"},
                    rel_ops={"==", "!="},
                    assign_ops={"="}
                    )

BoolType = UCType("bool",
                  unary_ops={"!"},
                  binary_ops={"||", "&&"},
                  rel_ops={"==", "!="},
                  assign_ops={"="}
                  )

VoidType = UCType("void")

PtrType = UCType("ptr")


class SymbolTable(dict):
    def __init__(self, decl=None):
        super().__init__()
        self.decl = decl

    def lookup(self, key):
        return self.get(key, None)

    def add(self, k, v):
        self[k] = v


class Environment(object):
    def __init__(self):
        self.loop_block = []
        self.rtypes = []
        self.loop_type = []
        self.stack = []
        self.root = SymbolTable()
        self.stack.append(self.root)
        self.root.update({
            'int': IntType,
            'float': FloatType,
            'char': CharType,
            'string': StringType,
            'bool': BoolType,
            'array': ArrayType,
            'ptr': PtrType,
            'void': VoidType
        })

    def lookup(self, obj):
        for scope in reversed(self.stack):
            this = scope.lookup(obj)
            if this is not None:
                return this
        return None

    def find(self, obj):
        cur_symtable = self.stack[-1]
        if obj in cur_symtable:
            return True
        else:
            return False

    def scope_level(self):
        return len(self.stack)-1

    def set_local(self, obj, model):
        self.get().add(obj.name, obj)
        obj.model = model
        obj.scope = self.scope_level()

    def get_root(self):
        return self.stack[0]

    def get(self):
        return self.stack[-1]

    def push(self, node):
        self.stack.append(SymbolTable(node))
        self.rtypes.append(self.loop_type)
        if isinstance(node, FuncDecl):
            self.loop_type = node.type.type.names
        else:
            self.loop_type = [VoidType]

    def pop(self):
        self.stack.pop()
        self.loop_type = self.rtypes.pop()


class NodeVisitor(object):
    """ A base NodeVisitor class for visiting uc_ast nodes.
        Subclass it and define your own visit_XXX methods, where
        XXX is the class name you want to visit with these
        methods.

        For example:

        class ConstantVisitor(NodeVisitor):
            def __init__(self):
                self.values = []

            def visit_Constant(self, node):
                self.values.append(node.value)

        Creates a list of values of all the constant nodes
        encountered below the given node. To use it:

        cv = ConstantVisitor()
        cv.visit(node)

        Notes:

        *   generic_visit() will be called for AST nodes for which
            no visit_XXX method was defined.
        *   The children of nodes for which a visit_XXX was
            defined will not be visited - if you need this, call
            generic_visit() on the node.
            You can use:
                NodeVisitor.generic_visit(self, node)
        *   Modeled after Python's own AST visiting facilities
            (the ast module of Python 3.0)
    """

    _method_cache = None

    def visit(self, node):
        """ Visit a node.
        """
        if self._method_cache is None:
            self._method_cache = {}

        visitor = self._method_cache.get(node.__class__.__name__, None)
        if visitor is None:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            self._method_cache[node.__class__.__name__] = visitor

        return visitor(node)

    def generic_visit(self, node):
        for c in node:
            print(type(node))
            print("Generic_visit: {0}".format(c))
            self.visit(c)


class Visitor(NodeVisitor):
    '''
    Program visitor class. This class uses the visitor pattern. You need to define methods
    of the form visit_NodeName() for each kind of AST node that you want to process.
    Note: You will need to adjust the names of the AST nodes if you picked different names.
    '''
    def __init__(self, debug):
        # Initialize the symbol table
        self.environment = Environment()
        self.type_mapping = {
            'int': IntType,
            'float': FloatType,
            'char': CharType,
            'array': ArrayType,
            'string': StringType,
            'bool': BoolType,
            'void': VoidType,
            'ptr': PtrType
        }
        self.debug = debug

    def visit_Program(self, node):
        if self.debug:
            print("@visit_Program")
            print(node)
        self.environment.push(node)
        node.symtab = self.environment.get_root()
        for _decl in node.gdecls:
            self.visit(_decl)
        self.environment.pop()
        if self.debug:
            print("visit_Program END")

    def visit_BinaryOp(self, node):
        coord = f"{node.coord}"
        if self.debug:
            print(f"@visit_BinaryOp {coord}")
            print(node)
        self.visit(node.left_val)
        assert node.left_val.type is not None, f"\"{node.left_val.name}\" is not defined {coord}"
        ltype = node.left_val.type.names[-1]
        self.visit(node.right_val)
        assert node.right_val.type is not None, f"\"{node.right_val.name}\" is not defined {coord}"
        rtype = node.right_val.type.names[-1]
        assert ltype == rtype, f"Cannot assign \"{rtype}\" to \"{ltype}\" {coord}"
        if node.op in ltype.binary_ops:
            node.type = Type([ltype], node.coord)
        elif node.op in ltype.rel_ops:
            node.type = Type([self.type_mapping["bool"]], node.coord)
        else:
            assert False, f"Assign operator \"{node.op}\" is not supported by \"{ltype}\" {coord}"
        if self.debug:
            print(f"visit_BinaryOp END")

    def visit_Assignment(self, node):
        coord = f"{node.coord}"
        if self.debug:
            print(f"@visit_Assignment {coord}")
            print(node)
        self.visit(node.value2)
        rtype = node.value2.type.names
        if isinstance(node.value2, FuncCall):
            if isinstance(node.value2.name.bind, PtrDecl):
                rtype = node.value2.type.names[1:]
        val = node.value1
        self.visit(val)
        if isinstance(val, ID):
            assert val.scope is not None, f"\"{val}\" is not defined {coord}"
        ltype = node.value1.type.names
        assert ltype == rtype, f"Cannot assign \"{rtype}\" to \"{ltype}\" {coord}"
        assert node.op in ltype[-1].assign_ops, f"Assign operator \"{node.op}\" not supported by \"{ltype[-1]}\""
        if self.debug:
            print(f"visit_Assignment END")

    def visit_Assert(self, node):
        coord = f"{node.expression.coord}"
        if self.debug:
            print(f"@visit_Assert {coord}")
            print(node)
        expr = node.expression
        self.visit(expr)
        if hasattr(expr, "type"):
            assert expr.type.names[0] == self.type_mapping["bool"], f"Expression must be boolean {coord}"
        else:
            assert False, f"Expression must be boolean {coord}"
        if self.debug:
            print(f"visit_Assert END")

    def visit_ArrayRef(self, node):
        if self.debug:
            print(f"@visit_ArrayRef")
            print(node)
        subsc = node.subscript
        self.visit(subsc)
        if isinstance(subsc, ID):
            coord = f"{subsc.coord}"
            assert subsc.scope is not None, f"\"{subsc.name}\" is not defined {coord}"
        stype = subsc.type.names[-1]
        coord = f"{node.coord}"
        assert stype == IntType, f"\"{stype}\" must be a Int type {coord}"
        self.visit(node.name)
        node.type = Type(node.name.type.names[1:], node.coord)
        if self.debug:
            print(f"visit_ArrayRef END")

    def visit_ArrayDecl(self, node):
        if self.debug:
            print("@visit_ArrayDecl")
            print(node)
        self.visit(node.type)
        arrayType = node.type
        while not isinstance(arrayType, VarDecl):
            arrayType = arrayType.type
        arrayId = arrayType.declname
        arrayId.type.names.insert(0, self.type_mapping["array"])
        if node.tam is not None:
            self.visit(node.tam)
        if self.debug:
            print("visit_ArrayDecl END")

    def visit_Break(self, node):
        coord = f"{node.coord}"
        if self.debug:
            print(f"@visit_Break {coord}")
            print(node)
        assert self.environment.loop_block != [], f"Break statement must be inside a loop block {coord}"
        node.bind = self.environment.loop_block[-1]
        if self.debug:
            print(f"visit_Break END")

    def visit_Cast(self, node):
        if self.debug:
            print("@visit_Cast")
            print(node)
        self.visit(node.expression)
        self.visit(node.cast)
        node.type = Type(node.cast.names, node.coord)
        if self.debug:
            print("visit_Cast END")

    def visit_Compound(self, node):
        if self.debug:
            print("@visit_Compound")
            print(node)
        for item in node.block_items:
            self.visit(item)
        if self.debug:
            print("visit_Compound END")

    def visit_Constant(self, node):
        if self.debug:
            print("@visit_Constant")
            print(node)
        if not isinstance(node.type, UCType):
            consType = self.type_mapping[node.rawtype]
            node.type = Type([consType], node.coord)
            if consType.typename == 'int':
                node.value = int(node.value)
            elif consType.typename == 'float':
                node.value = float(node.value)
        if self.debug:
            print("visit_Constant END")

    def setDim(self, nodeType, length, line, var):
        if self.debug:
            print("@setDim")
        if nodeType.tam is None:
            nodeType.tam = Constant('int', length)
            self.visit_Constant(nodeType.tam)
        else:
            assert False, f"Size mismatch on \"{var}\" {line}"
        if self.debug:
            print("setDim END")

    def checkInit(self, nodeType, init, var, line):
        if self.debug:
            print("@checkInit")
        self.visit(init)
        if isinstance(init, Constant):
            self.checkConstant(nodeType, init, var, line)
        elif isinstance(init, InitList):
            self.checkInitList(nodeType, init, var, line)
        elif isinstance(init, ArrayRef):
            self.checkArrayRef(nodeType, init, var, line)
        elif isinstance(init, ID):
            self.checkId(nodeType, init, var, line)
        if self.debug:
            print("checkInit END")

    def checkInitList(self, nodeType, init, var, line):
        length = len(init.expression)
        expression = init.expression
        if isinstance(nodeType, VarDecl):
            assert length == 1, f"Initialization must be a single element {line}"
            assert nodeType.type == expression[0].type, f"Initialization type mismatch {line}"
        elif isinstance(nodeType, ArrayDecl):
            size = length
            decl = nodeType
            while isinstance(nodeType.type, ArrayDecl):
                nodeType = nodeType.type
                length = len(expression[0].expression)
                for i in range(len(expression)):
                    assert len(expression[i].expression) == length, f"List have a different length {line}"
                expression = expression[0].expression
                if isinstance(nodeType, ArrayDecl):
                    self.setDim(nodeType, length, line, var)
                    size += length
                else:
                    assert expression[0].type == nodeType.type.type.names[
                        -1], f"\"{var}\" Initialization type mismatch {line}"
            nodeType = decl
            length = size
            if nodeType.tam is None:
                nodeType.tam = Constant('int', size)
                self.visit_Constant(nodeType.tam)
            else:
                assert nodeType.tam.value == length, f"Size mismatch \"{var}\" initialization {line}"

    def checkConstant(self, nodeType, init, var, line):
        if init.rawtype == 'string':
            assert nodeType.type.type.names == [self.type_mapping["array"],
                                                self.type_mapping["char"]], f"Initialization type mismatch {line}"
            self.setDim(nodeType, len(init.value), line, var)
        else:
            assert nodeType.type.names[0] == init.type.names[0], f"Initialization type mismatch {line}"

    def checkArrayRef(self, nodeType, init, var, line):
        initId = self.environment.lookup(init.name.name)
        if isinstance(init.subscript, Constant):
            rtype = initId.type.names[1]
            assert nodeType.type.names[0] == rtype, f"Initialization type mismatch \"{var}\" {line}"

    def checkId(self, nodeType, init, var, line):
        if isinstance(nodeType, ArrayDecl):
            idType = nodeType.type
            while not isinstance(idType, VarDecl):
                idType = idType.type
            assert idType.type.names == init.type.names, f"Initialization type mismatch {line}"
            self.setDim(nodeType, init.bind.dim.value, line, var)
        else:
            assert nodeType.type.names[-1] == init.type.names[-1], f"Initialization type mismatch {line}"

    def visit_Decl(self, node):
        coord = f"{node.name.coord}"
        if self.debug:
            print(f"@visit_Decl {coord}")
            print(node)
        declType = node.type
        self.visit(declType)
        declVar = node.name.name
        node.name.bind = declType
        if isinstance(declType, PtrDecl):
            while isinstance(declType, PtrDecl):
                declType = declType.type
        if isinstance(declType, FuncDecl):
            assert self.environment.lookup(declVar) is not None, f"\"{declVar}\" is not defined {coord}"
        else:
            assert self.environment.find(declVar) is not None, f"\"{declVar}\" is not defined"
            if node.init is not None:
                self.checkInit(declType, node.init, declVar, coord)
        if self.debug:
            print(f"visit_Decl END")

    def visit_DeclList(self, node):
        if self.debug:
            print("@visit_DeclList")
            print(node)
        for decl in node.decls:
            self.visit(decl)
            self.environment.funcdef.decls.append(decl)
        if self.debug:
            print("visit_DeclList END")

    def visit_EmptyStatement(self, node):
        if self.debug:
            print("@visit_EmptyStatement")
            print(node)
        pass

    def visit_ExprList(self, node):
        if self.debug:
            print("@visit_ExprList")
            print(node)
        for expr in node.expression:
            self.visit(expr)
            if isinstance(expr, ID):
                coord = f"{expr.coord}"
                assert expr.scope is not None, f"\"{expr.name}\" is not defined {coord}"
        if self.debug:
            print("visit_ExprList END")

    def visit_For(self, node):
        if self.debug:
            print("@visit_For")
            print(node)
        if isinstance(node.initial, DeclList):
            self.environment.push(node)
        self.environment.loop_block.append(node)
        self.visit(node.initial)
        self.visit(node.cond)
        self.visit(node.next)
        self.visit(node.statement)
        self.environment.loop_block.pop()
        if isinstance(node.initial, DeclList):
            self.environment.pop()
        if self.debug:
            print("visit_For END")

    def visit_FuncCall(self, node):
        if self.debug:
            print("@visit_FuncCall")
            print(node)
        coord = f"{node.coord}"
        funcLabel = self.environment.lookup(node.name.name)
        assert funcLabel is not None, f"\"{node.name.name}\" is not defined {coord}"
        assert funcLabel.model == "func", f"\"{funcLabel}\" is not a function {coord}"
        node.type = funcLabel.type
        node.name.type = funcLabel.type
        node.name.bind = funcLabel.bind
        node.name.model = funcLabel.model
        node.name.scope = funcLabel.scope
        if node.params is not None:
            sig = funcLabel.bind
            while isinstance(sig, PtrDecl):
                sig = sig.type
            if isinstance(node.params, ExprList):
                assert len(sig.params.params) == len(node.params.expression), f"Number of arguments mismatch {coord}"
                for(arg, fpar) in zip(node.params.expression, sig.params.params):
                    self.visit(arg)
                    coord = f"{arg.coord}"
                    if isinstance(arg, ID):
                        assert self.environment.find(arg.name), f"\"{arg.name}\" is not defined {coord}"
                    assert arg.type.names == fpar.type.type.names, f"Type mismatch for \"{fpar.type.declname.name}\" {coord}"
            else:
                self.visit(node.params)
                assert len(sig.params.params) == 1, f"Number of arguments mismatch {coord}"
                argType = sig.params.params[0].type
                while not isinstance(argType, VarDecl):
                    argType = argType.type
                assert node.params.type.names == argType.type.names, f"Type mismatch for \"{sig.params.params[0].name.name}\" {coord}"
        if self.debug:
            print("visit_FuncCall END")

    def visit_FuncDecl(self, node):
        if self.debug:
            print("@visit_FuncDecl")
            print(node)
        self.visit(node.type)
        func = self.environment.lookup(node.type.declname.name)
        func.model = 'func'
        func.bind = node.params
        self.environment.push(node)
        if node.params is not None:
            for arg in node.params:
                self.visit(arg)
        if self.debug:
            print("visit_FuncDecl END")

    def visit_FuncDef(self, node):
        if self.debug:
            print("@visit_FuncDef")
            print(node)
        node.decls = []
        self.environment.funcdef = node
        self.visit(node.spec)
        self.visit(node.decl)
        if node.param_decls is not None:
            for par in node.param_decls:
                self.visit(par)
        if node.body is not None:
            for body in node.body:
                self.visit(body)
        self.environment.pop()
        func = self.environment.lookup(node.decl.name.name)
        node.spec = func.type
        if self.debug:
            print("visit_FuncDef END")

    def visit_GlobalDecl(self, node):
        if self.debug:
            print("@visit_GlobalDecl")
            print(node)
        for decl in node.decls:
            self.visit(decl)
        if self.debug:
            print("visit_GlobalDecl END")

    def visit_ID(self, node):
        if self.debug:
            print("@visit_ID")
            print(node)
        varId = self.environment.lookup(node.name)
        if varId is not None:
            node.type = varId.type
            node.model = varId.model
            node.scope = varId.scope
            node.bind = varId.bind
        if self.debug:
            print("visit_ID END")

    def visit_If(self, node):
        coord = f"{node.cond.coord}"
        if self.debug:
            print("@visit_If")
            print(node)
        self.visit(node.cond)
        if hasattr(node.cond, 'type'):
            assert node.cond.type.names[0] == self.type_mapping["bool"], f"The condition must be a boolean type {coord}"
        else:
            assert False, f"The condition must be a boolean type {coord}"
        self.visit(node.true)
        if node.false is not None:
            self.visit(node.false)
        if self.debug:
            print("visit_If END")

    def visit_InitList(self, node):
        if self.debug:
            print("@visit_InitList")
            print(node)
        for expr in node.expression:
            self.visit(expr)
            if not isinstance(expr, InitList):
                coord = f"{expr.coord}"
                assert isinstance(expr, Constant), f"Expression must be a Constant {coord}"
        if self.debug:
            print("visit_InitList END")

    def visit_ParamList(self, node):
        if self.debug:
            print("@visit_ParamList")
            print(node)
        for par in node.params:
            self.visit(par)
        if self.debug:
            print("visit_ParamList END")

    def visit_Print(self, node):
        if self.debug:
            print("@visit_Print")
            print(node)
        if node.expression is not None:
            for expr in node.expression:
                self.visit(expr)
        if self.debug:
            print("visit_Print END")

    def visit_PtrDecl(self, node):
        if self.debug:
            print("@visit_PtrDecl")
            print(node)
        self.visit(node.type)
        ptrType = node.type
        while not isinstance(ptrType, VarDecl):
            ptrType = ptrType.type
        ptrType.declname.bind = node
        ptrType.type.names.insert(0, self.type_mapping["ptr"])
        if self.debug:
            print("visit_PtrDecl END")

    def checkLocation(self, var):
        if self.debug:
            print("@checkLocation")
        coord = f"{var.coord}"
        test = (isinstance(var, ArrayRef) and len(var.type.names) == 1)
        test = test or isinstance(var, ID)
        name = var.name
        if isinstance(name, ArrayRef):
            name = name.name.name + f"[{name.subscript.name}][{var.subscript.name}]"
        elif hasattr(var, 'subscript'):
            name = name.name + f"[{var.subscript.name}]"
        assert test, f"\"{name}\" is not a simple variable {coord}"
        if isinstance(var, ID):
            assert var.scope is not None, f"\"{name}\" is not defined {coord}"
        assert len(var.type.names) == 1, f"Type of \"{name}\" is not a primitive type"
        if self.debug:
            print("checkLocation END")

    def visit_Read(self, node):
        if self.debug:
            print("@visit_Read")
            print(node)
        for loc in node.expression:
            self.visit(loc)
            if isinstance(loc, ID) or isinstance(loc, ArrayRef):
                self.checkLocation(loc)
            elif isinstance(loc, ExprList):
                for var in loc.expression:
                    if isinstance(var, ID) or isinstance(var, ArrayRef):
                        self.checkLocation(var)
                    else:
                        coord = f"{var.coord}"
                        assert False, f"\"{var}\" is not a variable {coord}"
            else:
                coord = f"{loc.coord}"
                assert False, f"\"{loc}\" is not a variable {coord}"
        if self.debug:
            print("visit_Read END")

    def visit_Return(self, node):
        if self.debug:
            print("@visit_Return")
            print(node)
        if node.expression is not None:
            self.visit(node.expression)
            returnType = node.expression.type.names
        else:
            returnType = [self.type_mapping['void']]
        rtype = self.environment.loop_type
        coord = f"{node.coord}"
        assert returnType == rtype, f"Return type \"{returnType[-1].__str__()}\" is not compatible with \"{rtype[-1].__str__()}\" {coord}"
        if self.debug:
            print("visit_Return END")

    def visit_Type(self, node):
        if self.debug:
            print("@visit_Type")
            print(node)
        for i, name in enumerate(node.names or []):
            if not isinstance(name, UCType):
                nodeType = self.type_mapping[name]
                node.names[i] = nodeType
        if self.debug:
            print("visit_Type END")

    def visit_VarDecl(self, node):
        if self.debug:
            print("@visit_VarDecl")
            print(node)
        self.visit(node.type)
        var = node.declname
        self.visit(var)
        if isinstance(var, ID):
            coord = f"{var.coord}"
            assert not self.environment.find(var.name), f"\"{var.name}\" already defined in this scope {coord}"
            self.environment.set_local(var, 'var')
            var.type = node.type
        if self.debug:
            print("visit_VarDecl END")

    def visit_UnaryOp(self, node):
        if self.debug:
            print("@visit_UnaryOp")
            print(node)
        self.visit(node.expression)
        unaryType = node.expression.type.names[-1]
        coord = f"{node.coord}"
        assert node.op in unaryType.unary_ops, f"Unary operator \"{node.op}\" not supported {coord}"
        node.type = Type(names=list(node.expression.type.names), coord=node.coord)
        if node.op == "*":
            node.type.names.pop(0)
        elif node.op == "&":
            node.type.names.insert(0, self.type_mapping["ptr"])
        if self.debug:
            print("visit_UnaryOp END")

    def visit_While(self, node):
        if self.debug:
            print("@visit_While")
            print(node)
        self.environment.loop_block.append(node)
        self.visit(node.cond)
        ctype = node.cond.type.names[0]
        coord = f"{node.coord}"
        assert ctype == BoolType, f"Conditional expression must be a Boolean type {coord}"
        if node.statement is not None:
            self.visit(node.statement)
        self.environment.loop_block.pop()
        if self.debug:
            print("visit_While END")

