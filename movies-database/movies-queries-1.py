# import sqlite3


# Remember => list (rows) of tuples (columns)

def directors_count(db):
    db.execute("SELECT count(*) FROM directors d")
    return db.fetchone()[0]


def directors_list(db):
    # return the list of all the directors sorted in alphabetical order
    query = """SELECT d.name
                FROM directors d
                ORDER BY d.name"""
    db.execute(query)
    rows = db.fetchall()
    return [rows[i][0] for i in range(len(rows))]


def love_movies(db):
    # return the list of all movies which contain the exact word "love"
    # in their title, sorted in alphabetical order
    query = """SELECT m.title
FROM movies m
WHERE m.title LIKE '% love %'
	OR m.title LIKE 'love %'
	OR m.title LIKE '% love'
	OR m.title LIKE '% love.'
    OR m.title LIKE '% love''%'
    OR m.title LIKE '%love,%'
    OR m.title LIKE 'love'
ORDER BY m.title"""
    db.execute(query)
    rows = db.fetchall()
    return [rows[i][0] for i in range(len(rows))]


def directors_named_like_count(db, name):
    # return the number of directors which contain a given word in their name
    query = f"""SELECT COUNT(d.name)
FROM directors d
WHERE d.name LIKE '%{name}%'
"""
    db.execute(query)
    rows = db.fetchall()
    return int(rows[0][0])


def movies_longer_than(db, min_length):
    # return this list of all movies which are longer than a given duration,
    # sorted in the alphabetical order
    query = f"""SELECT m.title
FROM movies m
WHERE m.minutes > {min_length}
ORDER BY m.title"""
    db.execute(query)
    rows = db.fetchall()
    return [rows[i][0] for i in range(len(rows))]


# if __name__ == '__main__':
#     conn = sqlite3.connect('data/movies.sqlite')
#     db = conn.cursor()
#     directors_list(db)
