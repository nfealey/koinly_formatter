python3 -m venv path/to/venv
source path/to/venv/bin/activate
python3 -m pip install aider-install

export PATH="/Users/nick/.local/bin:$PATH"
aider --model llama3-70b --api-key groq=<key> d