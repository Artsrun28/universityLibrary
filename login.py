from functools import wraps
from flask import session, redirect, url_for, request

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('user') is None:
            return redirect(url_for("login", next=request.path))
        return func(*args, **kwargs)
    return wrapper
