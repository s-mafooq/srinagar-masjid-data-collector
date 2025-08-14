import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import random
import os
from datetime import datetime
import requests

def setup_driver():
    """Setup Chrome WebDriver using local driver."""
    try:
        print("🚗 Setting up Chrome WebDriver...")
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Use local Chrome driver
        chrome_driver_path = r"C:\DRIVERS\chromedriver.exe"
        print(f"  📂 Using local Chrome driver: {chrome_driver_path}")
        
        if not os.path.exists(chrome_driver_path):
            print(f"❌ Chrome driver not found at: {chrome_driver_path}")
            return None
        
        service = Service(chrome_driver_path)
        
        print("  🔧 Creating driver instance...")
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome WebDriver setup complete")
        return driver
        
    except Exception as e:
        print(f"❌ Chrome WebDriver setup failed: {e}")
        return None

def create_directories():
    """Create necessary directories."""
    directories = {
        'data': 'masjid_data',
        'images': 'masjid_images'
    }
    
    for dir_path in directories.values():
        os.makedirs(dir_path, exist_ok=True)
        print(f"📁 Created directory: {dir_path}")
    
    return directories

def rate_limit():
    """Implement rate limiting to avoid blocking."""
    base_delay = random.uniform(2, 4)
    time.sleep(base_delay)

def validate_coordinates(lat, lng):
    """Validate if coordinates are within Srinagar area."""
    # Srinagar approximate bounds (expanded for comprehensive coverage)
    srinagar_bounds = {
        'min_lat': 33.8, 'max_lat': 34.3,
        'min_lng': 74.6, 'max_lng': 74.9
    }
    
    return (srinagar_bounds['min_lat'] <= lat <= srinagar_bounds['max_lat'] and
            srinagar_bounds['min_lng'] <= lng <= srinagar_bounds['max_lng'])

def is_masjid_related(name):
    """Check if the place is actually a masjid/mosque."""
    masjid_keywords = [
        'masjid', 'mosque', 'مسجد', 'prayer', 'islamic', 'muslim',
        'jama masjid', 'masjid-e', 'masjid al', 'masjid ul',
        'prayer hall', 'prayer room', 'islamic center', 'jamia',
        'dargah', 'shrine', 'khanqah', 'imam bara', 'eidgah'
    ]
    
    text_to_check = name.lower()
    return any(keyword in text_to_check for keyword in masjid_keywords)

def download_masjid_image(image_url, masjid_name, images_dir):
    """Download masjid profile image."""
    try:
        if not image_url:
            return None
        
        # Clean masjid name for filename
        clean_name = re.sub(r'[^\w\s-]', '', masjid_name)
        clean_name = re.sub(r'[-\s]+', '_', clean_name)
        clean_name = clean_name.strip('_')
        
        # Create filename
        filename = f"{clean_name}.jpg"
        filepath = os.path.join(images_dir, filename)
        
        # Download image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"    📸 Image downloaded: {filename}")
        return filename
        
    except Exception as e:
        print(f"    ❌ Error downloading image: {e}")
        return None

def extract_masjid_image(driver):
    """Extract the first profile image of the masjid."""
    try:
        # Look for the profile image using the provided selector
        image_selectors = [
            'div.ZKCDEc img',  # Main profile image
            'button[aria-label*="Photo"] img',  # Photo button image
            'div.RZ66Rb img',  # Alternative selector
            'img[src*="googleusercontent.com"]'  # Google hosted images
        ]
        
        for selector in image_selectors:
            try:
                image_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if image_elements:
                    for img in image_elements:
                        src = img.get_attribute('src')
                        if src and 'googleusercontent.com' in src:
                            return src
            except:
                continue
        
        return None
        
    except Exception as e:
        print(f"    ❌ Error extracting image: {e}")
        return None

