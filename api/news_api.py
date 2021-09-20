# !/usr/bin/env python
# coding: utf-8

from math import ceil
from newsapi import NewsApiClient
import datetime as dt
from pandas.io.json import json_normalize
import pandas as pd
from datetime import datetime, timedelta
import pprint as pp
import requests
from bs4 import BeautifulSoup
import wordcloud
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from utils import utils


def top_headlines():
    country = input("Which country are you interested in? ")
    category = input("""Which category are you interested in? \nHere are the categories to choose from: 
                   \nbusiness\nentertainment\ngeneral\nhealth\nscience\ntechnology """)

    top_headlines = newsapi.get_top_headlines(category=category, language='en', country=country)
    top_headlines = json_normalize(top_headlines['articles'])
    newdf = top_headlines[["title", "url"]]
    dic = newdf.set_index('title')['url'].to_dict()
    top_headlines
    print("Here are some of the top articles\n\n")
    for (k, v) in dic.items():
        print(k + "\n\n" + v)
        # urn (top_headlines.url(10),top_headlines['title'].head(10),top_headlines['description'].head(10),top_headlines['content'].head(10))


def date(base):
    date_list = []
    yr = datetime.today().year
    if (yr % 400) == 0 or ((yr % 100 != 0) and (yr % 4 == 0)):
        numdays = 366
        date_list.append([base - timedelta(days=x) for x in range(366)])
    else:
        numdays = 365
        date_list.append([base - timedelta(days=x) for x in range(365)])
    newlist = []
    for i in date_list:
        for j in sorted(i):
            newlist.append(j)
    return newlist


def last_30(base):
    date_list = [base - timedelta(days=x) for x in range(30)]
    # newlist=[]
    # for i in sorted(date_list):
    #    newlist.append(j)
    return sorted(date_list)


def from_dt(x):
    from_dt = []
    for i in range(len(x)):
        from_dt.append(last_30(datetime.today())[i - 1].date())
        # to_dt=date(datetime.today())[i+1].date()
    return from_dt


def to_dt(x):
    to_dt = []
    for i in range(len(x)):
        # from_dt=date(datetime.today())[i].date()
        to_dt.append(last_30(datetime.today())[i].date())
    return to_dt



# /v2/everythin
# class query(chat):
# def func(query):
#     newdf = pd.DataFrame()
#     # query=match.groups()[0]
#     for (from_dt, to_dt) in zip(from_list, to_list):
#         all_articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', from_param=from_dt, to=to_dt)
#         d = json_normalize(all_articles['articles'])
#         newdf = newdf.append(d)
#
#     return newdf


# def text_from_urls(query):
#     newd = {}
#     for (from_dt, to_dt) in zip(from_list, to_list):
#         all_articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', from_param=from_dt, to=to_dt)
#         d = json_normalize(all_articles['articles'])
#         newdf = d[["url", "publishedAt", "source.name", "author"]]
#         newdf = newdf.head(1)
#         # print(newdf.head())
#         dic = newdf.set_index(["source.name", "publishedAt", "author"])["url"].to_dict()
#         # print(dic)
#         for (k, v) in dic.items():
#             # print(str(k[0])+str(k[1][5:10]))
#             page = requests.get(v)
#             html = page.content
#             soup = BeautifulSoup(html, "lxml")
#             text = soup.get_text()
#             d2 = soup.find_all("p")
#             # for a in d2:
#             newd[k] = re.sub(r'<.+?>', r'', str(d2))
#     return newd




def wordcld(dictionary):
    newd = {}
    for (k, v) in dictionary.items():
        if v != '[]':
            print((k, dictionary[k]))



def wordcld(dictionary):
    newd = {}
    for (k, v) in dictionary.items():
        if v != '[]':
            wordcloud = WordCloud().generate(str(dictionary[k]))
            fig, axes = plt.subplots(figsize=(20, 12), clear=True)
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.show()
            print(str(k[0]) + "_" + str(k[1][5:10]) + "_" + str(k[1][11:13]) + "_" + str(k[1][14:16]) + "_" + str(
                k[1][17:19]) + "_" + str(k[2]))
            wordcloud.to_file("wordcloud_images/" + (
                        str(k[0]) + "_" + str(k[1][5:10]) + "_" + str(k[1][11:13]) + "_" + str(k[1][14:16]) + "_" + str(
                    k[1][17:19])) + "_" + ".png")
        else:
            print(str(k[0]) + "_" + str(k[1][5:10]) + "_" + str(k[1][11:13]) + "_" + str(k[1][14:16]) + "_" + str(
                k[1][17:19]) + "_" + str(k[2]))
            print("Wordcloud Not applicable")


def NewsApi (tema):

    api_key = 'a7503f924ba94bf8874a440cc9d74fcb'
    newsapi = NewsApiClient(api_key=api_key)
    # data = newsapi.get_everything(q=tema, language='pt', page_size=20)

    # print(data['totalResults'])
    # print(data.keys())
    # print(data['status'])

    # articles = data['articles']
    #
    # for x,y in enumerate(articles):
    #     print('{0}  {1}'.format(x, y["title"]))
    #
    #
    # for key, value in articles[0].items():
    #     print("\n{0} {1}".format(key.ljust(15), value))
    #     #print(f"\n{key.ljust(15)} {value}")
    #
    # pub_data = dt.datetime.strptime(articles[0]['publishedAt'],"%Y-%m-%dT%H:%M:%SZ").date()
    # print(pub_data)
    #
    # df = pd.DataFrame(articles)


    ######### melhorar as buscas e evitar o estouro


    data = newsapi.get_everything(q=tema[0], from_param=utils.dateFormatNewsApi())
    # data = newsapi.get_everything(q=tema[0], from_param='2021-08-20')
    # print(data['totalResults'])

    return data

