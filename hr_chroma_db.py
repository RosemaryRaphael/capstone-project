import chromadb
from chromadb.utils import embedding_functions
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

source = r"HR.pdf"
print(f"Loading PDF from: {source}")
loader = PyPDFLoader(source)
docs = loader.load()
print(f"Loaded {len(docs)} pages from PDF.")

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)
texts = [chunk.page_content for chunk in chunks]
print(f"Split into {len(texts)} chunks.")

client = chromadb.PersistentClient(path="./chroma_db")

embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

try:
    client.delete_collection("ag2-docs")
    print("Deleted old collection 'ag2-docs'.")
except Exception:
    print("No previous collection found.")

collection = client.create_collection(
    name="ag2-docs",
    embedding_function=embedding_func
)
print("Created new Chroma collection: ag2-docs")

embeddings = embedding_func(texts)
collection.add(
    documents=texts,
    ids=[f"chunk_{i}" for i in range(len(texts))],
    embeddings=embeddings
)

print(f"Added {len(texts)} chunks to collection 'ag2-docs'.")
print("Completed.")
