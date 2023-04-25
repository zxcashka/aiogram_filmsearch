from bs4 import BeautifulSoup
import requests


class Api:
    def __init__(self, s):
        self.s = s
        self.films = self.do_parse()

    def get_html(self):
        s = self.s
        s = s.replace('  ', ' ')
        s = s.replace('  ', ' ')
        s = s.replace(' ', '+')
        search = f"https://www.kinopoisk.ru/index.php?kp_query={s}"
        res = requests.get(search).text
        return res

    def do_parse(self):
        def get_info(s):
            div_right = s.find("div", class_="right")
            rating = div_right.find("div")
            if rating:
                rating = rating.text
            else:
                rating = "нет"

            p_pic = s.find("p", class_="pic")
            a_pic = p_pic.find("a")
            film_id = str(a_pic).split("data-id=")[1].split('"')[1]
            bad_pic_url = f"https://www.kinopoisk.ru/images/sm_film/{film_id}.jpg"

            div_info = s.find("div", class_="info")
            p_name = div_info.find("p", class_="name")
            name = p_name.find("a").text
            year = p_name.find("span").text
            span_s = div_info.find_all("span", class_="gray")
            duration = span_s[0].text.split(',')[-1]
            return {"id": film_id, "name": name, 'rate': rating, "year": year, "duration": duration}

        html = self.get_html()
        soup = BeautifulSoup(html, features="html.parser")
        elements = soup.find_all("div", class_="search_results")
        most_wanted = elements[0].find("div", class_="element most_wanted")
        top5 = elements[1].find_all("div", class_="element")
        films = {}
        i = 0
        films[i] = get_info(most_wanted)
        for data in top5:
            i += 1
            films[i] = get_info(data)
        return films

    def get_info(self):
        return self.films

    def get_pic300x(self, film_id):
        bad_pic_url = f"https://www.kinopoisk.ru/images/sm_film/{film_id}.jpg"
        pic_url = requests.get(bad_pic_url).url.rsplit('/', 1)[0] + "/300x"
        return pic_url