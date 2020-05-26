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

# Create specific instances of types. You will need to add
# appropriate arguments depending on your definition of uCType
IntType = uCType("int",
                unary_ops   = {"-", "+", "--", "++", "p--", "p++", "*", "&"},
                binary_ops  = {"+", "-", "*", "/", "%"},
                rel_ops     = {"==", "!=", "<", ">", "<=", ">="},
                assign_ops  = {"=", "+=", "-=", "*=", "/=", "%="}
                )

FloatType = uCType("float",
                unary_ops   = {"-", "+", "--", "++", "p--", "p++", "*", "&"},
                binary_ops  = {"+", "-", "*", "/", "%"},
                rel_ops     = {"==", "!=", "<", ">", "<=", ">="},
                assign_ops  = {"=", "+=", "-=", "*=", "/=", "%="}
                )

#one character
CharType = uCType("char",
                unary_ops   = {"&"},
                rel_ops     = {"==", "!=", "<", ">", "<=", ">="},
                assign_ops  = {"="}
            )

StringType = uCType("string",
                unary_ops   = {"&"},
                rel_ops     = {"==", "!=", "<", ">", "<=", ">="},
                assign_ops  = {"="}
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

ArrayType = uCType("array",
                   unary_ops={"*", "&"},
                   rel_ops={"==", "!="},
                   assign_ops={"="}
            )

BoolType = uCType("bool",
                unary_ops={"!"},
                binary_ops={"||", "&&"},
                rel_ops={"==", "!="},
                assign_ops={"="}
            )       

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
VoidType = uCType("void")

PtrType = uCType("ptr")

class SymbolTable(dict):
    def __init__(self, decl=None):
        super().__init__()
        self.decl = decl

    def lookup(self, key):
        return self.get(key, None)

    def add(self, k, v):
        self[k] = v

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

class Environment(object):
    def __init__(self):
        self.loop = []
        self.types = []
        self.current_types = []
        self.stack = []
        self.root = SymbolTable()
        self.stack.append(self.root)
        self.root.update({
            'int': IntType,
            'float': FloatType,
            'char': CharType,
            'string': StringType,
            'int_array': ArrayType,
            'float_array': ArrayFloatType,
            'bool': BoolType,
            'void': VoidType,
            'array': ArrayType,
            'ptr': PtrType

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
        self.types.append(self.current_types)
        if isinstance(node, FuncDecl):
            self.current_types = node.type.type.names
        else:
            self.current_types = [VoidType]

    def pop(self):
        self.stack.pop()
        self.current_types = self.types.pop()


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
        print(type(node))
        for c in node:
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
        self.typemap = {
            'int': IntType,
            'float': FloatType,
            'char': CharType,
            'string': StringType,
            'int_array': ArrayIntType,
            'float_array': ArrayFloatType,
            'bool': BoolType,
            'void': VoidType,
            'array': ArrayType,
            'ptr': PtrType

        }
        self.debug = debug

    def setTam(self, node_type, length, line, var):
        if node_type.Tam is None:
            node_type.Tam = Constant('int', length)
            self.visit_Constant(node_type.tam)
        else:
            assert False, f"Size incompatible on \"{var}\" {line}"

    def examLocation(self, decl):
        coord = f"{decl.coord}"
        test = (isinstance(decl, ArrayRef) and len(decl.type.names) == 1)
        test = test or isinstance(decl, ID)
        name = decl.name
        if isinstance(name, ArrayRef):
            name = name.name.name + f"[{name.subscript.name}][{decl.subscript.name}]"
        elif hasattr(decl, 'subscript'):
            name = name.name + f"[{decl.subscript.name}]"
        assert test, f"\"{name}\" is not a simple variable {coord}"
        if isinstance(decl, ID):
            assert decl.scope is not None, f"\"{name}\" is not defined {coord}"
        assert len(decl.type.names) == 1, f"Type of \"{name}\" is not a primitive type"

    def examInit(self, node_type, init, decl, line):
        self.visit(init)
        if isinstance(init, Constant):
            self.examConstant(node_type, init, decl, line)
        elif isinstance(init, InitList):
            self.examInitList(node_type, init, decl, line)
        elif isinstance(init, ArrayRef):
            self.examArrayRef(node_type, init, decl, line)
        elif isinstance(init, ID):
            self.examID(node_type, init, decl, line)

    def examConstant(self, node_type, init, decl, line):
        if init.rawtype == 'string':
            assert node_type.type.type.names == [self.typemap["array"],
                                                self.typemap["char"]], f"Initialization type incompatible {line}"
            self.setTam(node_type, len(init.value), line, decl)
        else:
            assert node_type.type.names[0] == init.type.names[0], f"Initialization type incompatible {line}"

    def examInitList(self, node_type, init, decl, line):
        tam = len(init.expression)
        expression = init.expression
        if isinstance(node_type, VarDecl):
            assert tam == 1, f"Initialization must be a single element {line}"
            assert node_type.type == expression[0].type, f"Initialization type incompatible {line}"
        elif isinstance(node_type, ArrayDecl):
            Comprimento = tam
            decl = node_type
            while isinstance(node_type.type, ArrayDecl):
                node_type = node_type.type
                tam = len(expression[0].expression)
                for i in range(len(expression)):
                    assert len(expression[i].expression) == tam, f"List have a different tam {line}"
                expression = expression[0].expression
                if isinstance(node_type, ArrayDecl):
                    self.setTam(node_type, tam, line, decl)
                    Comprimento += tam
                else:
                    assert expression[0].type == node_type.type.type.names[
                        -1], f"\"{decl}\" Initialization type incompatible {line}"
            node_type = decl
            tam = Comprimento
            if node_type.tam is None:
                node_type.tam = Constant('int', Comprimento)
                self.visit_Constant(node_type.tam)
            else:
                assert node_type.tam.value == tam, f"Comprimento incompatible \"{decl}\" initialization {line}"

    def examArrayRef(self, node_type, init, decl, line):
        init_id = self.environment.lookup(init.name.name)
        if isinstance(init.subscript, Constant):
            var_type = init_id.type.names[1]
            assert node_type.type.names[0] == var_type, f"Initialization type incompatible \"{decl}\" {line}"

    def examID(self, node_type, init, decl, line):
        if isinstance(node_type, ArrayDecl):
            id_type = node_type.type
            while not isinstance(id_type, VarDecl):
                id_type = id_type.type
            assert id_type.type.names == init.type.names, f"Initialization type incompatible {line}"
            self.setTam(node_type, init.bind.tam.value, line, decl)
        else:
            assert node_type.type.names[-1] == init.type.names[-1], f"Initialization type incompatible {line}"

    def visit_Program(self, node):
        if self.debug:
            print("Program")
            print(node)
        self.environment.push(node)
        node.symtab = self.environment.get_root()
        for i in node.gdecls:
            self.visit(i)
        self.environment.pop()

    def visit_UnaryOp(self, node):
        if self.debug:
            print("UnaryOp")
            print(node)
        self.visit(node.expression)
        unary_type = node.expression.type.names[-1]
        coord = f"{node.coord}"
        assert node.op in unary_type.unary_ops, f"Unary operator \"{node.op}\" not supported {coord}"
        node.type = Type(names=list(node.expression.type.names), coord=node.coord)
        if node.op == "*":
            node.type.names.pop(0)
        elif node.op == "&":
            node.type.names.insert(0, self.typemap["ptr"])

    def visit_BinaryOp(self, node):
        coord = f"{node.coord}"
        if self.debug:
            print(f"BinaryOp {coord}")
            print(node)
        self.visit(node.left_val)
        assert node.left_val.type is not None, f"\"{node.left_val.name}\" is not defined {coord}"
        left_var = node.left_val.type.names[-1]
        self.visit(node.right_val)
        assert node.right_val.type is not None, f"\"{node.right_val.name}\" is not defined {coord}"
        right_var = node.right_val.type.names[-1]
        assert left_var == right_var, f"Cannot assign \"{right_var}\" to \"{left_var}\" {coord}"
        if node.op in left_var.binary_ops:
            node.type = Type([left_var], node.coord)
        elif node.op in left_var.rel_ops:
            node.type = Type([self.typemap["bool"]], node.coord)
        else:
            assert False, f"Assign operator \"{node.op}\" is not supported by \"{left_var}\" {coord}"

    def visit_GlobalDecl(self, node):
        if self.debug:
            print("GlobalDecl")
            print(node)
        for i in node.decls:
            self.visit(i)

    def visit_Assignment(self, node):
        coord = f"{node.coord}"
        if self.debug:
            print(f"Assignment {coord}")
            print(node)
        self.visit(node.value2)
        right_var = node.value2.type.names
        if isinstance(node.value2, FuncCall):
            if isinstance(node.value2.name.bind, PtrDecl):
                right_var = node.value2.type.names[1:]
        var = node.value1
        self.visit(var)
        if isinstance(var, ID):
            assert var.scope is not None, f"\"{var}\" is not defined {coord}"
        left_var = node.value1.type.names
        assert left_var == right_var, f"Cannot assign \"{right_var}\" to \"{left_var}\" {coord}"
        assert node.op in left_var[-1].assign_ops, f"Assign operator \"{node.op}\" not supported by \"{left_var[-1]}\""

    def visit_While(self, node):
        if self.debug:
            print("While")
            print(node)
        self.environment.loop.append(node)
        self.visit(node.cond)
        cond_type = node.cond.type.names[0]
        coord = f"{node.coord}"
        assert cond_type == BoolType, f"Conditional expression must be a Boolean type {coord}"
        if node.statement is not None:
            self.visit(node.statement)
        self.environment.loop.pop()

    def visit_For(self, node):
        if self.debug:
            print("For")
            print(node)
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

    def visit_If(self, node):
        coord = f"{node.cond.coord}"
        if self.debug:
            print("If")
            print(node)
        self.visit(node.cond)
        if hasattr(node.cond, 'type'):
            assert node.cond.type.names[0] == self.typemap["bool"], f"The condition must be a boolean type {coord}"
        else:
            assert False, f"The condition must be a boolean type {coord}"
        self.visit(node.true)
        if node.false is not None:
            self.visit(node.false)

    def visit_Break(self, node):
        coord = f"{node.coord}"
        if self.debug:
            print(f"Break {coord}")
            print(node)
        assert self.environment.loop != [], f"Break statement must be inside a loop block {coord}"
        node.bind = self.environment.loop[-1]

    def visit_Return(self, node):
        if self.debug:
            print("Return")
            print(node)
        if node.expression is not None:
            self.visit(node.expression)
            return_type = node.expression.type.names
        else:
            return_type = [self.typemap['void']]
        var_type = self.environment.current_types
        coord = f"{node.coord}"
        assert return_type == var_type, f"Return type \"{return_type[-1].__str__()}\" is not compatible with \"{var_type[-1].__str__()}\" {coord}"

    def visit_EmptyStatement(self, node):
        if self.debug:
            print("EmptyStatement")
            print(node)
        pass

    def visit_Print(self, node):
        if self.debug:
            print("Print")
            print(node)
        if node.expression is not None:
            for expression in node.expression:
                self.visit(expression)

    def visit_ID(self, node):
        if self.debug:
            print("ID")
            print(node)
        var_id = self.environment.lookup(node.name)
        if var_id is not None:
            node.type = var_id.type
            node.model = var_id.model
            node.scope = var_id.scope
            node.bind = var_id.bind

    def visit_Assert(self, node):
        coord = f"{node.expression.coord}"
        if self.debug:
            print(f"Assert {coord}")
            print(node)
        expression = node.expression
        self.visit(expression)
        if hasattr(expression, "type"):
            assert expression.type.names[0] == self.typemap["bool"], f"Expression must be boolean {coord}"
        else:
            assert False, f"Expression must be boolean {coord}"

    def visit_Type(self, node):
        if self.debug:
            print("Type")
            print(node)
        for i, name in enumerate(node.names or []):
            if not isinstance(name,uCType):
                nodeType = self.typemap[name]
                node.names[i] = nodeType

    def visit_Cast(self, node):
        if self.debug:
            print("Cast")
            print(node)
        self.visit(node.expression)
        self.visit(node.cast)
        node.type = Type(node.cast.names, node.coord)

    def visit_Compound(self, node):
        if self.debug:
            print("Compound")
            print(node)
        for i in node.block_items:
            self.visit(i)

    def visit_Constant(self, node):
        if self.debug:
            print("Constant")
            print(node)
        if not isinstance(node.type, uCType):
            const_type = self.typemap[node.rawtype]
            node.type = Type([const_type], node.coord)
            if const_type.typename == 'int':
                node.value = int(node.value)
            elif const_type.typename == 'float':
                node.value = float(node.value)

    def visit_Decl(self, node):
        coord = f"{node.name.coord}"
        if self.debug:
            print(f"Decl {coord}")
            print(node)
        var_type = node.type
        self.visit(var_type)
        var_name = node.name.name
        node.name.bind = var_type
        if isinstance(var_type, PtrDecl):
            while isinstance(var_type, PtrDecl):
                var_type = var_type.type
        if isinstance(var_type, FuncDecl):
            assert self.environment.lookup(var_name) is not None, f"\"{var_name}\" is not defined {coord}"
        else:
            assert self.environment.find(var_name) is not None, f"\"{var_name}\" is not defined"
            if node.init is not None:
                self.examInit(var_type, node.init, var_name, coord)

    def visit_DeclList(self, node):
        if self.debug:
            print("DeclList")
            print(node)
        for i in node.decls:
            self.visit(i)
            self.environment.funcdef.decls.append(i)

    def visit_VarDecl(self, node):
        if self.debug:
            print("VarDecl")
            print(node)
        self.visit(node.type)
        var = node.declname
        self.visit(var)
        if isinstance(var, ID):
            coord = f"{var.coord}"
            assert not self.environment.find(var.name), f"\"{var.name}\" already defined in this scope {coord}"
            self.environment.set_local(var, 'var')
            var.type = node.type

    def visit_ExprList(self, node):
        if self.debug:
            print("ExprList")
            print(node)
        for i in node.expression:
            self.visit(i)
            if isinstance(i, ID):
                coord = f"{i.coord}"
                assert i.scope is not None, f"\"{i.name}\" is not defined {coord}"

    def visit_InitList(self, node):
        if self.debug:
            print("InitList")
            print(node)
        for i in node.expression:
            self.visit(i)
            if not isinstance(i, InitList):
                coord = f"{i.coord}"
                assert isinstance(i, Constant), f"Expression must be a Constant {coord}"

    def visit_ParamList(self, node):
        if self.debug:
            print("ParamList")
            print(node)
        for i in node.params:
            self.visit(i)

    def visit_FuncCall(self, node):
        if self.debug:
            print("FuncCall")
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
        if self.debug:
            print("FuncDecl")
            print(node)
        self.visit(node.type)
        func = self.environment.lookup(node.type.declname.name)
        func.model = 'func'
        func.bind = node.params
        self.environment.push(node)
        if node.params is not None:
            for i in node.params:
                self.visit(i)

    def visit_FuncDef(self, node):
        if self.debug:
            print("FuncDef")
            print(node)
        node.decls = []
        self.environment.funcdef = node
        self.visit(node.spec)
        self.visit(node.decl)
        if node.param_decls is not None:
            for i in node.param_decls:
                self.visit(i)
        if node.body is not None:
            for body in node.body:
                self.visit(body)
        self.environment.pop()
        func = self.environment.lookup(node.decl.name.name)
        node.spec = func.type

    def visit_PtrDecl(self, node):
        if self.debug:
            print("PtrDecl")
            print(node)
        self.visit(node.type)
        ptr_type = node.type
        while not isinstance(ptr_type, VarDecl):
            ptr_type = ptr_type.type
        ptr_type.declname.bind = node
        ptr_type.type.names.insert(0, self.typemap["ptr"])

    def visit_Read(self, node):
        if self.debug:
            print("Read")
            print(node)
        for i in node.expression:
            self.visit(i)
            if isinstance(i, ID) or isinstance(i, ArrayRef):
                self.examLocation(i)
            elif isinstance(i, ExprList):
                for var in i.expression:
                    if isinstance(var, ID) or isinstance(var, ArrayRef):
                        self.examLocation(var)
                    else:
                        coord = f"{var.coord}"
                        assert False, f"\"{var}\" is not a variable {coord}"
            else:
                coord = f"{i.coord}"
                assert False, f"\"{i}\" is not a variable {coord}"

    def visit_ArrayRef(self, node):
        if self.debug:
            print(f"ArrayRef")
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

    def visit_ArrayDecl(self, node):
        if self.debug:
            print("ArrayDecl")
            print(node)
        self.visit(node.type)
        array_type = node.type
        while not isinstance(array_type, VarDecl):
            array_type = array_type.type
        array_id = array_type.declname
        array_id.type.names.insert(0, self.typemap["array"])
        if node.tam is not None:
            self.visit(node.tam)























































