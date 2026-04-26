from typing import List, Dict
from entity.creature import AgentMonster
from core.brain import Brain, Observation, Action
from ui.stage import BattleStage

class BattleManager:
    def __init__(self, participants: List[AgentMonster], environment: str, stage: BattleStage):
        self.participants = participants
        self.environment = environment
        self.stage = stage
        self.history = []
        self.brain = Brain()
        self.current_turn = 0
        self.last_action_power = 0
        self.impressions = {p.name: "" for p in participants}

    def run_turn(self):
        active_idx = self.current_turn % len(self.participants)
        opponent_idx = (active_idx + 1) % len(self.participants)
        
        active_agent = self.participants[active_idx]
        opponent = self.participants[opponent_idx]

        print(f"\n--- 第 {self.current_turn + 1} 回合: {active_agent.name} ---")

        # 1. Observation Phase
        obs = self.brain.observe(
            active_agent, 
            self.environment, 
            self.history[-4:], 
            self.impressions[active_agent.name],
            self.last_action_power
        )
        self.impressions[active_agent.name] = obs.impression
        active_agent.hp -= obs.damage
        if obs.damage > 0:
            print(f"💥 {active_agent.name} 受到了 {obs.damage} 点伤害!")

        # 2. Decision Phase
        action = self.brain.decide_action(
            active_agent,
            self.environment,
            obs,
            self.history[-4:]
        )

        # 3. Execution Phase
        print(f"🧠 [{active_agent.name} 想法]: {action.thought}")
        print(f"⚔️ [{active_agent.name} 行动]: {action.action}")
        print(f"묘 [{action.description}]")

        active_agent.mp -= action.mana_cost
        self.last_action_power = action.power
        
        # 4. Animation/UI Phase
        if action.type == "吟唱" or action.type == "魔法":
            self.stage.animate_spell(active_idx + 1)
        else:
            self.stage.animate_attack(active_idx + 1)

        # 5. State Update
        self.history.append(f"{active_agent.name}: {action.description}")
        self.current_turn += 1

    def is_over(self) -> bool:
        return any(p.hp <= 0 for p in self.participants)

    def get_winner(self) -> Optional[AgentMonster]:
        alive = [p for p in self.participants if p.hp > 0]
        return alive[0] if len(alive) == 1 else None
