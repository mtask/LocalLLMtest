This repository's contains some scripts that I have created to test local LLMs. 

# Setup ollama

The scripts expect Ollama to be running and listening on TCP port 11434. I've been using Docker for this setup and configured everything with Ansible
Modify `ansible-ollama.yml` to your needs.

1. `ansible-playbook ansible-ollama.yml` (expects the user be in "docker" group or run as root directly. I.e. no `become`s specified.)
2. Pull the `llama3.2:1b` model for testing.

```yaml
docker exec -it ollama ollama pull llama3.2:1b
```

## Python script - rss_query.py


This script fetches RSS feed data, stores that data in Whoosh index. Then it is used as a context for Ollama prompts. Feeds are configured inside the script.

```
python3 rss_query.py -h
usage: rss_query.py [-h] [--update] --days DAYS --ollama_prompt OLLAMA_PROMPT [--context_size CONTEXT_SIZE]

Manage RSS feed data and query Ollama.

options:
  -h, --help            show this help message and exit
  --update              Update Whoosh index with new RSS feed data.
  --days DAYS           The number of days for retrieving data from Whoosh.
  --ollama_prompt OLLAMA_PROMPT
                        The prompt for Ollama.
  --context_size CONTEXT_SIZE
                        The context size for Ollama.
```

### Query all (`--whoosh_query "all"`) data from the Whoosh and use the query results as context to prompt (`--ollama_prompt`)`.

```bash
python rss_query.py --update --whoosh_query "all" --ollama_prompt "Write a summary of the latest Hacker News articles." --context_size 128000
```

### Query based on published date (`published:[2025-02-20 TO]`) data from the Whoosh and use the query results as context to prompt (`--ollama_prompt`)`.

```bash
python rss_query.py --whoosh_query "published:[2025-02-20 TO]" --ollama_prompt "Summarize recent Hacker News articles." --context_size 2048
```

## Python script - cve_query.py

This script fetches CVE data, stores that data in Whoosh index. Then it is used as a context for Ollama prompts.

```bash
usage: cve_query.py [-h] [--update] --whoosh_query WHOOSH_QUERY --ollama_prompt OLLAMA_PROMPT [--context_size CONTEXT_SIZE]

Manage CVE data and query Ollama.

options:
  -h, --help            show this help message and exit
  --update              Update Whoosh index with new CVE data.
  --whoosh_query WHOOSH_QUERY
                        The query for Whoosh.
  --ollama_prompt OLLAMA_PROMPT
                        The prompt for Ollama.
  --context_size CONTEXT_SIZE
                        The context size for Ollama.
```

### Make query to Whoosh and update Whoosh index (`--update`)  with the latest CVE data. Use Whoosh query results as context to prompt (`--ollama_prompt`).

```bash
python cve_query.py --update --whoosh_query "severity: HIGH" --ollama_prompt "What software is recently affected by high vulnerablities based on the given context?"
```

### Use all data (`--whoosh_query "all"`) as context. Don't update the CVE data.

```bash
python cve_query.py --whoosh_query "all" --ollama_prompt "Write threat intellignece report based on the given context"
```

This script. It has its own logic to track already seen CVE's in file `.seen_cve_ids.json`. This is only because I originally wrote this code for something else that didn't have Whoosh used, so it required own tracking system for seen CVEs.
Not really necessary in this use case as I could handle duplicates in Whoosh.
