import sqlite3

conn = sqlite3.connect('fries.sqlite')
c = conn.cursor()
c.execute('CREATE TABLE county '
          + '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
          + 'issueTime TEXT, location TEXT, element TEXT, '
          + 'startTime TEXT, endTime TEXT, value TEXT)')
c.execute((
    'CREATE TABLE fries '
    '('
    'id INTEGER PRIMARY KEY AUTOINCREMENT, '
    'floor TEXT, '
    'parent_floor TEXT, '
    'reply_floor TEXT, '
    'user_name TEXT, '
    'user_id TEXT, '
    'gp TEXT, '
    'bp TEXT, '
    'time TEXT, '
    'content TEXT'
    ')'
))
conn.commit()
conn.close()