from groq import Client
from annoy import AnnoyIndex
import os
import pickle
import numpy as np
import tempfile
import requests
from bs4 import BeautifulSoup
import webbrowser
import subprocess
import re
import string
import random
import uuid
# Create a temporary directory
temp_dir = tempfile.mkdtemp()

# Initialize Groq client with your API key
client = Client(api_key=os.environ.get("GROQ_API_KEY"))

embedding_size = 384

# Initialize Annoy index
index_filename = os.path.join(temp_dir, "conversation_history.ann")
index = AnnoyIndex(embedding_size, 'angular')
text_storage_filename = os.path.join(temp_dir, "text_storage.pkl")
text_storage = {}  # Initialize text_storage as an empty dictionary

def get_model_choice():
        print("Select a model:")
        print("1. mixtral-8x7b-32768 (max_tokens 32768)")
        print("2. gemma-7b-it (max_tokens 8192)")
        print("3. llama2-70b-4096 (max_tokens 4096)")
        choice = input("Enter your choice (1, 2, or 3): ")
        
        if choice == "1":
            return "mixtral-8x7b-32768", 32768
        elif choice == "2":
            return "gemma-7b-it", 8192
        elif choice == "3":
            return "llama2-70b-4096", 4096
        else:
            print("Invalid choice. Using default model (mixtral-8x7b-32768).")
            return "mixtral-8x7b-32768", 32768

model_choice, max_tokens = get_model_choice()


def save_code_snippet(response):
    code_blocks = re.findall(r"```(.*?)```", response, re.DOTALL)
    if not code_blocks:
        print("No code snippets found in the response.")
        return

    for i, code_block in enumerate(code_blocks):
        # Extract language type if specified after the triple backticks
        match = re.match(r"```(.*?)\n(.*?)```", code_block, re.DOTALL)
        if match:
            language_type, code = match.groups()
            language_type = language_type.strip().lower()
        else:
            language_type = "plaintext"  # Default to plaintext if no language type specified
            code = code_block.strip()

        # Map language types to file extensions
        file_extension_map = {
            "python": "py",
            "html": "html",
            "javascript": "js",
            "css": "css"
            # Add more mappings as needed
        }

        # Determine file extension based on language type or default to 'txt' for plaintext
        file_extension = file_extension_map.get(language_type, "txt")

        # Generate a random filename with 12 characters
        random_filename = str(uuid.uuid4())[:12]

        # Save code snippet as file with appropriate extension
        filename = f"{random_filename}.{file_extension}"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(code.strip())
        print(f"Code snippet {i+1} saved as {filename}")



def load_text_storage_from_file(filename):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        # Create a new file if it doesn't exist or is corrupted
        with open(filename, "wb") as f:
            pickle.dump({}, f)
        return {}  # Return an empty dictionary if the file is newly created or corrupted

if os.path.exists(index_filename):
    index.load(index_filename)
    text_storage = load_text_storage_from_file(text_storage_filename)
else:
    # Build the index before saving it
    index.build(10)  # Build the index with 10 trees
    index.save(index_filename)

def save_text_storage_to_file(text_storage, filename):
    with open(filename, "wb") as f:
        pickle.dump(text_storage, f)

def store_conversation(user_input, response, text_storage):
    if len(text_storage) == 0:
        text_storage[0] = user_input
        text_storage[1] = response
    else:
        text_storage[len(text_storage)] = user_input
        text_storage[len(text_storage)] = response

    try:
        save_text_storage_to_file(text_storage, text_storage_filename)  # Save text_storage to a file
    except OSError as e:
        print(f"Error occurred while saving the text storage: {e}")

    return text_storage

def fetch_website_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        return text[:20000]  # Return the first 20,000 characters of the text
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching the website: {e}")
        return ""

def read_local_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        print(f"Error occurred while reading the local file: {e}")
        return ""


