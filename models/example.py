import pandas as pd

from decorator import register, ref
from connections import Connection

@register
@ref("example_upstream_node")
def example_base():
    df = pd.DataFrame({"a": [1,2,3]})
    df.to_sql("example_base", Connection.dev, if_exists="replace")
    return
