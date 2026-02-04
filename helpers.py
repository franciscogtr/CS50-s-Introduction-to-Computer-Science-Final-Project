from flask import redirect, session
from functools import wraps


# GET TO FINANCE EXERCISE

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/enter")
        return f(*args, **kwargs)

    return decorated_function