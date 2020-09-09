from django.dispatch import Signal


new_login = Signal(providing_args=["user", "login"])