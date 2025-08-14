import pandas as pd
import re
import unicodedata

def clean_text(text):
    """Remove emojis, symbols, and clean text."""
    if pd.isna(text) or text == '':
        return ''
    
    # Convert to string if not already
    text = str(text)
    
    # Remove emojis and symbols
    # Remove unicode characters that are not basic letters, numbers, or common punctuation
    cleaned = ''
    for char in text:
        if unicodedata.category(char) in ['Ll', 'Lu', 'Nd', 'Zs', 'Po', 'Pd']:  # Letters, numbers, spaces, punctuation
            cleaned += char
        elif char in '.,;:!?()[]{}"\'-/\\':  # Common punctuation
            cleaned += char
    
    # Remove extra whitespace and newlines
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()
    
    # Remove common unwanted patterns
    cleaned = re.sub(r'stars?', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'reviews?', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Write a review', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Add.*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Claim this business', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Suggest an edit', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Add missing information', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Add place.*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Tours & Activities', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'About these results', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Gives you more ways.*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Staybook.*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Local Guide.*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'More reviews.*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'People also search for', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Like', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Share', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'More', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Overview', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Reviews', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'About', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Directions', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Save', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Nearby', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Send to phone', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Sort', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'All', '', cleaned, flags=re.IGNORECASE)
    
    # Remove numbers in parentheses (like review counts)
    cleaned = re.sub(r'\(\d+\)', '', cleaned)
    
    # Remove extra whitespace again
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned

def clean_masjid_data(input_file, output_file):
    """Clean the masjid data CSV file."""
    print(f"Reading data from: {input_file}")
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    print(f"Original data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Clean each text column
    text_columns = ['name', 'rating', 'review_count', 'address', 'phone', 'website', 
                   'hours', 'category', 'description', 'services', 'amenities', 
                   'accessibility_features', 'prayer_times', 'historical_info', 
                   'school_of_thought', 'detailed_address', 'city', 'state']
    
    for col in text_columns:
        if col in df.columns:
            print(f"Cleaning column: {col}")
            df[col] = df[col].apply(clean_text)
    
    # Remove rows where name is empty or just whitespace
    df = df[df['name'].str.strip() != '']
    
    # Remove duplicate rows based on name and coordinates
    df = df.drop_duplicates(subset=['name', 'latitude', 'longitude'])
    
    # Select only essential columns for clean output
    essential_columns = [
        'name', 'latitude', 'longitude', 'address', 'phone', 'website',
        'hours', 'prayer_times', 'school_of_thought', 'amenities',
        'historical_info', 'city', 'state', 'search_area', 'image_url', 'image_filename'
    ]
    
    # Keep only columns that exist in the dataframe
    available_columns = [col for col in essential_columns if col in df.columns]
    df_clean = df[available_columns]
    
    # Save cleaned data
    df_clean.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"Cleaned data shape: {df_clean.shape}")
    print(f"Cleaned data saved to: {output_file}")
    
    # Show sample of cleaned data
    print("\nSample of cleaned data:")
    print(df_clean.head(3).to_string())
    
    return df_clean

if __name__ == "__main__":
    input_file = "masjid_data/comprehensive_masjids_20250730_201738.csv"
    output_file = "masjid_data/clean_masjid_data.csv"
    
    clean_df = clean_masjid_data(input_file, output_file)
    print(f"\n✅ Clean CSV file created: {output_file}") 