import time
import os
from ui.assets import get_effect

class BattleStage:
    def __init__(self, agent1, agent2):
        self.agent1 = agent1
        self.agent2 = agent2
        self.width = 80
        # Character positions (0 to 10)
        self.pos1 = 1
        self.pos2 = 8
        self.reaction1 = ""
        self.reaction2 = ""

    def clear_screen(self):
        # Using a fixed number of newlines to simulate a refresh
        print("\n" * 30)
        print("=" * self.width)

    def format_avatar(self, avatar_str):
        return avatar_str.strip().split('\n')

    def draw(self, effect_pos=None, effect_frame=None):
        self.clear_screen()
        
        # Draw Status
        hp1_max = self.agent1.ability_scores.derive_combat_stats()["hp"]
        hp2_max = self.agent2.ability_scores.derive_combat_stats()["hp"]
        hp1_p = max(0, self.agent1.hp) / hp1_max
        hp2_p = max(0, self.agent2.hp) / hp2_max
        
        bar1 = "[" + "#" * int(hp1_p * 15) + "-" * (15 - int(hp1_p * 15)) + "]"
        bar2 = "[" + "#" * int(hp2_p * 15) + "-" * (15 - int(hp2_p * 15)) + "]"
        
        print(f"{self.agent1.name[:15]:<15} {bar1} HP:{self.agent1.hp}/{hp1_max} | "
              f"{self.agent2.name[:15]:>15} {bar2} HP:{self.agent2.hp}/{hp2_max}")
        print("-" * self.width)

        # Draw Stage
        avatar1 = self.format_avatar(self.agent1.avatar)
        avatar2 = self.format_avatar(self.agent2.avatar)
        
        max_h = max(len(avatar1), len(avatar2)) + 2 # Extra space for reactions
        
        for h in range(max_h):
            line = [" "] * self.width
            
            # Reactions (Top row)
            if h == 0:
                if self.reaction1:
                    self._write_to_line(line, self.pos1 * 7, self.reaction1)
                if self.reaction2:
                    self._write_to_line(line, self.pos2 * 7, self.reaction2)
            
            # Avatars
            else:
                ah = h - 1
                if ah < len(avatar1):
                    self._write_to_line(line, self.pos1 * 7, avatar1[ah])
                if ah < len(avatar2):
                    self._write_to_line(line, self.pos2 * 7, avatar2[ah])
            
            # Effects
            if effect_pos is not None and effect_frame is not None:
                if h < len(effect_frame):
                    self._write_to_line(line, effect_pos * 7, effect_frame[h])

            print("".join(line))
        
        print("-" * self.width)

    def _write_to_line(self, line_list, start_pos, text):
        for i, char in enumerate(text):
            if 0 <= start_pos + i < len(line_list):
                line_list[start_pos + i] = char

    def animate_move(self, agent_num, target_pos):
        current_pos = self.pos1 if agent_num == 1 else self.pos2
        step = 1 if target_pos > current_pos else -1
        
        for p in range(current_pos, target_pos + step, step):
            if agent_num == 1: self.pos1 = p
            else: self.pos2 = p
            self.draw()
            time.sleep(0.05)

    def animate_action(self, agent_num, effect_name, target_pos=None):
        """Animates an action from agent to a target position"""
        start_pos = self.pos1 if agent_num == 1 else self.pos2
        if target_pos is None:
            target_pos = self.pos2 if agent_num == 1 else self.pos1
            
        effect = get_effect(effect_name)
        
        # If it's a projectile or movement-based
        if effect_name in ["fire", "ice", "spark"]:
            # Travel
            steps = range(start_pos, target_pos, 1 if target_pos > start_pos else -1)
            for p in steps:
                self.draw(effect_pos=p, effect_frame=effect)
                time.sleep(0.08)
        
        # Impact
        impact = get_effect("hit")
        self.draw(effect_pos=target_pos, effect_frame=impact)
        time.sleep(0.2)
        self.draw()

    def set_reaction(self, agent_num, text, duration=1.0):
        if agent_num == 1: self.reaction1 = text
        else: self.reaction2 = text
        self.draw()
        time.sleep(duration)
        if agent_num == 1: self.reaction1 = ""
        else: self.reaction2 = ""
        self.draw()
