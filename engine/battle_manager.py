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

        # 1. Observation Phase
        obs = self.brain.observe(
            active_agent, 
            self.environment, 
            self.history[-4:], 
            self.impressions[active_agent.name],
            self.last_action_power
        )
        self.impressions[active_agent.name] = obs.impression
        
        if obs.damage > 0:
            active_agent.hp -= obs.damage
            self.stage.set_reaction(active_idx + 1, f"HP-{obs.damage}!!", duration=0.5)

        # 2. Decision Phase
        action = self.brain.decide_action(
            active_agent,
            self.environment,
            obs,
            self.history[-4:]
        )

        # 3. Execution Phase & Animation
        print(f"🧠 [{active_agent.name} 想法]: {action.thought}")
        
        # Mapping action types/descriptions to effects
        effect = "spark"
        desc_lower = action.description.lower()
        if "火" in desc_lower or "fire" in desc_lower: effect = "fire"
        elif "冰" in desc_lower or "ice" in desc_lower: effect = "ice"
        elif "砍" in desc_lower or "斩" in desc_lower or "slash" in desc_lower: effect = "slash"
        
        # Dynamic Movement
        if action.type == "攻击" or action.type == "物理":
            orig_pos = self.stage.pos1 if active_idx == 0 else self.stage.pos2
            target_pos = self.stage.pos2 if active_idx == 0 else self.stage.pos1
            approach_pos = target_pos - 1 if target_pos > orig_pos else target_pos + 1
            
            self.stage.animate_move(active_idx + 1, approach_pos)
            self.stage.animate_action(active_idx + 1, effect, target_pos)
            self.stage.animate_move(active_idx + 1, orig_pos)
        else:
            self.stage.animate_action(active_idx + 1, effect)

        active_agent.mp -= action.mana_cost
        self.last_action_power = action.power
        
        # 5. State Update
        self.history.append(f"{active_agent.name}: {action.description}")
        self.current_turn += 1

    def is_over(self) -> bool:
        return any(p.hp <= 0 for p in self.participants)

    def get_winner(self) -> Optional[AgentMonster]:
        alive = [p for p in self.participants if p.hp > 0]
        return alive[0] if len(alive) == 1 else None
