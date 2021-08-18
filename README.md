# Bitnest (name change needed)

The core idea of bitnest is "conditional nested structures". 

# Documentation

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
