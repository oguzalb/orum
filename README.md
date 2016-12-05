# Örüm Graph Database


This is a pet project to understand how graph database stuff works

Doesn't have a parser, you will need to translate your query into Python objects and run them

This is how queries should be run (You can see the examples in tests also)

You will need to run the first two examples on the same graph before the
 other examples to create the first nodes

## Example 1: Create nodes
```
CREATE (you:Person {name:"Oguz"})
CREATE (you:Person {name:"Berker"})
```

Translates into

```
from orum import Graph, Create, QNode, Return, Match, Query, Set, Field


graph = Graph()
query1 = Query([
    Create(QNode(alias="you", labels=["Person"], props=dict(name="Oguz"))),
    Create(QNode(alias="friend", labels=["Person"], props=dict(name="Berker"))),
    Return(["you", "friend"])
])
print "GRAPH 1"
print "query result: %s" % graph.query(query1)
print graph
```

## Example 2: Match and Create Nodes Related with Matches
```
MATCH (you:Person {name:"Oguz"})
MATCH (friend:Person {name:"Berker"})
CREATE (you)-[:KNOWS]->(n:Person {name:"Tuna"}-[:KNOWS]->(friend))
RETURN you, n, friend
```
Translates into

```
from orum import Graph, Create, QNode, Return, Match, Query, Set, Field


graph = Graph()
query2 = Query([
    Match(
        QNode(alias="you", labels=["Person"], props=dict(name="Oguz"))),
    Match(
        QNode(alias="friend", labels=["Person"], props=dict(name="Berker"))),
    Create(
        QNode(
            alias="you",
            rels=dict(
                knows=[QNode(
                    alias="middle",
                    props=dict(name="Tuna"),
                    rels=dict(
                        knows=[QNode(alias="friend")])
                )],
            )
        ),
    ),
    Return(["you", "middle", "friend"])
])
print "query result: %s" % graph.query(query2)
print "GRAPH 2"
print graph
```

## Example 3: Match node in the middle
```
MATCH (you:Person {name:"Oguz"})-[:KNOWS]->(n)-[:KNOWS]->(friend:Person {name:"Berker"})
RETURN n
```

Translates into

```
from orum import Graph, Create, QNode, Return, Match, Query, Set, Field

graph = Graph()
...
...
query3 = Query([
Match(
    QNode(
        alias="you",
        rels=dict(
            knows=[QNode(
                alias="middle",
                props=dict(name="Tuna"),
                rels=dict(
                    knows=[QNode(alias="friend")])
            )],
        )
    ),
),
Return(['middle'])
])
print "query result: %s" % self.graph.query(query3)
print "GRAPH 3"
print self.graph
```

## Example 4: Match and Set field of a node
```
MATCH (you:Person {name:"Oguz"})-[:KNOWS]->(n)-[:KNOWS]->(friend:Person {name:"Berker"})
SET you.expertise = "python dev"
RETURN n
```

Translates into

```
from orum import Graph, Create, QNode, Return, Match, Query, Set, Field

graph = Graph()
...
...
query5 = Query([
    Match(
        QNode(
            alias="you",
            rels=dict(
                knows=[QNode(
                    alias="middle",
                    props=dict(name="Tuna"),
                    rels=dict(
                        knows=[QNode(alias="friend")])
                )],
            )
        ),
    ),
    Set(
        Field(
            alias='you',
            field_name='expertise'
        ),
        'python dev'
    ),
    Return(['middle'])
])
print "query result: %s" % self.graph.query(query5)
print "GRAPH 5"
print self.graph
```
