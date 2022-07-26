import mysql.connector
from mysql.connector import Error
from nownews import get_news
import threading
import requests

def set_interval(func, sec):
    global t
    def func_wrapper():
        set_interval(func, sec)
        all_news =func()
        # x=[]
        # counter=1
        # for l in all_news:
        #     one=[]
        #     if counter==5:
        #         break
        #     for k,v in l.items():
        #         # print(k,v)
        #         one.append(v)
        #     x.append(tuple(one))
        #     counter+=1
        # print(x)
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t
def conn():
    try:
        # 連接 MySQL/MariaDB 資料庫
        connection = mysql.connector.connect(
            host='localhost',          # 主機名稱
            database='demo', # 資料庫名稱
            user='root',        # 帳號
            password='12345678')  # 密碼

        # 查詢資料庫
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM news;")
        
        records = cursor.fetchall()
        print("資料筆數：", cursor.rowcount)
        # 列出查詢的資料 %s=string %d=decimal
        # for (Title, date, url) in records:
        #     print("Title: %s, date: %s, url: %s" % (Title, date, url))
        # 先刪除清空上一筆抓取的資料新聞
        cursor.execute("DELETE FROM news;")
        
        # 新增資料
        # sql = "INSERT INTO news (Title, date, url) VALUES (%s, %s, %s);"
        # new_data = ('all_news')
        # cursor = connection.cursor()
        # cursor.execute(sql, new_data)
        
        mySql_insert_query = """INSERT INTO news (Title, date, url) 
                            VALUES (%s, %s, %s) """
        all_news = get_news(num=1)
        # print(all_news[0])
        
        x=[]
        counter=1
        for l in all_news:
            one=[]
            if counter==5:
                break
            for k,v in l.items():
                # print(k,v)
                one.append(v)
            x.append(tuple(one))
            counter+=1
        # print(x)
        records_to_insert = x

        cursor = connection.cursor()
        cursor.executemany(mySql_insert_query, records_to_insert)
        connection.commit()

        # 確認資料有存入資料庫
        connection.commit()


    except Error as e:
        print("資料庫連接失敗：", e)

    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            data= "yes"
            url = f'192.168.22.203:8080?pid={data}'
            r = requests.get(url)
            print(r)
            print("資料庫連線已關閉")

# if __name__ == "__main__":
    # set_interval(conn, 3)
    
