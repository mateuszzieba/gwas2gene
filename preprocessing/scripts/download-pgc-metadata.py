import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

import preprocessing.src.pgc_gwas_analysis as pgc

# URL strony z danymi
url = "https://pgc.unc.edu/for-researchers/download-results/"

# Pobranie zawartości strony
response = requests.get(url)

# Sprawdzenie poprawności żądania
if response.status_code == 200:
    # Parsowanie HTML za pomocą BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Znalezienie tabel na stronie
    tables = soup.find_all('table')
    
    # Sprawdzenie, czy są dostępne jakieś tabele
    if len(tables) > 0:
        # Konwersja pierwszej tabeli na DataFrame
        table = tables[0]  # Wybór pierwszej tabeli
        df = pd.read_html(str(table))[0]  # Konwersja tabeli HTML na DataFrame
        
        # Wyświetlenie podglądu danych
        print(df)
    else:
        print("Nie znaleziono tabel na stronie.")
else:
    print(f"Nie udało się pobrać strony. Kod statusu: {response.status_code}")


# remove rows where first and second column are the same
df = df[df['Data DOI'] != df['publication']]

df['link_folder'] = 'https://figshare.com/articles/dataset/'

# in publication column replace adhd2018_SexSpecific by adhd2018SexSpecific
df['publication'] = df['publication'].str.replace('_','')

# add to link_folder column publication 
df['link_folder'] = df['link_folder'] + df['publication']

# create new column number_DOI with removing 10.6084/m9.figshare. from Data DOI`
df['number_DOI'] = df['Data DOI'].str.replace('10.6084/m9.figshare.','')

# replace 10.7488/ds/2458 in number_DOI by 2458
df['number_DOI'] = df['number_DOI'].str.replace('10.7488/ds/','')

# add to link_folder column number_DOI with / separately
df['link_folder'] = df['link_folder'] + '/' + df['number_DOI']

# remove rows with NaN in link_folder
df = df.dropna(subset=['link_folder'])

df.link_folder.tolist()

link2gzfiles=[]
link2zipfiles=[]

# Use tqdm to create a progress bar
for link in tqdm(df.link_folder.tolist(), desc="Processing links"):
    download_links = pgc.find_figshare_ndownloader_links(link)
    link2gzfiles.append(download_links[0])

    # if download_links only has one link fill nan
    if len(download_links) == 1:
        link2zipfiles.append('nan')
    else:
        link2zipfiles.append(download_links[1])


# add new column link2gzfiles to df
df['link2gzfiles'] = link2gzfiles

# add new column link2zipfiles to df
df['link2zipfiles'] = link2zipfiles

# create new column with file_name_output, by "raw/" + publication + ".meta.gz" 
df['file_name_output'] = 'raw/' + df['publication'] + '.meta.gz'

df