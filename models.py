from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Genre(db.Model):
    __tablename__ = "genres"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    books = db.relationship("Book", back_populates="genre_rel", lazy="dynamic")

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    author = db.Column(db.String(200), default="")
    description = db.Column(db.Text, default="")
    file_path = db.Column(db.String(600), unique=True, nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # cbz, pdf, docx, epub
    cover_path = db.Column(db.String(600), default="")
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"), nullable=True)
    genre_rel = db.relationship("Genre", back_populates="books")
    page_count = db.Column(db.Integer, default=0)
    file_size = db.Column(db.Integer, default=0)  # bytes
    date_added = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_read = db.Column(db.DateTime, nullable=True)
    read_progress = db.Column(db.Integer, default=0)  # current page/position

    def to_dict(self):
        from flask import url_for

        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "description": self.description,
            "file_type": self.file_type,
            "genre": self.genre_rel.name if self.genre_rel else "",
            "genre_id": self.genre_id,
            "cover_url": (
                url_for("library.get_cover", book_id=self.id)
                if self.cover_path
                else url_for("static", filename=f"img/cover_{self.file_type}.svg")
            ),
            "page_count": self.page_count,
            "file_size": self.file_size,
            "date_added": self.date_added.isoformat() if self.date_added else "",
            "last_read": self.last_read.isoformat() if self.last_read else None,
            "read_progress": self.read_progress,
        }
