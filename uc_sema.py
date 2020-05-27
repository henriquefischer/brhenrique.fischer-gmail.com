from ast import *


class uCType(object):
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

IntType = uCType("int",
                 unary_ops={"-", "+", "--", "++","p++","p--","*", "&"},
                 binary_ops={"+", "-", "*", "/", "%"},
                 rel_ops={"==", "!=", "<", ">", "<=", ">=", "||", "&&"},
                 assign_ops={"=", "+=", "-=", "*=", "/=", "%="}
                 )

FloatType = uCType("float",
                   unary_ops={"-", "*", "&"},
                   binary_ops={"+", "-", "*", "/", "%"},
                   rel_ops={"==", "!=", "<", ">", "<=", ">=", "||", "&&"},
                   assign_ops={"=", "+=", "-=", "*=", "/=", "%="}
                   )

CharType = uCType("char",
                  unary_ops={"*", "&"},
                  binary_ops={"+"},
                  rel_ops={"==", "!=", "<", ">", "<=", ">=", "||", "&&"},
                  assign_ops={"="}
                  )

ArrayType = uCType("array",
                   unary_ops={"*", "&"},
                   rel_ops={"==", "!="},
                   assign_ops={"="}
                   )

ArrayIntType = uCType("int_array",
                binary_ops  = {"+", "-", "*", "/", "%"},
                unary_ops   = {"*", "&"},
                rel_ops     = {"==", "!="}
            )

ArrayFloatType = uCType("float_array",
                binary_ops  = {"+", "-", "*", "/", "%"},
                unary_ops   = {"*", "&"},
                rel_ops     = {"==", "!="}
            )

StringType = uCType("string",
                    binary_ops={"+"},
                    rel_ops={"==", "!="},
                    assign_ops={"="}
                    )

BoolType = uCType("bool",
                  unary_ops={"!"},
                  binary_ops={"||", "&&"},
                  rel_ops={"==", "!="},
                  assign_ops={"="}
                  )

VoidType = uCType("void")

PtrType = uCType("ptr")

'''
ConstantType = uCType(
    if a == 'char':
        return CharType
    elif a == 'int':
        return IntType
    elif a == 'float':
        return FloatType
)
'''

