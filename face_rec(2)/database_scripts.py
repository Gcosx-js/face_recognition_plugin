import sqlite3 as sql
from venv import create

from charset_normalizer import detect


conn = sql.connect('face_rec.db')
cursor = conn.cursor()


def create_table():
    cursor.execute('''CREATE TABLE IF NOT EXISTS User_datas (
                    id TEXT,
                    Email TEXT NOT NULL,
                    Full_name TEXT NOT NULL,
                    Password NOT NULL)''')
    conn.commit()
    



def insert_data(id, email, full_name,password):
    cursor.execute('INSERT INTO User_datas (id, Email, Full_name,Password) VALUES (?, ?, ?,?)', (id, email, full_name,password))
    conn.commit()
    

def handle_null_base():
    pass

def update_data(id, email, full_name,password):
    cursor.execute('UPDATE User_datas SET Email=?, Full_name=?,Password =? WHERE id=?', (email, full_name,password,id))
    conn.commit()


def delete_data(id):
    cursor.execute('DELETE FROM User_datas WHERE id=?',(id,))
    conn.commit()
    
def fetch_data(id):
    cursor.execute('SELECT Email,Full_name,Password FROM User_datas WHERE id=?',(id,))
    data = cursor.fetchone()
    if data:
        return data
    else:
        return False

create_table()
#insert_data('12345','afsdhbhad@gmail.com','Elmir','23456')
#print(list(fetch_data('12345'))) #type: ignore
print('Table successfully created if not exist!')

