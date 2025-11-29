import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from difflib import get_close_matches
from datetime import datetime
import json
import time
# Race name mapping 
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
    'cota': 'united-states-grand-prix',
}


def extract_year(user_input):
    """Extract 4-digit year from user input"""
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', user_input)
    if year_match:
        year = year_match.group(1)
        current_year = datetime.now().year
        if 1950 <= int(year) <= current_year:
            return year
        else:
            print(f" Year {year} is out of valid F1 range (1950-{current_year})")
    return None


def normalize_race_name(user_input, year=None):
    """Clean and normalize race name from user input"""
    if year:
        user_input = user_input.replace(year, '')
    
    normalized = user_input.lower().strip()
    
    words_to_remove = ['grand prix', 'gp', 'formula 1', 'f1', 'the', 'race', 'prix']
    for word in words_to_remove:
        normalized = re.sub(rf'\b{word}\b', '', normalized)
    
    normalized = re.sub(r'[^\w\s-]', '', normalized)
    normalized = ' '.join(normalized.split())
    
    return normalized


def find_race_url(user_input):
    """Parse user input and return the race URL"""
    year = extract_year(user_input)
    
    if not year:
        print("No valid year found. Please include a year (e.g., 2023, 2024)")
        return None, None, None
    
    race_name = normalize_race_name(user_input, year)
    
    if not race_name:
        print("Could not identify race name. Please try again.")
        return None, None, None
    
    if race_name in RACE_MAPPING:
        race_url = RACE_MAPPING[race_name]
        full_url = f"https://pitwall.app/races/{year}-{race_url}"
        return full_url, year, race_name
    
    close_matches = get_close_matches(race_name, RACE_MAPPING.keys(), n=5, cutoff=0.5)
    
    if close_matches:
        print(f"\nDid you mean one of these?")
        for i, match in enumerate(close_matches, 1):
            print(f"   {i}. {match.title()} {year}")
        
        try:
            choice = input("\n  Enter number (or 0 to cancel): ").strip()
            
            if choice == '0':
                return None, None, None
            
            if choice.isdigit() and 1 <= int(choice) <= len(close_matches):
                selected_race = close_matches[int(choice) - 1]
                race_url = RACE_MAPPING[selected_race]
                full_url = f"https://pitwall.app/races/{year}-{race_url}"
                return full_url, year, selected_race
        except (ValueError, IndexError):
            print("Invalid choice")
            return None, None, None
    
    print(f"Could not find race matching '{race_name}' in {year}")
    return None, None, None


def scrape_race_results(url, year, race_name):
    """Scrape race results from the given URL"""
    print(f"\n Fetching data from: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            'Position': [],
            'Driver': [],
            'Constructor': [],
            'Time/Retired': [],
            'Grid': [],
            'Laps': [],
            'Points': []
        }
        
        # to find the results table
        table = None
        possible_selectors = [
            ('table', {'class': 'race-results'}),
            ('table', {'class': 'results'}),
            ('div', {'class': 'race-results'}),
            ('div', {'class': 'results-table'}),
            ('table', {}),
        ]
        
        for tag, attrs in possible_selectors:
            table = soup.find(tag, attrs)
            if table:
                print(f" Found results table using {tag}")
                break
        
        if not table:
            print("  Could not find results table on the page")
            print(" The website structure may have changed or data is not available")
            return data
        
        rows = table.find_all('tr')
        
        if len(rows) <= 1:
            print("  No race data found in table")
            return data
        
        # Parse each row
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            
            if len(cells) < 7:
                continue
            
            try:
                position = cells[0].get_text(strip=True)
                driver = cells[1].get_text(strip=True)
                constructor = cells[2].get_text(strip=True)
                time_retired = cells[3].get_text(strip=True)
                grid = cells[4].get_text(strip=True)
                laps = cells[5].get_text(strip=True)
                points = cells[6].get_text(strip=True)
                
                data['Position'].append(position)
                data['Driver'].append(driver)
                data['Constructor'].append(constructor)
                data['Time/Retired'].append(time_retired)
                data['Grid'].append(grid)
                data['Laps'].append(laps)
                data['Points'].append(points)
                
            except (IndexError, AttributeError) as e:
                continue
        
        if len(data['Position']) > 0:
            print(f" Successfully scraped {len(data['Position'])} race results!")
        else:
            print("  No data extracted. Website structure may be different than expected.")
        
        return data
        
    except requests.exceptions.Timeout:
        print("Request timed out. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        print("Connection error. Check your internet connection.")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f" Race not found at this URL.")
        else:
            print(f" HTTP Error: {e.response.status_code}")
        return None
    except Exception as e:
        print(f" Unexpected error: {e}")
        return None


def create_excel(data, filename):
    """Create Excel file from race data"""
    if not data:
        print("No data to export")
        return False
    
    if not data.get('Position') or len(data['Position']) == 0:
        print("No race results to export")
        return False
    
    try:
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"Excel file created: {filename}")
        print(f" Total rows: {len(df)}")
        return True
    except Exception as e:
        print(f"Error creating Excel file: {e}")
        return False


def create_csv(data, filename):
    """Create CSV file from race data"""
    if not data or len(data.get('Position', [])) == 0:
        print(" No data to export")
        return False
    
    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f" CSV file created: {filename}")
        return True
    except Exception as e:
        print(f" Error creating CSV file: {e}")
        return False


def main():
    """Main function to run the program"""
    print("=" * 70)
    print(" F1 RACE RESULTS SCRAPER")
    print("=" * 70)
    print("\n Examples of input:")
    print("  • '2024 Monaco GP'")
    print("  • 'Las Vegas 2023'")
    print("  • 'Brazilian Grand Prix 2024'")
    print("  • 'Sao Paulo 2023'")
    print("=" * 70)
    
    try:
        while True:
            print("\n" + "-" * 70)
            user_input = input("\nEnter race details (or 'quit' to exit): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n Thank you for using F1 Race Results Scraper!")
                break
            
            if not user_input:
                print(" Please enter something!")
                continue
            
            # Find the race URL
            url, year, race_name = find_race_url(user_input)
            
            if not url:
                continue
            
            # Scrape the data
            race_data = scrape_race_results(url, year, race_name)
            
            if race_data and len(race_data.get('Position', [])) > 0:
                # Ask for export format
                print("\n Choose export format:")
                print("  1. Excel (.xlsx)")
                print("  2. CSV (.csv)")
                print("  3. Both formats")
                
                export_choice = input("\n Select format (1-3): ").strip()
                
                # Create safe filename
                safe_race_name = race_name.replace(' ', '_').replace('/', '-')
                base_filename = f"{year}_{safe_race_name}"
                
                if export_choice == '1':
                    create_excel(race_data, f"{base_filename}.xlsx")
                elif export_choice == '2':
                    create_csv(race_data, f"{base_filename}.csv")
                elif export_choice == '3':
                    create_excel(race_data, f"{base_filename}.xlsx")
                    create_csv(race_data, f"{base_filename}.csv")
                else:
                    print(" Invalid choice, defaulting to Excel")
                    create_excel(race_data, f"{base_filename}.xlsx")
            else:
                print("\nNo data was scraped. Cannot create file.")
            
            # Ask if user wants to continue
            print()
            another = input(" Scrape another race? (yes/no): ").strip().lower()
            if another not in ['yes', 'y']:
                print("\n Thank you for using F1 Race Results Scraper!")
                break
    
    except KeyboardInterrupt:
        print("\n\n Program interrupted. Goodbye!")
    except Exception as e:
        print(f"\n Fatal error: {e}")


if __name__ == "__main__":
    main()