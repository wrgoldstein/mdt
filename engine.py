import sys
import pathlib
import jinja2
import time
import graphlib
import importlib.util

from sqlalchemy import text

from connections import Connection
from graph import graph


class Engine:
    current = None
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(""),
        finalize=lambda x: x if x is not None else ''
    )

    def ref(node_label: str, schema="public"):
        graph[Engine.current]["deps"].append(node_label)
        # todo use configured schemas
        return f"{schema}.{node_label}"

    def config(**config: dict):
        graph[Engine.current]["config"] = config

    def render(path: pathlib.Path):
        global graph
        Engine.current = path.stem
        t = Engine.env.from_string(path.read_text())
        graph[path.stem]["compiled"] = t.render().strip()
        graph[path.stem]["type"] = "sql"
        graph[path.stem]["name"] = path.stem

    def add_macro(path: pathlib.Path):
        m = Engine.env.from_string(path.read_text())
        macros = [x for x in dir(m.module) if not x.startswith("_")]
        for macro in macros:
            Engine.env.globals[macro] = getattr(m.module, macro)

    env.globals.update(ref=ref, config=config)

    def collect_items():
        global graph

        for macro in pathlib.Path("macros").glob("**/*.sql"):
            Engine.add_macro(macro)

        for model in pathlib.Path("models").glob("**/*.sql"):
            Engine.render(model)

        for file in pathlib.Path("models").glob("**/*.py"):
            spec = importlib.util.spec_from_file_location(file.stem, file)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[file.stem] = mod
            spec.loader.exec_module(mod)

    
    def get_sorted():
        sortable = { k:v["deps"] for k,v in graph.items() }
        ts = graphlib.TopologicalSorter(sortable)
        
        return list(ts.static_order())
    
    def run(node_label: str):
        # todo separate runners
        # todo handle errors with try/catch
        # todo errors block children but nondependents keep going
        if node_label not in graph:
            print(node_label, "not a registered table")
            return
        
        node = graph[node_label]
        print(f"running {node_label}...", end="", flush=True)

        tt = time.time()

        if node["type"] == "python":
            node["f"]()
            print(f"done ({(time.time() - tt):.2f} seconds)")

        elif node["type"] == "sql":
            sql = node["compiled"]
            mat = node["config"].get("materialized", "table")

            # todo: separate materializations strategy
            # todo: use configured schemas
            stmt = text(f"""
                begin;
                drop {mat} if exists {node_label};
                create {mat} {node_label} as ({sql});
                commit;
                """
            )
            with Connection.dev.connect() as con:
                con.execute(stmt)
            print(f"done ({(time.time() - tt):.2f} seconds)")

        else:
            raise Exception("unidentified node", node_label)
        
    def run_all():
        # todo graph selection syntax
        Engine.collect_items()
        for node_label in Engine.get_sorted():
            Engine.run(node_label)

if __name__ == "__main__":
    Engine.run_all()
