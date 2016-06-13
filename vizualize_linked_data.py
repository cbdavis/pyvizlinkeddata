# -*- coding: utf-8 -*-

import pandas as pd
import os
from rdflib import Graph
import re

def getAllSubjectTypes(g, prefixes):
    query_result = g.query(prefixes + 
        """
        select ?subjectType (count(?subjectType) as ?subjectTypeCount) where {
            ?s rdf:type ?subjectType
        } group by ?subjectType
       """)

    df = pd.DataFrame()
    for row in query_result:
        df = df.append({"subject": str(row[0]), "subjectCount" : int(row[1])}, ignore_index=True)        
        
    return df
    

def getAllDataTypeProperties(g, prefixes, subjectType):
    query_result = g.query(prefixes + 
        """
        select ?p (count(?p) as ?count) ?dataType where {
            BIND(<""" + subjectType + """> as ?subjectType) . 
            ?s rdf:type ?subjectType . 
            ?s ?p ?o . 
            filter(?p != rdf:type) . 
            OPTIONAL {?o rdf:type ?z} . 
            FILTER(!BOUND(?z)) . 
            BIND(datatype(?o) as ?dataType) . 
        } group by ?subjectType ?p ?dataType order by ?subjectType ?p ?dataType
       """)

    df = pd.DataFrame()
    for row in query_result:
        df = df.append({"subject": subjectType, 
                        "predicate" : str(row[0]), 
                        "object": str(row[2]), 
                        "count": int(row[1])}, ignore_index=True)        

    return df


def getAllObjectProperties(g, prefixes, subjectType):
    query_result = g.query(prefixes + 
    """
    select ?s ?p (count(?p) as ?instanceCount) ?objType where {
      BIND(<""" + subjectType + """> as ?subjectType) . 
      ?s rdf:type ?subjectType . 
      ?s ?p ?o . 
      filter(?p != rdf:type) . 
      ?o rdf:type ?objType .
    } group by ?subjectType ?p ?objType
    """)
    
    df = pd.DataFrame()
    
    
    for row in query_result:
        if str(row[1]) != 'None':
            df = df.append({"subject": subjectType, 
                            "predicate" : str(row[1]), 
                            "object" : str(row[3]), 
                            "count": int(row[2])}, ignore_index=True)        
    return df

# clean up characters so that graphviz will be able to make a link to a part of the table
def makeLinkPort(text):
    return re.sub(":|\\.|/", "_", text)



def visualize_linked_data(g, prefixes, dotFile):
    # remove the old dot file, we'll write a new one
    if (os.path.isfile(dotFile)):
        os.remove(dotFile)
    
    imgFile = dotFile.replace(".dot", ".png")
    
    text_file = open(dotFile, "a")
    # for rankdir, could try RL or TB (right-left or top-bottom) for alternative layouts
    # text_file.write('digraph G {\nrankdir=TB\nsize="50,50"\n\n')
    text_file.write('digraph G {\nrankdir=TB\nsize="50,50"\n\n')
    
    # figure out how many objects we have for each type of subject count
    subjectTypesAndCounts = getAllSubjectTypes(g, prefixes)
    
    subjectTypes = subjectTypesAndCounts.subject
    
    # iterate over subjects
    for subjTuple in subjectTypesAndCounts.itertuples():
        subjectType = subjTuple.subject
        subjectCount = subjTuple.subjectCount
    
        text_file.write("node [shape=plaintext]\n")
        text_file.write('"' + makeLinkPort(subjectType) + '" [label=<\n')
        text_file.write('<TABLE border="0" cellborder="1" cellspacing="0">\n')
        text_file.write('<tr>')
        text_file.write('<td colspan="3" port="' + makeLinkPort(subjectType) + '" bgcolor="yellow">')
        text_file.write(subjectType + ' (Count: ' + str(int(subjectCount)) + ')')
        text_file.write('</td></tr>\n')
        text_file.write('<tr><td colspan="3" port="PROPERTIES" bgcolor="pink">PROPERTIES</td></tr>\n')
        
        df = pd.DataFrame()
        df = df.append(getAllDataTypeProperties(g, prefixes, subjectType))
        df = df.append(getAllObjectProperties(g, prefixes, subjectType))
    
        text_file.write('<tr>')
        text_file.write('<td><FONT FACE="Times-Italic">Count</FONT></td>')
        text_file.write('<td><FONT FACE="Times-Italic">Name</FONT></td>')
        text_file.write('<td><FONT FACE="Times-Italic">Type</FONT></td>')
        text_file.write('</tr>\n')
    
        linkText = ""
    
        for row in df.itertuples():
            text_file.write('<tr>')
            text_file.write('<td>' + str(int(row.count)) + '</td>')
            text_file.write('<td ALIGN="LEFT">' + row.predicate + '</td>')
            text_file.write('<td port="' + makeLinkPort(row.predicate) + '">' + row.object + '</td>')
            text_file.write('</tr>\n')
            
            if row.object in str(subjectTypes):
                linkText += makeLinkPort(subjectType) + ':' 
                linkText += makeLinkPort(row.predicate) + ' -> '
                linkText += makeLinkPort(row.object) + ":" + makeLinkPort(row.object) + '\n'
            
        text_file.write('</TABLE>>];\n\n')
    
        text_file.write(linkText)
        text_file.write('\n\n')
    
        # write out links to other things
        
    text_file.write('}\n')
    text_file.close()
    
    # render png from dot file
    os.system("dot -Tpng -o " + imgFile + " " + dotFile)
