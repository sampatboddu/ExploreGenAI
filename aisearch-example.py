from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes import SearchIndex, SimpleField, ComplexField, DataType

# Set up your Azure Cognitive Search service
service_endpoint = "YOUR_SEARCH_SERVICE_ENDPOINT"
admin_key = "YOUR_ADMIN_KEY"

# Initialize the SearchIndexClient and SearchIndexerClient
credential = AzureKeyCredential(admin_key)
index_client = SearchIndexClient(service_endpoint, credential)
indexer_client = SearchIndexerClient(service_endpoint, credential)

# Define the index schema
index_name = "markdown-index"
index_fields = [
    SimpleField(name="id", type=DataType.String, key=True),
    SimpleField(name="title", type=DataType.String),
    SimpleField(name="content", type=DataType.String)
]
index = SearchIndex(name=index_name, fields=index_fields)

# Create the index
index_client.create_index(index)

# Define the indexer
indexer_name = "markdown-indexer"
indexer_data_source_name = "your-markdown-data-source"
indexer_skillset_name = "your-markdown-skillset"
indexer_target_index_name = "markdown-index"

# Define data source
data_source = {
    "name": indexer_data_source_name,
    "type": "azureblob",
    "container": {"name": "your-container-name"},
    "connection_string": "YOUR_CONNECTION_STRING"
}

# Define skillset
skillset = {
    "name": indexer_skillset_name,
    "skills": [
        {
            "@odata.type": "#Microsoft.Skills.Text.MarkdownSkill",
            "name": "markdownSkill",
            "context": "/document/content",
            "inputs": [
                {
                    "name": "text",
                    "source": "/document/content"
                }
            ],
            "outputs": [
                {
                    "name": "markdownText"
                }
            ]
        }
    ]
}

# Define indexer
indexer = {
    "name": indexer_name,
    "dataSourceName": indexer_data_source_name,
    "targetIndexName": indexer_target_index_name,
    "skillsetName": indexer_skillset_name,
    "parameters": {
        "maxFailedItems": 10,
        "maxFailedItemsPerBatch": 5,
        "base64EncodeKeys": False
    },
    "fieldMappings": [
        {
            "sourceFieldName": "content",
            "targetFieldName": "content"
        }
    ]
}

# Create data source, skillset, and indexer
indexer_client.create_data_source(data_source)
indexer_client.create_skillset(skillset)
indexer_client.create_indexer(indexer)




from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# Set up your Azure Cognitive Search service
service_endpoint = "YOUR_SEARCH_SERVICE_ENDPOINT"
query_key = "YOUR_QUERY_KEY"

# Initialize the SearchClient
credential = AzureKeyCredential(query_key)
search_client = SearchClient(service_endpoint, index_name="markdown-index", credential=credential)

# Define your search query
search_text = "your search query"
search_results = search_client.search(search_text)

# Process the search results
for result in search_results:
    print("Title:", result["title"])
    print("Content:", result["content"])
    print("Score:", result["@search.score"])
    print("------------------")
