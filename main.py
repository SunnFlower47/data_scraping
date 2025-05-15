import os
import requests
from groq import Groq
from flask import Flask, render_template, request
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Ambil API Key dari environment
AI_KEY = os.getenv("AI_KEY")
if not AI_KEY:
    raise ValueError("AI_KEY belum diatur di file .env!")

# Inisialisasi client Groq
client = Groq(
    api_key=AI_KEY,
)


# Fungsi panggil AI
def ai_call(year):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"berikan 1 fakta menarik seputar teknologi pada tahun {year}",
                }
            ],
            model="llama-3-8b-instruct",  # Gunakan model yang tersedia di Groq
            stream=False,
        )

        ai_output = chat_completion.choices[0].message.content
        return ai_output
    except Exception as e:
        print(f"AI Error: {e}")
        return "Maaf, AI tidak tersedia saat ini. Silakan coba lagi nanti."


# Tentukan elemen dan class berdasarkan media
def filtering(media_name):
    if media_name == "kompas":
        return "h1", "hlTitle"
    elif media_name == "detik":
        # Detik headline biasanya ada di <h2> dengan class 'media__title'
        return "h2", "media__title"
    return "", None


def scrape_news(media_name, url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')

        element_name, class_name = filtering(media_name)
        
        if class_name:
            headlines = soup.find_all(element_name, class_=class_name)
        else:
            headlines = soup.find_all(element_name)
        
        if not headlines:
            return ["Tidak ada berita ditemukan."]
        
        news_list = [headline.get_text(strip=True) for headline in headlines if len(headline.get_text(strip=True)) > 20]
        
        return news_list[:10]
    except Exception as e:
        print(f"Error saat scraping {media_name}: {e}")
        return ["Gagal mengambil berita."]


@app.route('/')
def main():
    kompas = scrape_news("kompas", "https://www.kompas.com/")
    detik = scrape_news("detik", "https://www.detik.com/")
    return render_template('index.html', kompas=kompas, detik=detik)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2004)
