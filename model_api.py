#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型API调用模块
支持多种大模型提供商的统一接口
"""

import aiohttp
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """大模型配置类"""
    name: str
    api_key: str
    base_url: str
    model: str
    provider: str

class ModelAPIClient:
    """大模型API客户端"""
    
    def __init__(self, timeout: int = 60):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
    
    async def call_model(self, config: ModelConfig, prompt: str, **kwargs) -> str:
        """统一的模型调用接口"""
        try:
            if config.provider == "openai":
                return await self._call_openai(config, prompt, **kwargs)
            elif config.provider == "anthropic":
                return await self._call_anthropic(config, prompt, **kwargs)
            elif config.provider == "google":
                return await self._call_google(config, prompt, **kwargs)
            elif config.provider == "dashscope":
                return await self._call_dashscope(config, prompt, **kwargs)
            else:
                raise ValueError(f"不支持的提供商: {config.provider}")
        except Exception as e:
            logger.error(f"调用模型 {config.name} 失败: {e}")
            raise
    
    async def _call_openai(self, config: ModelConfig, prompt: str, **kwargs) -> str:
        """调用OpenAI API"""
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": config.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000)
        }
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{config.base_url}/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API错误 {response.status}: {error_text}")
                
                result = await response.json()
                return result["choices"][0]["message"]["content"]
    
    async def _call_anthropic(self, config: ModelConfig, prompt: str, **kwargs) -> str:
        """调用Anthropic Claude API"""
        headers = {
            "x-api-key": config.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": config.model,
            "max_tokens": kwargs.get("max_tokens", 2000),
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{config.base_url}/v1/messages",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API错误 {response.status}: {error_text}")
                
                result = await response.json()
                return result["content"][0]["text"]
    
    async def _call_google(self, config: ModelConfig, prompt: str, **kwargs) -> str:
        """调用Google Gemini API"""
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "maxOutputTokens": kwargs.get("max_tokens", 2000)
            }
        }
        
        url = f"{config.base_url}/models/{config.model}:generateContent?key={config.api_key}"
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Google API错误 {response.status}: {error_text}")
                
                result = await response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
    
    async def _call_dashscope(self, config: ModelConfig, prompt: str, **kwargs) -> str:
        """调用阿里云通义千问API"""
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": config.model,
            "input": {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000)
            }
        }
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{config.base_url}/services/aigc/text-generation/generation",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"DashScope API错误 {response.status}: {error_text}")
                
                result = await response.json()
                return result["output"]["text"]

# 全局API客户端实例
api_client = ModelAPIClient()