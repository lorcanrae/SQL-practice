# import sqlite3

def detailed_movies(db):
    '''return the list of movies with their genres and director name'''
    query = """
SELECT m.title, m.genres, d.name
FROM movies m
JOIN directors d ON d.id = m.director_id
    """
    db.execute(query)
    rows = db.fetchall()
    return rows

def late_released_movies(db):
    '''return the list of all movies released after their director death'''
    query = """
SELECT m.title
FROM movies m
JOIN directors d ON d.id = m.director_id
WHERE m.start_year > d.death_year
    """
    db.execute(query)
    rows = db.fetchall()
    return [rows[i][0] for i in range(len(rows))]

def stats_on(db, genre_name):
    '''return a dict of stats for a given genre'''
    query = f"""
SELECT COUNT(*), SUM(m.minutes)
FROM movies m
WHERE m.genres LIKE ?
    """
    db.execute(query, (genre_name,))
    rows = db.fetchall()

    results = {
        'genre': genre_name,
        'number_of_movies': rows[0][0],
        'avg_length': round(rows[0][1] / rows[0][0], 2),
    }
    print(results)
    return results

def top_five_directors_for(db, genre_name):
    '''return the top 5 of the directors with the most movies for a given genre'''
    query = """
SELECT d.name, COUNT(m.director_id)
FROM movies m
JOIN directors d ON d.id = m.director_id
WHERE m.genres = ?
GROUP BY d.name
ORDER BY COUNT(m.director_id) DESC, d.name
LIMIT 5
    """
    db.execute(query, (genre_name,))
    rows = db.fetchall()
    return rows

def movie_duration_buckets(db):
    '''return the movie counts grouped by bucket of 30 min duration'''
    query = """
SELECT (m.minutes/30 + 1) * 30 AS buckets, COUNT(m.minutes/30)
FROM movies m
WHERE m.minutes NOTNULL
GROUP BY m.minutes/30
ORDER BY m.minutes/30
    """
    db.execute(query)
    rows = db.fetchall()
    return rows

def top_five_youngest_newly_directors(db):
    '''return the top 5 youngest directors when they direct their first movie'''
    query = """
SELECT d.name, (m.start_year - d.birth_year) as delta
FROM movies m
JOIN directors d ON d.id = m.director_id
WHERE delta NOTNULL
GROUP BY d.name
ORDER BY delta
LIMIT 5
    """
    db.execute(query)
    rows = db.fetchall()
    return rows

# if __name__ == '__main__':
#     conn = sqlite3.connect('data/movies.sqlite')
#     db = conn.cursor()
#     movie_duration_buckets(db)
