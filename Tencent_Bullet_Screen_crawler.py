import requests
import json
import time
import pandas as pd
import random
import os
from tqdm.notebook import tqdm

#Create a  JS request asking for bullet screen content

def create_urls(movie_info,url_prototype):
    
    target_id = movie_info["TargetID"].tolist()
    timestamp = movie_info["TimeStamp"].tolist()
    sites = {"targetid":target_id,'time':timestamp}
    url_list = []
    for i in range(len(target_id)):
        for t in range(sites['time'][i]):
            url = url_prototype.format(sites["targetid"][i],15+t*30)
            url_list.append(url)
    return(url_list)


def parse_base_info(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36'}
    html = requests.get(url,headers=headers)
    
    bs = json.loads(html.text,strict = False)
    targets = bs['target_id']
    
    df = pd.DataFrame()
    for i in bs['comments']:
        content = i['content']
        upcount = i['upcount']
        name = i['opername']
        user_degree = i['uservip_degree']
        timepoint = i['timepoint']
        comment_id = i['commentid']
        
        df = df.append({
            'Username':name,
            'Content':content,
            'UserLevel':user_degree,
            'TimePoint':timepoint,
            'Upcount':upcount,
            'CommentID':comment_id,
            'MovieID':targets
        }, ignore_index=True)
        
    return df



def main():
    movie_info = pd.read_excel("movie_info_df")
    url_prototype = 'https://mfm.video.qq.com/danmu?otype=json&target_id={}&timestamp={}'
    for _, movie in movie_info.iterrows():
        filename = f"danmu/{movie['DanmuID']}.txt"
        if os.path.isfile(filename):
            continue
        
    
    results = []
    for t in tqdm(range(movie['TimeStamp']), leave=False):
        url = url_prototype.format(movie['TargetID'], 15+t*30)
        try:
            result = parse_base_info(url)
            results.append(result)
        except:
            print('failed url:', url)
        time.sleep(0.05 + random.random())
    dfs = pd.concat(results, ignore_index=True)
    dfs.to_csv(filename, sep='\t', index=False, encoding= 'utf-8')

if __name__ == "__main__":
    main()