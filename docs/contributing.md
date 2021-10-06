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
 - integer `integer` 
 - float `float`
 - enum `enum`

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

## Python DSL

Suppose we have the simple structure. In python

```python
class StructB(Struct):
    """All about StructB description"""

    name = "StructB"
    fields = [
        SignedInteger(name="FieldB", size=8, help="info about FieldB")
    ]

    conditions = [
        FieldReference('FieldB') == 0x10
    ]

class StructC(Struct):
    """All about StructB description"""

    name = "StructC"
    fields = [
        SignedInteger(name="FieldC", size=8, help="info about FieldC")
    ]

class StructA(Struct):
    """All about StructA description"""

    name = "StructA"
    fields = [
        Bits(name="FieldA", size=4, help="info about FieldA"),
        Union(StructB, StructC),
    ]
```

Get converted into the following lisp like structure. The structure
can be thought of an the bitnest internal representation of a nested
binary structure. Mentioned previously this list structure is wrapped
in a `bitnest.core.Expression` object which allows for interacting
with this structure in a more pythonic way.

```python
StructA.expression()
```

```python
(struct, 'StructA', 
  (list, 
    (field, 'bits', 'FieldA', None, (integer, 4), None, {'help': 'info about FieldA'}), 
    (union, 
      (struct, 'StructB', 
        (list, 
          (field, 'signed_integer', 'FieldB', None, (integer, 8), None, {'help': 'info about FieldB'})), 
        (list, 
          (eq, (field_reference, 'FieldB', None), (integer, 16))), 
        {'help': 'All about StructB description'}), 
      (struct, 'StructC', 
        (list, 
          (field, 'signed_integer', 'FieldC', None, (integer, 8), None, {'help': 'info about FieldC'})), 
        (list,), 
        {'help': 'All about StructB description'}))), 
  (list,), 
  {'help': 'All about StructA description'})
```

## Passes

Once the structure has been formed there are many transform, analysis,
and backend passes that can be done.

### Transform Pass

#### Realize DataTypes

This transformation plays an important role and is usually the first
transform that takes place. Its job is to calculate all the complete
datatypes that can exist from a nested set of structs along with
uniquely identifying each field in the structure. This pass is a post
order traversal of the AST. Each field encountered is numbered and
since the traversal is deterministic the field id is deterministic as
well.

The first point of calculating all the paths that result in unique
datatypes deserves more discussion. Take for example the
representative Struct below. Each path through the structure
represents the construction of a datatype.

```python
class StructB(Struct):
    """All about StructB description"""

    name = "StructB"
    fields = [
        UnsignedInteger(name="FieldB", size=8, help="info about FieldB")
        Vector(StructD, length=FieldReference('FieldB'))
    ]

    conditions = [
        FieldReference('FieldB') == 0x10
    ]

class StructD(Struct):
    """All about StructD description"""

    name = "StructD"
    fields = [
        SignedInteger(name="FieldD", size=8, help="info about FieldD")
    ]

class StructC(Struct):
    """All about StructC description"""

    name = "StructC"
    fields = [
        SignedInteger(name="FieldC", size=8, help="info about FieldC")
    ]

class StructA(Struct):
    """All about StructA description"""

    name = "StructA"
    fields = [
        Bits(name="FieldA", size=4, help="info about FieldA"),
        Union(StructB, StructC),
    ]
```

Here is the general algorithm. When you encounter:
  - field node `(field ...)` this is a leaf node and results in one path.
  - union node `(union [<s1>] ... [<s2>])` a union node results in the
    addition of each path in the union. Suppose `(union [5] [3] [2])`
    where each element of the union has 5, 3, 2 paths then it will
    result in 9 total paths. We simply merge each path.
  - vector node `(vector [<s1>] length)` preserves the number of paths
    in `[<s1>]` thus if there were 4 paths then the application of
    vector would result in 4 paths.
  - struct node is the last an most tricky one to handle. Suppose we
    have `(struct [<f1>] ... [<fn>])`. The number of paths is the
    cross product of each field's paths. Thus if there are `(struct
    [4] [5] [2] [1])` paths for each field the number of resulting
    paths would be `4 * 5 * 2 * 1 = 40` paths. In the case of python
    we use `itertools.product` to calculate all combinations.

Lets look at the concrete example above. A high level representation
of this structure (not the actual lisp representation).

```python
(struct StructA
  (field FieldA)
  (union
    (struct StructB
       (field FieldB)
       (vector 
         (struct StructD
           (field FieldD))))
    (struct StructC
       (field FieldC))))
