from Bio import Entrez

# Ustaw swój e-mail, wymagane przez NCBI
Entrez.email = "your_email@example.com"

# Funkcja do pobrania szczegółów rsID
def get_gene_for_rsid(rsid):
    try:
        # Wyszukiwanie rsID w bazie dbSNP
        handle = Entrez.esearch(db="snp", term=rsid)
        record = Entrez.read(handle)
        handle.close()

        # Sprawdzenie, czy rsID istnieje w bazie
        if not record["IdList"]:
            return f"Nie znaleziono rsID {rsid} w bazie dbSNP."

        # Pobranie szczegółowych informacji o rsID
        handle = Entrez.efetch(db="snp", id=record["IdList"], retmode="xml")
        details = handle.read()
        handle.close()

        # Parsowanie wyników (XML)
        import xml.etree.ElementTree as ET
        root = ET.fromstring(details)
        genes = [gene.text for gene in root.findall(".//GeneName")]
        
        if genes:
            return f"rsID {rsid} jest powiązany z genami: {', '.join(genes)}"
        else:
            return f"Nie znaleziono informacji o genach dla rsID {rsid}."

    except Exception as e:
        return f"Błąd: {e}"

# Przykładowe użycie
rsid = "rs62513865"
print(get_gene_for_rsid(rsid))
