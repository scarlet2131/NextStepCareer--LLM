from flask import Blueprint

bp = Blueprint('api', __name__)

@bp.route('/test', methods=['GET'])
def test():
    return {"message": "API is working"}

from . import routes
