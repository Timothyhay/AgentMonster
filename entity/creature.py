
# --- 2. 定义我们的 Agent Monster 数据结构 ---
@dataclass
class AgentMonster:
    name: str
    description: str
    skills: List[str]
    hp: int = 100
    mp: int = 100
    lv: int = 0

    def to_prompt_string(self) -> str:
        """将 Agent 的信息格式化为适合 Prompt 的字符串"""
        skill_str = ", ".join(self.skills)
        return (
            f"名称: {self.name}\n"
            f"性格: {self.personality}\n"
            f"当前HP: {self.hp}\n"
            f"技能: [{skill_str}]"
        )