# mdt

A minimal data tool

## What is this

A directed graph of SQL statements (transformed to CTAS statements) and python functions, run in topological order.

## Example

This repo has an example data flow, where 

1. `example_base` is a table created / managed by a python function
2. `example1.sql` is a table that depends on `example_base`
3. `example2.sql` is a table that depends on `example1.sql`

```

       ┌────────────────┐     ┌─────────────┐     ┌──────────────┐
       │example_base(py)├────►│example1(sql)├────►│example2 (sql)│
       └────────────────┘     └─────────────┘     └──────────────┘

```

mdt will first run the python function, then the first CTAS statement, then the second one.

### Run the example

Assuming you have postgres installed, set up a local postgres instance with a database called `mdt_dev`:

```
createdb mdt_dev
```

Then run the example

```
python engine.py

running example_base...done (0.09 seconds)
running example1...done (0.01 seconds)
running example2...done (0.01 seconds)
```

and check that it worked

```
psql -d mdt_dev
Expanded display is used automatically.
psql (14.7 (Homebrew))
Type "help" for help.

mdt_dev=# \dt
            List of relations
 Schema |     Name     | Type  |  Owner
--------+--------------+-------+----------
 public | example1     | table | postgres
 public | example2     | table | postgres
 public | example_base | table | postgres
(3 rows)

mdt_dev=# select * from example2;
 index | a |  ?column?
-------+---+------------
     0 | 1 | look its a
     1 | 2 | look its a
     2 | 3 | look its a
(3 rows)
```

## Why do this

It's surprisingly hard to just schedule a little bit of sql and python, which is often all you need at a smaller startup to get pretty far with data engineering for BI workloads. I've found that combining a very simple executor with a simple scheduler, for example www.airplane.dev, you can just write SQL and python and not worry about the rest.

### Why not use dbt

dbt [only supports certain python execution environments](https://docs.getdbt.com/docs/build/python-models#specific-data-platforms), which doesn't work if you're not using databricks or snowflake. I also wanted something that would be easy to read, introspect, and change, where it would also be easy to run individual python scripts on demand without alteration.
