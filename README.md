# search_pmc

This code suite is a tool to use for improved and more efficient literature review. 

The code retrieves scientific literature from an NCBI database and parses the text fields into relational tables which can be
stored in a database.

With text in this format, researches can more easily search through a literature database to filter down to literature of interest.

NCBISearch.py and NCBIFetch.py do the work of searching for, and fetching documents, using NCBI's Entrez API based on user-specified
search terms. 

PMCParse.py parses the text from the documents into relational tables. 

Users should use the Jupyter Notebook, `run_ncbi_search.ipynb`, to specify their search terms, retrieve and view results.

For questions please contact s.rand525@gmail.com.
