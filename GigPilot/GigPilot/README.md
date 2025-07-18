# GigPilot - Freelancer Job Scraper

GigPilot is a Python project that scrapes freelance job listings from [freelancer.com](https://www.freelancer.com/) based on a list of keywords and provides a Streamlit dashboard for searching, filtering, and analyzing jobs.

## Features
- Scrape Freelancer.com jobs by keyword (up to 2 pages per keyword)
- Extract job title, short description, client location, budget/hourly rate, required skills, and job link
- Store jobs in a local SQLite database (`jobs.db`)
- Streamlit dashboard for:
  - Searchable, filterable job table (filter by keyword, country, budget, or skill)
  - Daily new job count
  - Bar chart of job count by keyword or skill
  - Mark/save favorite jobs
  - Real-time updates as new jobs are scraped

## Installation

1. Clone the repository or copy the project files.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Scrape Jobs
Run the scraper from the command line, providing keywords as arguments or via prompt:
```bash
python -m GigPilot.scraper python developer
```
Or, run and enter keywords when prompted:
```bash
python -m GigPilot.scraper
```

### Launch Dashboard
Start the Streamlit dashboard:
```bash
streamlit run GigPilot/dashboard.py
```

## Supported Python Version
- Python 3.8+

## Dependencies
- requests
- beautifulsoup4
- pandas
- streamlit
- urllib3

(Do not include `sqlite3` as it is part of the Python standard library.)

## License
MIT 