def handle_command(user_input):
    if user_input.startswith("#open "):
        url = user_input[6:].strip()  # Remove leading/trailing whitespaces
        
        # Check if the URL starts with 'http://' or 'https://', if not, prepend 'https://'
        if not url.startswith("http://") and not url.startswith("https://"):
            # Check if the URL starts with 'www.' or not, if not, prepend 'www.'
            if not url.startswith("www."):
                url = "www." + url
            url = "https://" + url
        
        webbrowser.open(url)
        return f"Opened {url} in your default web browser."



    elif user_input.startswith("#search "):
        query = user_input[8:]
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return f"Performed a web search for '{query}' in your default web browser."
    
    elif user_input.startswith("#read "):
        file_path = user_input[6:]
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return f"Contents of {file_path}:\n\n{content}"
        except Exception as e:
            return f"Error occurred while reading the file: {e}"

    elif user_input.startswith("#list "):
        directory = user_input[6:]
        try:
            files = os.listdir(directory)
            file_list = "\n".join(files)
            return f"Files in {directory}:\n\n{file_list}"
        except Exception as e:
            return f"Error occurred while listing files: {e}"

    elif user_input.startswith("#download "):
        parts = user_input[10:].split(" from ")
        if len(parts) != 2:
            return "Invalid command format. Use '@download [file] from [website]'."
        file_name, url = parts
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(file_name, 'wb') as file:
                file.write(response.content)
            return f"Downloaded {file_name} from {url}."
        except requests.exceptions.RequestException as e:
            return f"Error occurred while downloading the file: {e}"
        except Exception as e:
            return f"Error occurred while downloading the file: {e}"

    elif user_input.startswith("#extract "):
        file_or_image = user_input[9:]
        # Implement text extraction logic here
        return "Text extraction functionality is not implemented yet."

    elif user_input.startswith("#find "):
        parts = user_input[6:].split(" in ")
        if len(parts) != 2:
            return "Invalid command format. Use '@find [string] in [file or directory]'."
        search_string, target = parts
        try:
            if os.path.isfile(target):
                with open(target, 'r') as file:
                    content = file.read()
                if search_string in content:
                    return f"Found '{search_string}' in {target}."
                else:
                    return f"'{search_string}' not found in {target}."
            elif os.path.isdir(target):
                matches = []
                for root, dirs, files in os.walk(target):
                    for file in files:
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            content = f.read()
                        if search_string in content:
                            matches.append(file_path)
                if matches:
                    match_list = "\n".join(matches)
                    return f"Found '{search_string}' in the following files:\n\n{match_list}"
                else:
                    return f"'{search_string}' not found in {target}."
            else:
                return f"{target} is not a valid file or directory."
        except Exception as e:
            return f"Error occurred while searching: {e}"
    elif user_input.startswith(":@save"):
        if "```python" in user_input:
            save_code_snippet(user_input, "py")
        elif "```html" in user_input:
            save_code_snippet(user_input, "html")
        elif "```js" in user_input or "```javascript" in user_input:
            save_code_snippet(user_input, "js")
        elif "```css" in user_input:
            save_code_snippet(user_input, "css")
        else:
            print("No code snippets found in the response.")

    return ""

# Inside the main loop
while True:
    user_input = input("Enter a prompt (or 'quit' to exit): ")
    if user_input.lower() == 'quit':
        break

    # Check if the user input contains a command
    if user_input.startswith("#"):
        command_response = handle_command(user_input)
        if command_response:
            print(command_response)
        continue

    else:
        # Check if the user input contains a website URL or file path
        if "@" in user_input:
            domains = re.findall(r"@[\w.-]+", user_input)
            for domain in domains:
                url_or_domain = domain[1:].strip()  # Extract domain without the "@" symbol

                # Check if the input resembles a URL
                if re.match(r"(https?://)?(www\.)?[\w-]+\.[a-z]{2,}(\/\S*)?", url_or_domain):
                    # If the URL doesn't start with http:// or https://, prepend it
                    if not url_or_domain.startswith("http://") and not url_or_domain.startswith("https://"):
                        # Split the domain to check for subdomains
                        domain_parts = url_or_domain.split('.')
                        if len(domain_parts) > 2:
                            # If the URL doesn't start with www. and is not a subdomain, prepend it
                            if not url_or_domain.startswith("www."):
                                url_or_domain = "www." + url_or_domain
                        url_or_domain = "https://" + url_or_domain
                    website_text = fetch_website_text(url_or_domain)
                    user_input = user_input.replace(domain, website_text)
                elif url_or_domain.startswith("!"):
                    # If the input starts with @!, treat it as a file path
                    file_path = url_or_domain[1:]
                    file_content = read_local_file(file_path)
                    user_input = user_input.replace(domain, file_content)





    # Check if the user input is a command
    if user_input.startswith("@"):
        command_response = handle_command(user_input)
        if command_response:
            print(command_response)
        continue

    # Set the system message to provide instructions to the assistant
    system_message = {
        "role": "system",
        "content": "You are a helpful AI assistant."
    }



    # Create a chat completion request
    chat_completion = client.chat.completions.create(
        messages=[
            system_message,
            {
                "role": "user",
                "content": user_input,
            }
        ],
        model=model_choice,  # Use the selected model string
        temperature=0.7,
        max_tokens=max_tokens,  # Use the selected max_tokens value
        top_p=1,
        stop=None,
        stream=False,
    )

    # Extract the generated response from the chat completion
    response = chat_completion.choices[0].message.content
    text_storage = store_conversation(user_input, response, text_storage)
    save_code_snippet(response)
    print(response)