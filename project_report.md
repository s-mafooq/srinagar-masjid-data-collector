
# MASJID DATA SCRAPING PROJECT REPORT

## Project Overview
This project scrapes data about masjids in Srinagar from Google Maps, including:
- Basic information (names, addresses)
- Geographic coordinates
- Basic amenities (when detectable)
- Profile images (when downloadable)

## Files Created
1. **CSV Files:**
   - `masjid_data/srinagar_masjids_comprehensive_YYYYMMDD_HHMMSS.csv` — Main dataset with timestamp

2. **JSON Files (existing data snapshots):**
   - `masjid_data/detailed_masjid_data.json`
   - `masjid_data/final_masjid_data.json`

3. **Directories:**
   - `masjid_data/` — CSV and JSON data
   - `masjid_images/` — Downloaded images
   - `reports/` — Project reports

## Data Extracted
- **Names:** Masjid names
- **Coordinates:** Latitude and longitude
- **Addresses:** When available
- **Amenities:** Detected via page text (best-effort)
- **Images:** First available profile image (best-effort)

## Technical Implementation
- **Selenium WebDriver:** Automated browser control
- **Pandas:** Data manipulation and export
- **Requests:** Image downloads

## Challenges and Solutions
1. **Dynamic Google Maps UI:** Used multiple selectors and waits
2. **Amenity Detection:** Simple keyword scan on page text
3. **Rate Limiting:** Randomized delays between actions

## Future Improvements
1. Robust image extraction using different flows/APIs
2. Stronger amenity categorization and normalization
3. Reverse geocoding for address verification
4. Map visualization of results
5. Real-time updates/incremental scraping

## Usage
- `masjid_scraper.py` — Main scraper
- `clean_masjid_data.py` — Optional CSV cleaner

## Data Quality
- **Accuracy:** Best-effort extraction from Google Maps
- **Completeness:** Varies per listing
- **Consistency:** Structured CSV output

This project provides a solid baseline for masjid data collection and can be extended for other regions.
