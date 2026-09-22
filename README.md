# free-deepseek-py

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-Chat-purple.svg)](https://chat.deepseek.com/)

Local asynchronous Python client for DeepSeek Chat. Provides chat, file uploads, and image recognition using your DeepSeek account.

This is not the official DeepSeek API and not a local model. It is a browser-based client (works with DeepSeek Chat web version **2.5**): you authenticate in DeepSeek Chat, save the session, and use DeepSeek directly from your Python code.

## Overview
- **Chats** — list, create, load, rename, delete chats
- **Messages** — send prompts, receive responses, regenerate, stream chunks
- **Files** — upload files and attach to messages
- **Vision** — analyze images via file uploads
- **TTS** — generate text-to-speech audio for a specific message (Ogg Opus), with voice selection
- **Search** — enable internet search for real-time information
- **Thinking** — enable chain-of-thought reasoning
- **PoW challenge** — solve Proof-of-Work challenges for DeepSeek requests
- **Ticket** — get auth tickets for WebSocket connections

## Requirements
- Python 3.10+

## Quick Start
```bash
git clone https://github.com/z-ikura-t/free-deepseek-py
cd free-deepseek-py
pip install -r requirements.txt
```

## DeepSeek Chat Authorization

### Auto

Run the built-in script to automatically get your token:

```bash
python auth.py
```

A Chrome window will open. Log in or sign up to DeepSeek Chat, then return to the terminal and press Enter. The token will be saved to `.env` automatically.

> **Note:** Google Chrome is required for auto authorization. If Chrome is not installed, use the manual method below.

### Manual

Create a .env file in the root directory and add your DeepSeek token:

```env
DEEPSEEK_TOKEN=your_token_here
```

How to get the token manually:
1. Open **DeepSeek Chat** in your browser and log in
2. Open **Developer Tools** (F12 or right-click > Inspect)
3. Go to the **Network** tab
4. Send a message in DeepSeek Chat
5. Find the `completion` request in the **Network** tab
6. Open the **Headers** section
7. Find **Authorization** header under **Request Headers**
8. Copy the token value after `Bearer`  (without the "Bearer " prefix)

**Important:**
- Do not share your token with anyone.
- The token is stored locally in your `.env` file.
- Do not commit or publish your `.env` file.
- The token will change when you log out of your DeepSeek account.

## Methods

### Health

Check API health and DeepSeek token validity.

```python
result = await client.check_health()
```

**Response:**
```python
{
    'ok': True,
    'user_id': 'a0e2f909-ae4e-4ade-81d6-249e4c29d795',
    'detail': None,
    'service': 'free-deepseek-py',
}
```

### Load chats by index range

Return chats from `start` (inclusive) to `end` (exclusive).

```python
chats = await client.load_chats_by_range(0, 10)
```

### Load chats by timestamp

Return chats updated between two timestamps.

```python
import time

end = time.time()
start = end - 7 * 24 * 3600
chats = await client.load_chats_by_timestamp(start, end)
```

**Replace:**
- `start` — start timestamp (inclusive)
- `end` — end timestamp (exclusive)

### Delete chats

Delete one or more chats by their IDs.

```python
await client.delete_chats([chat_id1, chat_id2])
```

**Replace:**
- `chat_id1`, `chat_id2` — actual chat IDs

### Create a chat

Create a new empty chat.

```python
chat = await client.create_chat()
```

### Load a chat

Load a chat with all its messages by ID.

```python
chat = await client.load_chat(chat_id)
```

**Replace:**
- `chat_id` — actual chat ID

### Update chat title

Change the title of a chat by ID.

```python
result = await client.update_chat_title(chat_id, new_title)
```

**Replace:**
- `chat_id` — actual chat ID
- `new_title` — new chat title

### Upload files

Upload one or more files to DeepSeek and get their file IDs.

```python
files = await client.upload_files([
    '/path/to/document.pdf',
    '/path/to/image.png',
])
```

**Replace:**
- `/path/to/document.pdf`, `/path/to/image.png` — absolute paths to your files

**Important:**
- File size limit: 100 MB per file.

### Send a message

Send a user message and receive the assistant's response. Supports streaming for real-time output, file attachments (including images for vision-based analysis), web search, and thinking mode.

```python
response = await client.completion(
    chat_id=chat_id, 
    parent_message_id=None, 
    prompt='What is in this image?', 
    file_ids=[file_id1, file_id2]
)
```

**Replace:**
- `chat_id` — actual chat ID
- `parent_message_id` — `None` for the first message, or the ID of the previous assistant message
- `prompt` — your message text
- `file_id1`, `file_id2` — file IDs from **Upload files**

### Send a message (streaming)

```python
is_thinking = False
async for chunk in client.completion_stream(chat_id, parent_message_id, prompt, file_ids=[file_id1, file_id2]):
    if chunk['type'] == 'think':
        if not is_thinking:
            print('\n[think] ', end='', flush=True)
            is_thinking = True
        print(chunk['content'], end='', flush=True)
    
    elif chunk['type'] == 'response':
        if is_thinking:
            print('\n\n[response] ', end='', flush=True)
            is_thinking = False
        print(chunk['content'], end='', flush=True)
    
    elif chunk['type'] == 'message_data':
        print(f'\nid={chunk["message_id"]} role={chunk["role"]}')
```

**Replace:**
- `chat_id` — actual chat ID
- `parent_message_id` — `None` for the first message, or the ID of the previous assistant message
- `prompt` — your message text
- `file_id1`, `file_id2` — file IDs from **Upload files**

**Chunk types:**
- `message_data` — final message IDs
- `think` — model's internal reasoning
- `response` — final answer text
- `file` — attached file
- `error` — error occurred during streaming

### Regenerate a message

Regenerate an assistant's response in an existing chat. Supports web search and thinking mode.

```python
response = await client.regenerate(
    chat_id=chat_id,
    message_id=message_id
)
```

**Replace:**
- `chat_id` — actual chat ID
- `message_id` — ID of the **assistant** message

### Regenerate a message (streaming)

```python
async for chunk in client.regenerate_stream(chat_id, message_id):
    print(chunk)
```

**Replace:**
- `chat_id` — actual chat ID
- `message_id` — ID of the **assistant** message

**Chunk types:**
- `message_data` — final message IDs
- `think` — model's internal reasoning
- `response` — final answer text
- `error` — error occurred during streaming

### Generate audio for an assistant message

Returns **Ogg Opus** audio bytes.

```python
audio = await client.get_audio(chat_id, message_id)

with open('audio.opus', 'wb') as f:
    f.write(audio['audio_bytes'])
```

**Replace:**
- `chat_id` — actual chat ID
- `message_id` — ID of the **assistant** message

**Important:**
- Only assistant messages can be voiced.
- No streaming for TTS — the full audio is generated before returning.

### List voices

Return all available TTS voices.

```python
voices = await client.load_voices()
```

### Get current voice

Return the currently selected TTS voice.

```python
voice = await client.get_voice()
```

### Set voice

Change the current TTS voice.

```python
await client.set_voice(voice_id)
```

**Replace:**
- `voice_id` — ID of the voice to use

### Settings

#### Search

Enables internet search. Allows DeepSeek to retrieve real-time information from the web.

```python
search = client.get_search()
client.set_search(True)
```

#### Thinking

Enables chain-of-thought reasoning. Improves accuracy on complex tasks.

```python
thinking = client.get_thinking()
client.set_thinking(True)
```

#### Token

Shows or updates your DeepSeek authentication token.

```python
client.get_token()
await client.set_token('new_token_here')
```

### Advanced

#### Solve PoW Challenge

```python
result = await client.solve_pow_challenge(target_type)
```

**Replace:**
- `target_type` — `'message'` for chat or `'file'` for uploads

> **Note:** usually called internally — you don't need it unless you're adding a new method.

#### Get auth ticket

Returns a temporary ticket used for WebSocket connections.

```python
ticket = await client.get_ticket(scope)
```

**Replace:**
- `scope` — ticket scope. For example, `'tts'` for TTS WebSocket.

**Important:**
- Tickets expire in **10 minutes**.

## Usage Example

```python
import asyncio
from free_deepseek_py.client import DeepSeekClient

client = DeepSeekClient()

async def main():
    # Load chats
    chats = await client.load_chats_by_range(0, 1)
    print(f'Total chats: {len(chats["chats"])}')
    if not chats['chats']: return
    
    # Take the last chat
    last_chat_id = chats['chats'][0]['chat_id']
    print(f'Last chat ID: {last_chat_id}')
    
    # Load the chat
    chat = await client.load_chat(last_chat_id)
    current_message_id = chat['current_message_id']
    print(f'Current message ID: {current_message_id}')
    
    # Upload a file
    files = await client.upload_files(['/path/to/image.jpg'])
    if not files['files'][0]['ok']: raise Exception(files['files'][0]['detail'])
    file_id = files['files'][0]['file_id']
    print(f'Uploaded: {file_id}')
    
    # Enable search and thinking
    client.set_search(True)
    client.set_thinking(True)
    print('Search and thinking enabled')
    
    # Send a message with the file
    response = await client.completion(
        chat_id=last_chat_id,
        parent_message_id=current_message_id,
        prompt='What is in this image?',
        file_ids=[file_id],
    )
    print('Response:', response['assistant']['content'])
    
    # Change voice
    await client.set_voice('echo')
    print('Voice: echo')
    
    # Generate audio
    audio = await client.get_audio(
        last_chat_id,
        response['assistant']['message_id'],
    )
    with open('response.opus', 'wb') as f:
        f.write(audio['audio_bytes'])
    print('Saved: response.opus')


asyncio.run(main())
```

**This example:**
- Loads the last chat
- Gets its `current_message_id`
- Uploads an image
- Enables search and thinking
- Sends a message with the image
- Changes voice to `echo`
- Generates and saves TTS audio

## Limitations

- This is an unofficial client, use responsibly.
- The client is for local development and testing purposes only.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.