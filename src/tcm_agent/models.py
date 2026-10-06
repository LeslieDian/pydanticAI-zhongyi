"""模型工厂。注意 OpenAIProvider 会按模型名推断 profile。

若结构化输出/工具调用异常，需显式传 profile=...。"""
from __future__ import annotations

import logging

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from .config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    MINIMAX_API_KEY,
    MINIMAX_BASE_URL,
    MINIMAX_MODEL,
)

logger = logging.getLogger(__name__)


def build_model(name: str = "minimax"):
    """构建模型实例。

    Args:
        name: "minimax" 或 "deepseek"

    Returns:
        pydantic_ai 可接受的 model 标识（字符串或 OpenAIChatModel 实例）
    """
    if name == "minimax":
        if not MINIMAX_API_KEY:
            raise ValueError("MINIMAX_API_KEY 未设置（参考 .env.example）")
        # 注意：base_url 是 api.minimaxi.com（不是 .com）
        provider = OpenAIProvider(base_url=MINIMAX_BASE_URL, api_key=MINIMAX_API_KEY)
        model = OpenAIChatModel(MINIMAX_MODEL, provider=provider)
        logger.info("Built MiniMax model: %s @ %s", MINIMAX_MODEL, MINIMAX_BASE_URL)
        return model

    if name == "deepseek":
        # pydantic-ai 内置 deepseek provider
        logger.info("Using built-in deepseek provider")
        return f"deepseek:{DEEPSEEK_MODEL}"

    raise ValueError(f"未知模型：{name}（支持 minimax / deepseek）")
