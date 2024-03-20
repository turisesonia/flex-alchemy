class Scope:
    def boot(self, *args, **kwargs):
        raise NotImplementedError

    def apply(self, *args, **kwargs):
        raise NotImplementedError
