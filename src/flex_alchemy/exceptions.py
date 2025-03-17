class SessionNotProvidedError(ValueError):
    def __init__(self):
        super().__init__("Session is not provided or invalid")
