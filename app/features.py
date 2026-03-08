import sqlite3
import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
)

from app.db import get_db


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("index.index"))

        return view(**kwargs)

    return wrapped_view


bp = Blueprint("features", __name__, url_prefix="/features")


@login_required
@bp.route("/new", methods=("GET", "POST"))
def create_feature():
    db = get_db()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        raw_category_id = request.form.get("category_id", "").strip()

        try:
            category_id = int(raw_category_id)
        except ValueError, TypeError:
            category_id = None

        if not name:
            flash("Name is required")
        elif not category_id:
            flash("Category must be selected")
        else:
            try:
                db.execute(
                    "INSERT INTO features (name, description, category_id) VALUES (?, ?, ?)",
                    (name, description, category_id),
                )
                db.commit()

                flash("Feature created!")
                return redirect(url_for("features.features"))

            except sqlite3.IntegrityError as e:
                current_app.logger.error(f"Integrity error: {e}")
                flash("Selected category is invalid.")

            except sqlite3.Error as e:
                current_app.logger.error(f"Database error: {e}")
                flash("An internal database error occured.")

    categories = db.execute("SELECT id, name FROM categories ORDER BY name").fetchall()

    return render_template("features/create.html", categories=categories)
