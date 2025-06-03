# 🚗 Vehicle Scraper API with FastAPI

This FastAPI app scrapes vehicle inventory data from [Pujols Auto Sale](https://www.pujolsautosale.com) using pagination. It extracts vehicle JSONP URLs from paginated HTML pages and parses the vehicle data into structured JSON.

---

## 📦 Features

- Input total vehicle count and pagination dynamically via POST body
- Parses JSONP vehicle data (from embedded scripts)
- Handles retry logic for robust scraping
- FastAPI endpoint returns full vehicle data in JSON

---

## 🛠 Requirements

Install dependencies:

```bash
pip install -r requirements.txt

uvicorn main:app --host 0.0.0.0 --port 5000

ngrok http 5000
