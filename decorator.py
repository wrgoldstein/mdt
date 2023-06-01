from graph import graph

def register(f):    
    "Specifies that a python function creates a table"
    node = graph[f.__name__]
    graph[f.__name__] = {
        **node, "f": f, "type": "python", "name": f.__name__
    }
    return f

def ref(node_label):
    "Specifies a python function relies on a table"
    def decorator_ref(f):
        graph[f.__name__]["deps"].append(node_label)
        return f

    return decorator_ref
