class ControllerError(Exception):
    pass


class NotFoundError(ControllerError):
    pass


class ConflictError(ControllerError):
    pass
