class uCType(object):
    '''
    Class that represents a type in the uC language.  Types 
    are declared as singleton instances of this type.
    '''
    def __init__(self, name, bin_ops=set(), un_ops=set(), rel_ops=set(), assign_ops=set()):
        '''
        You must implement yourself and figure out what to store.
        '''
        self.typename = typename
        self.unary_ops = unary_ops or set()
        self.binary_ops = binary_ops or set()
        self.rel_ops = rel_ops or set()
        self.assign_ops = assign_ops or set()

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

BoolType = uCType("bool",
                unary_ops={"!"},
                binary_ops={"||", "&&"},
                rel_ops={"==", "!="},
                assign_ops={"="}
)

ConstantType = uCType(a)(
    if a == 'char':
        return CharType
    elif a == 'int':
        return IntType
    elif a == 'float':
        return FloatType
)

VoidType = uCType("void")






