# Make query and update Whoosh index with the latest CVE data

```bash
python cve_query.py --update --whoosh_query "severity: HIGH" --ollama_prompt "What software is recently affected by high vulnerablities based on the given context?"
```

```bash
python cve_query.py --whoosh_query "all" --ollama_prompt "Write threat intellignece report based on the given context"
```
