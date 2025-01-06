import requests
import re
from tqdm import tqdm

def find_figshare_ndownloader_links(page_url):
    """
    Finds all URLs starting with 'https://figshare.com/ndownloader'
    in the source code of the given webpage.

    Args:
        page_url (str): The URL of the webpage to analyze.

    Returns:
        list: A list of found URLs or an empty list if none are found.
    """
    try:
        # Fetch the webpage's source code
        response = requests.get(page_url)
        response.raise_for_status()  # Check if the request was successful

        # Extract the source code of the webpage
        source_code = response.text

        # Regular expression to find URLs starting with 'https://figshare.com/ndownloader'
        pattern = r"https://figshare\.com/ndownloader[^\s\"']+"
        download_links = re.findall(pattern, source_code)

        # Ensure the result is explicitly returned as a list
        return list(download_links)

    except requests.RequestException as e:
        # Handle errors in fetching the webpage
        print(f"Error fetching the webpage: {e}")
        return []
    

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
    
# example usage
# page_url = "https://figshare.com/articles/dataset/adhd2022/22564390"
# download_links = find_figshare_ndownloader_links(page_url)
# download_links