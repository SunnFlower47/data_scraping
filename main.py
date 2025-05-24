import os
import requests
from flask import Flask, render_template, request
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


# Tentukan elemen dan class berdasarkan media
def filtering(media_name):
    if media_name == "kompas":
        return "h1", "hlTitle"
    elif media_name == "detik":
        return "h2", "media__title"
    return "", None


def scrape_news(media_name, url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        news_list = []

        if media_name == "kompas":
            # Struktur: <div class="hlItem"><a href="..."><h1 class="hlTitle">Judul</h1></a></div>
            items = soup.find_all('div', class_='hlItem')
            for item in items:
                a_tag = item.find('a', href=True)
                h1_tag = a_tag.find('h1', class_='hlTitle') if a_tag else None
                if a_tag and h1_tag:
                    title_text = h1_tag.get_text(strip=True)
                    link = a_tag['href']
                    news_list.append({"title": title_text, "link": link})

        elif media_name == "detik":
            # Struktur: <h2 class="media__title"><a href="...">Judul</a></h2>
            headlines = soup.find_all("h2", class_="media__title")
            for headline in headlines:
                link_tag = headline.find('a', href=True)
                if link_tag:
                    title = link_tag.get_text(strip=True)
                    link = link_tag['href']
                    news_list.append({"title": title, "link": link})

        if not news_list:
            return [{"title": "Tidak ada berita ditemukan.", "link": "#"}]

        return news_list[:10]

    except Exception as e:
        print(f"Error saat scraping {media_name}: {e}")
        return [{"title": "Gagal mengambil berita.", "link": "#"}]



@app.route('/')
def main():
    kompas = scrape_news("kompas", "https://www.kompas.com/")
    detik = scrape_news("detik", "https://www.detik.com/")
    return render_template('index.html', kompas=kompas, detik=detik)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2004)
