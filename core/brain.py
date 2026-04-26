import textwrap
import json
from typing import List, Optional
from pydantic import BaseModel
from core.model import call_model, DEFAULT_CLIENT
from entity.creature import AgentMonster

class Action(BaseModel):
    action: str
    description: str
    type: str
    thought: str
    mana_cost: int
    power: int

class Observation(BaseModel):
    impression: str = ""
    damage: int = 0

class Brain:
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        self.model_name = model_name

    def observe(self, creature: AgentMonster, environment: str, history: List[str], 
                last_impression: str, incoming_power: int) -> Observation:
        history_str = "\n".join(history) if history else "战斗刚刚开始。"
        
        prompt = textwrap.dedent(f"""
            你是一个游戏AI裁判。分析局势并输出该角色的观察结果。
            ** 角色信息：** {creature.to_json()}
            ** 环境：** {environment}
            ** 过去的印象：** {last_impression}
            ** 战斗记录：** {history_str}
            ** 上回合对手招式威力：** {incoming_power}
            请输出 JSON: "impression" (简短概述), "damage" (角色受到的实际伤害)。
        """)
        
        return call_model(user_prompt=prompt, output_schema_class=Observation)

    def decide_action(self, creature: AgentMonster, environment: str, 
                      observation: Observation, history: List[str]) -> Action:
        history_str = "\n".join(history) if history else "战斗刚刚开始。"
        
        system_prompt = textwrap.dedent("""
            你是一个游戏AI裁判。决定角色的行动。
            必须返回 JSON:
            - "action": 行动名称
            - "type"：攻击/吟唱/防御/其他
            - "description": 生动的行动描述
            - "thought": 角色内心想法
            - "mana_cost": MP消耗
            - "power": 预计威力
        """)

        user_prompt = textwrap.dedent(f"""
            # 环境: {environment}
            # 历史: {history_str}
            # 角色: {creature.to_json()}
            # 观察: {observation.impression}
            现在是 {creature.name} 的回合。请决策。
        """)

        # Fallback logic for mock keys is handled in call_model, but we keep the structure
        return call_model(system_prompt=system_prompt, user_prompt=user_prompt, output_schema_class=Action)
