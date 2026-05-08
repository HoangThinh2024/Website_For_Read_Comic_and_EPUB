import os
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    jsonify,
)
from werkzeug.utils import secure_filename
from models import db, Book, Genre
from utils.file_handler import (
    allowed_file,
    get_file_type,
    extract_metadata,
    extract_cover,
)

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["GET"])
def upload_page():
    genres = Genre.query.order_by(Genre.name).all()
    return render_template("upload.html", genres=genres)


@upload_bp.route("/upload", methods=["POST"])
def do_upload():
    files = request.files.getlist("files")
    genre_id = request.form.get("genre_id") or None
    custom_genre = request.form.get("custom_genre", "").strip()

    if not files or all(f.filename == "" for f in files):
        flash("Vui lòng chọn ít nhất một file.", "danger")
        return redirect(url_for("upload.upload_page"))

    # Handle custom genre
    if custom_genre:
        genre = Genre.query.filter_by(name=custom_genre).first()
        if not genre:
            genre = Genre(name=custom_genre)
            db.session.add(genre)
            db.session.flush()
        genre_id = genre.id
    elif genre_id:
        genre_id = int(genre_id)
    else:
        genre_id = None

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    cover_dir = current_app.config["COVER_FOLDER"]
    results = []

    for f in files:
        if f.filename == "":
            continue
        if not allowed_file(f.filename):
            results.append({"name": f.filename, "ok": False, "msg": "Định dạng không được hỗ trợ."})
            continue

        file_type = get_file_type(f.filename)
        filename = secure_filename(f.filename)

        # Ensure unique filename
        dest = os.path.join(upload_folder, filename)
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(dest):
            filename = f"{base}_{counter}{ext}"
            dest = os.path.join(upload_folder, filename)
            counter += 1

        f.save(dest)
        file_size = os.path.getsize(dest)

        # Extract metadata
        meta = extract_metadata(dest, file_type)
        title = meta.get("title") or os.path.splitext(f.filename)[0]
        author = meta.get("author", "")
        description = meta.get("description", "")
        page_count = meta.get("page_count", 0)

        # Override with form data if provided
        if request.form.get("title"):
            title = request.form.get("title")
        if request.form.get("author"):
            author = request.form.get("author")

        book = Book(
            title=title,
            author=author,
            description=description,
            file_path=dest,
            file_type=file_type,
            genre_id=genre_id,
            page_count=page_count,
            file_size=file_size,
        )
        db.session.add(book)
        db.session.flush()  # get book.id

        # Extract cover
        cover_path = extract_cover(dest, file_type, cover_dir, book.id)
        book.cover_path = cover_path
        db.session.commit()

        results.append({"name": f.filename, "ok": True, "msg": "Tải lên thành công."})

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(results)

    successes = sum(1 for r in results if r["ok"])
    flash(f"Đã tải lên thành công {successes}/{len(results)} file.", "success" if successes else "danger")
    return redirect(url_for("library.index"))


# ---------------------------------------------------------------------------
# Edit book metadata
# ---------------------------------------------------------------------------

@upload_bp.route("/books/<int:book_id>/edit", methods=["GET"])
def edit_page(book_id):
    book = Book.query.get_or_404(book_id)
    genres = Genre.query.order_by(Genre.name).all()
    return render_template("edit.html", book=book, genres=genres)


@upload_bp.route("/books/<int:book_id>/edit", methods=["POST"])
def do_edit(book_id):
    book = Book.query.get_or_404(book_id)
    book.title = request.form.get("title", book.title)
    book.author = request.form.get("author", book.author)
    book.description = request.form.get("description", book.description)

    genre_id = request.form.get("genre_id") or None
    custom_genre = request.form.get("custom_genre", "").strip()
    if custom_genre:
        genre = Genre.query.filter_by(name=custom_genre).first()
        if not genre:
            genre = Genre(name=custom_genre)
            db.session.add(genre)
            db.session.flush()
        book.genre_id = genre.id
    elif genre_id:
        book.genre_id = int(genre_id)
    else:
        book.genre_id = None

    db.session.commit()
    flash("Cập nhật thành công.", "success")
    return redirect(url_for("library.index"))
