# OPENCORE - ADD
"""

Helper function that returns a session object

# A session_factory() instance establishes all conversations with the shared.database
# and represents a "staging zone" for all the objects loaded into the
# shared.database session object. Any change made against the objects in the
# session won't be persisted into the shared.database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()

"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from shared.database.core import Base
import os
from contextlib import contextmanager
import time
from shared.settings import settings
from sqlalchemy import event as sqlalchemy_event


if settings.DIFFGRAM_SYSTEM_MODE == "production":
    engine = create_engine(settings.DATABASE_URL,
                           pool_size=10, max_overflow=2, echo=False)

if settings.DIFFGRAM_SYSTEM_MODE in ["sandbox", "staging", "testing", "testing_e2e"]:
    engine = create_engine(settings.DATABASE_URL, pool_size=10, max_overflow=2)

# see http://docs.sqlalchemy.org/en/latest/core/pooling.html
# Each worker will use up to pool size + max_overflow it would appear


Base.metadata.bind = engine
session_factory = sessionmaker(bind=engine)
scoped_session_registry = scoped_session(session_factory)


def check_for_listener_and_attach(session, callback):
    if not sqlalchemy_event.contains(session, 'after_commit', callback):
        sqlalchemy_event.listen(session, 'after_commit', callback)

    return session


class AfterCommitAction:
    """
        Singleton Pattern For AfterCommitAction.
        The idea of doing this is to keep a single object at all time for the
        AfterCommitActions, that way we can save multiple function calls with arguments
        for each session commit().
    """
    instance = None

    class __AfterCommitAction:

        def after_commit(self, session):
            for i in range(0, len(self.callback_args_map[session])):
                self.callbacks_map[session][i](**self.callback_args_map[session][i])

            self.callbacks_map[session] = {}
            self.callback_args_map[session] = {}

        def __init__(self,
                     session,
                     callback,
                     callback_args):
            """

            :param session: a sql alchemy session object
            :param operation: one of insert, update, delete
            """
            self.callbacks_map = {}
            self.callback_args_map = {}

            self.callbacks_map[session] = [callback]
            self.callback_args_map[session] = [callback_args]

            check_for_listener_and_attach(session, self.after_commit)

        def __str__(self):
            return repr(self)

    def __init__(self, session, callback, callback_args):
        if not AfterCommitAction.instance:
            AfterCommitAction.instance = AfterCommitAction.__AfterCommitAction(session, callback, callback_args)
        else:
            check_for_listener_and_attach(session, AfterCommitAction.instance.after_commit)
            if AfterCommitAction.instance.callbacks_map.get(session):
                AfterCommitAction.instance.callbacks_map.get(session).append(callback)
                AfterCommitAction.instance.callback_args_map.get(session).append(callback_args)
            else:
                AfterCommitAction.instance.callbacks_map[session] = [callback]
                AfterCommitAction.instance.callback_args_map[session] = [callback_args]

    def __getattr__(self, name):
        return getattr(self.instance, name)


@contextmanager
def session_scope():
    import shared.database.input as input  # TODO fix circular imports
    """
    Provide a transactional scope around a series of operations.

    example, call:
    with sessionMaker.session_scope() as session:
        # do something  
    
    """
    session = session_factory()
    try:
        yield session

        session.commit()

    except:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def session_scope_threaded():
    import shared.database.input as input  # TODO fix circular imports
    """Provide a transactional scope around a series of operations.
    
    """

    session = scoped_session_registry()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        scoped_session_registry.remove()
