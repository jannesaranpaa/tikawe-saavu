import secrets
import sqlite3

from flask import Flask
from flask import abort, flash, redirect, render_template, request, session

import config
import users
import categories
import features
import events

app = Flask(__name__)
app.secret_key = config.secret_key


def require_login():
    if "user_id" not in session:
        abort(403)


def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username:
            flash("Username is required")
            return redirect("/register")
        if not password:
            flash("Password is required")
            return redirect("/register")

        try:
            users.create_user(username, password)
        except sqlite3.IntegrityError:
            flash(f"User {username} is already taken")
            return redirect("/register")

        return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        else:
            flash("Incorrect username or password.")
            return redirect("/login")


@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
        del session["csrf_token"]
    return redirect("/")


@app.route("/categories")
def list_categories():
    all_categories = categories.get_categories()
    return render_template("categories/list.html", categories=all_categories)


@app.route("/new_category", methods=["GET", "POST"])
def new_category():
    require_login()

    if request.method == "GET":
        return render_template("categories/create.html")

    if request.method == "POST":
        check_csrf()
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Name is required")
            return redirect("/new_category")

        categories.add_category(name, description)
        flash("Category created!")
        return redirect("/categories")


@app.route("/category/<int:category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    require_login()

    category = categories.get_category(category_id)
    if not category:
        abort(404)

    if request.method == "GET":
        return render_template("categories/edit.html", category=category)

    if request.method == "POST":
        check_csrf()
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Name is required")
            return redirect("/category/" + str(category_id))

        categories.update_category(category_id, name, description)
        flash("Category updated succesfully!")
        return redirect("/categories")


@app.route("/remove_category/<int:category_id>", methods=["POST"])
def remove_category(category_id):
    require_login()
    check_csrf()
    categories.remove_category(category_id)
    flash("Category deleted")
    return redirect("/categories")


@app.route("/features")
def list_features():
    all_features = features.get_features()
    return render_template("features/list.html", features=all_features)


@app.route("/new_feature", methods=["GET", "POST"])
def new_feature():
    require_login()
    all_categories = categories.get_categories()

    if request.method == "GET":
        return render_template("features/create.html", categories=all_categories)

    if request.method == "POST":
        check_csrf()
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        raw_category_id = request.form.get("category_id", "").strip()

        try:
            category_id = int(raw_category_id) if raw_category_id else None
        except ValueError:
            category_id = None

        if not name:
            flash("Name is required")
            return redirect("/new_feature")
        if not category_id:
            flash("A category must be selected")
            return redirect("/new_feature")

        try:
            features.add_feature(name, description, category_id)
            flash("Feature created!")
            return redirect("/features")
        except sqlite3.IntegrityError:
            flash("Selected category is invalid.")
            return redirect("/new_feature")


@app.route("/feature/<int:feature_id>", methods=["GET", "POST"])
def edit_feature(feature_id):
    require_login()

    feature = features.get_feature(feature_id)
    if not feature:
        abort(404)

    all_categories = categories.get_categories()

    if request.method == "GET":
        return render_template(
            "features/edit.html", feature=feature, categories=all_categories
        )

    if request.method == "POST":
        check_csrf()
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        raw_category_id = request.form.get("category_id", "").strip()

        try:
            category_id = int(raw_category_id) if raw_category_id else None
        except ValueError:
            category_id = None

        if not name:
            flash("Name is required")
            return redirect("/feature/" + str(feature_id))
        if not category_id:
            flash("A category must be selected")
            return redirect("/feature/" + str(feature_id))

        try:
            features.update_feature(feature_id, name, description, category_id)
            flash("Feature updated successfully!")
            return redirect("/features")
        except sqlite3.IntegrityError:
            flash("Selected category is invalid.")
            return redirect("/feature/" + str(feature_id))


@app.route("/remove_feature/<int:feature_id>", methods=["POST"])
def remove_feature(feature_id):
    require_login()
    check_csrf()
    features.remove_feature(feature_id)
    flash("Feature deleted")
    return redirect("/features")


@app.route("/events")
def list_events():
    all_events = events.get_events()
    return render_template("events/list.html", events=all_events)


@app.route("/event/<slug>")
def view_event(slug):
    event = events.get_event(slug)
    if not event:
        abort(404)
    return render_template("events/view.html", event=event)


@app.route("/new_event", methods=["GET", "POST"])
def new_event():
    require_login()
    all_features = events.get_all_features_with_categories()

    if request.method == "GET":
        return render_template("events/create.html", features=all_features)

    if request.method == "POST":
        check_csrf()
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        slug = events.generate_slug(name)

        if not name:
            flash("Name is required")
            return redirect("/new_event")

        selected_feature_ids = request.form.getlist("feature_ids")
        selected_features = []
        for feature_id in selected_feature_ids:
            input_name = "feature_note_" + str(feature_id)
            note_text = request.form.get(input_name, "")
            selected_features.append((feature_id, note_text))

        events.add_event(name, slug, description, selected_features)
        return redirect("/events")


@app.route("/edit_event/<slug>", methods=["GET", "POST"])
def edit_event(slug):
    require_login()

    event = events.get_event(slug)
    if not event:
        abort(404)

    all_features = features.get_features()

    if request.method == "GET":
        event_features_map = {}
        for f in event["features"]:
            event_features_map[f["id"]] = f["notes"]
        return render_template(
            "events/edit.html",
            event=event,
            all_features=all_features,
            event_features_map=event_features_map,
        )

    if request.method == "POST":
        check_csrf()
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Name is required")
            return redirect("/edit_event/" + slug)

        selected_feature_ids = request.form.getlist("feature_ids")
        selected_features = []
        for feature_id in selected_feature_ids:
            input_name = "feature_note_" + str(feature_id)
            note_text = request.form.get(input_name, "").strip()
            selected_features.append((feature_id, note_text))

        events.update_event(event["id"], name, description, selected_features)
        flash("Event updated successfully!")
        return redirect("/event/" + slug)


@app.route("/remove_event/<int:event_id>", methods=["POST"])
def remove_event(event_id):
    require_login()
    check_csrf()
    events.remove_event(event_id)
    return redirect("/events")
