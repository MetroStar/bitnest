# Contributing

## Terminology

 - `Field` is sequential bits not necessarily byte aligned. There are
   many Field subclasses such as `UnsignedInteger`, `SignedInteger`,
   `Bits`, etc.
 - `Struct` is an ordered collection of Fields, Union of Structs, and
   Vectors or Structs
 - `Union` is a 

## Internal Representation

 - Field :: `Field (...)`
 - Struct :: `(Struct ... ...)`
 - Union a collection of one or more `Struct` :: `(Union (Struct ... ...)+)`
 - Vector a repeated `Struct` :: `(Vector (Struct ... ...))`

## Compiler Stages

### DataType Calculation

Lets take the following simple specification. This specification is
also used for testing of bitnest.

```python
class StructB(Struct):
    name = "StructB"
    fields = [Bits(name="FieldB", 8)]

class StructC(Struct):
    name = "StructC"
    fields = [Bits(name="FieldC", 4)]

class StructA(Struct):
    name = "StructA"
    fields = [Bits(name="FieldA", 4), Union(StructB, StructC)]
```

When we pass `datatype = realize_datatype(StructA)` we need a
structural representation of the datatype. We get the
following. Notice however that while this form is compact this does
not realize the "paths" or different structs we could encounter. 

```python
(StuctA FieldA (Union (StructB FieldB) (StructC FieldC)))
```

For this we use the `structs = realize_datatype_paths(datatype)` where
structs is a collection of all the datastructures that the given
specification could represent. In this case there is a single union
meaning that the number of posible structs are `2`. The result is the
following. We keep the `structs` in the structure to preserve
heigharchy. A depth first search is used to construct these paths.

```python
structs = [
    (StructA FieldA (StructB FieldB)),
    (StructA FieldA (StructC FieldC)),
]
```

This can be reduced further by removing the Struct definitions.

```python
structs = [
    (FieldA FieldB),
    (FieldA FieldC)
]
```

There is a straightforward way of calculating all the paths. This took
some time to formalize. Whenever a `Struct` element is encountered the
number of resulting paths is the cartesian product of all paths. In
this case `n x m x j`.

```
(Struct (n paths) (m paths) ... (j paths))
```

If a `Union` element is encountered the number of resulting paths is
an addition of all the paths. `n + m + j`.

```
(Union (n paths) (m paths) ... (j paths))
```

Since a `Vector` is a single path `(Vector (Struct ...))` this element
does not affect the number of paths. Thus `(Vector (n paths))` results
in `n` paths. Fields behave very much the same way except for the fact
that `Field` are leaf nodes to the tree and thus always result in a
single path.
