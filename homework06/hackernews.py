from bottle import (
    route, run, template, request, redirect
)

from scrapper import get_news
from db import News, session
from bayes import NaiveBayesClassifier


@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    
        if len(rows) == 0:
        news = get_news("https://news.ycombinator.com/newest", 5)
        for neew in news[::-1]:
            s = session()
            add_news = News(title=neew['title'],
                            author=neew['author'],
                            url=neew['url'],
                            comments=neew['comments'],
                            points=neew['points'])
            s.add(add_news)
            s.commit()
    rows = s.query(News).filter(News.label == None).all()[::-1]
    
    return template('news_template', rows=rows)


@route("/add_label/")
def add_label():
    s = session()
    needed_row = s.query(News).filter_by(id=request.query.id).first()
    needed_row.label = request.query.label
    s.commit()
    redirect("/news")


@route("/update")
def update_news():
    s = session()
    rows = s.query(News).filter().all()
    need_title = rows[0].title
    need_url = rows[0].url
    added_news = get_news("https://news.ycombinator.com/newest")
    for news in added_news[::-1]:
        if need_title == news["title"] and need_url == news["url"]:
            break
        else:
            s = session()
            news = News(title=news['title'],
                        author=news['author'],
                        url=news['url'],
                        comments=news['comments'],
                        points=news['points'])
            s.add(news)
            s.commit()    
    redirect("/news")


@route("/classify")
def classify_news():
    s = session()
    rows_teach = s.query(News).filter(News.label != None).all()
    rows_test = s.query(News).filter(News.label == None).all()
    X_test, y_test = [], []
    X = []
    for el in rows_teach:
        X_test.append(clean(el.title))
        y_test.append(el.label)
    for el in rows_test:
        X.append(clean(el.title))
    model = NaiveBayesClassifier(alpha=0.05)
    model.fit(X_test, y_test)
    result = model.predict(X)
    for i, row in enumerate(rows_test):
        if result[i][1]=="good":
            row.result = 0
        elif result[i][1]=="maybe":
            row.result = 1
        else:
            row.result = 2

    rows_test.sort(key=lambda x: x.result)

    for i, row in enumerate(rows_test):
        print(row.title)
        print(row.result)

    return template('news_template', rows=rows_test)


if __name__ == "__main__":
    run(host="localhost", port=8080)

