from entity.creature import AgentMonster, character_r


def check_health_loss(character: AgentMonster):
    combat_stat = character.ability_scores.derive_combat_stats()
    max_hp = combat_stat["hp"]
    max_mp = combat_stat["mp"]
    curr_hp = character.hp
    curr_mp = character.mp

    return curr_hp / max_hp, max_hp - curr_hp


if __name__ == '__main__':
    character_r.init_basic_status()
    character_r.hp -= 25
    ratio, loss = check_health_loss(character_r)
    print(f"HP Remains: {ratio * 100:.3f}% (-{loss} pts.)")