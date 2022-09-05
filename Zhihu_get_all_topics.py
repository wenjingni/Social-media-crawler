# Scrape dow the list of topics on Zhihu 
# father topics are listed on the page https://www.zhihu.com/topics
# son-topics are embedded within each father topic
import requests
from lxml import etree
import json
from tqdm import tqdm
import time
import pandas as pd

#First, scrape down all father topics shown on the top borad of Zhihu topic plaza
def get_father_topic(url,headers,prototype):
    request_session = requests.session()
    access_web = request_session.get(url,headers=headers)
    selector = etree.HTML(access_web.text)
    topics = selector.xpath(prototype)
    topic_ids = []
    topic_names = []
    for topic in topics:
        topic_ids.append(topic.xpath('./@data-id')[0])
        topic_names.append(topic.xpath('./a/text()')[0])
    father_topics = dict(zip(topic_ids,topic_names))
    return father_topics
  
  #For each father topic, there are many subtopics/son-topics embedded in
  #To get these topics, we need to request the node "TopicsPlazzaListV2"
  #These subtopics are arranged with an offset of 20, and the method "next"
  
  def get_son_topics(father_topics,url,headers):

    request_session = requests.session()
    son_topic_ids = []
    son_topic_names = []
    son_topic_full = {}

    for i in tqdm(father_topics,leave=False):
        
        # father_index = i
        # father_name = father_topics[i]
        son_url = url + "#" + father_topics[i]
        offset = -20
        while True:
            offset += 20
            data = {
                "method":"next",
                "params": '{"topic_id":' + str(i) + ',"offset":' + str(offset) + ',"hash_id":""}'
            }
            try:
                request_data = request_session.post("https://www.zhihu.com/node/TopicsPlazzaListV2", data=data, headers = headers).content
                data_info = json.loads(request_data)
                son_topic_list = data_info["msg"]
                if son_topic_list == []:
                    break
                for s in son_topic_list:
                    selector = etree.HTML(s)
                    son_topic_name = selector.xpath("//strong/text()")[0]
                    son_topic_id = selector.xpath('//a[contains(@href,"topic")]/@href')[0].split('/')[2]
                    
                    son_topic_names.append(son_topic_name)
                    son_topic_ids.append(son_topic_id)
                    son_topics = dict(zip(son_topic_ids,son_topic_names))

            except requests.exceptions.RequestException as e:  
                raise SystemExit(e)
    
        son_topic_full.update(son_topics)
        df = pd.DataFrame(list(son_topic_full.items()),columns = ['TopicID','TopicName'])
        df.to_excel('zhihuTopics.xlsx')
    return df, son_topic_full
  
  def main():
    
    url = "https://www.zhihu.com/topics"
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}
    prototype = '//li[@class="zm-topic-cat-item"]'
    father_topics = get_father_topic(url,headers,prototype)
    son_topics = get_son_topics(father_topics,url,headers)
  
  if __name__ == "__main__":
    main()
  
  
