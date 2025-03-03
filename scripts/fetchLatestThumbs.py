import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse

def download_meteor_images():
    """
    Downloads meteor detection images from Global Meteor Network stations.
    Finds images by locating 'Captured thumbnails' text and getting the first linked image after it.
    Preserves original image filenames.
    """
    # Get station codes from user
    print("Enter station codes separated by spaces (e.g., 'hr0001 hr0002 hr0003'): ")
    station_codes = input().strip().split()
    
    # Create downloads directory if it doesn't exist
    download_dir = "meteor_images"
    os.makedirs(download_dir, exist_ok=True)
    
    # Process each station
    for code in station_codes:
        # Convert to uppercase and create URL
        code = code.upper()
        url = f"https://globalmeteornetwork.org/weblog/{code[:2]}/{code}/latest/"
        
        try:
            # Fetch the webpage
            print(f"\nProcessing station {code}...")
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find paragraph starting with "Captured thumbnails"
            captured_p = None
            for p in soup.find_all('p'):
                if p.get_text().strip().startswith('Captured thumbnails'):
                    captured_p = p
                    break
            
            if captured_p:
                # Find first anchor tag after the paragraph
                next_a = captured_p.find_next('a')
                
                if next_a and next_a.get('href'):
                    # Get image URL and download image
                    img_url = next_a['href']
                    if not img_url.startswith('http'):
                        img_url = requests.compat.urljoin(url, img_url)
                    
                    # Extract original filename from URL
                    original_filename = os.path.basename(urlparse(img_url).path)
                    
                    img_response = requests.get(img_url)
                    img_response.raise_for_status()
                    
                    # Save with original filename
                    filepath = os.path.join(download_dir, original_filename)
                    
                    # If file already exists, add station code as prefix
                    if os.path.exists(filepath):
                        filepath = os.path.join(download_dir, f"{code}_{original_filename}")
                    
                    # Save image
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    print(f"Successfully downloaded image for station {code} to {filepath}")
                else:
                    print(f"No image link found after 'Captured thumbnails' for station {code}")
            else:
                print(f"Could not find 'Captured thumbnails' text for station {code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Error downloading from station {code}: {str(e)}")
        except Exception as e:
            print(f"Unexpected error processing station {code}: {str(e)}")

if __name__ == "__main__":
    download_meteor_images()