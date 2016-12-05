import unittest
from orum import Graph, Create, QNode, Return, Match, Query, Set, Field, Node


class QueryTests(unittest.TestCase):
    def setUp(self):
        graph = Graph()
        neo4j_query1 = '''
        CREATE (you:Person {name:"Oguz"})
        CREATE (you:Person {name:"Berker"})
        '''
        print "QUERY 1: %s" % neo4j_query1
        query1 = Query([
            Create(QNode(alias="you", labels=["Person"], props=dict(name="Oguz"))),
            Create(QNode(alias="friend", labels=["Person"], props=dict(name="Berker"))),
            Return(["you", "friend"])
        ])
        print "GRAPH 1"
        result = graph.query(query1)
        expected_result = [
            Node(
                labels=["Person"],
                props=dict(name="Oguz")),
            Node(
                labels=["Person"],
                props=dict(name="Berker")
            )
        ]
        self.assertEquals(result, expected_result)
        print "query result: %s" % result
        print graph


        neo4j_query2 = '''
        MATCH (you:Person {name:"Oguz"})
        MATCH (friend:Person {name:"Berker"})
        CREATE (you)-[:KNOWS]->(n:Person {name:"Tuna"}-[:KNOWS]->(friend))
        RETURN you, n, friend
        '''
        print "QUERY 2: %s" % neo4j_query2
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
        result = graph.query(query2)
        expected_result = [
            Node(
                labels=["Person"],
                props=dict(name="Oguz"),
                rels=dict(
                    knows=[
                        Node(
                            labels=[],
                            props=dict(name="Tuna"),
                            rels=dict(
                                knows=[Node(
                                    labels=["Person"],
                                    props=dict(name="Berker"))]
                            )
                        )
                    ])
            ),
            Node(
                labels=[],
                props=dict(name="Tuna"),
                rels=dict(
                    knows=[Node(
                        labels=["Person"],
                        props=dict(name="Berker"))])),
            Node(
                labels=["Person"],
                props=dict(name="Berker")
            )
        ]
        self.assertEquals(result, expected_result)
        print "query result: %s" % result
        print "GRAPH 2"
        print graph
        self.graph = graph

    def test_query_middle_man(self):
        neo4j_query3 = '''
        MATCH (you:Person {name:"Oguz"})-[:KNOWS]->(n)-[:KNOWS]->(friend:Person {name:"Berker"})
        RETURN n
        '''
        print "QUERY 3: %s" % neo4j_query3
        query3 = Query([
            Match(
                QNode(
                    alias="you",
                    labels=["Person"],
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
        result = self.graph.query(query3)
        expected_result = [Node(
            labels=[],
            props=dict(name="Tuna"),
            rels=dict(
                knows=[Node(
                    labels=["Person"],
                    props=dict(name="Berker"))]))]
        self.assertEquals(result, expected_result)
        print "query result: %s" % result
        print "GRAPH 3"
        print self.graph

    def test_query_non_existent_relation(self):
        neo4j_query4 = '''
            MATCH (you:Person {name:"Oguz"})-[:KNOWS]->(n)-[:NONEXISTANTRELATION]->(friend:Person {name:"Berker"})
            RETURN n
            '''
        print "QUERY 4: %s" % neo4j_query4
        query4 = Query([
            Match(
                QNode(
                    alias="you",
                    rels=dict(
                        knows=[QNode(
                            alias="middle",
                            props=dict(name="Tuna"),
                            rels=dict(
                                NONEXISTANTRELATION=[QNode(alias="friend")])
                        )],
                    )
                ),
            ),
            Return(['middle'])
        ])
        result = self.graph.query(query4)
        self.assertEquals(result, [])
        print "query result: %s" % result
        print "GRAPH 4"
        print self.graph

    def test_set(self):
        neo4j_query5 = '''
        MATCH (you:Person {name:"Oguz"})-[:KNOWS]->(n)-[:KNOWS]->(friend:Person {name:"Berker"})
        SET you.expertise = "python dev"
        RETURN n
        '''
        print "QUERY 5: %s" % neo4j_query5
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
        result = self.graph.query(query5)
        expected_result = [Node(
            labels=[],
            props=dict(name="Tuna"),
            rels=dict(
                knows=[Node(
                    labels=["Person"],
                    props=dict(name="Berker"))]))]
        self.assertEquals(result, expected_result)
        print "query result: %s" % result
        print "GRAPH 5"
        print self.graph