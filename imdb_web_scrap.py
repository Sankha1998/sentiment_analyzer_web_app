from  bs4 import BeautifulSoup
from io import StringIO
import requests
l=[]
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}


url="https://www.imdb.com/find?q=dhoom&ref_=nv_sr_sm"

s=requests.get(url, headers= headers).text

l=l.append(StringIO(s))