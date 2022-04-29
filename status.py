import sqlite3
from pathlib import Path
from contextlib import closing
from datetime import datetime

table_creation_status = '''CREATE TABLE IF NOT EXISTS status (
                               user_id TEXT NOT NULL,
                               account_id TEXT NOT NULL UNIQUE
                           );'''

table_creation_history = '''CREATE TABLE IF NOT EXISTS history (
                                user_id TEXT NOT NULL,
                                account_id TEXT NOT NULL,
                                login_time REAL NOT NULL
                            );'''

def connect(group_id: str) -> 'closing(Connection)':
    dbFile = Path.cwd() / Path('hoshino/modules/clan_daidao_record/db/{}.db'.format(group_id))
    dbFile.resolve()
    isExists = dbFile.exists()
    
    con = sqlite3.connect(dbFile)
    
    if not isExists:
        _initiate_tables(con)
    
    return closing(con)

def _initiate_tables(con: 'Connection') -> None:
    with closing(con.cursor()) as cur:
        cur.execute(table_creation_status)
        cur.execute(table_creation_history)

def loginStatus(con: 'Connection', account_id: str) -> 'user_id':
    with closing(con.cursor()) as cur:
        result = cur.execute('SELECT user_id FROM status WHERE account_id = ?', (account_id,)).fetchone()
        
        if result is None:
            return None
        else:
            return result[0]

def login(con: 'Connection', user_id: str, account_id: str) -> None:
    with closing(con.cursor()) as cur:
        cur.execute('INSERT INTO status VALUES(?, ?)', (user_id, account_id))
        cur.execute('INSERT INTO history VALUES(?, ?, ?)', (user_id, account_id, datetime.now().timestamp()))
        con.commit()

def logout(con: 'Connection', account_id: str) -> None:
    with closing(con.cursor()) as cur:
        cur.execute('DELETE FROM status WHERE account_id = ?', (account_id,))
        con.commit()

def logoutAll(con: 'Connection', user_id: str) -> None:
    with closing(con.cursor()) as cur:
        cur.execute('DELETE FROM status WHERE user_id = ?', (user_id,))
        con.commit()

def getCurStatus(con: 'Connection', user_id: str = None) -> [('user_id', 'account_id')]:
    result = []
    
    with closing(con.cursor()) as cur:
        if user_id is not None:
            for row in cur.execute('SELECT * FROM status WHERE user_id = ?', (user_id,)):
                result.append(row)
        else:
            for row in cur.execute('SELECT * FROM status ORDER BY user_id'):
                result.append(row)
    
    return result

def clearStatus(con: 'Connection') -> None:
    with closing(con.cursor()) as cur:
        cur.execute('DELETE FROM status')
        con.commit()

def getDaidaoCount(con: 'Connection', user_id: str, begin: datetime, end: datetime) -> int:
    result = 0
    
    with closing(con.cursor()) as cur:
        result = cur.execute('SELECT COUNT(*) FROM history WHERE user_id = ? AND login_time >= ? AND login_time < ?', (user_id, begin.timestamp(), end.timestamp())).fetchone()[0]
    
    return result

def deleteHistory(con: 'Connection', lastDay: datetime) -> None:
    with closing(con.cursor()) as cur:
        cur.execute('DELETE FROM history WHERE login_time < ?', (lastDay.timestamp(),))
        con.commit()
