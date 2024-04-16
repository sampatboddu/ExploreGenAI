import os
import glob
import markdown
import openai
import numpy as np
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient


# Azure Cognitive Search details
endpoint = "<url>"
index_name = "<index_name>"
api_key = None

def read_markdown_files(folder_path):
    markdown_files = glob.glob(os.path.join(folder_path, "*.md"))
    texts = []
    for file in markdown_files:
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
            html = markdown.markdown(text)
            texts.append((file, html))
    return texts

def chunk_text(text, chunk_size):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks

def create_embeddings(texts):
    embeddings = []
    i = 0
    for file, text in texts:
        sentences = text.split('.')  # Split by sentences
        print("Processing... ", text)
        print("length of sentences... ", len(sentences))
        for sentence in sentences:
            response = openai.Embedding.create(
                model="text-embedding-ada-002",  # Use the text-davinci-002 model
                input=sentence,
                # max_tokens=0,
                # return_prompt=False,
                # return_sequences=False
            )
            embedding = response['data'][0]['embedding']
            print(embedding)
            embeddings.append((sentence, embedding))
            i = i+1
            print(i)
            if i == 25:
                break
    return embeddings

def store_embeddings_in_azure_search(embeddings):
    credential = AzureKeyCredential(api_key)
    client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
    
    documents = []
    for i, (file, embedding) in enumerate(embeddings):
        document = {
            "id": str(i),
            "filename": os.path.basename(file),  # Store filename
            "content": file, #open(file, "r", encoding="utf-8").read(),  # Store content
            "embedding": np.array(embedding).tolist()
        }
        documents.append(document)
    
    client.upload_documents(documents)

# Example usage:
folder_path = "md_files"
markdown_texts = read_markdown_files(folder_path)

# Create embeddings
embeddings = create_embeddings(markdown_texts)
# print("Embeddings shape:", embeddings.shape)

# Store embeddings in Azure Cognitive Search
store_embeddings_in_azure_search(embeddings)
