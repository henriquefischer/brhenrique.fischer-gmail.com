import sys

def _repr(obj):
  """
  Get the representation of an object, with dedicated pprint-like format for lists.
  """
  if isinstance(obj, list):
      return '[' + (',\n '.join((_repr(e).replace('\n', '\n ') for e in obj))) + '\n]'
  else:
      return repr(obj) 

class Node(object):
    """ Abstract base class for AST nodes.
    """
    def __repr__(self):
      """ Generates a python representation of the current node
      """
      result = self.__class__.__name__ + '('
      indent = ''
      separator = ''
      for name in self.__slots__[:-2]:
          result += separator
          result += indent
          result += name + '=' + (_repr(getattr(self, name)).replace('\n', '\n  ' + (' ' * (len(name) + len(self.__class__.__name__)))))
          separator = ','
          indent = ' ' * len(self.__class__.__name__)
      result += indent + ')'
      return result

def children(self):
    """ A sequence of all children that are Nodes
    """
    pass

def show(self, buf=sys.stdout, offset=0, attrnames=False, nodenames=False, showcoord=False, _my_node_name=None):
  """ Pretty print the Node and all its attributes and children (recursively) to a buffer.
      buf:
          Open IO buffer into which the Node is printed.
      offset:
          Initial offset (amount of leading spaces)
      attrnames:
          True if you want to see the attribute names in name=value pairs. False to only see the values.
      nodenames:
          True if you want to see the actual node names within their parents.
      showcoord:
          Do you want the coordinates of each Node to be displayed.
    """
    lead = ' ' * offset
    if nodenames and _my_node_name is not None:
      buf.write(lead + self.__class__.__name__+ ' <' + _my_node_name + '>: ')
    else:
      buf.write(lead + self.__class__.__name__+ ': ')

    if self.attr_names:
      if attrnames:
          nvlist = [(n, getattr(self, n)) for n in self.attr_names if getattr(self, n) is not None]
          attrstr = ', '.join('%s=%s' % nv for nv in nvlist)
      else:
          vlist = [getattr(self, n) for n in self.attr_names]
          attrstr = ', '.join('%s' % v for v in vlist)
      buf.write(attrstr)

    if showcoord:
      if self.coord:
        buf.write('%s' % self.coord)
    buf.write('\n')

    for (child_name, child) in self.children():
      child.show(buf, offset + 4, attrnames, nodenames, showcoord, child_name)

class Coord(object):
  """ Coordinates of a syntactic element. Consists of:
          - Line number
          - (optional) column number, for the Lexer
  """
  __slots__ = ('line', 'column')

  def __init__(self, line, column=None):
    self.line = line
    self.column = column

  def __str__(self):
    if self.line:
      coord_str = "   @ %s:%s" % (self.line, self.column)
    else:
      coord_str = ""
    return coord_str



class Program(Node):
  __slots__ = ('gdecls', 'coord')
  
  def __init__(self, gdecls, coord=None):
    self.gdecls = gdecls
    self.coord = coord

  def children(self):
    nodelist = []
    for i, child in enumerate(self.gdecls or []):
      nodelist.append(("gdecls[%d]" % i, child))
    return tuple(nodelist)

  attr_names = ()

class UnaryOp(Node):
  __slots__ = ('op', 'value', 'coord')
  def __init__(self, op, value, coord=None):
    self.op = op
    self.value = value
    self.coord = coord

  def children(self):
    nodelist = []
    if self.value is not None: 
      nodelist.append(("value", self.value))
    return tuple(nodelist)

  attr_names = ('op', )

class BinaryOp(Node):
  __slots__ = ('op', 'lvalue', 'rvalue', 'coord')
  
  def __init__(self, op, left, right, coord=None):
    self.op = op
    self.lvalue = left
    self.rvalue = right
    self.coord = coord

  def children(self):
    nodelist = []
    if self.lvalue is not None: 
      nodelist.append(("lvalue", self.lvalue))
    if self.rvalue is not None: 
      nodelist.append(("rvalue", self.rvalue))
    return tuple(nodelist)

  attr_names = ('op', )

