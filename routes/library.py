import os
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    send_file,
    abort,
    current_app,
)
from models import db, Book, Genre
from utils.file_handler import cbz_get_page, docx_to_html
from datetime import datetime, timezone

library_bp = Blueprint("library", __name__)


# ---------------------------------------------------------------------------
# Library page
# ---------------------------------------------------------------------------

@library_bp.route("/")
def index():
    genres = Genre.query.order_by(Genre.name).all()
    file_types = ["cbz", "pdf", "docx", "epub"]
    return render_template("library.html", genres=genres, file_types=file_types)


# ---------------------------------------------------------------------------
# API: list books (JSON)
# ---------------------------------------------------------------------------

@library_bp.route("/api/books")
def api_books():
    q = Book.query

    search = request.args.get("search", "").strip()
    if search:
        pattern = f"%{search}%"
        q = q.filter(
            db.or_(Book.title.ilike(pattern), Book.author.ilike(pattern))
        )

    file_type = request.args.get("file_type", "").strip().lower()
    if file_type and file_type != "all":
        q = q.filter(Book.file_type == file_type)

    genre_id = request.args.get("genre_id", "").strip()
    if genre_id and genre_id != "0":
        try:
            q = q.filter(Book.genre_id == int(genre_id))
        except ValueError:
            pass

    sort = request.args.get("sort", "date_desc")
    if sort == "title_asc":
        q = q.order_by(Book.title.asc())
    elif sort == "title_desc":
        q = q.order_by(Book.title.desc())
    elif sort == "author_asc":
        q = q.order_by(Book.author.asc())
    elif sort == "date_asc":
        q = q.order_by(Book.date_added.asc())
    else:  # date_desc default
        q = q.order_by(Book.date_added.desc())

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 24, type=int)
    paginated = q.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(
        {
            "books": [b.to_dict() for b in paginated.items],
            "total": paginated.total,
            "pages": paginated.pages,
            "current_page": paginated.page,
        }
    )


# ---------------------------------------------------------------------------
# API: genres
# ---------------------------------------------------------------------------

@library_bp.route("/api/genres")
def api_genres():
    genres = Genre.query.order_by(Genre.name).all()
    return jsonify([g.to_dict() for g in genres])


# ---------------------------------------------------------------------------
# API: book detail
# ---------------------------------------------------------------------------

@library_bp.route("/api/books/<int:book_id>")
def api_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())


# ---------------------------------------------------------------------------
# API: update progress
# ---------------------------------------------------------------------------

@library_bp.route("/api/books/<int:book_id>/progress", methods=["POST"])
def api_progress(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json(force=True)
    if "progress" in data:
        book.read_progress = int(data["progress"])
    book.last_read = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# API: delete book
# ---------------------------------------------------------------------------

@library_bp.route("/api/books/<int:book_id>", methods=["DELETE"])
def api_delete(book_id):
    book = Book.query.get_or_404(book_id)
    # Remove physical files
    try:
        if book.file_path and os.path.exists(book.file_path):
            os.remove(book.file_path)
    except OSError:
        pass
    try:
        if book.cover_path and os.path.exists(book.cover_path):
            os.remove(book.cover_path)
    except OSError:
        pass
    db.session.delete(book)
    db.session.commit()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Cover serving
# ---------------------------------------------------------------------------

@library_bp.route("/covers/<int:book_id>")
def get_cover(book_id):
    book = Book.query.get_or_404(book_id)
    if book.cover_path and os.path.exists(book.cover_path):
        return send_file(book.cover_path, mimetype="image/jpeg")
    # Return default SVG
    svg_name = f"img/cover_{book.file_type}.svg"
    svg_path = os.path.join(current_app.static_folder, svg_name)
    if os.path.exists(svg_path):
        return send_file(svg_path, mimetype="image/svg+xml")
    abort(404)


# ---------------------------------------------------------------------------
# Reader page
# ---------------------------------------------------------------------------

@library_bp.route("/read/<int:book_id>")
def read(book_id):
    book = Book.query.get_or_404(book_id)
    book.last_read = datetime.now(timezone.utc)
    db.session.commit()

    extra = {}
    if book.file_type == "docx":
        try:
            extra["html_content"] = docx_to_html(book.file_path)
        except Exception:
            extra["html_content"] = "<p>Không thể đọc file DOCX này.</p>"

    return render_template("reader.html", book=book, **extra)


# ---------------------------------------------------------------------------
# CBZ page endpoint
# ---------------------------------------------------------------------------

@library_bp.route("/cbz/<int:book_id>/page/<int:page>")
def cbz_page(book_id, page):
    book = Book.query.get_or_404(book_id)
    if book.file_type != "cbz":
        abort(400)
    data, mime = cbz_get_page(book.file_path, page)
    if data is None:
        abort(404)
    from flask import Response
    return Response(data, mimetype=mime)


# ---------------------------------------------------------------------------
# PDF file serving
# ---------------------------------------------------------------------------

@library_bp.route("/files/<int:book_id>")
def serve_file(book_id):
    book = Book.query.get_or_404(book_id)
    if book.file_type not in ("pdf", "epub"):
        abort(400)
    if not os.path.exists(book.file_path):
        abort(404)
    mime = "application/pdf" if book.file_type == "pdf" else "application/epub+zip"
    return send_file(book.file_path, mimetype=mime)
