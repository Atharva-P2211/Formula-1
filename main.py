import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
from difflib import get_close_matches

#Race name mapping
RACE_MAPPING = { 
                
    'abu dhabi': 'abu-dhabi-grand-prix',
    'australia': 'australian-grand-prix',
    'australian': 'australian-grand-prix',
    'austria': 'austrian-grand-prix',
    'austrian': 'austrian-grand-prix',
    'azerbaijan': 'azerbaijan-grand-prix',
    'bahrain': 'bahrain-grand-prix',
    'belgium': 'belgian-grand-prix',
    'belgian': 'belgian-grand-prix',
    'spa': 'belgian-grand-prix',
    'brazil': 'sao-paulo-grand-prix',
    'brazilian': 'sao-paulo-grand-prix',
    'sao paulo': 'sao-paulo-grand-prix',
    'canada': 'canadian-grand-prix',
    'canadian': 'canadian-grand-prix',
    'china': 'chinese-grand-prix',
    'chinese': 'chinese-grand-prix',
    'emilia romagna': 'emilia-romagna-grand-prix',
    'imola': 'emilia-romagna-grand-prix',
    'britain': 'british-grand-prix',
    'british': 'british-grand-prix',
    'silverstone': 'british-grand-prix',
    'hungary': 'hungarian-grand-prix',
    'hungarian': 'hungarian-grand-prix',
    'italy': 'italian-grand-prix',
    'italian': 'italian-grand-prix',
    'monza': 'italian-grand-prix',
    'japan': 'japanese-grand-prix',
    'japanese': 'japanese-grand-prix',
    'suzuka': 'japanese-grand-prix',
    'las vegas': 'las-vegas-grand-prix',
    'vegas': 'las-vegas-grand-prix',
    'mexico': 'mexico-city-grand-prix',
    'mexican': 'mexico-city-grand-prix',
    'mexico city': 'mexico-city-grand-prix',
    'miami': 'miami-grand-prix',
    'monaco': 'monaco-grand-prix',
    'netherlands': 'dutch-grand-prix',
    'dutch': 'dutch-grand-prix',
    'zandvoort': 'dutch-grand-prix',
    'qatar': 'qatar-grand-prix',
    'saudi arabia': 'saudi-arabian-grand-prix',
    'saudi': 'saudi-arabian-grand-prix',
    'jeddah': 'saudi-arabian-grand-prix',
    'singapore': 'singapore-grand-prix',
    'spain': 'spanish-grand-prix',
    'spanish': 'spanish-grand-prix',
    'barcelona': 'spanish-grand-prix',
    'usa': 'united-states-grand-prix',
    'us': 'united-states-grand-prix',
    'united states': 'united-states-grand-prix',
    'austin': 'united-states-grand-prix',
    'cota': 'united-states-grand-prix',}

def extract_year(user_input):
    """Extract 4-digit year from user input."""
    year_match = re.search(r'\b(20\d{2})\b', user_input)
    if year_match:
        return year_match.group(1)
    
    
    
def normalize_race_name(user_input, year=None):
    # Remove year if present
    if year:
        user_input = user_input.replace(year, '')
    
    # Convert to lowercase and strip
    normalized = user_input.lower().strip()
    
    # Remove common unnecessary words
    words_to_remove = ['grand prix', 'gp', 'formula 1', 'f1', 'the', 'race']
    for word in words_to_remove:
        normalized = normalized.replace(word, '')
        
    # Clean up extra spaces
    normalized = ' '.join(normalized.split())
    
    return normalized

def find_race_url(user_input):
    # Extract year
    year = extract_year(user_input)
    
    if not year:
        print("No year found in input. Please include a year (e.g., 2023, 2024)")
        return None
    
    
        # Normalize race name
    race_name = normalize_race_name(user_input, year)
    
    if not race_name:
        print("Could not identify race name. Please try again.")
        return None
    
    # Try exact match first
    if race_name in RACE_MAPPING:
        race_url = RACE_MAPPING[race_name]
        return f"https://pitwall.app/races/{year}-{race_url}"
    
    
    
        # Try fuzzy matching
    close_matches = get_close_matches(race_name, RACE_MAPPING.keys(), n=3, cutoff=0.6)
    
    if close_matches:
        print(f"\n Did you mean one of these?")
        for i, match in enumerate(close_matches, 1):
            print(f"{i}. {match.title()} {year}")
        
        choice = input("\nEnter number (or 0 to cancel): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(close_matches):
            selected_race = close_matches[int(choice) - 1]
            race_url = RACE_MAPPING[selected_race]
            return f"https://pitwall.app/races/{year}-{race_url}"
    
    print(f"Could not find race matching '{race_name}' in {year}")
    return None

def scrape_race_results(url):
    """Scrape race results from the given URL"""
    print(f"\n Fetching data from: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("Data fetched successfully!")
        print("Note: You need to implement the actual HTML parsing based on the website structure")
        
        # Placeholder data structure
        data = {
            'Position': [],
            'Driver': [],
            'Constructor': [],
            'Time/Retired': [],
            'Grid': [],
            'Laps': [],
            'Points': []
        }
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None




    

 
    


                



