# Bitnest (name change needed)

The core idea of bitnest is "conditional nested structures". 

# Documentation

To build the documentation

```shell
cd docs
sphinx-build -b html . _build
```

The documents should also be readable in github via its built in
markdown renderer.

# Usage

Currently this problem is being approached from the high level user
interface. 

## [Graphviz](https://graphviz.org/) representation of Specification

```python
from bitnest.output.visualize import visualize

from models.simple import MILSTD_1553_Message

graph = visualize(MILSTD_1553_Message)
graph.view()
```

## Markdown document of specification

```python
from bitnest.output.markdown import markdown

from models.simple import MILSTD_1553_Message

print(markdown(MILSTD_1553_Message))
```
