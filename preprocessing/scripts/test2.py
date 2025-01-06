import requests
import os
import pandas as pd


# print current working directory
print(os.getcwd())

def download_file(url, save_path):
    """
    Pobiera plik z podanego URL i zapisuje go w określonej ścieżce.

    :param url: URL pliku do pobrania
    :param save_path: Ścieżka do zapisania pliku
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Sprawdza, czy żądanie zakończyło się sukcesem
        
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"Plik został zapisany w: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Wystąpił błąd podczas pobierania pliku: {e}")


def get_nearest_gene_by_rsid(rsid):
    """
    Fetches the nearest gene associated with a given rsID using the Ensembl REST API.

    Parameters:
        rsid (str): The rsID to query (e.g., 'rs7412').

    Returns:
        dict: Information about the nearest gene or a message if not found.
    """
    base_url = "https://rest.ensembl.org"
    variation_endpoint = f"/variation/homo_sapiens/{rsid}?content-type=application/json"

    try:
        # Step 1: Get the location of the rsID
        response = requests.get(base_url + variation_endpoint, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        data = response.json()

        if "mappings" not in data or not data["mappings"]:
            return {"rsid": rsid, "message": "No mappings found for this rsID."}

        # Collect the region of the rsID
        regions = [(mapping["seq_region_name"], mapping["start"], mapping["end"]) for mapping in data["mappings"]]

        # Step 2: Find the nearest gene for each region
        nearest_genes = []
        for seq_region, start, end in regions:
            overlap_endpoint = f"/overlap/region/human/{seq_region}:{start}-{end}?feature=gene;content-type=application/json"
            gene_response = requests.get(base_url + overlap_endpoint, headers={"Content-Type": "application/json"})
            
            if gene_response.status_code == 200:
                genes_data = gene_response.json()
                if genes_data:
                    # Find the closest gene by distance
                    distances = [
                        (gene, abs(gene["start"] - start)) 
                        for gene in genes_data 
                        if "external_name" in gene
                    ]
                    if distances:
                        closest_gene = min(distances, key=lambda x: x[1])[0]
                        nearest_genes.append(closest_gene["external_name"])
        
        if not nearest_genes:
            return {"rsid": rsid, "message": "No nearby genes found for this rsID."}

        return {"rsid": rsid, "nearest_genes": nearest_genes}

    except requests.exceptions.RequestException as e:
        return {"rsid": rsid, "error": f"Request failed: {str(e)}"}
    except KeyError as e:
        return {"rsid": rsid, "error": f"Missing key: {str(e)}"}
    except Exception as e:
        return {"rsid": rsid, "error": f"An unexpected error occurred: {str(e)}"}


def filter_and_return_snps(path_to_file, pvalue_threshold):
    """
    Reads a file, filters rows based on a p-value threshold, and returns the filtered SNPs.

    Parameters:
        path_to_file (str): Path to the input file.
        pvalue_threshold (float): Threshold for filtering rows based on the 'P' column.

    Returns:
        list: A list of SNPs that meet the p-value threshold.
    """
    try:
        # Read the file
        df = pd.read_csv(path_to_file, sep=' ')

        # Filter the DataFrame by the p-value threshold
        df_filtered = df[df['P'] < pvalue_threshold]

        # Extract the SNP column as a list
        filtered_snps = df_filtered['SNP'].tolist()

        print(f"Filtered SNPs count: {len(filtered_snps)}")
        return filtered_snps
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        # Delete dataframes to free memory
        del df
        del df_filtered



url = "https://figshare.com/ndownloader/files/40036684/ADHD2022_iPSYCH_deCODE_PGC.meta.gz"
save_path = "raw/ADHD2022_iPSYCH_deCODE_PGC.meta.gz"

download_file(url, save_path)

rsid_vector_adhd_1e5 = filter_and_return_snps(save_path, 0.000000001)

len(rsid_vector_adhd_1e5)


file_list = ["raw/ADHD2022_iPSYCH_deCODE_PGC.meta.gz"]
# from 10^-9 to 10^-2
pvalue_threshold_list = [0.000000001, 0.00000001, 0.0000001, 0.000001, 0.00001, 0.0001, 0.001, 0.01]

# empty list to store all results
all_results = []

# for loop for file_list and pvalue_threshold_list
for file in file_list:
    for pvalue_threshold in pvalue_threshold_list:
        print(f"File: {file}, P-value threshold: {pvalue_threshold}")
        filtered_snps = filter_and_return_snps(file, pvalue_threshold)
        print(filtered_snps[:5])  # Display the first 5 SNPs

        # for loop for filtered_snps and get_nearest_gene_by_rsid, save to list
        nearest_genes = []
        for rsid in filtered_snps:
            gene_info = get_nearest_gene_by_rsid(rsid)
            nearest_genes.append(gene_info)

        # calculate the number of unique genes
        all_genes = [gene for sublist in nearest_genes for gene in sublist]
        unique_genes = list(set(all_genes))

        # keep results in a dictionary
        result = {
            "file": file,
            "pvalue_threshold": pvalue_threshold,
            "filtered_snps": filtered_snps,
            "unique_genes": unique_genes
        }

        all_results.append(result)






# Example usage
rsid_to_query = "rs9824501"  # Replace with your rsID


# for loop for rsid_vector_adhd_1e5 and get_nearest_gene_by_rsid, save to list
from tqdm import tqdm

nearest_genes = []
for rsid in tqdm(rsid_vector_adhd_1e5, desc="Processing RSIDs"):
    print(rsid)
    gene_info = get_nearest_gene_by_rsid(rsid)
    nearest_genes.append(gene_info)

print(nearest_genes)

# Spłaszczenie kolumny `nearest_genes` i usunięcie NaN
all_genes = [gene for sublist in df['nearest_genes'].dropna() for gene in sublist]

# Uzyskanie unikalnych wartości
unique_genes = list(set(all_genes))

print("Unikalne geny:", unique_genes)



gene_info = get_nearest_gene_by_rsid(rsid_to_query)
print(gene_info)
