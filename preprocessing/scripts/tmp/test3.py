import requests
import re

def find_figshare_ndownloader_links(page_url):
    """
    Znajduje wszystkie URL-e zaczynające się od 'https://figshare.com/ndownloader'
    w kodzie źródłowym podanej strony.

    Args:
        page_url (str): URL strony, której kod źródłowy ma zostać przeanalizowany.

    Returns:
        list: Lista znalezionych URL-i lub pusta lista, jeśli brak wyników.
    """
    try:
        # Pobierz kod źródłowy strony
        response = requests.get(page_url)
        response.raise_for_status()  # Sprawdź, czy żądanie się powiodło

        # Kod źródłowy strony
        source_code = response.text

        # Regex do wyszukiwania URL-i zaczynających się od 'https://figshare.com/ndownloader'
        pattern = r"https://figshare\.com/ndownloader[^\s\"']+"
        download_links = re.findall(pattern, source_code)

        return download_links

    except requests.RequestException as e:
        print(f"Błąd przy pobieraniu strony: {e}")
        return []

import requests
from tqdm import tqdm

def download_file_with_progress(file_url, save_path):
    """
    Downloads a file from the given URL with a progress bar and saves it to the specified location.

    Args:
        file_url (str): The URL of the file to download.
        save_path (str): The local path where the file will be saved.

    Returns:
        bool: True if the file was successfully downloaded, False otherwise.
    """
    try:
        # Send a GET request to the file URL
        response = requests.get(file_url, stream=True)
        response.raise_for_status()  # Check for HTTP request errors

        # Get the total file size from headers
        total_size = int(response.headers.get('content-length', 0))

        # Open the file in write-binary mode and download with progress bar
        with open(save_path, "wb") as file, tqdm(
            desc=f"Downloading {save_path}",
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=8192):
                # Write each chunk to the file
                file.write(chunk)
                # Update the progress bar
                progress_bar.update(len(chunk))
        
        print(f"\nFile downloaded successfully and saved to {save_path}")
        return True

    except requests.RequestException as e:
        # Print an error message if the download fails
        print(f"Error downloading the file: {e}")
        return False

# Example usage
file_url = "https://figshare.com/ndownloader/articles/22564390/versions/1"  # Replace with the actual download link
save_path = "downloaded_file.zip"  # Replace with your desired file name and path


# Przykład użycia
page_url = "https://figshare.com/articles/dataset/adhd2022/22564390"
links = find_figshare_ndownloader_links(page_url)

if links:
    print("Znalezione linki do pobrania:")
    for link in links:
        print(link)
else:
    print("Nie znaleziono linków do pobrania.")


if download_file_with_progress(file_url, save_path):
    print("Download completed.")
else:
    print("Download failed.")   