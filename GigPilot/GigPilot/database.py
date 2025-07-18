"""
database.py
Module for handling SQLite database operations for job listings.
"""

import sqlite3
from typing import List, Dict, Optional

class JobDatabase:
    def __init__(self, db_path: str = 'data/gigpilot.db'):
        """
        Initialize the database connection and create tables if needed.
        """
        self.db_path = db_path
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._create_tables()
        except sqlite3.Error as e:
            print(f"[FATAL] Could not connect to database: {e}")
            raise

    def _create_tables(self):
        """Create jobs and favorites tables if they do not exist."""
        try:
            with self.conn:
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS jobs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        description TEXT,
                        country TEXT,
                        budget TEXT,
                        skills TEXT,
                        date_posted TEXT,
                        link TEXT UNIQUE,
                        keyword TEXT
                    )
                ''')
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS favorites (
                        job_id INTEGER,
                        FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE
                    )
                ''')
        except sqlite3.Error as e:
            print(f"[ERROR] Error creating tables: {e}")
            raise

    def insert_jobs(self, jobs: List[Dict]):
        """Insert a list of jobs into the database, ignoring duplicates."""
        with self.conn:
            for job in jobs:
                try:
                    self.conn.execute('''
                        INSERT OR IGNORE INTO jobs (title, description, country, budget, skills, date_posted, link, keyword)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        job.get('title', ''),
                        job.get('description', ''),
                        job.get('country', ''),
                        job.get('budget', ''),
                        ','.join(job.get('skills', [])),
                        job.get('date_posted', ''),
                        job.get('link', ''),
                        job.get('keyword', '')
                    ))
                except sqlite3.Error as e:
                    print(f"[ERROR] Error inserting job: {e}")

    def get_jobs(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Query jobs with optional filters (e.g., keyword, country, skill).
        Returns a list of job dicts.
        """
        query = "SELECT * FROM jobs"
        params = []
        if filters:
            clauses = []
            if 'keyword' in filters:
                clauses.append("keyword = ?")
                params.append(filters['keyword'])
            if 'country' in filters:
                clauses.append("country = ?")
                params.append(filters['country'])
            if 'skill' in filters:
                clauses.append("skills LIKE ?")
                params.append(f"%{filters['skill']}%")
            if clauses:
                query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY date_posted DESC"
        try:
            cur = self.conn.cursor()
            cur.execute(query, params)
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
        except sqlite3.Error as e:
            print(f"[ERROR] Error querying jobs: {e}")
            return []

    def get_daily_job_count(self) -> Dict[str, int]:
        """Return a dict of date_posted to job count."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT date_posted, COUNT(*) FROM jobs GROUP BY date_posted")
            return {row[0]: row[1] for row in cur.fetchall()}
        except sqlite3.Error as e:
            print(f"[ERROR] Error getting daily job count: {e}")
            return {}

    def get_skill_frequency(self) -> Dict[str, int]:
        """Return a dict of skill to frequency across all jobs."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT skills FROM jobs")
            skill_count = {}
            for (skills_str,) in cur.fetchall():
                for skill in skills_str.split(','):
                    skill = skill.strip()
                    if skill:
                        skill_count[skill] = skill_count.get(skill, 0) + 1
            return skill_count
        except sqlite3.Error as e:
            print(f"[ERROR] Error getting skill frequency: {e}")
            return {}

    def add_favorite(self, job_id: int):
        """Add a job to favorites."""
        try:
            with self.conn:
                self.conn.execute("INSERT OR IGNORE INTO favorites (job_id) VALUES (?)", (job_id,))
        except sqlite3.Error as e:
            print(f"[ERROR] Error adding favorite: {e}")

    def remove_favorite(self, job_id: int):
        """Remove a job from favorites."""
        try:
            with self.conn:
                self.conn.execute("DELETE FROM favorites WHERE job_id = ?", (job_id,))
        except sqlite3.Error as e:
            print(f"[ERROR] Error removing favorite: {e}")

    def get_favorites(self) -> List[Dict]:
        """Return a list of favorited jobs."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT jobs.* FROM jobs
                JOIN favorites ON jobs.id = favorites.job_id
                ORDER BY date_posted DESC
            """)
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
        except sqlite3.Error as e:
            print(f"[ERROR] Error getting favorites: {e}")
            return []
