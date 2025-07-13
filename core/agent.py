import json
import textwrap
from typing import List

from pydantic import BaseModel

from core.model import call_model, DEFAULT_CLIENT
from entity.creature import AgentMonster


class InterAction(BaseModel):
    action: str
    description: str
    type: str
    thought: str
    mana_cost: int
    power: int


def observe(active_agent: AgentMonster, environment: str, history: List[str], impression="") -> str:
    # 构建最近历史的字符串
    history_str = "\n".join(history) if history else "战斗刚刚开始。"
    if not impression:
        impression = f"{active_agent.name} 与对手初次见面。"

    observation_prompt = textwrap.dedent(f"""
    你是一个富有想象力的游戏AI裁判。你的任务是根据该角色的属性、特性、与对手的战斗记录，以该角色的视角进行思考，观察对手与环境。
    通常来说角色的智力、感知越高能够越快理解对手的技能和魔法；战斗经验丰富的角色可能更容易理解对手的战术。

    ** 扮演角色信息：**
    {active_agent.to_json()}
    
    ** 环境：**
    {environment}

    ** 战斗记录：**
    {history_str}

    ** 过去的印象：**
    {impression}

    总之，请分析已有的情报，以该角色的视角输出一个字符串，表示当前回合该角色对对手的印象或理解，帮助该角色更好地战斗。
    请注意，这句话应当简短但能全面地概述该角色迄今为止的观察。因为它会替换掉之前该角色的观察。
    """)

    observation = call_model(user_prompt=observation_prompt)
    return observation


# 模拟一回合的行动 ---
def simulate_turn(active_agent: AgentMonster, environment: str, observation: str, history: List[str]) -> dict:
    """
    使用 LLM 决定一个 Agent 的行动。

    Args:
        active_agent: 当前行动的 Agent。
        environment: 战斗环境。
        observation: 对环境和对手的观察。
        history: 最近的战斗历史记录。

    Returns:
        一个包含行动信息的字典。
    """
    print(f"\n[系统] 正在为 {active_agent.name} 思考行动...")

    # 构建最近历史的字符串
    history_str = "\n".join(history) if history else "战斗刚刚开始。"

    system_prompt = textwrap.dedent("""
    你是一个富有想象力的游戏AI裁判。你的任务是根据角色设定和当前战况，决定一个角色的行动。
    请严格遵守以下规则：
    1. 深入分析当前行动者的描述和技能。
    2. 结合环境和对手的状态，选择一个最合理的行动。
    3. 角色特殊技能只代表他拥有的某个不寻常的技能，这个角色根据其描述可以使用其他合理技能。角色需要使用这些未列出的技能时请推断一个合理的MP消耗。
    4. 角色的属性值不代表绝对的强弱，结合环境、描述和幸运可以使战斗有不一样的结果。
    5. 你的输出必须是一个JSON对象，不能包含任何其他文字。
    6. JSON对象必须包含下文字段：
       - "action": 一个简短的行动名称（通常是技能名或一个描述性短语）。
       - "type"：行动类型。攻击、吟唱、防御或其他。
       - "description": 一段生动的、符合角色性格的行动描述。
       - "thought": 角色思考这么行动的内心想法。
       - "mana_cost": 这次行动消耗的MP。这个值不能大于角色剩余MP，但极特殊情况下（如竭尽全力时）可以适当调整。简单攻击的MP消耗可以为0。
       - "power": 这次行动预计会对对手造成多少伤害。对于不造成伤害的行动，这个字段应该是0。
    """)

    user_prompt = textwrap.dedent(f"""
    # 战斗环境
    {environment}

    # 最近的战斗历史
    {history_str}

    # 当前行动者
    {active_agent.to_json()}

    # 对对手的观察
    {observation}

    # 你的任务
    现在是 **{active_agent.name}** 的回合。请根据它的描述、技能和当前局势，决定它的行动。请以JSON格式返回结果。
    """)

    try:
        response = DEFAULT_CLIENT.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},  # 强制要求模型输出JSON
            temperature=0.8,  # 增加一点创造性
        )

        action_data = json.loads(response.choices[0].message.content)
        return action_data

    except Exception as e:
        print(f"[错误] 调用 LLM 失败: {e}")
        # 返回一个保底的行动，防止程序崩溃
        return {
            "action": "发呆",
            "type": "其他",
            "description": f"{active_agent.name} 似乎因为某些未知原因，愣在原地，什么也没做。",
            "thought": "LLM API调用失败，执行备用方案。",
            "mana_cost": 0,
            "power": 0
        }