```

Lets walk through the tree is post order traversal (L->RN).

 - `(field FieldA)` -> `[(field FieldA 0)]`
 - `(field FieldB)` -> `[(field FieldB 1)]`
 - `(field FieldD)` -> `[(field FieldD 2)]`
 - `(struct StructD [(field FieldD 2)])` -> `[(struct StructD (field FieldD 2))]`
 - `(vector [(struct StructD (field FieldD 2))])` -> `[(vector (struct StructD (field FieldD 2)))]`
 - `(struct StructB [(field FieldB 1)] [(vector (struct StructD (field FieldD 2)))])` -> `[(struct StructB (field FieldB 1) (vector (struct StructD (field FieldD 2))))]`
 - `(field FieldC)` -> `[(field FieldC 3)]`
 - `(struct StructC [(field FieldC 3)])` -> `[(struct StructC (field FieldC 3))]`
 - `(union [(struct StructB (field FieldB 1) (vector (struct StructD (field FieldD 2))))] [(struct StructC (field FieldC 3))])` -> `[(struct StructB (field FieldB 1) (vector (struct StructD (field FieldD 2)))), (struct StructC (field FieldC 3))]`
 - `(struct StructA [(field FieldA 0)] [(struct StructB (field FieldB 1) (vector (struct StructD (field FieldD 2)))), (struct StructC (field FieldC 3))])` -> `[(struct StructA (field FieldA 0) (struct StructB (field FieldB 1) (vector (struct StructD (field FieldD 2)))), (struct StructA (field FieldA 0) (struct StructC (field FieldC 3))]`
 
This shows the whole process and we see that it results in 2 datatypes:
 - `(struct StructA (field FieldA 0) (struct StructB (field FieldB 1) (vector (struct StructD (field FieldD 2))))`
 - `(struct StructA (field FieldA 0) (struct StructC (field FieldC 3))`

These structures are most importantly deterministic and we can
calculate all the positions for fields and easily write a parser for
these datatypes. The only slight difficulty is in handling vectors
since this makes the location of datafields depend on the length etc.

This transformation then wraps these paths in `datatype` nodes. It is
important to preserve the lisp like datastructure to make future
transformation compose nicely. Importantly we can see from this that
the growth of the number of datatypes is roughly proportional to the
product of the lengths/cardinality of all unions (ends up being
slightly less depending on nesting).

```python
(list
  (datatype (struct StructA (field FieldA 0) (struct StructB (field FieldB 1) (vector (struct StructD (field FieldD 2))))))
  (datatype (struct StructA (field FieldA 0) (struct StructC (field FieldC 3)))))
```

#### Realize Conditions

Once we have all the resulting datatypes we then need to link
conditions with their corresponding fields. As mentioned in the
previous translation each field has been assigned a field id (not
shown in the example above).

Take for example the condition `FieldReference('FieldB') == 0x10`
within the `StructB` struct. Within bitnest this has an equivalent
form.

```python
(eq (field_reference "FieldB") (integer 0x10))
```

Once this traversal is complete the field id is updated to reflect the
actual id within the tree. This is a little trickier than just
aimlessly searching for the field within the tree since there can be
multiple occurences of a field within a tree. Thus we have to traverse
the tree to find the field from the place that the condition was
added.

```python
(eq (field_reference "FieldB" 1) (integer 0x10))
```

#### Realize Offsets

Take the example above. While not included in this high level
description we have the size (number of bits).
 - FieldA (4 bits)
 - FieldB (8 bits)
 - FieldC (8 bits)
 - FieldD (8 bits)

```python
(list
  (datatype (struct StructA (field FieldA 0) (struct StructB (field FieldB 1) (vector (struct StructD (field FieldD 2))))))
  (datatype (struct StructA (field FieldA 0) (struct StructC (field FieldC 3)))))
```

When we look at both of the datatypes we get the following structures:
 - `[FieldA FieldB Vector(FieldD)]`
 - `[FieldA FieldC]`

Also note that the Vector has length equal to the value of
FieldB. From this we have all we need to calculate offsets from the
beginning of the structure along with the total length. Lets start
with the second one since the calculation is easier.

`[FieldA FieldC]`:

  - FieldA (size 4) (offset 0)
  - fieldC (size 8) (offset 0 + 4)

With the total size being 12 bits for the second datatype. Now lets
look at the first datatype.

`[FieldA FieldB Vector(FieldD)]`
 
 - FieldA (size 4) (offset 0)
 - FieldB (size 8) (offset 0 + 4)

Now the next part is trickier we know that the total length of the
vector is equal to FieldB. We need to calculate the size of the
contents of `Vector` to know the total size of the datatype. In this
case the inner structure is only `FieldD` but this can be more complex
and we need to recursively calculate the size. This means we can only
know the size of the message at runtime. This is okay we have a
symbolic formula to calculate the size. The size of FieldD is 8
bits. Thus the formula for offset for FieldD (assume we assign `i` to
the vector index.

 - FieldD (size 8) (offset 0 + 4 + 8 + (i * 8))

And the total size of the message is `0 + 4 + 8 +
(FieldReference(FieldC) * 8)`. Since bitnest was designed to be
symbolic this is a perfectly fine representation of the total length.

#### Arithmetic Simplify

This transformation is critical to for having easy to read
expressions. Currently only addition operations are simplified. As
additional simplification is needed this routine will be
improved. Shows how expressions are simplified.

```
(+ 1 (+ a 3)) -> (+ 1 a 3) -> (+ a 4)
(+ 1 (+ 2 3)) -> (+ 1 2 3) -> (+ 6) -> 6
```

#### Parser Datatype 

The parser datatype takes all of the information from the previous
transformations to generate a program that can parse the datatype. All
of the previous transformations were critical in getting enough
information to write the program.

```python
(list
  (datatype (struct StructA (field FieldA 0 4 0) (struct StructB (field FieldB 1 8 4) (vector (struct StructD (field FieldD 2 8 (12 + i*8)))))))  # total size 12 + FieldReference(FieldC) * 8
  (datatype (struct StructA (field FieldA 0 4 0) (struct StructC (field FieldC 3 8 4))))) # total size 12.
```

Additionally we have a condition for StructB.
 - `(eq (field_reference "FieldB" 1) (integer 0x10))`

In pseudo code we want to create a program that says the following:

```
if (FieldB == 0x10) and (length of message is 12 + FieldReference(FieldC) * 8):
   # it is datatype 1!
if (lenth of message is 12):
   # it is datatype 2!
```

This is exactly what this transformation generates. This is the power
of having composible transformations! Note that this is a high level
(not totally accurate portrayal of the programming AST). Notice that
this AST that is emitted is language independent and can easily create
efficient c and python code.

```
(statements
  (if (and (eq (field FieldB) 0x10) (len message (add 12 (mul (field_reference FieldC) 8))))
     (assign datatype 1)
  (if (len message 12)
     (assign datatype 2))))
```

### Analysis Pass

The analysis passes do not return an `Expression` object. They do
however ruturn python datastructures about the AST after running the
analysis.

#### Inspect Datatype

Take the following example above once we have all the offsets
etc. This analysis stage can be run earlier in the process it just
requires `datatype` nodes to exist.

```python
(list
  (datatype (struct StructA (field FieldA 0 4 0) (struct StructB (field FieldB 1 8 4) (vector (struct StructD (field FieldD 2 8 (12 + i*8)))))))  # total size 12 + FieldReference(FieldC) * 8
  (datatype (struct StructA (field FieldA 0 4 0) (struct StructC (field FieldC 3 8 4))))) # total size 12.
```


Several outputs come from the analysis for each datatype:
 - fields
 - conditions
 - regions

`fields` is the list of fields that result from the datatype:
 - `[FieldA FieldB Vector(FieldD)]`
 - `[FieldA FieldC]`

`conditions` is the list of conditions for each datatype:
 - `(eq (field_reference "FieldB" 1) (integer 0x10))`
 - N/A

`regions` is so that we can understand the regions that a given
struct/vector take.
 - StructA (0-4 bits), StructB (4-12 bits), Vector (12 - 12 + FieldReference(FieldC) * 8), StructD (12 - 12 + FieldReference(FieldC) * 8)
 - StructA (0-4 bits), StructC (4-12 bits)

### Backend

Currently there is only a python backend and soon a c backend. But
future ones should be easy enough to add.

#### Python

Take the following expression to see how the python backend works.

```python
(eq (add (integer 1) (variable "a")) (integer 3))
```

We visit the tree in post order.

 - `(integer 1)` -> `ast.Constant(1)`
 - `(variable "a")` -> `ast.Name("a")`
 - `(add ast.Constant(1) ast.Name("a"))` -> `ast.BinOp(ast.Add() ast.Constant(1) ast.Name("a"))`
 - `(integer 3)` -> `ast.Constant(3)`
 - `(eq ast.BinOp(ast.Add() ast.Constant(1) ast.Name("a")) ast.Constant(3))` -> `ast.Compare(ast.BinOp(ast.Add() ast.Constant(1) ast.Name("a")), ops=[ast.Eq()], comparators=[ast.Constant(3)])`

Now that we have the ast representation in python
`ast.Compare(ast.BinOp(ast.Add() ast.Constant(1) ast.Name("a")),
ops=[ast.Eq()], comparators=[ast.Constant(3)])` we can
`astor.tosource(...)` on the ast and get the source code.

```python
((1 + a) == 3)
```
