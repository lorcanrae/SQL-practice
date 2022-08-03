import sqlite3

def format_date(db):
    '''Returns formatted dates'''
    query = '''
SELECT DISTINCT
  -- Select the order date
  order_date,
  -- Format the order date
  TO_CHAR(order_date, 'FMDay DD, FMMonth YYYY') AS format_order_date
FROM orders
ORDER BY order_date ASC
LIMIT 3;
    '''
    db.execute(query)
    rows = db.fetchall()
    return rows




## Delete me after

def placeholder(db):
    '''placeholder'''
    query = '''

    '''
    db.execute(query)
    rows = db.fetchall()
    return rows