def extract_address(driver):
    """Extract address from the masjid page."""
    try:
        address_selectors = [
            'button[data-item-id*="address"]',
            'div[data-item-id*="address"]',
            'span[aria-label*="Address"]',
            'div[aria-label*="Address"]'
        ]
        
        for selector in address_selectors:
            try:
                address_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if address_elements:
                    address = address_elements[0].text.strip()
                    if address and len(address) > 10:
                        return address
            except:
                continue
        
        # Try to find address in page text
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        address_patterns = [
            r'Address[:\s]+([^\n]+)',
            r'Location[:\s]+([^\n]+)',
            r'([A-Za-z\s,]+Srinagar[,\s]+Jammu and Kashmir[,\s]*\d{6})'
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ''
        
    except Exception as e:
        print(f"    ❌ Error extracting address: {e}")
        return ''

def extract_amenities(driver):
    """Extract amenities from the masjid page."""
    try:
        page_text = driver.find_element(By.TAG_NAME, 'body').text.lower()
        
        # Check for common amenities
        amenity_keywords = [
            'parking', 'wifi', 'restroom', 'wheelchair', 'accessible',
            'air conditioning', 'heating', 'prayer room', 'ablution',
            'parking lot', 'street parking', 'free wifi', 'public wifi',
            'ramp', 'elevator', 'braille', 'hearing aid', 'library',
            'madrasa', 'school', 'education', 'community center',
            'carpet', 'fan', 'lighting', 'speaker', 'microphone',
            'water', 'toilet', 'washroom', 'shoes rack', 'clock'
        ]
        
        found_amenities = []
        for keyword in amenity_keywords:
            if keyword in page_text:
                found_amenities.append(keyword.title())
        
        return '; '.join(found_amenities)
        
    except Exception as e:
        print(f"    ❌ Error extracting amenities: {e}")
        return ''

def extract_masjid_data(driver, masjid_name, coordinates, images_dir):
    """Extract comprehensive data for a masjid."""
    
    data = {
        'name': masjid_name,
        'address': '',
        'latitude': coordinates[0],
        'longitude': coordinates[1],
        'amenities': '',
        'image_url': '',
        'image_filename': ''
    }
    
    try:
        # Extract address
        data['address'] = extract_address(driver)
        
        # Extract amenities
        data['amenities'] = extract_amenities(driver)
        
        # Extract and download masjid image
        image_url = extract_masjid_image(driver)
        if image_url:
            data['image_url'] = image_url
            image_filename = download_masjid_image(image_url, masjid_name, images_dir)
            data['image_filename'] = image_filename if image_filename else ''
        
        print(f"  📊 Extracted data:")
        print(f"     Name: {data['name']}")
        print(f"     Address: {data['address'][:50]}..." if data['address'] else "     Address: Not found")
        print(f"     Coordinates: {data['latitude']}, {data['longitude']}")
        print(f"     Amenities: {len(data['amenities'].split('; ')) if data['amenities'] else 0} found")
        print(f"     Image: {'Downloaded' if data['image_filename'] else 'Not found'}")
        
    except Exception as e:
        print(f"  ❌ Error extracting data: {e}")
    
    return data

def scrape_all_srinagar_masjids():
    """Scrape ALL masjids from every corner of Srinagar."""
    
    # Comprehensive search areas covering all of Srinagar
    search_areas = [
        # Central Srinagar
        "Srinagar", "Nowhatta", "Lal Chowk", "Dal Gate", "Boulevard", "Rajbagh",
        "Jawahar Nagar", "Karan Nagar", "Gandhi Nagar", "Zaina Kadal", "Maharaj Ganj",
        
        # North Srinagar
        "Hazratbal", "Nishat", "Shalimar", "Pari Mahal", "Chashme Shahi", "Zadibal",
        "Hawal", "Soura", "Sanat Nagar", "Hyderpora", "Batamaloo",
        
        # South Srinagar
        "Chanapora", "Bemina", "HMT", "Zewan", "Pampore", "Khrew", "Awantipora",
        
        # East Srinagar
        "Pulwama", "Budgam", "Ganderbal",
        
        # Additional areas for comprehensive coverage
        "Alamgari Bazar", "Khawaja Bazar", "Sarai Bala", "Sarai Payeen", "Zadibal",
        "Hawal", "Soura", "Sanat Nagar", "Hyderpora", "Batamaloo", "Chanapora",
        "Bemina", "HMT", "Zewan", "Pampore", "Khrew", "Awantipora", "Pulwama",
        "Budgam", "Ganderbal", "Tral", "Shopian", "Kulgam", "Anantnag", "Bijbehara",
        "Aishmuqam", "Qazigund"
    ]
    
    # Multiple search term variations
    search_variations = [
        "Masjids in {area}",
        "مسجد in {area}",
        "Mosques in {area}",
        "Prayer halls in {area}",
        "Islamic centers in {area}",
        "Prayer rooms in {area}",
        "{area} masjids",
        "{area} مسجد",
        "{area} mosques"
    ]
    
    # Create comprehensive search queries
    search_queries = []
    for area in search_areas:
        for variation in search_variations:
            search_queries.append(variation.format(area=area))
    
    driver = None
    directories = create_directories()
    
    all_masjid_data = []
    processed_urls = set()
    
    try:
        driver = setup_driver()
        if not driver:
            print("❌ Failed to setup Chrome WebDriver")
            return None
        
        print("🗺️ Navigating to Google Maps...")
        driver.get("https://www.google.com/maps")
        time.sleep(5)
        
        # Handle cookie consent
        try:
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept all')]"))
            )
            cookie_button.click()
            time.sleep(2)
            print("✅ Handled cookie consent")
        except:
            print("⚠️ No cookie consent found or already handled")
        
        print(f"🔍 Starting comprehensive masjid search...")
        print(f"📁 Data will be saved to: {directories['data']}")
        print(f"🖼️ Images will be saved to: {directories['images']}")
        
        # Process each search query
        for i, search_query in enumerate(search_queries):
            print(f"\n🔍 Searching for: {search_query} ({i + 1}/{len(search_queries)})")
            
            try:
                # Search for masjids
                search_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "searchboxinput"))
                )
                search_box.clear()
                search_box.send_keys(search_query)
                search_box.send_keys(Keys.RETURN)
                time.sleep(5)
                
                # Rate limiting
                rate_limit()
                
                # Wait for results to load
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
                    )
                except:
                    print(f"  ⚠️ No results found for: {search_query}")
                    continue
                
                # Scroll multiple times to load ALL results
                for scroll in range(5):  # Increased scrolls to get more results
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                
                # Find all masjid links
                links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
                print(f"  📊 Found {len(links)} potential masjid links")
                
                # Process ALL links (no limit)
                for j, link in enumerate(links):
                    try:
                        href = link.get_attribute('href')
                        
                        if not href or href in processed_urls:
                            continue
                        
                        processed_urls.add(href)
                        
                        # Extract coordinates
                        coords = None
                        coords_match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', href)
                        if coords_match:
                            lat, lng = coords_match.groups()
                            coords = (float(lat), float(lng))
                        
                        # Alternative coordinate format
                        if not coords:
                            coords_match = re.search(r'!8m2!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)', href)
                            if coords_match:
                                lat, lng = coords_match.groups()
                                coords = (float(lat), float(lng))
                        
                        if not coords:
                            continue
                        
                        # Validate coordinates
                        if not validate_coordinates(coords[0], coords[1]):
                            continue
                        
                        # Extract name
                        name = None
                        try:
                            name_selectors = [
                                'h3[role="heading"]',
                                'div[role="heading"]',
                                'span[aria-label*="masjid"]',
                                'span[aria-label*="mosque"]'
                            ]
                            
                            for selector in name_selectors:
                                name_elements = link.find_elements(By.CSS_SELECTOR, selector)
                                if name_elements:
                                    name = name_elements[0].text.strip()
                                    if name:
                                        break
                            
                            if not name:
                                place_name = href.split('/place/')[-1].split('/')[0]
                                name = place_name.replace('+', ' ').replace('-', ' ')
                                
                        except Exception as e:
                            continue
                        
                        if not name:
                            continue
                        
                        # Validate if it's actually a masjid
                        if not is_masjid_related(name):
                            continue
                        
                        print(f"  🏛️ Processing: {name}")
                        print(f"    📍 Coordinates: {coords}")
                        
                        # Click on the link to open details
                        try:
                            link.click()
                            time.sleep(3)  # Wait for details to load
                            
                            # Extract data
                            masjid_info = extract_masjid_data(driver, name, coords, directories['images'])
                            
                            # Check if this masjid is already in our data
                            duplicate = False
                            for existing in all_masjid_data:
                                if existing['name'] == name and existing['latitude'] == coords[0] and existing['longitude'] == coords[1]:
                                    duplicate = True
                                    break
                            
                            if not duplicate:
                                all_masjid_data.append(masjid_info)
                                print(f"    ✅ Added new masjid")
                            else:
                                print(f"    ⚠️ Duplicate masjid, skipping")
                            
                            # Rate limiting between masjid processing
                            rate_limit()
                            
                        except Exception as e:
                            print(f"    ❌ Error processing details: {e}")
                            # Still add basic data if not duplicate
                            basic_data = {
                                'name': name,
                                'address': '',
                                'latitude': coords[0],
                                'longitude': coords[1],
                                'amenities': '',
                                'image_url': '',
                                'image_filename': ''
                            }
                            
                            # Check for duplicates
                            duplicate = False
                            for existing in all_masjid_data:
                                if existing['name'] == name and existing['latitude'] == coords[0] and existing['longitude'] == coords[1]:
                                    duplicate = True
                                    break
                            
                            if not duplicate:
                                all_masjid_data.append(basic_data)
                                print(f"    ✅ Added basic data")
                        
                        # Go back to results
                        try:
                            driver.back()
                            time.sleep(2)
                        except:
                            # If back fails, reload the search
                            search_box = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.ID, "searchboxinput"))
                            )
                            search_box.clear()
                            search_box.send_keys(search_query)
                            search_box.send_keys(Keys.RETURN)
                            time.sleep(5)
                        
                    except Exception as e:
                        print(f"    ❌ Error processing link {j}: {e}")
                        continue
                
                # Rate limiting between queries
                rate_limit()
                
            except Exception as e:
                print(f"  ❌ Error processing query '{search_query}': {e}")
                continue
        
        # Create DataFrame and save to CSV
        if all_masjid_data:
            df = pd.DataFrame(all_masjid_data)
            
            # Save to CSV with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"masjid_data/srinagar_masjids_comprehensive_{timestamp}.csv"
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            
            print(f"\n✅ Scraping completed!")
            print(f"📊 Total masjids found: {len(all_masjid_data)}")
            print(f"💾 Data saved to: {csv_filename}")
            
            # Create summary
            print(f"\n📊 SUMMARY:")
            print(f"🏛️ Total Masjids: {len(df)}")
            print(f"📸 Masjids with Images: {len(df[df['image_filename'].notna() & (df['image_filename'] != '')])}")
            print(f"🏗️ Masjids with Amenities: {len(df[df['amenities'].notna() & (df['amenities'] != '')])}")
            print(f"📍 Masjids with Addresses: {len(df[df['address'].notna() & (df['address'] != '')])}")
            
            return df
        else:
            print("❌ No data collected")
            return None
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return None
        
    finally:
        if driver:
            try:
                driver.quit()
                print("🔒 Chrome WebDriver closed")
            except:
                pass

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Masjid Scraper...")
    print("=" * 50)
    print("📋 Will extract: Name, Address, Coordinates, Amenities, Images")
    print("🎯 Target: ALL masjids from every corner of Srinagar")
    print("🚗 Using local Chrome driver: C:\\DRIVERS\\chromedriver.exe")
    print("=" * 50)
    
    df = scrape_all_srinagar_masjids()
    
    if df is not None:
        print("\n🎉 Scraping completed successfully!")
    else:
        print("\n❌ Scraping failed or no data collected") 