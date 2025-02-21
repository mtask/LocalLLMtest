Start chat between two instances of specified LLMs (`--model1 <first model> --model2 <second model>`).

```bash
python3 chatbot.py --model1 dolphin-mistral --model2 dolphin-mistral
initial prompt > Start casual conversation about anything you feel like
```

Initial prompt is given to model1, then model1's answer is then given as prompt to model2 and so on.
It should keep the context window for each bot while the same process is running. Not sure what happens when context size is exceeded.
Previous messages are stored in a list of dictionaries, so it might be that the model just gets X first messages as context if the context size is exceeded.

You can "debug" model1 or model2 in seperate debug prompts by giving an cli argument `--debug_model1` or `--debug_model2`. 

Prompts are prompted between chat responses and do not affect the actual (debug has its own messages context), but the actual chat so far is part of the debugging context for debugging purposes.