class UndoStack:

    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)
    
    def pop(self, item):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items)-1]

    def size(self):
        return len(self.items)

    def isEmpty(self):
        return self.items == []

    def __str__(self):
        for i in self.items:
            print(i)

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
        self.loop = []
        self.array_types = []
        self.current_type = []
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
            'int_array': ArrayIntType,
            'float_array': ArrayFloatType,
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

    def scope_nivel(self):
        return len(self.stack)-1

    def add_local(self, obj, model):
        self.get().add(obj.name, obj)
        obj.model = model
        obj.scope = self.scope_nivel()

    def get_root(self):
        return self.stack[0]

    def get(self):
        return self.stack[-1]

    def push(self, node):
        self.stack.append(SymbolTable(node))
        self.array_types.append(self.current_type)
        if isinstance(node, FuncDecl):
            self.current_type = node.type.type.names
        else:
            self.current_type = [VoidType]

    def pop(self):
        self.stack.pop()
        self.current_type = self.array_types.pop()


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
            'int_array': ArrayIntType,
            'float_array': ArrayFloatType,
            'string': StringType,
            'bool': BoolType,
            'void': VoidType,
            'ptr': PtrType
        }
        self.debug = debug

    def examLocal(self, var):
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

    def examInit(self, nodeType, init, var, line):
        self.visit(init)
        if isinstance(init, Constant):
            self.examConstant(nodeType, init, var, line)
        elif isinstance(init, InitList):
            self.examInitList(nodeType, init, var, line)
        elif isinstance(init, ArrayRef):
            self.examArrayRef(nodeType, init, var, line)
        elif isinstance(init, ID):
            self.examID(nodeType, init, var, line)

    def examInitList(self, nodeType, init, var, line):
        length = len(init.expression)
        expression = init.expression
        if isinstance(nodeType, VarDecl):
            assert length == 1, f"Initialization must be a single element {line}"
            assert nodeType.type == expression[0].type, f"Initialization type incompatible {line}"
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
                    self.setTam(nodeType, length, line, var)
                    size += length
                else:
                    assert expression[0].type == nodeType.type.type.names[
                        -1], f"\"{var}\" Initialization type incompatible {line}"
            nodeType = decl
            length = size
            if nodeType.tam is None:
                nodeType.tam = Constant('int', size)
                self.visit_Constant(nodeType.tam)
            else:
                assert nodeType.tam.value == length, f"Size incompatible \"{var}\" initialization {line}"

    def examID(self, nodeType, init, var, line):
        if isinstance(nodeType, ArrayDecl):
            idType = nodeType.type
            while not isinstance(idType, VarDecl):
                idType = idType.type
            assert idType.type.names == init.type.names, f"Initialization type incompatible {line}"
            self.setTam(nodeType, init.bind.dim.value, line, var)
        else:
            assert nodeType.type.names[-1] == init.type.names[-1], f"Initialization type incompatible {line}"

    def examConstant(self, nodeType, init, var, line):
        if init.rawtype == 'string':
            assert nodeType.type.type.names == [self.type_mapping["array"],
                                                self.type_mapping["char"]], f"Initialization type incompatible {line}"
            self.setTam(nodeType, len(init.value), line, var)
        else:
            assert nodeType.type.names[0] == init.type.names[0], f"Initialization type incompatible {line}"

    def setTam(self, nodeType, length, line, var):
        if nodeType.tam is None:
            nodeType.tam = Constant('int', length)
            self.visit_Constant(nodeType.tam)
        else:
            assert False, f"Size incompatible on \"{var}\" {line}"

    def examArrayRef(self, nodeType, init, var, line):
        initId = self.environment.lookup(init.name.name)
        if isinstance(init.subscript, Constant):
            rtype = initId.type.names[1]
            assert nodeType.type.names[0] == rtype, f"Initialization type incompatible \"{var}\" {line}"

    def visit_Program(self, node):
        self.environment.push(node)
        node.symtab = self.environment.get_root()
        for i in node.gdecls:
            self.visit(i)
        self.environment.pop()

    def visit_GlobalDecl(self, node):
        for i in node.decls:
            self.visit(i)

    def visit_UnaryOp(self, node):
        self.visit(node.expression)
        unary_type = node.expression.type.names[-1]
        coord = f"{node.coord}"
        assert node.op in unary_type.unary_ops, f"Unary operator \"{node.op}\" not supported {coord}"
        node.type = Type(names=list(node.expression.type.names), coord=node.coord)
        if node.op == "*":
            node.type.names.pop(0)
        elif node.op == "&":
            node.type.names.insert(0, self.type_mapping["ptr"])

    def visit_BinaryOp(self, node):
        coord = f"{node.coord}"
        self.visit(node.left_val)
        assert node.left_val.type is not None, f"\"{node.left_val.name}\" is not defined {coord}"
        left_type = node.left_val.type.names[-1]
        self.visit(node.right_val)
        assert node.right_val.type is not None, f"\"{node.right_val.name}\" is not defined {coord}"
        right_type = node.right_val.type.names[-1]
        assert left_type == right_type, f"Cannot assign \"{right_type}\" to \"{left_type}\" {coord}"
        if node.op in left_type.binary_ops:
            node.type = Type([left_type], node.coord)
        elif node.op in left_type.rel_ops:
            node.type = Type([self.type_mapping["bool"]], node.coord)
        else:
            assert False, f"Assign operator \"{node.op}\" is not supported by \"{left_type}\" {coord}"

    def visit_Assignment(self, node):
        coord = f"{node.coord}"
        self.visit(node.value2)
        right_type = node.value2.type.names
        if isinstance(node.value2, FuncCall):
            if isinstance(node.value2.name.bind, PtrDecl):
                right_type = node.value2.type.names[1:]
        val = node.value1
        self.visit(val)
        if isinstance(val, ID):
            assert val.scope is not None, f"\"{val}\" is not defined {coord}"
        left_type = node.value1.type.names
        assert left_type == right_type, f"Cannot assign \"{right_type}\" to \"{left_type}\" {coord}"
        assert node.op in left_type[-1].assign_ops, f"Assign operator \"{node.op}\" not supported by \"{left_type[-1]}\""

    def visit_Assert(self, node):
        coord = f"{node.expression.coord}"
        var_exprs = node.expression
        self.visit(var_exprs)
        if hasattr(var_exprs, "type"):
            assert var_exprs.type.names[0] == self.type_mapping["bool"], f"Expression must be boolean {coord}"
        else:
            assert False, f"Expression must be boolean {coord}"

    def visit_Constant(self, node):
        if not isinstance(node.type, uCType):
            const_type = self.type_mapping[node.rawtype]
            node.type = Type([const_type], node.coord)
            if const_type.typename == 'int':
                node.value = int(node.value)
            elif const_type.typename == 'float':
                node.value = float(node.value)

    def visit_Type(self, node):
        for i, name in enumerate(node.names or []):
            if not isinstance(name, uCType):
                nodeType = self.type_mapping[name]
                node.names[i] = nodeType

    def visit_ID(self, node):
        var_id = self.environment.lookup(node.name)
        if var_id is not None:
            node.type = var_id.type
            node.model = var_id.model
            node.scope = var_id.scope
            node.bind = var_id.bind

    def visit_If(self, node):
        coord = f"{node.cond.coord}"
        self.visit(node.cond)
        if hasattr(node.cond, 'type'):
            assert node.cond.type.names[0] == self.type_mapping["bool"], f"The condition must be a boolean type {coord}"
        else:
            assert False, f"The condition must be a boolean type {coord}"
        self.visit(node.true)
        if node.false is not None:
            self.visit(node.false)

    def visit_Cast(self, node):
        self.visit(node.expression)
        self.visit(node.cast)
        node.type = Type(node.cast.names, node.coord)

    def visit_Break(self, node):
        coord = f"{node.coord}"
        assert self.environment.loop != [], f"Break statement must be inside a loop block {coord}"
        node.bind = self.environment.loop[-1]

    def visit_Print(self, node):
        if node.expression is not None:
            for i in node.expression:
                self.visit(i)

    def visit_Compound(self, node):
        for i in node.block_items:
            self.visit(i)

    def visit_For(self, node):
        if isinstance(node.initial, DeclList):
            self.environment.push(node)
        self.environment.loop.append(node)
        self.visit(node.initial)
        self.visit(node.cond)
        self.visit(node.next)
        self.visit(node.statement)
        self.environment.loop.pop()
        if isinstance(node.initial, DeclList):
            self.environment.pop()

    def visit_While(self, node):
        self.environment.loop.append(node)
        self.visit(node.cond)
        curr_type = node.cond.type.names[0]
        coord = f"{node.coord}"
        assert curr_type == BoolType, f"Conditional expression must be a Boolean type {coord}"
        if node.statement is not None:
            self.visit(node.statement)
        self.environment.loop.pop()

    def visit_Read(self, node):
        for i in node.expression:
            self.visit(i)
            if isinstance(i, ID) or isinstance(i, ArrayRef):
                self.examLocal(i)
            elif isinstance(i, ExprList):
                for current_var in i.expression:
                    if isinstance(current_var, ID) or isinstance(current_var, ArrayRef):
                        self.examLocal(current_var)
                    else:
                        coord = f"{current_var.coord}"
                        assert False, f"\"{current_var}\" is not a variable {coord}"
            else:
                coord = f"{i.coord}"
                assert False, f"\"{loc}\" is not a variable {coord}"

    def visit_Return(self, node):
        if node.expression is not None:
            self.visit(node.expression)
            return_type = node.expression.type.names
        else:
            return_type = [self.type_mapping['void']]
        type_return = self.environment.current_type
        coord = f"{node.coord}"
        assert return_type == type_return, f"Return type \"{return_type[-1].__str__()}\" is not compatible with \"{type_return[-1].__str__()}\" {coord}"

    def visit_InitList(self, node):
        for i in node.expression:
            self.visit(i)
            if not isinstance(i, InitList):
                coord = f"{i.coord}"
                assert isinstance(i, Constant), f"Expression must be a Constant {coord}"

    def visit_ParamList(self, node):
        for i in node.params:
            self.visit(i)

    def visit_EmptyStatement(self, node):
        pass

    def visit_ExprList(self, node):
        for i in node.expression:
            self.visit(i)
            if isinstance(i, ID):
                coord = f"{i.coord}"
                assert i.scope is not None, f"\"{i.name}\" is not defined {coord}"

    def visit_PtrDecl(self, node):
        self.visit(node.type)
        ptrType = node.type
        while not isinstance(ptrType, VarDecl):
            ptrType = ptrType.type
        ptrType.declname.bind = node
        ptrType.type.names.insert(0, self.type_mapping["ptr"])

    def visit_Decl(self, node):
        coord = f"{node.name.coord}"
        decl_type = node.type
        self.visit(decl_type)
        decl_var = node.name.name
        node.name.bind = decl_type
        if isinstance(decl_type, PtrDecl):
            while isinstance(decl_type, PtrDecl):
                decl_type = decl_type.type
        if isinstance(decl_type, FuncDecl):
            assert self.environment.lookup(decl_var) is not None, f"\"{decl_var}\" is not defined {coord}"
        else:
            assert self.environment.find(decl_var) is not None, f"\"{decl_var}\" is not defined"
            if node.init is not None:
                self.examInit(decl_type, node.init, decl_var, coord)

    def visit_DeclList(self, node):
        for i in node.decls:
            self.visit(i)
            self.environment.funcdef.decls.append(i)

    def visit_VarDecl(self, node):
        self.visit(node.type)
        var = node.declname
        self.visit(var)
        if isinstance(var, ID):
            coord = f"{var.coord}"
            assert not self.environment.find(var.name), f"\"{var.name}\" already defined in this scope {coord}"
            self.environment.add_local(var, 'var')
            var.type = node.type

    def visit_ArrayRef(self, node):
        subsc = node.subscript
        self.visit(subsc)
        if isinstance(subsc, ID):
            coord = f"{subsc.coord}"
            assert subsc.scope is not None, f"\"{subsc.name}\" is not defined {coord}"
        subs_type = subsc.type.names[-1]
        coord = f"{node.coord}"
        assert subs_type == IntType, f"\"{subs_type}\" must be a Int type {coord}"
        self.visit(node.name)
        node.type = Type(node.name.type.names[1:], node.coord)

    def visit_ArrayDecl(self, node):
        self.visit(node.type)
        arrayType = node.type
        while not isinstance(arrayType, VarDecl):
            arrayType = arrayType.type
        arrayId = arrayType.declname
        arrayId.type.names.insert(0, self.type_mapping["array"])
        if node.tam is not None:
            self.visit(node.tam)

    def visit_FuncCall(self, node):
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
                assert len(sig.params.params) == len(node.params.expression), f"Number of arguments incompatible {coord}"
                for(arg, fpar) in zip(node.params.expression, sig.params.params):
                    self.visit(arg)
                    coord = f"{arg.coord}"
                    if isinstance(arg, ID):
                        assert self.environment.find(arg.name), f"\"{arg.name}\" is not defined {coord}"
                    assert arg.type.names == fpar.type.type.names, f"Type incompatible for \"{fpar.type.declname.name}\" {coord}"
            else:
                self.visit(node.params)
                assert len(sig.params.params) == 1, f"Number of arguments incompatible {coord}"
                argType = sig.params.params[0].type
                while not isinstance(argType, VarDecl):
                    argType = argType.type
                assert node.params.type.names == argType.type.names, f"Type incompatible for \"{sig.params.params[0].name.name}\" {coord}"

    def visit_FuncDecl(self, node):
        self.visit(node.type)
        func = self.environment.lookup(node.type.declname.name)
        func.model = 'func'
        func.bind = node.params
        self.environment.push(node)
        if node.params is not None:
            for arg in node.params:
                self.visit(arg)

    def visit_FuncDef(self, node):
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
