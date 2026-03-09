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


bp = Blueprint("categories", __name__, url_prefix="/categories")


@bp.route("/", methods=("GET",))
def list():
    db = get_db()
    categories = db.execute(
        "SELECT id, name, description FROM categories ORDER BY name"
    ).fetchall()

    return render_template("categories/list.html", categories=categories)


@login_required
@bp.route("/<int:id>", methods=("GET", "POST"))
def edit(id):
    db = get_db()

    category = db.execute("SELECT * FROM categories WHERE id = ?", (id,)).fetchone()

    if category is None:
        abort(404, f"Category id {id} not found.")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Name is required")
        else:
            try:
                db.execute(
                    "UPDATE categories SET name = ?, description = ? WHERE id = ?",
                    (name, description, id),
                )
                db.commit()

                flash("Category updated succesfully!")
                return redirect(url_for("categories.list"))

            except sqlite3.Error as e:
                current_app.logger.error(f"Database error: {e}")
                flash("An internal database error occured.")

    return render_template("categories/edit.html", category=category)


@login_required
@bp.route("/new", methods=("GET", "POST"))
def categories():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        db = get_db()

        if not name:
            flash("Name is required")
        else:
            try:
                db.execute(
                    "INSERT INTO categories (name, description) VALUES (?, ?)",
                    (name, description),
                )
                db.commit()

                flash("Category created!")
                return redirect(url_for("categories.list"))

            except sqlite3.Error as e:
                current_app.logger.error(f"Database error: {e}")
                flash("An internal database error occured.")

    return render_template("categories/create.html")


@login_required
@bp.route("/<int:id>/delete", methods=("POST",))
def delete(id):
    db = get_db()

    try:
        db.execute("DELETE FROM categories WHERE id = ?", (id,))
        db.commit()
        flash("Category deleted")

    except sqlite3.Error as e:
        current_app.logger.error(f"Database error: {e}")
        flash("An internal database error occured.")

    return redirect(url_for("categories.list"))
