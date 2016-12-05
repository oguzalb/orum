from collections import defaultdict
from itertools import chain
from pprint import pformat
from collections import namedtuple

class Node(object):
    def __init__(self, labels=None, rels=None, props=None):
        if rels is None:
            rels = defaultdict(list)
        if props is None:
            props = {}
        if labels is None:
            labels = []
        self.labels = labels
        self.rels = rels
        self.props = props

    def matches(self, qnode):
        matches = defaultdict(list)

        if not all((label in self.labels for label in qnode.labels)):
            return {}, False

        if not all(
            (field in self.props and self.props[field] == value
             for (field, value) in qnode.props.iteritems())):
            return {}, False

        for rel_qname, rel_qnodes in qnode.rels.iteritems():
            if rel_qname not in self.rels:
                return {}, False
            for rel_qnode in rel_qnodes:
                for node in self.rels[rel_qname]:
                    sub_matches, is_match = node.matches(rel_qnode)
                    if not is_match:
                        return {}, False
                    for key, lst in sub_matches.iteritems():
                        matches[key].extend(sub_matches[key])
        if qnode.alias:
            matches[qnode.alias].append(self)
        return matches, True

    def __repr__(self):
        return pformat(dict(rels={k:[n.props for n in ns] for k, ns in self.rels.iteritems()}, props=self.props, labels=self.labels))

    def __eq__(self, other):
        return self.props == other.props and self.rels == other.rels

Rels = defaultdict(list)


class Query(list):
    pass


class QNode(Node):
    def __init__(self, alias, *args, **kwargs):
        super(QNode, self).__init__(*args, **kwargs)
        self.alias = alias

    def create(self, graph, matches):
        if self.props:
            node = self.node()
            nodes = [node]
            graph.append(node)
            if self.alias:
                matches[self.alias].append(nodes[0])
        else:
            nodes = matches[self.alias]

        if self.rels:
            for node in nodes:
                qrel_name, qrel_nodes = self.rels.items()[0]
                qrel_node = qrel_nodes[0]
                sub_nodes = qrel_node.create(graph, matches)
                node.rels[qrel_name].extend(sub_nodes)
        return nodes
                
    def node(self):
        node = Node(labels=self.labels, props=self.props)
        return node


Create = namedtuple('Create', ('node',))


Match = namedtuple('Match', ('node',))


class Field(object):
    def __init__(self, alias, field_name):
        self.alias = alias
        self.field_name = field_name


class Set(object):
    def __init__(self, leftvalue, constant):
        if not isinstance(leftvalue, Field):
            raise ValueError("leftvalue should be a field")
        self.leftvalue = leftvalue
        self.constant = constant


class Return(list):
    pass


class Graph(list):
    def query(self, query):
        match_queries = []
        create_queries = []
        set_queries = []
        return_tok = []

        it = iter(query)
        token = next(it, None)
        while token is not None and isinstance(token, Match):
            match_queries.append(token)
            token = next(it, None)

        while token is not None and isinstance(token, Create):
            create_queries.append(token)
            token = next(it, None)

        while token is not None and isinstance(token, Set):
            set_queries.append(token)
            token = next(it, None)

        if token is not None and isinstance(token, Return):
            return_tok = token
            token = next(it, None)

        if token is not None:
            raise ValueError("%s not expected!" % token)

        matches = defaultdict(list)
        for match_query in match_queries:
            for node in self:
                qnode = match_query.node
                submatches, is_match = node.matches(qnode)
                if is_match:
                    for key, lst in submatches.iteritems():
                        matches[key].extend(submatches[key])
            print("matches: " + pformat(dict(matches)))
        for create_query in create_queries:
            qnode = create_query.node
            qnode.create(self, matches)
        for set_query in set_queries:
            leftvalue = set_query.leftvalue
            constant = set_query.constant
            # leftvalue can only be a field currently
            for node in matches.get(leftvalue.alias, []):
                node.props[leftvalue.field_name] = constant
        return list(chain(*[matches[alias] for alias in return_tok]))

    def __repr__(self):
        return pformat(list(self))

