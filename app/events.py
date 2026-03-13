import json
import re
import hashlib
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


bp = Blueprint("events", __name__, url_prefix="/events")


@bp.route("/", methods=("GET",))
def list():
    db = get_db()

    events = db.execute(
        """
        SELECT e.id, e.name, e.slug, e.description
        FROM events e
        ORDER BY e.created_at ASC
        """
    ).fetchall()

    return render_template("events/list.html", events=events)


@bp.route("/<slug>", methods=["GET"])
def view(slug):
    db = get_db()

    event = db.execute(
        """SELECT
    e.id,
    e.name,
    e.slug,
    e.description,
    e.user_id,
    e.created_at,
    json_group_array(
        json_object(
            'id', f.id,
            'name', f.name,
            'description', f.description,
            'notes', ef.description,
            'category', json_object(
                'id', c.id,
                'name', c.name
            )
        )
    ) FILTER (WHERE f.id IS NOT NULL) AS features_json
FROM events e
LEFT JOIN event_features ef ON e.id = ef.event_id
LEFT JOIN features f ON ef.feature_id = f.id
LEFT JOIN categories c ON f.category_id = c.id
WHERE e.slug = ?
GROUP BY e.id;
""",
        (slug,),
    ).fetchone()

    if event is None:
        abort(404, "Event not found.")

    # Parse the database row into a standard dictionary
    event_dict = dict(event)
    event_dict["features"] = json.loads(event_dict["features_json"])

    return render_template("events/view.html", event=event_dict)


@bp.route("/edit/<string:slug>", methods=("GET", "POST"))
def edit(slug):
    db = get_db()

    event = db.execute(
        """SELECT
    e.id,
    e.name,
    e.slug,
    e.description,
    e.user_id,
    e.created_at,
    json_group_array(
        json_object(
            'id', f.id,
            'name', f.name,
            'description', f.description,
            'notes', ef.description,
            'category', json_object(
                'id', c.id,
                'name', c.name
            )
        )
    ) FILTER (WHERE f.id IS NOT NULL) AS features_json
FROM events e
LEFT JOIN event_features ef ON e.id = ef.event_id
LEFT JOIN features f ON ef.feature_id = f.id
LEFT JOIN categories c ON f.category_id = c.id
WHERE e.slug = ?
GROUP BY e.id;
""",
        (slug,),
    ).fetchone()

    if event is None:
        abort(404, f"Feature id {id} not found.")

    event_dict = dict(event)
    event_dict["features"] = json.loads(event_dict["features_json"])
    print(event_dict["features"])

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        selected_features = request.form.getlist("feature_ids")

        if not name:
            flash("Name is required")
        else:
            try:
                db.execute(
                    "UPDATE events SET name = ?, description = ? WHERE id = ?",
                    (name, description, event_dict["id"]),
                )

                db.execute(
                    "DELETE FROM event_features WHERE event_id = ?", (event_dict["id"],)
                )

                for feature_id in selected_features:
                    input_name = f"feature_note_{feature_id}"
                    note_text = request.form.get(input_name, "").strip()

                    db.execute(
                        "INSERT INTO event_features (event_id, feature_id, description) VALUES (?, ?, ?)",
                        (event_dict["id"], feature_id, note_text),
                    )

                db.commit()

                flash("Event updated successfully!")

                return redirect(url_for("events.view", slug=slug))

            except sqlite3.Error as e:
                db.rollback()
                current_app.logger.error(f"Database error: {e}")
                flash("An internal database error occurred.")

    all_features = db.execute("SELECT * FROM features").fetchall()

    event_features_map = {f["id"]: f["notes"] for f in event_dict["features"]}

    return render_template(
        "events/edit.html",
        event=event_dict,
        all_features=all_features,
        event_features_map=event_features_map,
    )


def generate_slug(name: str) -> str:
    hash_suffix = hashlib.md5(name.encode("utf-8")).hexdigest()[:8]

    slug = name.lower()
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug[:50].strip("-")

    if slug:
        return f"{slug}-{hash_suffix}"

    return hash_suffix


@login_required
@bp.route("/new", methods=("GET", "POST"))
def create():
    db = get_db()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        slug = generate_slug(name)

        if not name:
            flash("Name is required")
        else:
            try:
                cursor = db.execute(
                    "INSERT INTO events (name, slug, description) VALUES (?, ?, ?)",
                    (name, slug, description),
                )
                new_event_id = cursor.lastrowid

                selected_features = request.form.getlist("feature_ids")

                for feature_id in selected_features:
                    input_name = f"feature_note_{feature_id}"
                    note_text = request.form.get(input_name, "")

                    db.execute(
                        "INSERT INTO event_features (event_id, feature_id, description) VALUES (?, ?, ?)",
                        (new_event_id, feature_id, note_text),
                    )

                db.commit()

            except sqlite3.Error as e:
                current_app.logger.error(f"Database error: {e}")
                flash("An internal database error occurred.")

    features = db.execute(
        "SELECT f.id, f.name, f.description, c.name FROM features f JOIN categories c ON f.category_id = c.id ORDER BY f.name"
    ).fetchall()

    return render_template("events/create.html", features=features)


@login_required
@bp.route("/<int:id>/delete", methods=("POST",))
def delete(id):
    db = get_db()

    try:
        db.execute("DELETE FROM events WHERE id = ?", (id,))
        db.commit()
        flash("Feature deleted")

    except sqlite3.Error as e:
        current_app.logger.error(f"Database error: {e}")
        flash("An internal database error occurred.")

    return redirect(url_for("events.list"))
