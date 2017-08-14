from connexion import request, ProblemException

from app.config import ADMINS
from app.extensions import db
from app.libs.authorization.simple import Authorization


class AdminOnly(Authorization):
    """Only Admins can delete objects"""

    def delete(self, obj: db.Model, **kwargs) -> None:
        if not hasattr(request, 'user') or not request.user or request.user not in ADMINS:
            raise ProblemException(
                status=401, title='UnAuthorized', detail='Only Admins are allowed to delete this resource!')
