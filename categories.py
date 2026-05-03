import db


def get_categories():
    sql = "SELECT id, name, description FROM categories ORDER BY name"
    return db.query(sql)


def get_category(category_id):
    sql = "SELECT * FROM categories WHERE id = ?"
    result = db.query(sql, [category_id])
    return result[0] if result else None


def add_category(name, description):
    sql = "INSERT INTO categories (name, description) VALUES (?, ?)"
    db.execute(sql, [name, description])


def update_category(category_id, name, description):
    sql = "UPDATE categories SET name = ?, description = ? WHERE id = ?"
    db.execute(sql, [name, description, category_id])


def remove_category(category_id):
    sql = "DELETE FROM categories WHERE id = ?"
    db.execute(sql, [category_id])
