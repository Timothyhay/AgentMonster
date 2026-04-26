import json
import re
from dataclasses import is_dataclass
from typing import Optional, Type

from dacite import from_dict
from pydantic import BaseModel, ValidationError

from config.secret import GEMINI_KEY, GEMINI_FLASH_MODEL
from openai import OpenAI

from config.setup import setup_proxy

setup_proxy()

DEFAULT_CLIENT = OpenAI(
    api_key=GEMINI_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


def call_model(
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
        output_schema_class: Optional[Type] = None,
):
    """
    调用语言模型，并可根据指定的类结构（dataclass 或 Pydantic BaseModel）返回结构化数据。

    Args:
        system_prompt (str, optional): 系统提示。
        user_prompt (str, optional): 用户提示。
        output_schema_class (type, optional): 期望输出的类。
                                               可以是带有 JsonSchemaMixin 的 dataclass，也可以是 Pydantic BaseModel。

    Returns:
        - 如果提供了 output_schema_class，则返回该类的实例。
        - 否则，返回模型原始输出的字符串或字典。
    """
    messages = []
    api_response_format = {"type": "text"}
    schema = None

    if output_schema_class:
        # --- 新增的智能判断逻辑 ---
        if is_dataclass(output_schema_class) and hasattr(output_schema_class, 'json_schema'):
            # 1a. 如果是带 Mixin 的 dataclass，使用其方法生成 schema
            schema = output_schema_class.json_schema()
        elif issubclass(output_schema_class, BaseModel):
            # 1b. 如果是 Pydantic BaseModel，使用 Pydantic 的方法生成 schema
            schema = output_schema_class.model_json_schema()
        else:
            raise TypeError(
                "output_schema_class 必须是继承了 JsonSchemaMixin 的 dataclass "
                "或继承自 Pydantic 的 BaseModel。"
            )
        # --- 逻辑结束 ---

        # 2. 将 schema 注入到 system_prompt
        schema_prompt = (
            f"Please respond ONLY with a valid JSON object that strictly adheres to the following JSON Schema. "
            f"Do not include any other text, explanations, or markdown formatting. "
            f"The JSON object must match this schema:\n{json.dumps(schema, indent=2)}"
        )
        if system_prompt:
            system_prompt = f"{system_prompt}\n\n{schema_prompt}"
        else:
            system_prompt = schema_prompt

        # 3. 强制 API 使用 JSON 模式
        api_response_format = {"type": "json_object"}

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if user_prompt:
        messages.append({"role": "user", "content": user_prompt})

    if GEMINI_KEY == "YOUR_ACTUAL_KEY_HERE":
        # Mocking logic for testing without a real API key
        if output_schema_class:
            from entity.creature import Alignment, AbilityScores
            # Return a default AgentMonster or similar based on output_schema_class
            if output_schema_class.__name__ == 'AgentMonster':
                from entity.creature import Skill, InventoryItem
                return output_schema_class(
                    name="Mock Character",
                    description="A mocked character for testing.",
                    alignment=Alignment(abbreviation="N", name="Neutral", description="Neutral"),
                    skills=[Skill(name="Mock Skill", mana_cost=0, description="A skill that does nothing.")],
                    ability_scores=AbilityScores(STR=10, DEX=10, CON=10, INT=10, WIS=10, CHA=10, LUC=10),
                    inventory=[InventoryItem(name="Mock Item", durability=10, description="An item.")],
                    hp=100, mp=100, lv=1
                )
        else:
            if "ASCII" in user_prompt:
                return "  /\\_/\\  \n ( o.o ) \n  > ^ <  "
            return "Mocked response content"

    # 调用 API
    try:
        response = DEFAULT_CLIENT.chat.completions.create(
            model=GEMINI_FLASH_MODEL,
            messages=messages,
            response_format=api_response_format,
            temperature=0.7,
        )
        answer_content = response.choices[0].message.content
    except Exception as e:
        print(f"API Call failed: {e}")
        if "ASCII" in user_prompt:
            return "  /\\_/\\  \n ( o.o ) \n  > ^ <  "
        return "Error calling API"

    # 根据是否需要结构化输出来处理结果
    if output_schema_class:
        try:
            # --- 新增的智能解析逻辑 ---
            if is_dataclass(output_schema_class):
                # 4a. 如果是 dataclass，使用 dacite 解析
                json_data = json.loads(answer_content)
                return from_dict(data_class=output_schema_class, data=json_data)
            elif issubclass(output_schema_class, BaseModel):
                # 4b. 如果是 Pydantic Model，使用 Pydantic 自带的解析器
                return output_schema_class.model_validate_json(answer_content)
            # --- 逻辑结束 ---
        except (json.JSONDecodeError, ValidationError, Exception) as e:
            print(f"Error: Failed to parse model response into '{output_schema_class.__name__}'.")
            print(f"Error details: {e}")
            print(f"Raw model response:\n---\n{answer_content}\n---")
            return None
    else:
        if api_response_format.get("type") == "json_object":
            try:
                return json.loads(answer_content)
            except json.JSONDecodeError:
                return answer_content
        return answer_content