import json
import re

from dacite import from_dict

from config.secret import GEMINI_KEY
from openai import OpenAI

from config.setup import setup_proxy

setup_proxy()

DEFAULT_CLIENT = OpenAI(
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
    api_response_format = {"type": "text"}

    if output_schema_class:
        schema = output_schema_class.json_schema()
        schema_prompt = (
            f"Please respond ONLY with a valid JSON object that strictly adheres to the following JSON Schema. "
            f"Do not include any other text, explanations, or markdown formatting like ```json. "
            f"The JSON object must match this schema:\n{json.dumps(schema, indent=2)}"
        )
        if system_prompt:
            system_prompt = f"{system_prompt}\n\n{schema_prompt}"
        else:
            system_prompt = schema_prompt
        api_response_format = {"type": "json_object"}

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if user_prompt:
        messages.append({"role": "user", "content": user_prompt})

    response = DEFAULT_CLIENT.chat.completions.create(
        model="gemini-1.5-flash",  # 使用你实际的模型
        messages=messages,
        response_format=api_response_format,
        temperature=0.8,
    )
    answer_content = response.choices[0].message.content
    print(answer_content)

    if output_schema_class:
        try:
            # --- START OF CHANGE ---

            # 2. 使用正则表达式从可能包含额外文本的响应中提取出 JSON 块。
            #    r'\{[\s\S]*\}' 会匹配从第一个 '{' 到最后一个 '}' 之间的所有内容。
            match = re.search(r'\{[\s\S]*\}', answer_content)

            if not match:
                # 如果连一个JSON对象都找不到，就抛出错误
                raise json.JSONDecodeError("No JSON object found in the model's response.", answer_content, 0)

            # 3. 获取匹配到的纯净的 JSON 字符串
            json_string = match.group(0)

            # 4. 将提取出的干净的 JSON 字符串解析为字典
            json_data = json.loads(json_string)

            # --- END OF CHANGE ---

            # 使用 dacite 将字典转换为 dataclass 实例
            return from_dict(data_class=output_schema_class, data=json_data)

        except (json.JSONDecodeError, Exception) as e:
            print(f"Error parsing model response or creating dataclass instance: {e}")
            print(f"Raw model response:\n{answer_content}")  # 打印原始、未清洗的响应，便于调试
            return None
    else:
        # 非结构化输出逻辑保持不变
        if api_response_format.get("type") == "json_object":
            try:
                return json.loads(answer_content)
            except json.JSONDecodeError:
                return answer_content
        return answer_content