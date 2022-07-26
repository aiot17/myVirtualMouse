import time
# import schedule
# import random
import requests
import json
from threading import Timer


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
}


def get_news(num=3):
    all_news = []
    pid = ''
    while len(all_news) < num:
        url = f'https://www.nownews.com/nn-client/api/v1/cat/breaking/?pid={pid}'
        r = requests.get(url, headers=HEADERS)
        if r.status_code != requests.codes.ok:
            print(f'Requests Error: {r.status_code}')
            break

        data = r.json()
        news_list = data['data']['newsList']
        for news in news_list:
            news_data = {
                # 'id': news['id'],
                
                'title': news['postTitle'],
                # 'content': news['postContent'],
                'date': news['newsDate'],
                'url': 'https://www.nownews.com' + news['postOnlyUrl']
            }
            all_news.append(news_data)

        # pid = all_news[-1]['id']
        # time.sleep(random.uniform(1, 2))
    return all_news

if __name__ == "__main__":
    all_news = get_news(num=1)
    print(all_news[0])
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
    print(x)
    # Timer(5, get_news).start()
    # t=Timer(5, get_news)
    # t.start()
    # print(all_news)

# schedule.every(1).minute.do(get_news)
# while True:
#     schedule.run_pending()
#     time.sleep(1)
#     print("爬蟲")

        