# pyvizlinkeddata

## What?
This code runs a series of SPARQL queries on linked data and maps out the data structures that are found.

It runs the following steps:
* Find all distinct URLs for `rdf:type`
* For each type, find all data type and object properties along with their use count
* Find links between instances of each type. 

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
