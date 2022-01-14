import sqlite3
from tools import plot_wordcloud_by_userid


def find_top40_users():
    """Return: List[str_userid]"""
    conn = sqlite3.connect('./fries.sqlite')
    c = conn.cursor()
    c.execute((
        'SELECT user_id FROM fries '
        'WHERE content IS NOT NULL '
        'GROUP BY user_id '
        'ORDER BY COUNT(user_id) DESC '
        'LIMIT 40;'
    ))
    conn.commit()
    res = c.fetchall()
    conn.close()
    res = list(map(lambda tup: tup[0], res))   # List[Tuple(str)] -> List[str]
    return res
    

if __name__ == '__main__':
    user_ids = find_top40_users()
    for i, uid in enumerate(user_ids):
        print(f'{i+1}/40  {uid} ... ', end='')
        plot_wordcloud_by_userid(uid)
        print('[Done]')