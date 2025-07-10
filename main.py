import os
import json
import textwrap
from dataclasses import dataclass, field
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

# --- 1. 准备工作：加载 API 密钥并初始化客户端 ---
from config.secret import GEMINI_KEY
from google import genai

# setup_proxy()
from core.model import call_model
from entity.creature import AgentMonster
from prompt.prompt import create_creature_system_prompt

os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"


client = OpenAI(
    api_key=GEMINI_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


def create_monster(query: str):
    creature = call_model(system_prompt=create_creature_system_prompt,
                          user_prompt=query,
                          output_schema_class=AgentMonster)
    creature.init_basic_status()
    return creature

## https://open.spotify.com/track/4LsLiCvF7whO3wNqgqS8Mo?si=337440aaef174b25

# 模拟一回合的行动 ---
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


# --- 4. 主程序：创建 Agent 并开始模拟 ---
if __name__ == "__main__":
    sample_character_description = """
    我的伙伴是来自不列颠的骑士王，代号为Saber，真名是阿尔托莉雅·潘德拉贡。她本性高洁，忠诚而善良。我使用来自古代不列颠的神秘信物将她召唤而来。
    她拥有很强的直觉、对魔力技能，也就是对各种魔法类攻击和控制都能有一定抵抗能力。
    她使用叫风王结界的技能用风的力量扭曲光线的散射，使敌人无法看清她的武器——誓约胜利之剑。
    敌人能看清这把圣剑时，就是她发动宝具的时候：这是一种使用圣剑将强大魔力蓄力后放出的毁灭性范围攻击。
    
    同时她也是一位大胃王，在直率的性格下有可爱的一面。
    """
    saber = create_monster(sample_character_description)
    print(saber.to_json)

    sample_character_description = """
    这是一位眼神如蓝宝石一般纯净闪耀的冒险者，大家都叫他R。他是一位用剑和魔法的高手，但却不常使用寻常的剑，而是通过凝聚空气中的水汽等成分组成一把冰刃作为常用武器。
    他的身体有很强的魔法亲和性，由于他对冰属性魔法的极高天赋，使他可以借助空气中的魔力与水汽修复自己的身体。这种对空气的利用也允许他制作致密冰晶组成的寒冰护甲。
    他对极强的学习天赋和意志力，在他下定决心后没有什么可以阻止他。
    
    他一直随身携带一柄皓月长剑，剑格是一个月牙型的空腔。这把武器比起剑更像权杖，因为它的独特设计使它成为无与伦比的的魔力导体，
    他没有太多关于过去的回忆，但他的心灵也如冰晶一样善良纯洁；但在广阔多重宇宙中的冒险经历让他逐渐理解人性。但——这世界上只有一种英雄主义，他依然热爱自己的人生。
    """
    player = create_monster(sample_character_description)
    print(player.to_json)


    print("--- 欢迎来到 LLM Agent Monster 战斗模拟器 MVP ---")

    # # 创建两个 Agent Monster
    # monster_a = AgentMonster(
    #     name="熔岩巨像",
    #     personality="暴躁，直接，崇尚绝对的力量，脑子里只有'碾碎'二字，行动大开大合。",
    #     skills=["熔岩重拳", "火山咆哮", "坚硬岩石皮肤"]
    # )
    #
    # monster_b = AgentMonster(
    #     name="诡影刺客",
    #     personality="狡猾，冷静，喜欢从阴影中发动突袭，善于利用环境和敌人的弱点。",
    #     skills=["暗影步", "背刺", "毒刃"]
    # )
    #
    # # 设定环境
    game_environment = "这是一个现代都市的公园里。公园有路灯、秋千、沙坑、滑梯和跷跷板。周围有自动售货机。"

    # 初始化战斗
    game_history = []
    active_agent, opponent = player, saber

    print("\n[战斗开始!]")
    print(f"环境: {game_environment}")
    print(f"对战双方: {active_agent.name} vs {opponent.name}")
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


# EXAMPLE
"""
[战斗开始!]
环境: 这是一个现代都市的公园里。公园有路灯、秋千、沙坑、滑梯和跷跷板。周围有自动售货机。
对战双方: R vs 阿尔托莉雅·潘德拉贡
--------------------
--- 第 1 回合 ---

[系统] 正在为 R 思考行动...
🧠 [R 的想法]: 阿尔托莉雅拥有强大的'对魔力'，这使得纯粹的冰系魔法攻击效率低下。作为一名精通剑术的冒险者，我应该利用我的冰刃和敏捷优势进行物理攻击，同时辅以冰系力量强化威力。'冰刃凝聚'能以极低的消耗增强我的主武器，这既能造成有效伤害，又能保存MP以应对后续战况，比如使用'寒冰护甲'进行防御，或是'极寒自愈'恢复伤势。初次交锋，我需要试探她的真实实力和'风王结界'的范围。
⚔️ [R 的行动]: 疾风冰斩
묘 [R的眼神如冰晶般锐利，他身形一闪，敏捷地跃向阿尔托莉雅。空气中的水汽在他手中迅速凝聚，化作一道锋利的冰刃，其威力在瞬间得到强化。他凭借精湛的剑术，将冰刃化为一道带着彻骨寒意的流光，直取对手。这迅疾而精准的一击，试图穿透风王结界的阻碍。]
--- 第 2 回合 ---

[系统] 正在为 阿尔托莉雅·潘德拉贡 思考行动...
🧠 [阿尔托莉雅·潘德拉贡 的想法]: R在上一回合对我发动了攻击，虽然风王结界有效抵御，但我也需要给予回击。现在并非使用宝具的最好时机，R的生命值尚高，而我的MP需要留存。作为骑士，我擅长的是直接而强力的剑术。利用风王结界的隐匿优势，我可以发动一次出其不意的迅捷斩击，既能消耗对手，又能保持自身MP的充裕，为后续的战斗做好准备。
⚔️ [阿尔托莉雅·潘德拉贡 的行动]: 风王结界·迅捷斩击
묘 [阿尔托莉雅的眼神坚定，她凭借对风王结界的精妙操控，将圣剑完全隐匿于扭曲的光线之后。她身形如风般迅捷，在R尚未完全反应过来之际，圣剑带着无形的凌厉之势，划破空气，直取其身。这一击无声无息，却蕴含着骑士王纯粹的力量与精准。]
--- 第 3 回合 ---

[系统] 正在为 R 思考行动...
🧠 [R 的想法]: 阿尔托莉雅的“风王结界”让她的攻击难以预测，R在上一回合因此受了伤。直接的攻击可能再次被隐形效果规避，而单纯防御也无法解决核心问题。R决定利用他冰属性魔法的“控场”能力和对水汽的精妙操控，制造一场冰霜迷雾。这不仅能阻碍对方视线，更关键的是，他希望通过密集的冰晶干扰甚至暂时破除“风王结界”对光线的扭曲效果，从而揭示圣剑的真正位置，为接下来的反击创造机会。这符合他快速学习和适应的特性，并且不直接依赖于伤害输出，避免了阿尔托莉雅的“对魔力”抗性。MP消耗20是合理的战术技能消耗。
⚔️ [R 的行动]: 冰霜迷雾
묘 [R的眼神变得深邃，他深吸一口气，周围空气中的水汽仿佛被无形的力量牵引，迅速凝聚并极速冷却。一股带着彻骨寒意的浓密冰霜迷雾以R为中心迅速扩散，笼罩了公园的一部分区域。这迷雾不仅阻碍视线，更试图以其密集的冰晶干扰风王结界对光线的扭曲，期望能让阿尔托莉雅的圣剑显露出哪怕一丝轮廓。]
--- 第 4 回合 ---

[系统] 正在为 阿尔托莉雅·潘德拉贡 思考行动...
🧠 [阿尔托莉雅·潘德拉贡 的想法]: R的冰霜迷雾试图干扰风王结界并暴露圣剑。阿尔托莉雅作为一名直率且强大的骑士，不会被这种控场伎俩所困扰。相反，她将R的行动视为一个使用宝具的信号。宝具“誓约胜利之剑”是光之洪流，其强大的光芒和冲击力能够完全穿透或蒸发冰雾，从而完美克制R的防御性策略。同时，R的HP已经受损，此时释放高伤害宝具可以争取一击定胜负的机会，避免R利用“极寒自愈”恢复。阿尔托莉雅拥有足够的MP来释放宝具，这是当前最有效率且最具决定性的行动。
⚔️ [阿尔托莉雅·潘德拉贡 的行动]: 誓约胜利之剑
묘 [阿尔托莉雅感受着R周围冰霜迷雾的魔力波动，嘴角微微上扬。她明白R试图通过干扰风王结界来窥探圣剑的真貌。然而，这恰恰为她提供了一个绝佳的机会。她不再压抑圣剑中涌动的魔力，将“风王结界”瞬间解除，璀璨的金光骤然冲破迷雾，照亮了整个公园。她举起完全显现的圣剑，将汇聚的魔力化作一道炽热的光之洪流，伴随着“Excalibur！”的庄严宣告，撕裂冰雾，直冲R而去，誓要将一切障碍与敌人尽数斩灭。]

--- 模拟结束 ---

Process finished with exit code 0

"""