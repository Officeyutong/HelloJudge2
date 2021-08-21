import flask_sqlalchemy
from common.exceptions import APIException


class ModelAPI:
    def __init__(self, db: flask_sqlalchemy.SQLAlchemy) -> None:
        self.db = db

    def ensure_problem_id(self, problem_id: int):
        from models import Problem
        problem = self.db.session.query(Problem.id).filter_by(
            id=problem_id).one_or_none()
        if not problem:
            raise APIException("Problem not found!", -1)
