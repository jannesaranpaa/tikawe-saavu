import sqlite3
import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
    abort,
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


@bp.route("/", methods=("GET",))
def list():
    db = get_db()

    features = db.execute(
        """
        SELECT f.id, f.name, f.description, c.name as category_name 
        FROM features f
        LEFT JOIN categories c ON f.category_id = c.id
        ORDER BY c.name ASC, f.name ASC
        """
    ).fetchall()

    return render_template("features/list.html", features=features)


@login_required
@bp.route("/<int:id>", methods=("GET", "POST"))
def edit(id):
    db = get_db()

    feature = db.execute("SELECT * FROM features WHERE id = ?", (id,)).fetchone()

    if feature is None:
        abort(404, f"Feature id {id} not found.")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        raw_category_id = request.form.get("category_id", "").strip()

        try:
            category_id = int(raw_category_id) if raw_category_id else None
        except ValueError:
            category_id = None

        if not name:
            flash("Name is required")
        elif not category_id:
            flash("A category must be selected")
        else:
            try:
                db.execute(
                    "UPDATE features SET name = ?, description = ?, category_id = ? WHERE id = ?",
                    (name, description, category_id, id),
                )
                db.commit()

                flash("Feature updated successfully!")
                return redirect(url_for("features.list"))

            except sqlite3.IntegrityError:
                flash("Selected category is invalid.")
            except sqlite3.Error as e:
                current_app.logger.error(f"Database error: {e}")
                flash("An internal database error occurred.")

    categories = db.execute("SELECT id, name FROM categories ORDER BY name").fetchall()

    return render_template("features/edit.html", feature=feature, categories=categories)


@login_required
@bp.route("/new", methods=("GET", "POST"))
def create():
    db = get_db()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        raw_category_id = request.form.get("category_id", "").strip()

        try:
            category_id = int(raw_category_id) if raw_category_id else None
        except ValueError:
            category_id = None

        if not name:
            flash("Name is required")
        elif not category_id:
            flash("A category must be selected")
        else:
            try:
                db.execute(
                    "INSERT INTO features (name, description, category_id) VALUES (?, ?, ?)",
                    (name, description, category_id),
                )
                db.commit()

                flash("Feature created!")
                return redirect(url_for("features.list"))

            except sqlite3.IntegrityError:
                flash("Selected category is invalid.")
            except sqlite3.Error as e:
                current_app.logger.error(f"Database error: {e}")
                flash("An internal database error occurred.")

    categories = db.execute("SELECT id, name FROM categories ORDER BY name").fetchall()

    return render_template("features/create.html", categories=categories)


@login_required
@bp.route("/<int:id>/delete", methods=("POST",))
def delete(id):
    db = get_db()

    try:
        db.execute("DELETE FROM features WHERE id = ?", (id,))
        db.commit()
        flash("Feature deleted")

    except sqlite3.Error as e:
        current_app.logger.error(f"Database error: {e}")
        flash("An internal database error occurred.")

    return redirect(url_for("features.list"))
