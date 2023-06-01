import collections

graph = collections.defaultdict(lambda: dict(deps=[], compiled=None, config={}))