class Cast(Node):
  __slots__ = ('cast', 'coord')

  def __init__(self, cast, coord=None):
      self.cast = cast
      self.coord = coord

  def children(self):
      nodelist = []
      if self.cast is not None:
        nodelist.append(('cast', self.cast))
      return tuple(nodelist)

  attr_names = ()

class Constant(Node):
  __slots__ = ('type', 'value', 'coord')
  
  def __init__(self, type, value, coord=None):
    self.type = type
    self.value = value
    self.coord = coord

  def children(self):
    nodelist = []
    return tuple(nodelist)

  attr_names = ('type', 'value', )

class GlobalDecl(Node):
  __slots__ = ('decls', 'coord')

  def __init__(self, decls, coord=None):
    self.decls = decls
    self.coord = coord

  def children(self):
    nodelist = []
    for i,decl in enumerate(self.decls if self.decls is not None else []):
        if self.decls is not None:
          nodelist.append(("decls[%d]" % i, decl))
    return tuple(nodelist)

  def __iter__(self):
    if self.decls is not None:
        yield self.decls

  attr_names = ()

class EmptyStatement(Node):
  __slots__ = ("coord")

  def __init__(self, coord=None):
    self.coord = coord

  def children(self):
    return ()

  attr_names = ()

class FuncDef(Node):
  __slots__ = ('spec', 'decl', 'params', 'body','coord')

  def __init__(self, spec, decl, params, body, coord=None):
    self.spec = spec
    self.decl = decl
    self.params = params
    self.body = body
    self.coord = None

  def children(self):
    nodelist = []
    if self.spec is not None: 
      nodelist.append(("spec", self.spec))
    if self.decl is not None: 
      nodelist.append(("decl", self.decl))
    if self.params is not None: 
      nodelist.append(("params", self.params))
    if self.body is not None: 
      nodelist.append(("body", self.body))
    return tuple(nodelist)

    attr_names = ()

class Type(Node):
  __slots__ = ('names', 'coord')

  def __init__(self, names, coord=None):
    self.names = names
    self.coord = coord

  def children(self):
    nodelist = []
    return tuple(nodelist)

  def __iter__(self):
    return
    yield

  attr_names = ('names',)

class ID(Node):
  __slots__ = ('name', 'coord')

  def __init__(self, name, coord=None):
    self.name = name
    self.coord = coord

  def children(self):
    nodelist = []
    return tuple(nodelist)

  def __iter__(self):
    return
    yield

  attr_names = ('name', )

class Compound(Node):
  __slots__ = ('coord')

  def __init__(self, coord=None):
    self.coord = coord

  def children(self):
    nodelist = []
    return tuple(nodelist)

  attr_names = ()

class Read(Node):
  __slots__ = ('expression', 'coord')

  def __init__(self, expression, coord=None):
    self.expression = expression
    self.coord = coord

  def children(self):
    nodelist = []
    nodelist = [('read', self.expression)]
    return tuple(nodelist)

  attr_names = ()

class Print(Node):
  __slots__ = ('expression', 'coord')

  def __init__(self, expression, coord=None):
    self.expression = expression
    self.coord = coord

  def children(self):
    nodelist = []
    if self.expression is not None: 
      nodelist.append(('print', self.expression))
    return tuple(nodelist)

  attr_names = ()

class Assert(Node):
  __slots__ = ('expression', 'coord')

  def __init__(self, expression, coord=None):
    self.expression = expression
    self.coord = coord

  def children(self):
    nodelist = []
    nodelist = [('assert', self.expression)]
    return tuple(nodelist)

  attr_names = ()

class Return(Node):
  __slots__ = ('expression', 'coord')

  def __init__(self, expression, coord=None):
      self.expression = expression
      self.coord = coord

  def children(self):
      nodelist = []
      if self.expression is not None: 
        nodelist.append(('expression', self.expression))
      return tuple(nodelist)

  attr_names = ()

class Break(Node):
  __slots__ = ('coord')

  def __init__(self, coord=None):
    self.coord = coord

  def children(self):
    return ()

  attr_names = ()

