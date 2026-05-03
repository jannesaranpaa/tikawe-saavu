import db


def get_features():
    sql = """SELECT f.id, f.name, f.description, c.name as category_name 
             FROM features f
             LEFT JOIN categories c ON f.category_id = c.id
             ORDER BY c.name ASC, f.name ASC"""
    return db.query(sql)


def get_feature(feature_id):
    sql = "SELECT * FROM features WHERE id = ?"
    result = db.query(sql, [feature_id])
    return result[0] if result else None


def add_feature(name, description, category_id):
    sql = "INSERT INTO features (name, description, category_id) VALUES (?, ?, ?)"
    db.execute(sql, [name, description, category_id])


def update_feature(feature_id, name, description, category_id):
    sql = "UPDATE features SET name = ?, description = ?, category_id = ? WHERE id = ?"
    db.execute(sql, [name, description, category_id, feature_id])


def remove_feature(feature_id):
    sql = "DELETE FROM features WHERE id = ?"
    db.execute(sql, [feature_id])
