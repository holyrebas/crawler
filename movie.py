from urllib.request import urlopen
import urllib.error
from bs4 import BeautifulSoup
from multiprocessing import Process
from multiprocessing import Manager
import re


def get_rotten(title, year, ret):
    if ":_" in title:
        title = title.replace(":_", "_")
    if "_:_" in title:
        title = title.replace("_:_", "_")
    if "_-_" in title:
        title = title.replace("_-_", "_")
    if ",_" in title:
        title = title.replace(",_", "_")
    if "'" in title:
        title = title.replace("'", "")
    if "." in title:
        title = title.replace(".", "")
    if "~" in title:
        title = title.replace("~", "")
    url = ["https://www.rottentomatoes.com/m/" + title,
           "https://www.rottentomatoes.com/m/" + title + "_" + str(year)]
    for i in range(2):
        try:
            html = urlopen(url[i])
        except urllib.error.HTTPError as e:
            pass
        except UnicodeEncodeError as f:
            pass
        else:
            rotten = BeautifulSoup(html, "html.parser")
            tomato = rotten.find("span", {"class": "meter-value"})
            if tomato:
                ret['rotten'] = " ▪ Tomato: " + tomato.get_text()
                return


def get_naver(title, year, ret):
    try:
        html = urlopen("https://movie.naver.com/movie/search/result.nhn?section=movie&query=" + title)
    except urllib.error.HTTPError as e:
        pass
    except UnicodeEncodeError as f:
        pass
    else:
        naver_page = BeautifulSoup(html, "html.parser")
        for naver in naver_page.findAll("dl"):
            for y in naver.findAll("a"):
                if y.get_text() == year:
                    star = naver.find("em", {"class": "num"})
                    if star:
                        ret['naver'] = " ▪ Naver: " + star.get_text()
                        return


def get_watcha(title, year, ret):
    try:
        html = urlopen("https://watcha.com/search?query=" + title)
    except urllib.error.HTTPError as e:
        pass
    except UnicodeEncodeError as f:
        pass
    else:
        watcha_page = BeautifulSoup(html, "html.parser")
        for watcha in watcha_page.findAll("li", {"class":"StackableListItem-s18nuw36-0"}):
            y = watcha.find("div",{"class": "SearchResultItemForContent__ResultExtraInfo-s1phcxqf-0"})
            if y:
                if str(year) in y.get_text():
                    next_link = watcha.find("a", {"class": "InnerPartOfListWithImage__LinkSelf-s11a1hqv-1"}).attrs[
                        'href']
                    try:
                        next_html = urlopen("https://watcha.com/ko-KR/" + next_link)
                    except urllib.error.HTTPError as e:
                        pass
                    else:
                        next_page = BeautifulSoup(next_html, "html.parser")
                        star = next_page.find("div", {"class": "ContentJumbotron__ContentRatings-yf8npk-16"})
                        ret['watcha'] = " ▪ Watcha: " + star.get_text()[4:7]
                        return


def get_movie(key):
    cnt = 0
    html = urlopen("https://www.imdb.com/search/title?title="+key+"&title_type=feature")
    print("# Now Loading...\n")
    imdb_page = BeautifulSoup(html, "html.parser")
    for movie in imdb_page.findAll("div", {"class": "lister-item"}):
        title = movie.find("img", {"class": "loadlate"})
        year = movie.find("span", {"class": "lister-item-year"})
        grade = movie.find("span", {"class": "certificate"})
        runtime = movie.find("span", {"class": "runtime"})
        genre = movie.find("span", {"class": "genre"})
        direct = movie.findAll("a", href=re.compile("li_dr"))
        act = movie.findAll("a", href=re.compile("li_st"))
        rating = movie.find("strong")
        metascore = movie.find("span", {"class": "metascore"})

        if year and grade and runtime and genre:
            manager = Manager()
            ret = manager.dict()
            procs = []
            procs.append(Process(target=get_rotten, args=(title['alt'].replace(" ", "_"), year.get_text()[1:5], ret)))
            procs.append(Process(target=get_naver, args=(title['alt'].replace(" ", "+"), year.get_text()[1:5], ret)))
            procs.append(Process(target=get_watcha, args=(title['alt'].replace(" ", "+"), year.get_text()[1:5], ret)))
            for p in procs:
                p.start()
            for p in procs:
                p.join()

            print(title['alt'], end=" ")
            print(year.get_text())
            print("[ " + grade.get_text(), end=" | ")
            print(runtime.get_text(), end=" | ")
            print(genre.get_text().strip() + " ]")

            if direct and act:
                print("[ ", end="")
                for i in range(len(direct)):
                    if i < len(direct)-1:
                        print(direct[i].get_text(), end=", ")
                    else:
                        print(direct[i].get_text(), end=" | ")
                for i in range(len(act)):
                    if i < len(act)-1:
                        print(act[i].get_text(), end=", ")
                    else:
                        print(act[i].get_text() + " ]")

            if rating: print(" ▪ IMDb: " + rating.get_text())
            if metascore: print(" ▪ Meta: " + metascore.get_text().strip())
            if ret.get('rotten'): print(ret['rotten'])
            if ret.get('naver'): print(ret['naver'])
            if ret.get('watcha'): print(ret['watcha'])

            cnt += 1
            print()

    return cnt


keyword = input()
print("# Searching [ " + keyword + " ]")
result = get_movie(keyword.replace(" ", "+"))

if result == 0:
    print("# Not founded.")
elif result == 1:
    print("# 1 movie founded.")
else:
    print("#", result , "movies founded.")
