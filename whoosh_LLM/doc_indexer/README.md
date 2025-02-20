### Index PDF to Whoosh index

```bash
python3 index.py --path somedocument.pdf
```

### Prompt LLM via Ollama and provide context from Whoosh search

```bash
python3 search_prompt.py --whoosh_query 'LED' --ollama_prompt 'How can LED lights be used in cyber attack?'
```
