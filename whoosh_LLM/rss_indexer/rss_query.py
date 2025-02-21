import argparse
import os
import sys
import feedparser
from langchain_ollama import OllamaLLM
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, DATETIME, KEYWORD
from whoosh.query import DateRange, And
from whoosh.qparser import QueryParser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Define the LLM model to be used
#llm_model = "llama3.2:1b"
llm_model = "llama3.2:3b"

class RssFeed:
    def __init__(self):
        self.schema = Schema(
            id=ID(stored=True, unique=True),
            title=TEXT(stored=True),
            link=ID(stored=True),
            description=TEXT(stored=True),
            published=DATETIME(stored=True),
            category=KEYWORD(stored=True),
            summary=TEXT(stored=True)
        )
        self.index_dir = os.path.join(os.getcwd(), "whoosh_rss_index")
        if not os.path.exists(self.index_dir):
            os.mkdir(self.index_dir)

    def create_index(self, url):
        """Create or update a Whoosh index with RSS feed data."""
        feed = feedparser.parse(url)
        # Check if the index exists
        if index.exists_in(self.index_dir):
            ix = index.open_dir(self.index_dir)
        else:
            ix = index.create_in(self.index_dir, self.schema)
        writer = ix.writer()
        for entry in feed.entries:
            published = datetime(*entry.published_parsed[:6]) if 'published_parsed' in entry else datetime.now()
            # Check if 'description' attribute exists
            if 'description' in entry:
                description = BeautifulSoup(entry.description, 'html.parser').get_text()
                # Clean up description by removing empty lines and extra whitespace
                description = "\n".join(line.strip() for line in description.splitlines() if line.strip())
            else:
                description = "No description available."
            # Generate a summary (for simplicity, using the first 200 characters as summary)
            summary = description[:200] + "..." if len(description) > 200 else description
            # Extract 'term' attribute from tags if available
            category = ", ".join(tag['term'] for tag in entry.tags) if 'tags' in entry else "Uncategorized"
            writer.update_document(
                id=entry.id,
                title=entry.title,
                link=entry.link,
                description=description,
                published=published,
                category=category,
                summary=summary
            )
        writer.commit()
        print(f"RSS feed data from {url} has been indexed into Whoosh")

    def search_index(self, days, query_str=None, n_results=None):
        """Search the Whoosh index for documents published within the given number of days and optionally matching the query."""
        ix = index.open_dir(self.index_dir)
        date_limit = datetime.now() - timedelta(days=days)
        date_query = DateRange("published", date_limit, datetime.now())
        if query_str:
            qp = QueryParser("description", ix.schema)
            keyword_query = qp.parse(query_str)
            combined_query = And([date_query, keyword_query])
        else:
            combined_query = date_query
        with ix.searcher() as searcher:
            results = searcher.search(combined_query, limit=n_results)
            documents = [hit.fields() for hit in results]
            return documents

def query_ollama(prompt, context_size):
    """Send a query to Ollama and retrieve the response."""
    llm = OllamaLLM(model=llm_model, num_ctx=context_size)
    return llm.invoke(prompt)

def get_response(rss_feed, days, whoosh_query, ollama_prompt, context_size):
    retrieved_docs = rss_feed.search_index(days, whoosh_query)
    context = " ".join([
        f"ID: {doc['id']}\nTitle: {doc['title']}\nLink: {doc['link']}\nDescription: {doc['description']}\nPublished: {doc['published']}\nCategory: {doc['category']}\nSummary: {doc['summary']}"
        for doc in retrieved_docs
    ]) if retrieved_docs else "No relevant documents found."
    augmented_prompt = f"Context: {context}\n\nQuestion: {ollama_prompt}\nAnswer:"
    print(augmented_prompt)

    response = query_ollama(augmented_prompt, context_size)
    return response

def main():
    parser = argparse.ArgumentParser(description="Manage RSS feed data and query Ollama.")
    parser.add_argument('--update', action='store_true', help="Update Whoosh index with new RSS feed data.")
    parser.add_argument('--days', type=int, required=True, help="The number of days for retrieving data from Whoosh.")
    parser.add_argument('--ollama_prompt', type=str, required=True, help="The prompt for Ollama.")
    parser.add_argument('--whoosh_query', type=str, required=False, help="The query for Whoosh.")
    parser.add_argument('--context_size', type=int, default=2048, help="The context size for Ollama.")
    args = parser.parse_args()
    rss_urls = [
         "https://feeds.feedburner.com/TheHackersNews",
         "https://cvefeed.io/rssfeed/severity/high.xml",
         "https://cvefeed.io/rssfeed/newsroom.xml",
         "https://krebsonsecurity.com/feed/"
    ]

    rss_feed = RssFeed()
    if args.update:
        for rss_url in rss_urls:
            rss_feed.create_index(rss_url)

    response = get_response(rss_feed, args.days, args.whoosh_query, args.ollama_prompt, args.context_size)
    print(response)

if __name__ == "__main__":
    main()
