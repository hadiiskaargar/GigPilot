# 🧠 GigPilot: Freelance Job Scraper for Freelancer.com

&#x20;&#x20;

GigPilot is a simple yet powerful freelance job scraper and dashboard designed specifically for [Freelancer.com](https://www.freelancer.com/). It fetches freelance job listings based on keywords and visualizes them in a dashboard for quick filtering and analysis.

---

## 🚀 Features

- 🔍 Keyword-based job scraping from Freelancer.com
- 📊 Interactive dashboard with Streamlit
- 🧠 Skill/tag extraction from job data
- 📁 SQLite database storage

---

## ⚙️ How to Use

### 1. Activate virtual environment

```bash
source venv/bin/activate
```

### 2. Run the scraper

```bash
python scraper.py
```

- Enter keywords when prompted (e.g., `web scraping, automation, data entry`)
- Jobs will be saved in `jobs.db`

### 3. Launch the dashboard

```bash
streamlit run dashboard.py
```

- View and explore scraped jobs in your browser

---

## 🧰 Tech Stack

- **Python 3.9+**
- **Requests** — for sending HTTP requests
- **BeautifulSoup** — for parsing HTML
- **SQLite3** — for local database storage
- **Pandas** — for data manipulation
- **Streamlit** — for creating the interactive dashboard

---

## 📸 Screenshot



---

## 📂 Project Structure

```
GigPilot/
├── data/                     # Optional CSV output
├── dashboard.py             # Streamlit dashboard
├── database.py              # Database handler
├── scraper.py               # Main scraper
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 🤛‍♂️ Author

**Hadis Kargar** — [GitHub](https://github.com/hadiiskaargar)

Feel free to ⭐️ the repo if you find it useful! PRs and issues welcome!

