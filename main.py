import os
import json
from dataclasses import dataclass, field
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

# --- 1. 准备工作：加载 API 密钥并初始化客户端 ---
from config.secret import GEMINI_KEY
from google import genai

# setup_proxy()
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

# --- 1. 准备工作：加载 API 密钥并初始化客户端 ---


# 为 Gemini 配置 API 密钥
client = OpenAI(
    api_key=GEMINI_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# --- 2. 定义我们的 Agent Monster 数据结构 ---
@dataclass
class AgentMonster:
    name: str
    personality: str
    skills: List[str]
    hp: int = 100

    def to_prompt_string(self) -> str:
        """将 Agent 的信息格式化为适合 Prompt 的字符串"""
        skill_str = ", ".join(self.skills)
        return (
            f"名称: {self.name}\n"
            f"性格: {self.personality}\n"
            f"当前HP: {self.hp}\n"
            f"技能: [{skill_str}]"
        )


# --- 3. 核心逻辑：模拟一回合的行动 ---
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

    # --- 这是整个游戏最关键的部分：Prompt Engineering ---
    system_prompt = """
你是一个富有想象力的游戏AI裁判。你的任务是根据角色设定和当前战况，决定一个角色的行动。
请严格遵守以下规则：
1. 深入分析当前行动者的性格和技能。
2. 结合环境和对手的状态，选择一个最合理的行动。
3. 你的输出必须是一个JSON对象，不能包含任何其他文字。
4. JSON对象必须包含三个字段：
   - "action_name": 一个简短的行动名称（通常是技能名或一个描述性短语）。
   - "description": 一段生动的、符合角色性格的行动描述。
   - "thought_process": 角色为什么这么做的内心想法，用于调试。
"""

    user_prompt = f"""
# 战斗环境
{environment}

# 战斗历史
{history_str}

# 当前行动者
{active_agent.to_prompt_string()}

# 对手
{opponent.to_prompt_string()}

# 你的任务
现在是 **{active_agent.name}** 的回合。请根据它的性格、技能和当前局势，决定它的行动。请以JSON格式返回结果。
"""

    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash",  # gpt-4o 或 gpt-3.5-turbo 都可以，gpt-4o 效果更好
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
            "thought_process": "LLM API调用失败，执行备用方案。"
        }


# --- 4. 主程序：创建 Agent 并开始模拟 ---
if __name__ == "__main__":
    print("--- 欢迎来到 LLM Agent Monster 战斗模拟器 MVP ---")

    # 创建两个 Agent Monster
    monster_a = AgentMonster(
        name="熔岩巨像",
        personality="暴躁，直接，崇尚绝对的力量，脑子里只有'碾碎'二字，行动大开大合。",
        skills=["熔岩重拳", "火山咆哮", "坚硬岩石皮肤"]
    )

    monster_b = AgentMonster(
        name="诡影刺客",
        personality="狡猾，冷静，喜欢从阴影中发动突袭，善于利用环境和敌人的弱点。",
        skills=["暗影步", "背刺", "毒刃"]
    )

    # 设定环境
    game_environment = "场景是一个古老的、布满残垣断壁的竞技场，到处都是可以藏身的石柱和阴影。"

    # 初始化战斗
    game_history = []
    active_agent, opponent = monster_a, monster_b

    print("\n[战斗开始!]")
    print(f"环境: {game_environment}")
    print(f"对战双方: {monster_a.name} vs {monster_b.name}")
    print("-" * 20)

    # 模拟 4 个回合
    for turn in range(1, 5):
        print(f"--- 第 {turn} 回合 ---")

        # 核心：调用 LLM 模拟一回合
        action_result = simulate_turn(active_agent, opponent, game_environment, game_history[-2:])  # 只传递最近2条历史记录

        # 打印结果
        print(f"🧠 [{active_agent.name} 的想法]: {action_result.get('thought_process', '无')}")
        print(f"⚔️ [{active_agent.name} 的行动]: {action_result['action_name']}")
        print(f"묘 [{action_result['description']}]")

        # 更新历史记录
        game_history.append(f"第{turn}回合, {active_agent.name} {action_result['description']}")

        # 交换行动方
        active_agent, opponent = opponent, active_agent

    print("\n--- 模拟结束 ---")