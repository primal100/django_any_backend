from django.db.utils import DataError, OperationalError, IntegrityError, InternalError, ProgrammingError, \
    NotSupportedError, DatabaseError, InterfaceError, Error

class Database(object):

    class DataError(DataError):
        pass

    class OperationalError(OperationalError):
        pass

    class IntegrityError(IntegrityError):
        pass

    class InternalError(InternalError):
        pass

    class ProgrammingError(ProgrammingError):
        pass

    class NotSupportedError(NotSupportedError):
        pass

    class DatabaseError(DatabaseError):
        pass

    class InterfaceError(InterfaceError):
        pass

    class Error(Error):
        pass





