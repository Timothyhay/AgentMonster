import json
import textwrap
from dataclasses import dataclass, field, asdict
from typing import List, Dict, ClassVar
from dataclasses_jsonschema import JsonSchemaMixin

@dataclass
class AbilityScores(JsonSchemaMixin):
    STR: int  # 力量 Strength: 力气
    DEX: int  # 敏捷 Dexterity: 灵活性、反应能力和平衡感
    CON: int  # 体质 Constitution: 健康程度和耐力
    INT: int  # 智力 Intelligence: 推理能力和记忆力
    WIS: int  # 感知 Wisdom: 洞察力和精神坚韧程度
    CHA: int  # 魅力 Charisma: 自信、仪态以及吸引力
    LUC: int  # 幸运 Luck: 影响随机事件和机遇的因素

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
class InventoryItem(JsonSchemaMixin):
    name: str         # 物品名称
    durability: int   # 物品耐久度
    description: str  # 物品描述

    def __post_init__(self):
        """验证耐久度非负"""
        if self.durability < 0:
            raise ValueError(f"耐久度不能为负数: {self.durability}")


@dataclass
class Skill(JsonSchemaMixin):
    name: str         # 技能名
    mana_cost: int    # MP消耗
    description: str  # 技能描述

    def __post_init__(self):
        """验证MP消耗非负"""
        if self.mana_cost < 0:
            raise ValueError(f"MP消耗不能为负数: {self.mana_cost}")



@dataclass
class Alignment(JsonSchemaMixin):
    abbreviation: str  # 阵营缩写，例如 "LG"
    name: str          # 阵营全称，例如 "Lawful Good"
    description: str   # 阵营描述

    # 1. 将 _alignments 声明为类变量，而不是实例字段
    #    这样 asdict 默认就不会处理它
    _alignments: ClassVar[Dict[str, 'Alignment']] = {}
    # 存储所有阵营的字典，用于通过缩写索引
    # _alignments: Dict[str, 'Alignment'] = field(default_factory=dict)

    @classmethod
    def get_by_abbreviation(cls, abbreviation: str) -> 'Alignment':
        """通过缩写获取阵营"""
        return cls._alignments.get(abbreviation.upper(), None)

    @classmethod
    def all_alignments(cls) -> Dict[str, 'Alignment']:
        """返回所有阵营的字典"""
        return cls._alignments

    def __post_init__(self):
        """在实例化后将自身添加到 _alignments 字典"""
        self._alignments[self.abbreviation.upper()] = self


@dataclass
class AgentMonster(JsonSchemaMixin):
    name: str
    description: str
    alignment: Alignment
    skills: List[Skill]
    ability_scores: AbilityScores
    inventory: list[InventoryItem]
    hp: int = 100
    mp: int = 100
    lv: int = 0

    def init_basic_status(self):
        combat_stat = self.ability_scores.derive_combat_stats()
        self.hp = combat_stat["hp"]
        self.mp = combat_stat["mp"]

    def to_prompt_string(self) -> str:
        """将 Agent 的信息格式化为适合 Prompt 的字符串"""
        skill_str = "; ".join(
            f"{skill.name} (MP消耗: {skill.mana_cost}, 描述: {skill.description})"
            for skill in self.skills
        )
        return textwrap.dedent(f"""
            **名称:**  {self.name}
            **描述:**  {self.description}
            **当前HP:** {self.hp}
            **当前MP:** {self.mp}
            **能力等级:** {self.ability_scores}
            **特殊技能:** [{skill_str}]
            **"
        """)

    def to_json(self, indent: int = 2) -> str:
        """
        将 AgentMonster 实例的所有属性序列化为 JSON 格式的字符串。

        Args:
            indent (int, optional): JSON 输出的缩进级别，用于美化输出。默认为 2。
                                   如果为 None，则不进行美化，输出为紧凑格式。

        Returns:
            str: 代表该实例的 JSON 字符串。
        """
        # asdict 会递归地将 dataclass 及其嵌套的 dataclass 转换为字典
        obj_dict = asdict(self)

        # json.dumps 将字典转换为 JSON 字符串
        # ensure_ascii=False 确保中文字符等能正常显示，而不是被转义
        return json.dumps(obj_dict, indent=indent, ensure_ascii=False)



