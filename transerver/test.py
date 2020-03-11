#from translate import translate_onesentence

#res = translate_onesentence("Hi, this is my best friend Tom. He is a good man.", prefix="呵呵")
#print(res)

#from store import storeonesent2mysql

#storeonesent2mysql("Hi, this is my best friend Tom.","你好，这是我最好的朋友汤姆。","en","zh")



# test select function
import pymysql
db = pymysql.connect("172.17.0.1","root","root","corpus")
print('db:',db)

sql = f'''select sourcetext, targettext from table_pe2zh'''

try:
    with db.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
except Exception as e:
    print(e)

print(result)

for res in result:
    print(res, res[0], res[1])

print(len(res))