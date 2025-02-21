import os
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from langchain_ollama import OllamaLLM

class Engine:

    def __init__(self, index_conf, model="llama3.2:1b"):
        self.index_dir = index_conf['index_dir']
        if not os.path.isdir(self.index_dir):
            print("Creating index")
            os.mkdir(self.index_dir)
            self.create_index()
        self.ix = open_dir(self.index_dir)
        self.ollama_model = model

    def create_index(self):
        schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True))
        index.create_in(self.index_dir, schema)

    def chunk_text(self, text, chunk_size=100):
        chunks = []
        current_chunk = []
        words = text.split()
        for word in words:
            current_chunk.append(word)
            if len(current_chunk) >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    def index_doc(self, title, content, path):
        print(f"[*] Indexing document with title: {title}")
        writer = self.ix.writer()
        chunks = self.chunk_text(content)
        for chunk in chunks:
            writer.add_document(title=title, content=chunk.strip(), path=path)
        writer.commit()

    def search(self, query_str):
        results = []
        with self.ix.searcher() as searcher:
            query = QueryParser("content", self.ix.schema).parse(query_str)
            hits = searcher.search(query, limit=30)
            for hit in hits:
                results.append(hit['content'])
        return results

    def query_ollama(self, prompt, context_size):
        """Send a query to Ollama and retrieve the response."""
        llm = OllamaLLM(model=self.ollama_model, num_ctx=context_size)
        return llm.invoke(prompt)

    def generate_response(self, query, prompt, context_size=4096):
        retrieved_docs = self.search(query)
        context = " ".join(retrieved_docs)
        # Separate the prompt and the retrieved context
        augmented_prompt = f"Context: {context}\n\nQuestion: {prompt}\nAnswer:"
        print(augmented_prompt)
        ollama_response = self.query_ollama(prompt=augmented_prompt, context_size=context_size)
        return ollama_response

# Usage example
if __name__ == "__main__":
    conf = {'index_dir': 'whoosh_doc_index'}
    engine = Engine(conf)

    # Example: Indexing a document
    sample_title = "Sample Document"
    sample_content = "This is the content of the document. It contains information about various topics."
    sample_path = "path/to/sample_document.txt"
    engine.index_doc(title=sample_title, content=sample_content, path=sample_path)

    # Example: Generating a response
    whoosh_query = "title:'Sample Document'"
    ollama_prompt = "Explain the main concepts of quantum mechanics"
    response = engine.generate_response(query=whoosh_query, prompt=ollama_prompt)
    print(response)

