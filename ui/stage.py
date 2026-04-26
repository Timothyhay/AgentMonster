import time
import os
import sys

class BattleStage:
    def __init__(self, agent1, agent2):
        self.agent1 = agent1
        self.agent2 = agent2
        self.width = 80

    def clear_screen(self):
        # os.system('cls' if os.name == 'nt' else 'clear')
        # In a CLI agent environment, clearing the screen might not be ideal or work as expected.
        # We'll just print a separator.
        print("\n" * 2 + "=" * self.width + "\n")

    def format_avatar(self, avatar_str):
        lines = avatar_str.strip().split('\n')
        return lines

    def draw(self, effect1="", effect2=""):
        self.clear_screen()
        
        # Draw HP bars
        hp1_percent = max(0, self.agent1.hp) / self.agent1.ability_scores.derive_combat_stats()["hp"]
        hp2_percent = max(0, self.agent2.hp) / self.agent2.ability_scores.derive_combat_stats()["hp"]
        
        hp1_bar = "[" + "#" * int(hp1_percent * 20) + "-" * (20 - int(hp1_percent * 20)) + "]"
        hp2_bar = "[" + "#" * int(hp2_percent * 20) + "-" * (20 - int(hp2_percent * 20)) + "]"
        
        print(f"{self.agent1.name:^30} | {self.agent2.name:^30}")
        print(f"HP: {hp1_bar} {self.agent1.hp:<5} | HP: {hp2_bar} {self.agent2.hp:<5}")
        print("-" * self.width)
        
        # Draw Avatars
        avatar1_lines = self.format_avatar(self.agent1.avatar)
        avatar2_lines = self.format_avatar(self.agent2.avatar)
        
        max_lines = max(len(avatar1_lines), len(avatar2_lines))
        
        for i in range(max_lines):
            line1 = avatar1_lines[i] if i < len(avatar1_lines) else ""
            line2 = avatar2_lines[i] if i < len(avatar2_lines) else ""
            
            # Pad lines to ensure alignment
            line1_display = f"{line1:<35}"
            line2_display = f"{line2:>35}"
            
            # Insert effects if any
            mid = " vs "
            if effect1 and i == max_lines // 2:
                mid = f" {effect1} "
            elif effect2 and i == max_lines // 2:
                mid = f" {effect2} "
                
            print(f"{line1_display} {mid} {line2_display}")
        
        print("-" * self.width)

    def animate_attack(self, attacker_num):
        """attacker_num: 1 or 2"""
        frames = [">>>", " >>>", "  >>>", "   >>>", "    >>>"]
        if attacker_num == 2:
            frames = ["<<<", "<<< ", "<<<  ", "<<<   ", "<<<    "]
            
        for frame in frames:
            if attacker_num == 1:
                self.draw(effect1=frame)
            else:
                self.draw(effect2=frame)
            time.sleep(0.1)
        self.draw()

    def animate_spell(self, attacker_num):
        frames = [" * ", "( * )", "(( * ))", " ( * ) ", "  *  "]
        for frame in frames:
            if attacker_num == 1:
                self.draw(effect1=frame)
            else:
                self.draw(effect2=frame)
            time.sleep(0.1)
        self.draw()

    def animate_idle(self):
        self.draw()
