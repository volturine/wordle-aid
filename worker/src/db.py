"""D1 helpers for Python Workers.

D1 bindings are JavaScript objects accessed through Pyodide's FFI.
These helpers convert results back to plain Python objects.
"""
try:
    from pyodide.ffi import JsProxy
except ImportError:  # local dev / unit tests run outside the Workers runtime
    JsProxy = type(None)


async def d1_all(db, sql: str, *params) -> list[dict]:
    """Run a query and return all rows as a list of dicts."""
    stmt = db.prepare(sql)
    stmt = stmt.bind(*params) if params else stmt
    result = await stmt.all()
    rows = result.results
    return rows.to_py() if isinstance(rows, JsProxy) else list(rows)


async def d1_first(db, sql: str, *params):
    """Run a query and return the first row as a dict, or None."""
    stmt = db.prepare(sql)
    stmt = stmt.bind(*params) if params else stmt
    result = await stmt.first()
    return result.to_py() if isinstance(result, JsProxy) else result


async def d1_run(db, sql: str, *params) -> None:
    """Run a mutation query (INSERT/UPDATE/DELETE)."""
    stmt = db.prepare(sql)
    stmt = stmt.bind(*params) if params else stmt
    await stmt.run()
