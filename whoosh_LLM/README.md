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

### Get all RSS feed data from the Whoosh for last five days (`--days 5`) and use the results as context to prompt (`--ollama_prompt`)`.

```bash
python rss_query.py --update --days 5 --ollama_prompt "What are the top security threats to focus on based on the given context." --context_size 128000
```

`--update` specifies that Whoosh index is updated with the latest data from the RSS feeds.

## Python script - cve_query.py

This script fetches CVE data and stores that data in Whoosh index. Then it is used as a context for Ollama prompts.
RSS feed can also use feed of CVE data but this has more specific Whoosh schema for CVE data and allows making queries based on that schema.

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

### Make query to Whoosh (`--whoosh_query "severity: HIGH"`) and update Whoosh index (`--update`)  with the latest CVE data. Use Whoosh query results as context to prompt (`--ollama_prompt`).

```bash
python cve_query.py --update --whoosh_query "severity: HIGH" --ollama_prompt "What software is recently affected by high vulnerablities based on the given context?"
```

### Use all data (`--whoosh_query "all"`) as context. Don't update the CVE data.

```bash
python cve_query.py --whoosh_query "all" --ollama_prompt "Write threat intellignece report based on the given context"
```

This script. It has its own logic to track already seen CVE's in file `.seen_cve_ids.json`. This is only because I originally wrote this code for something else that didn't have Whoosh used, so it required own tracking system for seen CVEs.
Not really necessary in this use case as I could handle duplicates in Whoosh.
