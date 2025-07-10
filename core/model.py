import json

from dacite import from_dict

from config.secret import GEMINI_KEY
from openai import OpenAI

from config.setup import setup_proxy

setup_proxy()

client = OpenAI(
    api_key=GEMINI_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


def call_model(system_prompt=None, user_prompt=None, output_schema_class=None):
    """
    调用语言模型。

    Args:
        system_prompt (str, optional): 系统提示。
        user_prompt (str, optional): 用户提示。
        output_schema_class (type, optional): 期望输出的 dataclass 类。
                                               如果提供，模型将被强制要求以该类的 JSON Schema 格式输出。

    Returns:
        - 如果提供了 output_schema_class，则返回该类的实例。
        - 否则，返回模型原始输出的字符串或字典。
    """
    messages = []

    # 默认 response_format
    api_response_format = {"type": "text"}

    if output_schema_class:
        # 1. 从 dataclass 生成 JSON Schema
        schema = output_schema_class.json_schema()

        # 2. 更新 system_prompt，要求模型遵循此 Schema
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

    # 调用 API
    response = client.chat.completions.create(
        model="gemini-2.5-flash",  # 或者你使用的其他模型
        messages=messages,
        response_format=api_response_format,  # 使用我们定义的 api_response_format
        temperature=0.8,
    )

    answer_content = response.choices[0].message.content

    # 根据是否需要结构化输出来处理结果
    if output_schema_class:
        try:
            # 将 JSON 字符串解析为字典
            json_data = json.loads(answer_content)
            # 使用 dacite 将字典转换为 dataclass 实例
            return from_dict(data_class=output_schema_class, data=json_data)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error parsing model response or creating dataclass instance: {e}")
            print(f"Raw model response:\n{answer_content}")
            return None  # 或者抛出异常
    else:
        # 如果是普通的 JSON 请求但没有指定 schema，则尝试解析
        if api_response_format.get("type") == "json_object":
            try:
                return json.loads(answer_content)
            except json.JSONDecodeError:
                return answer_content  # 解析失败则返回原始字符串
        return answer_content