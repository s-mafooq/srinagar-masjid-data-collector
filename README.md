🕌 Srinagar Masjid Data Collector
Python + Selenium web scraper for collecting masjid/mosque data from Google Maps focused on Srinagar, India.
Automatically captures names, addresses, coordinates, amenities, and profile images — saving them into organized timestamped CSVs and image folders.



[Python](https://img.shields.io/badge/Python-3.
MIT(https://img.shields.io/badge/License-MIT-green.svgaping]
(https://img.shields.io/badge/Tool-Web%20Scraper Features)

Accurate data extraction — names, coordinates, addresses

Basic location validation — checks within Srinagar bounds

Optional amenities parsing — detects features from listing text

Profile images — downloads first visible image if available

Error handling & gentle rate limiting for stability

📦 Installation
Prerequisites
Python 3.8+

Google Chrome installed

ChromeDriver available locally (default path: C:\DRIVERS\chromedriver.exe)

### Setup

1. Clone the project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the scraper:
```bash
python masjid_scraper.py
```

What it does:
- Opens Google Maps and runs comprehensive searches across Srinagar areas
- Extracts: name, address (when available), latitude/longitude, amenities (when detectable), and tries to download a profile image
- Saves data with a timestamped CSV under `masjid_data/`
- Saves images (if any) under `masjid_images/`

Example outputs:
- `masjid_data/srinagar_masjids_comprehensive_YYYYMMDD_HHMMSS.csv`
- `masjid_images/<Masjid_Name>.jpg`

### Clean an existing CSV (optional)
Use the cleaner to remove noise and standardize text:
```bash
python clean_masjid_data.py
```
Adjust the `input_file` and `output_file` variables inside `clean_masjid_data.py` as needed.


📝 Notes
Update Chromedriver path in `masjid_scraper.py` if different from `C:\DRIVERS\chromedriver.exe`

`.gitignore` excludes all generated CSVs/images to keep repo lightweight
(commit sample data if needed)

Respect Google Maps Terms of Service


📜 License

MIT License © 2025 Shiekh Mafooq
This tool is for educational purposes only — use responsibly.