# 初始化所有阵营
ALIGNMENTS = [
    Alignment(
        abbreviation="LG",
        name="Lawful Good",
        description="守序善良生物尽力做社会认为正确的事情。毫不犹豫地与不公作斗争、保护无辜者的人，可能是守序善良的。"
    ),
    Alignment(
        abbreviation="NG",
        name="Neutral Good",
        description="中立善良生物尽其所能地做行善，在规则限度内行事，但并不感觉被规则束缚。按照他人需求帮助他们的和善之人，可能是中立善良的。"
    ),
    Alignment(
        abbreviation="CG",
        name="Chaotic Good",
        description="混乱善良生物依照其良心行动，几乎不在意别人怎么想。拦路抢劫某个冷酷男爵的税官，将赃款用于帮助穷人的人，可能是混乱善良的。"
    ),
    Alignment(
        abbreviation="LN",
        name="Lawful Neutral",
        description="守序中立的个体依法律、传统或个人信条办事。遵守一套严格的行事准则，且不会被临危者的请求或邪恶的诱惑动摇的人，可能是守序中立的。"
    ),
    Alignment(
        abbreviation="N",
        name="Neutral",
        description="绝对中立阵营是那些宁可回避道德问题，不愿意选边站，按当时看来最好的做法行事的人的阵营。厌倦了道德思辨的人可能是绝对中立的。"
    ),
    Alignment(
        abbreviation="CN",
        name="Chaotic Neutral",
        description="混乱中立的生物按其一时奇想行事，认为他们的个人自由比其他一切都重要。靠小聪明谋生、四处游荡的流氓，可能是混乱中立的。"
    ),
    Alignment(
        abbreviation="LE",
        name="Lawful Evil",
        description="守序邪恶的生物有条不紊地在传统、忠诚或秩序的规定之内获取他们想要的东西。在利用市民同时又阴谋获取权力的贵族，可能是守序邪恶的。"
    ),
    Alignment(
        abbreviation="NE",
        name="Neutral Evil",
        description="中立邪恶是那些不在意在追逐自身想要的东西过程中造成破坏的人所属的阵营。随心所欲抢劫杀人的罪犯，可能是中立邪恶的。"
    ),
    Alignment(
        abbreviation="CE",
        name="Chaotic Evil",
        description="混乱邪恶的生物会随意施暴，这种暴力受其憎恨或嗜血欲望的驱策。"
    ),
    Alignment(
        abbreviation="UC",
        name="Unaligned Creatures",
        description="缺乏理性思维能力的生物没有阵营归属，即它们是无阵营。比如，普通鲨鱼shark是凶猛的掠食者，但它们并不邪恶，因此它们无阵营。"
    ),
]


"""
    e.g.
"""

character_r = AgentMonster(name='R', description='一位拥有蓝宝石般纯净眼眸的冒险者。他是冰系魔法与剑术的大师，以凝聚空气中的水汽形成冰刃作战。他拥有由冰晶组成的、宝石般坚固的外骨骼和护甲，并通过操纵空气进行快速自我修复。R具有卓越的学习天赋和坚韧的意志力，能迅速洞察环境与敌人的弱点。在极端情况下，他能运用急速结晶化能力瞬间冻结接触到的有机生命体血液。', alignment=Alignment(abbreviation='NG', name='中立善良', description='中立善良生物尽其所能地做行善，在规则限度内行事，但并不感觉被规则束缚。按照他人需求帮助他们的和善之人，可能是中立善良的。'), skills=[Skill(name='急速血液结晶化', mana_cost=30, description='通过接触迅速冻结目标体内的血液，使其瞬间停止活动。对无血液或非有机生命体效果有限或无效。')], ability_scores=AbilityScores(STR=13, DEX=17, CON=16, INT=18, WIS=17, CHA=14, LUC=13), inventory=[InventoryItem(name='皓月长剑', durability=999, description='一柄剑格呈月牙形空腔的长剑。与其说是剑，不如说更像权杖，因为它独特的设计使其成为无与伦比的魔力导体。')], hp=163, mp=0, lv=0)
character_saber = AgentMonster(name='Saber', description='The Knight King of Britain, a highly noble, loyal, and kind warrior. She possesses exceptional intuition and resistance to magical attacks. In combat, she uses the Wind King Barrier to conceal her holy sword, the Sword of Promised Victory (Excalibur), making her attacks unpredictable. When revealing her true power, she unleashes a devastating ranged attack with Excalibur. Despite her regal bearing, she has a surprisingly large appetite and a straightforward, sometimes cute, personality.', alignment=Alignment(abbreviation='LG', name='守序善良', description='守序善良生物尽力做社会认为正确的事情。毫不犹豫地与不公作斗争、保护无辜者的人，可能是守序善良的.'), skills=[Skill(name='风王结界', mana_cost=10, description='使用风的力量扭曲光线，隐藏武器外观，使敌人难以看清所持的剑。'), Skill(name='对魔力', mana_cost=0, description='对魔法攻击和控制效果有很强的抗性。'), Skill(name='直觉', mana_cost=0, description='增强感知和预判能力，提升规避危险和战斗反应的速度。'), Skill(name='宝具：誓约胜利之剑', mana_cost=80, description='释放圣剑蓄积的强大魔力，造成大范围毁灭性打击。')], ability_scores=AbilityScores(STR=18, DEX=17, CON=18, INT=12, WIS=16, CHA=14, LUC=12), inventory=[InventoryItem(name='誓约胜利之剑', durability=999, description='来自湖中仙女的圣剑，蕴含强大魔力，是骑士王最重要的武器。')], hp=145, mp=3, lv=0)