import uuid
from typing import Literal
from loguru import logger

from .src import settings
from .src.files import Files
from .src.chat import Chat
from .src import credentials
from .src.chats import Chats
from .src.tts.tts_client import TTS
from .src.message import Message
from .src.health import check_health
from .src.pow_challenge.pow_challenge import POWChallenge

from . import validation
from .src.exceptions import APIError, ValidationError, UnknownError

logger.remove()



class DeepSeekClient:
    def __init__(self):
        self._chat = Chat
        self._chats = Chats
        self._files = Files
        self._message = Message
        self._pow_challenge = POWChallenge
    
    
    async def check_health(self) -> dict:
        health_status = await check_health()
        return {
            **health_status, 
            'service': 'free-deepseek-py'
        }
    
    
    async def load_chats_by_range(self, start: int | None = None, end: int | None = None) -> dict:
        validation.validate_int(start, 'start', allow_none=True)
        validation.validate_int(end, 'end', allow_none=True)
        
        chats = await self._chats.load_range(start, end)
        return chats
    
    
    async def load_chats_by_timestamp(self, start: float | None = None, end: float | None = None) -> dict:
        validation.validate_timestamp(start, 'start')
        validation.validate_timestamp(end, 'end')
        
        chats = await self._chats.load_timestamp(start, end)
        return chats
    
    
    async def delete_chats(self, chat_ids: list[str]) -> None:
        validation.validate_chat_ids(chat_ids)
        
        await self._chats.delete(chat_ids)
    
    
    async def create_chat(self) -> dict:
        new_chat = await self._chat.create()
        return new_chat
    
    
    async def load_chat(self, chat_id: str) -> dict:
        validation.validate_chat_id(chat_id)
        
        chat = await self._chat.load(chat_id)
        return chat
    
    
    async def update_chat_title(self, chat_id: str, new_title: str) -> dict:
        validation.validate_chat_id(chat_id)
        validation.validate_str(new_title, 'new_title')
        
        new_chat_title = await self._chat.update_title(chat_id, new_title)
        return new_chat_title
    
    
    async def upload_files(self, file_paths: list[str]) -> dict:
        validation.validate_list(file_paths, 'file_paths', str)
        
        uploaded_files = await self._files.upload(file_paths)
        return uploaded_files
    
    
    async def completion(self, chat_id: str, parent_message_id: int | None, prompt: str, file_ids: list[str] | None = None) -> dict:
        validation.validate_chat_id(chat_id)
        validation.validate_int(parent_message_id, 'parent_message_id', min_value=2, allow_none=True)
        validation.validate_str(prompt, 'prompt')
        if not file_ids is None: validation.validate_list(file_ids, 'file_ids', str)
        
        message = await self._message.completion(chat_id, parent_message_id, prompt, file_ids=file_ids)
        return message
    
    
    async def completion_stream(self, chat_id: str, parent_message_id: int | None, prompt: str, file_ids: list[str] | None = None):
        validation.validate_chat_id(chat_id)
        validation.validate_int(parent_message_id, 'parent_message_id', min_value=2, allow_none=True)
        validation.validate_str(prompt, 'prompt')
        if not file_ids is None: validation.validate_list(file_ids, 'file_ids', str)
        
        message_gen = self._message.completion_stream(chat_id, parent_message_id, prompt, file_ids=file_ids)
        async for chunk in message_gen:
            yield chunk
    
    
    async def solve_pow_challenge(self, target_type: Literal['message', 'file']) -> dict:
        validation.validate_str(target_type, 'target_type')
       
        if target_type == 'message': target_path = '/api/v0/chat/completion'
        elif target_type == 'file': target_path = '/api/v0/file/upload_file'
        else: raise ValidationError('Target type must be "message" or "file"')
        
        x_ds_pow_response = await self._pow_challenge.solve(target_path)
        return x_ds_pow_response
    
    
    async def get_ticket(self, scope: Literal['tts']) -> dict:
        validation.validate_str(scope, 'scope')
        
        ticket = await credentials.get_ticket(scope)
        return ticket
    
    
    async def get_audio(self, chat_id: str, message_id: int) -> dict:
        validation.validate_chat_id(chat_id)
        validation.validate_int(message_id, 'message_id', min_value=1)
        
        audio = await TTS.get_audio(chat_id, message_id)
        return audio
    
    
    async def load_voices(self) -> dict:
        voices = await TTS.load_voices()
        return {
            'voices': voices['voices']
        }
    
    
    async def get_voice(self) -> dict:
        voices = await TTS.load_voices()
        return {
            'voice_id': voices['current_voice_id']
        }
    
    
    async def set_voice(self, new_voice_id: str) -> dict:
        validation.validate_str(new_voice_id, 'new_voice_id')
        
        new_voice_id = await TTS.set_voice(new_voice_id)
        return new_voice_id
    
    
    def get_search(self) -> dict:
        return {
            'enabled': settings.DEEPSEEK_SEARCH_ENABLED
        }
    
    
    def set_search(self, enabled: bool = False) -> dict:
        validation.validate_bool(enabled, 'enabled')
        
        settings.DEEPSEEK_SEARCH_ENABLED = enabled
        return {
            'enabled': settings.DEEPSEEK_SEARCH_ENABLED
        }
    
    
    def get_thinking(self) -> dict:
        return {
            'enabled': settings.DEEPSEEK_THINKING_ENABLED
        }
    
    
    def set_thinking(self, enabled: bool = False) -> dict:
        validation.validate_bool(enabled, 'enabled')
        
        settings.DEEPSEEK_THINKING_ENABLED = enabled
        return {
            'enabled': settings.DEEPSEEK_THINKING_ENABLED
        }
    
    
    def get_token(self) -> dict:
        return {
            'token': settings.DEEPSEEK_TOKEN
        }
    
    
    async def set_token(self, new_token: str) -> dict:
        validation.validate_str(new_token, 'new_token')
        
        await credentials.update_token(new_token)
        return {
            'token': settings.DEEPSEEK_TOKEN
        }