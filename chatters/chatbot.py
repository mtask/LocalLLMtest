import os
import json
import argparse
import re
import sys

from ollama import chat
from ollama import ChatResponse
from ollama import Options


class bcolors:
    BLUE = '\033[94m'
    RED = '\033[91m'
    END = '\033[0m'


class Bot:

    def __init__(self, model="deepseek-r1:1.5b"):
        self.messages = []
        self.model = model
        self.debug = False
        # Used when debug is set to Ture
        self.debug_messages = []

    def _add_message(self, message, role):
        if self.debug:
            self.debug_messages = self.messages.copy()
            self.debug_messages.append({'role': role, 'content': message})
        else:
            self.messages.append({'role': role, 'content': message})

    def _send_messages(self):
        if self.debug:
            response: ChatResponse = chat(model=self.model, messages=self.debug_messages)
            # Always reset debug messages
            self.debug_messages = []
        else:
            response: ChatResponse = chat(model=self.model, messages=self.messages)
            # Is this useful option to override num_ctx here an does it even work?
            #response: ChatResponse = chat(model=self.model, messages=self.messages, options=Options(num_ctx=8192))
            # Add response only when not debugging
            self._add_message(response.message.content, 'assistant')
        return response.message.content

    def talk(self, input_data):
        self._add_message(input_data, 'user')
        output_data = self._send_messages()
        output_data = re.sub(r'<think>.*?</think>', '', output_data, flags=re.DOTALL)
        return(output_data)

def debug(bot, name):
    """
    Debug questions until an empty prompt is given
    """
    bot.debug = True
    while True:
        debug = input(f"debug prompt ({name})> ")
        if debug == "":
            break
        r = bot.talk(debug)
        print(f"<debug>\n{r}\n</debug>")
    bot.debug = False

def interrupt(bot1, bot2):
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
            debug(bot1, "BOT1")
            break
        elif ans.strip() == "3":
            debug(bot2, "BOT2")
            break


def parse_args():
    parser = argparse.ArgumentParser(description="A sample program to demonstrate argparse")
    parser.add_argument("--model1", required=True,
                        help="First LLM model. It needs to be pulled with Ollama already'")
    parser.add_argument("--model2", required=True,
                        help="Second LLM model. It needs to be pulled with Ollama already")
    parser.add_argument('--debug_model1', action='store_true', help="Debug prompt between the responses")
    parser.add_argument('--debug_model2', action='store_true', help="Debug prompt between the responses")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    # Initialize bots
    bot1 = Bot(args.model1)
    bot2 = Bot(args.model2)
    # Initial promprt for bot1
    start = input("initial prompt> ")
    r = bot1.talk(start)
    print(f"{bcolors.BLUE}BOT1: {r}{bcolors.END}")
    while True:
        try:
            r = bot2.talk(r)
            print(f"{bcolors.RED}BOT2: {r}{bcolors.END}")
            if args.debug_model2:
                debug(bot2, "bot2")
            r = bot1.talk(r)
            print(f"{bcolors.BLUE}BOT1: {r}{bcolors.END}")
            if args.debug_model1:
                debug(bot1, "bot1")
        except KeyboardInterrupt:
            interrupt(bot1, bot2)
