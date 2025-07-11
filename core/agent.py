import textwrap
from typing import List

from entity.creature import AgentMonster


def simulate_turn(active_agent: AgentMonster, opponent: AgentMonster, environment: str, history: List[str]) -> dict:
    """
    使用 LLM 决定一个 Agent 的行动。

    Args:
        active_agent: 当前行动的 Agent。
        opponent: 对手 Agent。
        environment: 当前的环境描述。
        history: 最近的战斗历史记录。

    Returns:
        一个包含行动信息的字典。
    """
    print(f"\n[系统] 正在为 {active_agent.name} 思考行动...")

    # 构建最近历史的字符串
    history_str = "\n".join(history) if history else "战斗刚刚开始。"

    observation_prompt = """
    你需要扮演该角色，根据该角色的属性、技能与对手的战斗记录进行思考。
    """

    system_prompt = textwrap.dedent("""
    你是一个富有想象力的游戏AI裁判。你的任务是根据角色设定和当前战况，决定一个角色的行动。
    请严格遵守以下规则：
    1. 深入分析当前行动者的描述和技能。
    2. 结合环境和对手的状态，选择一个最合理的行动。
    3. 角色特殊技能只代表他拥有的某个不寻常的技能，这个角色根据其描述可以使用其他合理技能。角色需要使用这些未列出的技能时请推断一个合理的MP消耗。
    4. 角色的属性值不代表绝对的强弱，结合环境、描述和幸运可以使战斗有不一样的结果。
    5. 你的输出必须是一个JSON对象，不能包含任何其他文字。
    6. JSON对象必须包含下文字段：
       - "action_name": 一个简短的行动名称（通常是技能名或一个描述性短语）。
       - "description": 一段生动的、符合角色性格的行动描述。
       - "thought_process": 角色为什么这么做的内心想法，用于调试。
       - "damage": 一个整型数值，表示这次行动对对手造成了多少伤害。对于不造成伤害的技能，这个字段应该是0。
    """)

    user_prompt = textwrap.dedent(f"""
    # 战斗环境
    {environment}

    # 战斗历史
    {history_str}

    # 当前行动者
    {active_agent.to_prompt_string()}

    # 对手
    {opponent.to_prompt_string()}

    # 你的任务
    现在是 **{active_agent.name}** 的回合。请根据它的描述、技能和当前局势，决定它的行动。请以JSON格式返回结果。
    """)

    try:
        response = client.chat.completions.create(
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
            "action_name": "发呆",
            "description": f"{active_agent.name} 似乎因为某些未知原因，愣在原地，什么也没做。",
            "thought_process": "LLM API调用失败，执行备用方案。",
            "damage": 0
        }
