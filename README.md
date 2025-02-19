This repository's content has been mainly created for me to test and learn things about local LLMs. 

# Setup ollama

- `ansible-playbook ansible-ollama.yml` (expects the user be in "docker" group or run as root directly. I.e. no `become`s specified.)

- Pull the `llama3.2:1b` model for testing.

```yaml
docker exec -it ollama ollama pull llama3.2:1b
```

Used model is specified inside the python scripts (check below).

## Python script - rss_query.py

```bash
python rss_query.py --update --whoosh_query "all" --ollama_prompt "Write a summary of the latest Hacker News articles." --context_size 128000
```

## Python script - cve_query.py

This script downloads recent CVE data and indexes it to Whoosh index. Then this data is used as a context for prompts with Ollama.

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

## Make query to Whoosh and update Whoosh index (`--update`)  with the latest CVE data. Use Whoosh query results as context to prompt (`--ollama_prompt`).

```bash
python cve_query.py --update --whoosh_query "severity: HIGH" --ollama_prompt "What software is recently affected by high vulnerablities based on the given context?"
```

## Use all data (`--whoosh_query "all"`) as context. Don't update the CVE data.

```bash
python cve_query.py --whoosh_query "all" --ollama_prompt "Write threat intellignece report based on the given context"
```
