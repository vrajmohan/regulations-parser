from json import JSONDecoder, JSONEncoder

class Node:
    APPENDIX = u'appendix'
    INTERP = u'interp'
    REGTEXT = u'regtext'

    INTERP_MARK = 'Interp'

    def __init__(self, text='', children=[], label=[], title=None, 
            node_type=REGTEXT):
        self.text = unicode(text)
        self.children = list(children)  #   defensive copy
        self.label = [str(l) for l in label if l != '']
        title = unicode(title or '')
        self.title = title or None
        self.node_type = node_type

    def __repr__(self):
        return (("Node( text = %s, children = %s, label = %s, title = %s, "
            + "node_type = %s)") % (repr(self.text), repr(self.children), 
                repr(self.label), repr(self.title), repr(self.node_type)))

    def __cmp__(self, other):
        return cmp(repr(self), repr(other))

    def label_id(self):
        return '-'.join(self.label)


class NodeEncoder(JSONEncoder):
    """Custom JSON encoder to handle Node objects"""
    def default(self, obj):
        if isinstance(obj, Node):
            fields = dict(obj.__dict__)
            if obj.title is None:
                del fields['title']
            return fields
        return JSONEncoder.default(self, obj)


def node_decode_hook(d):
    """Convert a JSON object into a Node"""
    if set(('text', 'children', 'label', 'node_type')) - set(d.keys()) == set():
        return Node(d['text'], d['children'], d['label'],
            d.get('title', None), d['node_type'])
    else:
        return d


def walk(node, fn):
    """Perform fn for every node in the tree. Pre-order traversal. fn must
    be a function that accepts a root node."""
    result = fn(node)
    if result != None:
        results = [result]
    else:
        results = []
    for child in node.children:
        results += walk(child, fn)
    return results


def find(root, label):
    """Search through the tree to find the node with this label."""
    def check(node):
        if node.label_id() == label:
            return node
    response = walk(root, check)
    if response:
        return response[0]


def join_text(node):
    """Join the text of this node and all children"""
    bits = []
    walk(node, lambda n: bits.append(n.text))
    return ''.join(bits)


def treeify(nodes):
    """Given a list of nodes, convert those nodes into the appropriate tree
    structure based on their labels. This assumes that all nodes will fall
    under a set of 'root' nodes, which have the min-length label."""
    if not nodes:
        return nodes
    
    min_len, with_min = len(nodes[0].label), []

    for node in nodes:
        if len(node.label) == min_len:
            with_min.append(node)
        elif len(node.label) < min_len:
            min_len = len(node.label)
            with_min = [node]

    roots = []
    for root in with_min:
        if root.label[-1] == Node.INTERP_MARK:
            is_child = lambda n: n.label[:len(root.label)-1] == root.label[:-1]
        else:
            is_child = lambda n: n.label[:len(root.label)] == root.label
        children = [n for n in nodes if n != root and is_child(n)]
        root.children = root.children + treeify(children)
        roots.append(root)
    return roots