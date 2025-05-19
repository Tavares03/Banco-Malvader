import pymysql

def conectar():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='030406',
        database='banco_malvader',
        cursorclass=pymysql.cursors.DictCursor
    )