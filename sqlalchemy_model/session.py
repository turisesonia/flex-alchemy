class SessionHandler:
    _db = None

    @classmethod
    def set_session(cls, session):
        cls._db = session
