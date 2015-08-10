Neo_Wordnet
-----------

This software matches [WordNet](http://wordnet-rdf.princeton.edu/) and [ConceptNet 5.3](http://conceptnet5.media.mit.edu/downloads/current/) and loads them into neo4j 2.2.2. 
This is a sister project of [Neo_Concept](https://github.com/redsk/neo_concept) and [Neo_Wordnet](https://github.com/redsk/neo_wordnet).

Pre-Requisites
--------------

- neo4j version 2.2.2 (needed for the [new import tool](http://neo4j.com/docs/2.2.2/import-tool.html))
- [Neo_Concept](https://github.com/redsk/neo_concept)
- [Neo_Wordnet](https://github.com/redsk/neo_wordnet)
- regular Python, no dependencies

Tested with neo4j-community-2.2.2.

How-To 
-------------------

    mkdir neo-kbs
    cd neo-kbs
    git clone https://github.com/redsk/neo_merger.git

    # Follow [Neo_Concept](https://github.com/redsk/neo_concept) how-to but do not import the two CSV files
    # Follow [Neo_Wordnet](https://github.com/redsk/neo_wordnet) how-to but do not import the two CSV files

    mkdir merged-kbs
    python neo_merger/neo_merger.py wordnet/WNnodes.csv wordnet/WNedges.csv conceptnet/nodes.csv conceptnet/edgesPOS.csv merged-kbs/nodes.csv merged-kbs/edges.csv

    # import the merged nodes.csv and edges.csv using the new import tool
    neo4j-community-2.2.2/bin/neo4j-import --into neo4j-community-2.2.2/data/graph.db --nodes merged-kbs/nodes.csv --relationships merged-kbs/edges.csv --delimiter "TAB"

    # start neo4j
    neo4j-community-2.2.2/bin/neo4j start


Go to localhost:7474 to see the graph. Create indexes on labels for performance reasons:

    CREATE INDEX ON :`lemon#LexicalEntry`(id)
    CREATE INDEX ON :`lemon#LexicalSense`(id)
    CREATE INDEX ON :`wdo#Synset`(id)
    CREATE INDEX ON :Concept(id)

You can now query the database. Example:

    MATCH (c0:`lemon#LexicalEntry` { id:"wn/bus+driver-n"}),(c1:`lemon#LexicalEntry` { id:"wn/drive-v"}),path=allShortestPaths((c0)-[*..10]-(c1))
    RETURN c0,c1,path
