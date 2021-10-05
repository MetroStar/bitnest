# Contributing

## Architecture

At a high level bitnest is a compiler that generates parsers for
binary data. Compilers can be represented in three sections frontend,
transform, backend. In literature the transform step is usually
referred to as term-rewriting.

### Frontend

In the case of Bitnest the frontend is a python domain specific
language (DSL). This was chosen because of the burden on creating new
languages and that python is flexible enough to accurately represent
the relationship between structs, fields, vectors, and unions. Great
examples of these are in the [models
directory](https://github.com/MetroStar/bitnest/tree/master/models). Once
a binary structure is represented in the model it is quickly converted
into an internal AST done in
[bitnest/field.py](https://github.com/MetroStar/bitnest/blob/master/bitnest/field.py). The
internal AST structures is simply a nesting of python tuples. Why such
a simple structure? This simple structure makes the later stages much
easier to handle. And in my opinion where LISP shines. These nested
tuple structures are wrapped in the [Expression
class](https://github.com/MetroStar/bitnest/blob/master/bitnest/core.py#L53)
which allows for the pythonic construction of the AST. Sometimes this
class makes it easier to build a tree. For example suppose we have
`1 + a`. In the internal AST this would be represented as

```
Expression((Symbol("add"), (Symbol("integer"), 1), (Symbol("variable"), "a")))
```

We can easily construct this using `bitnest.core` via `Integer(1) +
Variable("a")`.

### Transform/Analysis

Now that we have an internal AST we need to transform and analyze the
AST. Often times it can be confusing when working with the internal
AST since it is hard to keep track of the passes being made and where
we are in the process. To help with this we have adopted the [LLVM
approach](https://llvm.org/docs/Passes.html) to working with the
AST. We can think of each transformation as a logical pass over the
tree. Within bitnest there are three types of passes.

The `analysis` pass will not modify the internal AST. It will analyze
the AST and return information in python datastructures. See
[bitnest/analysis](https://github.com/MetroStar/bitnest/tree/master/bitnest/analysis). An
example is `inspect_datatypes.py` which returns the fields within each
datatype, conditions for each datatype, and other useful information
for understanding the AST.

The `transform` pass will modify the internal AST. The modifications
can be simpler such as `(Symbol("add"), (Symbol("integer"), 1),
(Symbol("add"), (Symbol("integer"), 2), (Symbol("integer"), 3)))` to
`(Symbol("add"), (Symbol("integer"), 2), (Symbol("integer"), 3)`. The
idea is to convert `(+ 1 (+ 2 3))` to `(+ 1 2 3)`. This is just one
example of a transformation. This transformation is done in
[bitnest/transform/arithmetic_simplify.py](https://github.com/MetroStar/bitnest/blob/master/bitnest/transform/arithmetic_simplify.py).

Finally we have the `backend`. This pass takes the internal AST after
several transformations and generates code that can then be executed
independent of the compiler. The simplest example of this is the
[bitnest/backend/python.py](https://github.com/MetroStar/bitnest/blob/master/bitnest/backend/python.py). This
will convert for example `(Symbol("add"), (Symbol("integer"), 1),
(Symbol("integer"), 2))` into `ast.BinOp(ast.Add(), 1, 2)` into `(1 +
2)`. Here bitnest lowers the internal AST into the python ast which
then gets written to python source code.

It is common for multiple passes to be performed. Each pass through
the tree is done in a specific order. Using the following labeling
node `N`, left most child node `L`, right most child node `R`. See
[tree traversal](https://en.wikipedia.org/wiki/Tree_traversal)
currently pre-order (NL->R) and post-order (L->RN) are being used. In
some cases both are used together (see
[bitnest/transform/realize_offsets.py](https://github.com/MetroStar/bitnest/blob/master/bitnest/transform/realize_offsets.py)
which visit in the following pattern (NL->RN).

### Backend

The backend as mentioned previously is responsible for generating
executable code. The first example of this the python backend
[bitnest/backend/python.py](https://github.com/MetroStar/bitnest/blob/master/bitnest/backend/python.py). However,
are being written for more efficient execution.

### End-To-End Example

Take the following example of a MILSTD 1553 Packet

```python
from models.simple import MILSTD_1553_Message

MILSTD_1553_Message.expression() \
    .transform("realize_datatypes") \
    .transform("realize_conditions") \
    .transform("realize_offsets") \
    .transform("parser_datatype") \
    .transform("arithmetic_simplify") \
    .backend("python")
```

Will generate the following code. Currently simple output but this
will improve over time.

```python
__datatype_mask = 0
if __bits[8:13] == 31:
    __datatype_mask = __datatype_mask | 1
if __bits[13:16] == 0:
    __datatype_mask = __datatype_mask | 2
```

## Internal AST Nodes

Bitnest uses a LISP like internal representation of the abstract
syntax tree (ast). In this section we will describe the structure of
each of these nodes. At a high level there are three types of
nodes. `Arithmetic` nodes deal with math operations on
variables. `Field` nodes are data representations of the structure and
relationship between structures. Finally `Programming` nodes are used
near the end of the AST transformation to represent things that are
necessary for representing programs to process the structures. 

### Arithmetic Nodes

 - unary operation: invert `not`
 - logical and `logical_and`, logical or `logical_or`
 - bitwise and `bit_and`, bitwise or `bit_or`
 - addition `add`, subtraction `sub`, multiply `mul`, floor divide `floordiv`, true divide `truediv` all support `N` arguments `(<op> <1> ... <N>)`
 - modulus `mod`
 - equal `eq`, not equal `ne`, less than `lt`, greater than `gt`, less than equal `le`, greater than equal `ge`

### Field Nodes

 - `field` is sequential bits not necessarily byte aligned. There are
   many Field subclasses such as `UnsignedInteger`, `SignedInteger`,
   `Bits`, etc. which is represented by a 
 - `struct` is an ordered collection of Fields, Union of Structs, and
   Vectors or Structs
 - `union` is a set of `Struct`'s 
 - `vector` is `N` repeats of a given `Struct` represented as `(Symbol('vector'), <Struct> <length>)`
 - `datatype` is a representation of a concrete structure (without
   `union` in the tree) important for reasoning about the size of a
   structure. Generated in the `realize_datatype` transform pass.

### Programming Nodes

 - `quote` is to protect it's arg from evaluation (not used much in
   bitnest) but a valuable concept in lisp `(quote (...))`
 - `list` defined a list of `N` elements (represented as the args)
   `(list <1> ... <N>)`
 - `assign` meant for assignment statements e.g. `(assign (variable a)
   (integer 1))` which is equivalent to `a = 1`.
 - `variable` which represents a given variable in the code that does
   not have a set value. `(variable "<name>")`.
 - for convenience there is a `UniqueVariable()` constructor that is
   guaranteed to generate a unique variable name. Not used at the
   moment but a critical function needed for some AST transformation.
 - `if` for representing conditional statements to execute `(if (eq 1
   1) (assign (variable a) (integer 10)))` which is equivalent to `if
   (1 == 1): a = 10`. Currently else not implemented but may be
   valuable.
 - `statements` is a way of representing a list of
   statements. `(statement (assign (variable a) (integer 10)) (assign
   (variable a) (add (variable a) (integer 20))))` which is equivalent
   to `a = 10; a = a + 20`.
 - `index` for indexing into a vector done via `(index (variable a)
   (integer 20) (integer 30))` which is equivalent to `a[20:30]`.

## Transform Passes

