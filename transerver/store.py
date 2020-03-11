import pymysql
from datetime import datetime
from logging import getLogger
import time

logger = getLogger()
mutex = 0
db = pymysql.connect("172.17.0.1","root","root","corpus",3306)
'''
def storeonesent2mysql(sourceText, targetText, sourceLang, targetLang):
    date = datetime.now().strftime("%Y-%m-%d")
    sql = f"""insert into {sourceLang}2{targetLang} (sourcetext, targettext, date) values('{sourceText}','{targetText}','{date}')"""
    cursor.execute(sql)
    db.commit()
'''

def storeonesent2mysql(sourceText, targetText, sourceLang, targetLang):
    global mutex
    date = datetime.now().strftime("%Y-%m-%d")
    sql = f'''insert into {sourceLang}2{targetLang} (sourcetext, targettext, date) values(%s, %s, %s)'''
    while mutex == 1:
        time.sleep(0.05)
    mutex = 1
    try:
        with db.cursor() as cursor: 
            cursor.execute(sql, (sourceText, targetText, date))
            db.commit()
            mutex = 0
    except Exception as e:
        mutex = 0
        logger.info(str(e))
        db.ping(reconnect=True)

def update_table_viamysql(table, sourceLang, targetLang):
    #
    global mutex
    sql = f'''select sourcetext, targettext from table_{sourceLang}2{targetLang}'''
    while mutex == 1:
        time.sleep(0.05)
    mutex = 1
    try:
        with db.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            db.commit()
            mutex = 0
    except Exception as e:
        mutex = 0
        logger.info(str(e))
        db.ping(reconnect=True)
    for r in result:
        sourcetext, targettext = r[0], r[1]
        table[sourcetext] = targettext
    if '$TAG' not in table:
        table['$TAG'] = '$TAG'
    return len(result)

def update_mysql_viafile(table, sourceLang, targetLang):
    # table = {} update mysql table_pe2zh
    global mutex
    db.ping(reconnect=True)
    search_sql = f'''select count(*) from table_{sourceLang}2{targetLang} where sourcetext=%s'''
    update_sql = f'''update table_{sourceLang}2{targetLang} set targettext=%s where sourcetext=%s'''
    insert_sql = f'''insert into table_{sourceLang}2{targetLang} (sourcetext, targettext) values(%s, %s)'''
    while mutex == 1:
        time.sleep(0.05)
    try:
        for sourcetext, targettext in table.items():
            mutex = 1
            with db.cursor() as cursor:
                cursor.execute(search_sql, (sourcetext))
                result = cursor.fetchall()[0][0]
                if result > 0:
                    cursor.execute(update_sql, (targettext, sourcetext))
                else:
                    cursor.execute(insert_sql, (sourcetext, targettext))
            mutex = 0
        mutex = 1
        db.commit()
        mutex = 0
    except Exception as e:
        mutex = 0
        return e
    return None

        
