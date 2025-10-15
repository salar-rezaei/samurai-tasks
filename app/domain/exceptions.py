# app/domain/exceptions.py
class DomainError(Exception):
    pass


class TaskNotFoundError(DomainError):
    pass
