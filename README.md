# pyvizlinkeddata

Use:
```
prefixes = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
"""

g = Graph().parse('example.json', format="json-ld")
# Specify the location where a dot file will be saved
# This will be used by Graphviz to render a png with the same name (but png extension).
dotFile = "/path/to/example.dot"
visualize_linked_data(g, prefixes, dotFile)
```
