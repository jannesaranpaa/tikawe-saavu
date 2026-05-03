import hashlib
import json
import re

import db


def generate_slug(name):
    hash_suffix = hashlib.md5(name.encode("utf-8")).hexdigest()[:8]
    slug = name.lower()
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug[:50].strip("-")

    if slug:
        return f"{slug}-{hash_suffix}"
    return hash_suffix


def get_events():
    sql = """SELECT e.id, e.name, e.slug, e.description
             FROM events e
             ORDER BY e.created_at ASC"""
    return db.query(sql)


def get_event(slug):
    sql = """SELECT
             e.id, e.name, e.slug, e.description, e.user_id, e.created_at,
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
             GROUP BY e.id"""
    result = db.query(sql, [slug])
    if not result:
        return None

    event_dict = dict(result[0])
    event_dict["features"] = json.loads(event_dict["features_json"])
    return event_dict


def get_all_features_with_categories():
    sql = """SELECT f.id, f.name, f.description, c.name FROM features f 
             JOIN categories c ON f.category_id = c.id 
             ORDER BY f.name"""
    return db.query(sql)


def add_event(name, slug, description, selected_features):
    sql = "INSERT INTO events (name, slug, description) VALUES (?, ?, ?)"
    db.execute(sql, [name, slug, description])
    event_id = db.last_insert_id()

    sql = "INSERT INTO event_features (event_id, feature_id, description) VALUES (?, ?, ?)"
    for feature_id, note_text in selected_features:
        db.execute(sql, [event_id, feature_id, note_text])


def update_event(event_id, name, description, selected_features):
    sql = "UPDATE events SET name = ?, description = ? WHERE id = ?"
    db.execute(sql, [name, description, event_id])

    sql = "DELETE FROM event_features WHERE event_id = ?"
    db.execute(sql, [event_id])

    sql = "INSERT INTO event_features (event_id, feature_id, description) VALUES (?, ?, ?)"
    for feature_id, note_text in selected_features:
        db.execute(sql, [event_id, feature_id, note_text])


def remove_event(event_id):
    sql = "DELETE FROM events WHERE id = ?"
    db.execute(sql, [event_id])
