from jwt import PyJWTError
from api import db
from api.auth import decode_jwt
from api.constants import INVALID_TOKEN, NOT_AUTHENTICATED, SIGNATURE_EXP
from api.db_models import User


def get_user_context(request):
    context = {
        'error': NOT_AUTHENTICATED,
        'request': request,
        'user': None
    }
    if 'Authorization' in request.headers:
        auth = request.headers['Authorization']
        scheme, token = auth.split() if len(auth.split()) > 1 else ['', auth]
        if scheme.lower() != 'bearer':
            return context
        try:
            user_id: str = decode_jwt(token)
            if user_id is None:
                return context
            if user_id == INVALID_TOKEN or user_id == SIGNATURE_EXP:
                context['error'] = user_id
                return context
        except PyJWTError:
            return context
        user = db.session.query(User).filter(User.id == user_id).one_or_none()
        if user is not None:
            context['error'] = None
            context['user'] = user
    return context
