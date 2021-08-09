# OPENCORE - ADD
import time
import cProfile
import io
import pstats
import contextlib
import inspect

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Executable, ClauseElement, _literal_as_text


def timeit(method):
    def timed(*args, **kw):

        start = time.time()

        result = method(*args, **kw)

        end = time.time()

        print('%r  %2.2f ms' % \
                  (method.__name__, (end - start) * 1000))
        return result
    return timed


# https://docs.sqlalchemy.org/en/13/faq/performance.html?highlight=explain
@contextlib.contextmanager
def profiled(to_file=None):

    # Trying to get it to print first function in context
    # https://stackoverflow.com/questions/5067604/determine-function-name-from-within-that-function-without-using-traceback
    #print(inspect.stack()[1][3])
    pr = cProfile.Profile()
    pr.enable()
    yield
    pr.disable()
    if to_file is None:
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats('tottime')
        # cumulative
        ps.print_stats(5)
        # uncomment this to see who's calling what
        # ps.print_callers()
        print(s.getvalue())
    else:
        pr.dump_stats(to_file)


# https://github.com/sqlalchemy/sqlalchemy/wiki/Query-Plan-SQL-construct
class explain(Executable, ClauseElement):
    def __init__(self, stmt, analyze=False):
        self.statement = _literal_as_text(stmt)
        self.analyze = analyze


@compiles(explain, "postgresql")
def pg_explain(element, compiler, **kw):
    text = "EXPLAIN "
    if element.analyze:
        text += "ANALYZE "
    text += compiler.process(element.statement, **kw)

    return text
