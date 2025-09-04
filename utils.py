import sys
import time
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def typing_effect(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def print_bot_message(message):
    print(f"\n🤖 NeuroBot: ", end="")
    typing_effect(message, delay=0.015)  # Faster typing for more natural feel

def print_separator():
    print("\n" + "-" * 50)

def get_user_input():
    try:
        return input("\n💭 You: ").strip()
    except KeyboardInterrupt:
        print("\n\n👋 peace out!")
        sys.exit(0)
    except EOFError:
        print("\n\n👋 peace out!")
        sys.exit(0)