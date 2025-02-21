This repository's contains some scripts that I have created to test local LLMs. 

# Setup ollama

The scripts expect Ollama to be running and listening on TCP port 11434. I've been using Docker for this setup and configured everything with Ansible
Modify ansible playbook `ansible-ollama.yml` to your needs.

1. `ansible-playbook ansible-ollama.yml` (expects the user be in "docker" group or run as root directly. I.e. no `become`s specified.)
2. Pull the `llama3.2:1b` model for testing.

```yaml
docker exec -it ollama ollama pull llama3.2:1b
```

## whoosh_LLM

This directory contains scripts that uses Whoosh to index additional context which is then combined with the prompt. It has its own README with more details.

## chatters

This directory contains script where you can put two LLM instances to "talk" with each other. It will ask an initial prompt which will kickstart the discussion with the first bot.
