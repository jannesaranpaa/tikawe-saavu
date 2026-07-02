from werkzeug.security import check_password_hash, generate_password_hash
import db


def get_user(user_id):
    sql = "SELECT id, username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None


def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])


def check_login(username, password):
    sql = "SELECT id, hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if not result:
        return None

    user_id = result[0]["id"]
    password_hash = result[0]["hash"]
    if check_password_hash(password_hash, password):
        return user_id
    else:
        return None


def get_user_profile_data(user_id):
    c_count = db.query(
        "SELECT COUNT(id) AS count FROM categories WHERE user_id = ?", [user_id]
    )[0]["count"]
    f_count = db.query(
        "SELECT COUNT(id) AS count FROM features WHERE user_id = ?", [user_id]
    )[0]["count"]
    e_count = db.query(
        "SELECT COUNT(id) AS count FROM events WHERE user_id = ?", [user_id]
    )[0]["count"]

    user_events = db.query(
        "SELECT id, name, slug, description FROM events WHERE user_id = ? ORDER BY created_at DESC",
        [user_id],
    )

    return {
        "categories_count": c_count,
        "features_count": f_count,
        "events_count": e_count,
        "events": user_events,
    }
