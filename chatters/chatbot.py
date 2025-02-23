import os
import json
import argparse
import re
import sys

from ollama import chat
from ollama import ChatResponse
from ollama import Options
from tokenizers import Tokenizer

class bcolors:
    BLUE = '\033[94m'
    RED = '\033[91m'
    END = '\033[0m'


class Bot:
    def __init__(self, model="deepseek-r1:1.5b"):
        self.messages = []
        self.model = model
        self.debug = False
        self.tokenizer = Tokenizer.from_pretrained("gpt2")
        # Used when debug is set to Ture
        self.debug_messages = []

    # Function to track tokens
    def _count_tokens(self, message):
        tokens = self.tokenizer.encode(message)
        return len(tokens.ids)

     # Function to trim conversation history
    def _trim_conversation(self, max_tokens):
        token_count = sum(self._count_tokens(msg['content']) for msg in self.messages)
        print(f"Token count: {token_count}")
        while token_count > max_tokens:
            self.messages.pop(0)
            token_count = sum(self._count_tokens(msg['content']) for msg in self.messages)

    def _add_message(self, message, role):
        if self.debug:
            self.debug_messages = self.messages.copy()
            self.debug_messages.append({'role': role, 'content': message})
        else:
            self.messages.append({'role': role, 'content': message})

    def _send_messages(self):
        if self.debug:
            response: ChatResponse = chat(model=self.model, messages=self.debug_messages)
            self.debug_messages = []
        else:
            response: ChatResponse = chat(model=self.model, messages=self.messages)
            self._add_message(response.message.content, 'assistant')
        return response.message.content

    def talk(self, input_data, max_tokens):
        self._add_message(input_data, 'user')
        self._trim_conversation(max_tokens)
        output_data = self._send_messages()
        output_data = re.sub(r'<think>.*?</think>', '', output_data, flags=re.DOTALL)
        return(output_data)

def debug(bot, name, max_tokens):
    """
    Debug questions until an empty prompt is given
    """
    bot.debug = True
    while True:
        debug = input(f"debug prompt ({name})> ")
        if debug == "":
            break
        r = bot.talk(debug, max_tokens)
        print(f"<debug>\n{r}\n</debug>")
    bot.debug = False

def interrupt(bot1, bot2, max_tokens):
    print("""
    Select an option:
    1) Exit
    2) Debug bot1
    3) Debug bot2
    """)
    while True:
        ans = input("select> ")
        if ans.strip() == "1":
            sys.exit(0)
        elif ans.strip() == "2":
            debug(bot1, "BOT1", max_tokens)
            break
        elif ans.strip() == "3":
            debug(bot2, "BOT2", max_tokens)
            break


def parse_args():
    parser = argparse.ArgumentParser(description="A sample program to demonstrate argparse")
    parser.add_argument("--model1", required=True,
                        help="First LLM model. It needs to be pulled with Ollama already'")
    parser.add_argument("--model2", required=True,
                        help="Second LLM model. It needs to be pulled with Ollama already")
    parser.add_argument('--debug_model1', action='store_true', help="Debug prompt between the responses")
    parser.add_argument('--debug_model2', action='store_true', help="Debug prompt between the responses")
    parser.add_argument("--max_tokens", required=False, default="2048",
                        help="Max tokens. Default 8192")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    max_tokens = int(args.max_tokens)
    # Initialize bots
    bot1 = Bot(args.model1)
    bot2 = Bot(args.model2)
    # Initial promprt for bot1
    start = input("initial prompt> ")
    r = bot1.talk(start, max_tokens)
    print(f"{bcolors.BLUE}BOT1: {r}{bcolors.END}")
    while True:
        try:
            r = bot2.talk(r,max_tokens)
            print(f"{bcolors.RED}BOT2: {r}{bcolors.END}")
            if args.debug_model2:
                debug(bot2, "bot2", max_tokens)
            r = bot1.talk(r,max_tokens)
            print(f"{bcolors.BLUE}BOT1: {r}{bcolors.END}")
            if args.debug_model1:
                debug(bot1, "bot1", max_tokens)
        except KeyboardInterrupt:
            interrupt(bot1, bot2, max_tokens)
