# AI Assistant with Web Browsing and File Handling Capabilities

This Python script provides an AI assistant with the ability to browse the web, search Google, read and list files, download files, find strings within files or directories, and save code snippets from responses. It utilizes the Groq API for language model capabilities and the Annoy library for efficient vector similarity search.

## Features

- **Interactive AI Assistant**: Engage in natural language conversations with the AI assistant.
- **Web Browsing**: Open websites in the default web browser using the `#open` command.
- **Google Search**: Perform web searches on Google using the `#search` command.
- **File Reading**: Read the contents of a local file using the `#read` command.
- **File Listing**: List files in a directory using the `#list` command.
- **File Download**: Download files from a website using the `#download` command.
- **String Search**: Find occurrences of a string within a file or directory using the `#find` command.
- **Code Snippet Saving**: Save code snippets from the AI assistant's responses as separate files.

## Usage

1. Install the required dependencies by running `pip install -r requirements.txt`.
2. Set your Groq API key as an environment variable named `GROQ_API_KEY`. (Get one here: https://console.groq.com/keys)
3. Run the script with `python ai_assistant.py`.
4. Follow the prompts to select a language model and provide input.
5. Use the available commands (e.g., `#open`, `#search`, `#read`, `#list`, `#download`, `#find`) to interact with the AI assistant and perform various tasks.
6. To exit the script, enter `quit`.

## Command Reference

- `#open <url>`: Open a website in the default web browser.
- `#search <query>`: Perform a web search on Google for the specified query.
- `#read <file_path>`: Read the contents of a local file.
- `#list <directory>`: List files in the specified directory.
- `#download <file_name> from <url>`: Download a file from a website.
- `#find <string> in <file_or_directory>`: Find occurrences of a string within a file or directory.
- `@website <url>`: Include a website contents in the conversation context (allows multiple websites to be included).
- `#extract <file_or_image>`: Extract text from a file or image (not implemented yet).

## Code Structure

The script is organized into several functions:

- `get_model_choice()`: Prompts the user to select a language model.
- `save_code_snippet(response)`: Saves code snippets from the AI assistant's response as separate files.
- `load_text_storage_from_file(filename)`: Loads the conversation history from a file.
- `save_text_storage_to_file(text_storage, filename)`: Saves the conversation history to a file.
- `store_conversation(user_input, response, text_storage)`: Stores the user input and AI assistant's response in the conversation history.
- `fetch_website_text(url)`: Fetches the text content of a website.
- `read_local_file(file_path)`: Reads the content of a local file.
- `handle_command(user_input)`: Handles various commands entered by the user.

The main loop of the script handles user input, processes commands, and interacts with the Groq API to generate responses from the selected language model.

## Dependencies

- `groq`: Groq API client library for interacting with language models.
- `annoy`: Library for approximate nearest neighbor search, used for efficient vector similarity search.
- `requests`: Library for making HTTP requests to fetch website content.
- `beautifulsoup4`: Library for parsing HTML content from websites.
- `webbrowser`: Module for opening websites in the default web browser.
- `subprocess`: Module for running external commands.
- `re`: Module for working with regular expressions.
- `string`: Module for string operations.
- `random`: Module for generating random values.
- `uuid`: Module for generating universally unique identifiers.
- `tempfile`: Module for creating temporary directories.
- `pickle`: Module for serializing and deserializing Python objects.
- `numpy`: Library for numerical operations, required by the Annoy library.
- `os`: Module for interacting with the operating system.

## License

This project is licensed under the [MIT License](LICENSE).
