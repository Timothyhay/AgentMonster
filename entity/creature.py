from dataclasses import dataclass
from typing import List

@dataclass
class AbilityScores:
    STR: int  # 力量
    DEX: int  # 敏捷
    CON: int  # 体质
    INT: int  # 智力
    WIS: int  # 感知
    CHA: int  # 魅力
    LUC: int  # 幸运

    def derive_combat_stats(self) -> dict:
        """根据能力值计算战斗属性"""
        return {
            "hp": self.CON * 10 + self.STR,
            "mp": self.INT * 5 + self.CHA * 2,
            "patk": self.STR * 2 + self.DEX * 0.5,
            "matk": self.INT * 2 + self.WIS,
            "speed": self.DEX * 1.2 + self.INT * 0.5,
            "hit": self.DEX * 1.5 + self.WIS * 0.5,
            "evasion": self.DEX * 2,
            "critical": self.DEX * 0.5 + self.CHA * 0.3
        }

    def to_ability_level(self) -> dict:
        """将能力值转换为等级（E 到 S）"""
        def get_level(value: int) -> str:
            if value <= 10:
                return "E"
            elif value <= 20:
                return "D"
            elif value <= 30:
                return "C"
            elif value <= 40:
                return "B"
            elif value <= 50:
                return "A"
            return "S"

        return {
            "STR": get_level(self.STR),
            "DEX": get_level(self.DEX),
            "CON": get_level(self.CON),
            "INT": get_level(self.INT),
            "WIS": get_level(self.WIS),
            "CHA": get_level(self.CHA),
            "LUC": get_level(self.LUC),
        }


@dataclass
class AgentMonster:
    name: str
    description: str
    skills: List[str]
    ability_scores: AbilityScores
    hp: int = 100
    mp: int = 100
    lv: int = 0

    def init_basic_status(self):
        combat_stat = self.ability_scores.derive_combat_stats()
        self.hp = combat_stat["hp"]
        self.mp = combat_stat["mp"]

    def to_prompt_string(self) -> str:
        """将 Agent 的信息格式化为适合 Prompt 的字符串"""
        skill_str = ", ".join(self.skills)
        return (
            f"**名称:**  {self.name}\n"
            f"**描述:**  {self.description}\n"
            f"**当前HP:** {self.hp}\n"
            f"**当前MP:** {self.mp}\n"
            f"**特殊技能:** [{skill_str}]"
        )





