import traceback

try:
    from app.books.models import Book  # noqa: F401
except ImportError:
    traceback.print_exc()
