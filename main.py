import os
from openai import OpenAI
from config.secret import GEMINI_KEY
from core.model import call_model
from entity.creature import AgentMonster
from memory.valhalla import summon_from_valhalla
from prompt.prompt import create_creature_system_prompt
from engine.battle_manager import BattleManager
from ui.stage import BattleStage

def create_monster(query: str) -> AgentMonster:
    creature = call_model(system_prompt=create_creature_system_prompt,
                          user_prompt=query,
                          output_schema_class=AgentMonster)
    creature.init_basic_status()
    if not creature.avatar:
        creature.generate_avatar()
    return creature

def main():
    print("--- 欢迎来到 AgentMonster: 重构版 ---")
    
    # 1. Setup participants
    p1 = create_monster(summon_from_valhalla("r"))
    p2 = create_monster(summon_from_valhalla("saber"))
    
    # 2. Setup environment and UI
    game_env = "这是一个充满樱花的古老神社庭院。微风拂过，花瓣飘落。"
    stage = BattleStage(p1, p2)
    
    # 3. Initialize Engine
    engine = BattleManager([p1, p2], game_env, stage)
    
    print(f"\n[战斗开始!]")
    print(f"环境: {game_env}")
    print(f"对战双方: {p1.name} vs {p2.name}")
    print("-" * 20)

    # 4. Game Loop
    while not engine.is_over() and engine.current_turn < 20:
        engine.run_turn()

    # 5. Result
    winner = engine.get_winner()
    if winner:
        print(f"\n🏆 胜利者是: {winner.name}!")
    else:
        print("\n🤝 战斗以平局结束。")

if __name__ == "__main__":
    main()
