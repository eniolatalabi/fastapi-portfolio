"""Shared rate limiter instance.

Lives in its own module so both the app (which registers the handler)
and the auth router (which decorates /login) can import it without a
circular import through main.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
