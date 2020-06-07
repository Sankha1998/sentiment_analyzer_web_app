from flask import Flask, render_template, request
import numpy as np
import pickle
from bs4 import BeautifulSoup as bs
import requests
import re





app=Flask(__name__)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}




pre_model= open('pre_model.pickle','rb')
pre_model = pickle.load(pre_model)


model= open('model.pickle','rb')
model = pickle.load(model)

# Function to clean html tags
def clean_html(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

# function to convert to lower_case
def convert_lower(text):
    return text.lower()


def remove_special(text):
    x = ''

    for i in text:
        if i.isalnum():
            x = x + i
        else:
            x = x + ' '
    return x



def url_link(text):
    clean = re.compile('/title/')
    x = re.sub(clean, '', text)
    i=0
    res=''
    while i<len(x):
        if x[i]=='/':
            break
        else:
            res+=x[i]
        i=i+1
    return res


def search_item(movie_name):
    if len(movie_name)==0:
        return "Write Mobvie Name"
    else:
        url = "https://www.imdb.com/find?q=" + movie_name + "&ref_=nv_sr_sm"
        webpage = requests.get(url, headers=headers).text
        soup = bs(webpage, 'lxml')
        scr_res = soup.find_all('div', class_='findSection')
        movies, url_movie_detail_link = [], []
        for i in scr_res[0].find_all('td', class_="result_text"):
            movies.append((i.text).strip())
            url_movie_detail_link.append(url_link(i.find('a', href=re.compile(r'[/]([a-z]|[A-Z])\w+')).attrs['href']))

        return movies, url_movie_detail_link

def movie_plot(url):
    plot=''
    webpage=requests.get(url, headers= headers).text
    soup=bs(webpage,'lxml')
    for i in soup.find_all('div',class_='summary_text'):
        if (((i.text).strip()=='Add a Plot »') or (len((i.text).strip())<15)):
            plot = 'Not Available'
        else:
            plot = (i.text).strip()
    return plot


def movie_details(url):
    webpage = requests.get(url, headers=headers).text
    soup = bs(webpage, 'lxml')
    movie_name = ''
    l = []
    movie_rating = ''
    for i in soup.find_all('h1', class_=""):
        movie_name = (remove_special(i.text).strip()).strip()
    for i in soup.find_all('div', class_='ratingValue'):
        movie_rating = (i.text).strip()

    for i in soup.find_all('div', class_="credit_summary_item"):
        l.append(remove_special((i.text).strip()).strip())
    s = []
    f = []
    val = 0
    while val < len(l):
        for i in l[val].split(' '):
            if i == 'See':
                break
            else:
                s.append(i.strip())
                x = ' '.join(s)
        f.append(x.strip())
        s.clear()

        val = val + 1

    return movie_name, movie_rating, f


def movie_img(url):
    ul=''
    webpage=requests.get(url, headers= headers).text
    soup=bs(webpage,'lxml')
    for i in soup.find_all('div',class_='poster'):
        ul = (i.find('img')).get('src')
    return ul



def site_review(u):
    page = requests.get(u, headers=headers).text

    soup = bs(page, 'lxml')
    pg = soup.find_all('div', class_='lister-item-content')

    url_user_name, url_title, url_rating, url_reviews = [], [], [], []  ## content

    for i in pg:
        try:
            url_title.append((i.find('a', class_="title").text).strip())
        except:
            url_title.append('not available')
        try:
            url_rating.append((i.find('span', class_="rating-other-user-rating").text).strip())
        except:
            url_rating.append('not available')
        try:
            url_user_name.append((i.find('span', class_="display-name-link").text).strip())
        except:
            url_user_name.append('not available')
        try:
            url_reviews.append((i.find('div', class_="text show-more__control").text).strip())
        except:
            url_reviews.append('not available')
    return url_user_name, url_title, url_rating, url_reviews

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/register')
def about():
    return render_template("registration.html")

@app.route('/search_movie', methods=['POST','GET'])
def search_val():
    movie_name = request.form.get('name')
    movies, res, = search_item(movie_name)
    return render_template("movies.html",element=movies,urlss=res)


@app.route('/responsed_url/<string:type>')
def movie_ul(type):
    url1 = "https://www.imdb.com/title/{}/?ref_=fn_tt_tt_1".format(type)
    url2 = "https://www.imdb.com/title/{}/reviews?ref_=tt_urv".format(type)
    rv=""
    mov_plt=movie_plot(url1)
    movi=str(movie_img(url1))
    mov_name,mov_rating,mov_d=movie_details(url1)
    user_name, url_title, url_rating, url_reviews = site_review(url2)
    rev=[]
    clrr=[]

    if len(url_reviews)>10:
        for tre in url_reviews:
            tre = np.array([tre[100:]])
            text_re = pre_model.transform(tre)
            res = model.predict(text_re)
            if res[0] == 0:
                rev.append("text-danger")
                clrr.append("red")
            else:
                rev.append("text-success")
                clrr.append("green")
        return render_template('imdb_review.html', imag=movi, movie_name=mov_name, movie_rating=mov_rating,
                                   movie_details=mov_d, plot=mov_plt,
                                   review_complete=zip(url_title, url_rating, user_name, rev, clrr, url_reviews))
    else:
        url_title.append('X')
        url_rating.append('x')
        user_name.append('X')
        rev.append('text-light')
        clrr.append("white")
        url_reviews.append('No Review Avalilable')

        return render_template('imdb_review.html', imag=movi, movie_name=mov_name, movie_rating=mov_rating,
                               movie_details=mov_d, plot=mov_plt,
                               review_complete=zip(url_title, url_rating, user_name, rev, clrr, url_reviews))





@app.route('/review', methods=['POST','GET'])
def rev():
    user_review = request.form.get('review')
    tre = np.array([user_review])
    text_re = pre_model.transform(tre)
    res = model.predict(text_re)
    if res[0] == 0:
        return render_template('review.html', content='Negative')
    else:
        return render_template('review.html', content='Positive')




if __name__=="__main__":
    app.run(debug=True)