lass For(Node):
  __slots__ = ('initial','cond','next','statement','coord')

  def __init__(self, initial, cond, next, statement, coord=None):
    self.initial = initial
    self.cond = cond
    self.next = next
    self.statement = statement
    self.coord = coord

  def children(self):
      nodelist = []
      if self.inital is not None: 
        nodelist.append(('inital', self.inital))
      if self.cond is not None: 
        nodelist.append(('cond', self.cond))
      if self.next is not None: 
        nodelist.append(('next', self.next))
      if self.statement is not None: 
        nodelist.append(('statement', self.statement))
      return tuple(nodelist)

  attr_names = ()

class While(Node):
  __slots__ = ('cond', 'statement', 'coord')

  def __init__(self, cond, statement, coord=None):
    self.cond = cond
    self.statement = statement
    self.coord = coord

  def children(self):
    nodelist = []
    if.self.cond is not None:
      nodelist.append(('cond', self.cond))
    if.self.statement is not None:
      nodelist.append(('statement', self.statement))
    return tuple(nodelist)

  attr_names = ()

class If(Node):
  __slots__ = ('cond', 'true', 'false', 'coord')

  def __init__(self, cond, true, false, coord=None):
    self.cond = cond
    self.true = true
    self.false = false
    self.coord = coord

  def children(self):
    nodelist = []
    if.self.cond is not None:
      nodelist.append(('cond', self.cond))
    if.self.true is not None: 
      odelist.append(('true', self.true))
    if.self.false is not None:
      nodelist.append(('false', self.false))
    return tuple(nodelist)

  attr_names = ()

class Assignment(Node):
  __slots__ = ('value0', 'op', 'value1', 'coord')

  def __init__(self, value0, op, value1, coord=None):
    self.value0 = value0
    self.op = op
    self.value1 = value1
    self.coord = coord

  def children(self):
    nodelist = []
    if self.value0 is not None: 
      nodelist.append(('value0', self.value0))
    if self.value1 is not None: 
      nodelist.append(('value1', self.value1))
    return tuple(nodelist)

  attr_names = ('op', )


class ParamList(Node):
  __slots__ = ('params', 'coord')

  def __init__(self, params, coord=None):
    self.params = params
    self.coord = coord

  def children(self):
    nodelist = []
    for i, child in enumerate(self.params or []):
      nodelist.append(("params[%d" % i, child))
      return tuple(nodelist)

  def __iter__(self):
    for child in (self.params or []):
      yield child

  attr_names = () 

class InitList(Node):
  __slots__ = ('first', 'second', 'coord')

  def __init__(self, first, coord=None):
    self.first = first
    self.coord = coord

  def children(self):
    nodelist = []
    fot i, child in enumerate(self.first or []):
      nodelist.append(("expres[{}]".format(i), child))
    return tuple(nodelist)

  attr_names = ()

class Decl(Node):
  __slots__ = ('name', 'type', 'initializer', 'coord')

  def __init__(self, name, type, initializer, coord=None):
      self.name = name
      self.type = type
      self.initializer = initializer
      self.coord = coord

  def children(self):
      nodelist = []
      if self.type is not None: 
        nodelist.append(('type', self.type))
      if self.initializer is not None: 
        nodelist.append(('initializer', self.initializer))
      return tuple(nodelist)

  def __iter__(self):
      if self.name is not None:
          yield self.name
      if self.type is not None:
          yield self.type
      if self.initializer is not None:
          yield self.initializer

  attr_names = ('name', )

class VarDecl(Node):
  __slots__ = ('type', 'namevar', 'coord')

  def __init__(self,  type, namevar, coord=None):
    self.type = type
    self.namevar = namevar
    self.coord = coord

  def children(self):
    nodelist = []
    if self.namevar is not None: 
      nodelist.append(('namevar', self.namevar))
    if self.type is not None: 
      nodelist.append(('type', self.type))
    return tuple(nodelist)

    def __iter__(self):
    if self.type is not None:
        yield self.type
    if self.namevar is not None:
        yield self.namevar

    attr_names = ()
