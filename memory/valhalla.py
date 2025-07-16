import textwrap

import yaml
from pathlib import Path

sample_character_description = textwrap.dedent("""
    这是一位眼神如蓝宝石一般纯净闪耀的冒险者，大家都叫他R。他是一位用剑和魔法的高手，但却不常使用寻常的剑，而是通过凝聚空气中的水汽等成分组成一把冰刃作为常用武器。
    他的身体有很强的魔法亲和性，由于他对冰属性魔法的极高天赋，使他可以借助空气中的魔力与水汽修复自己的身体。这种对空气的利用也允许他制作致密冰晶组成的寒冰护甲。
    他有极强的学习天赋和意志力，让他可以快速理解环境与敌人的秘密。
    在必要时，他可以急速冰冻接触到敌人的血液，这会让绝大多数有机生命瞬间停止活动。
    
    他一直随身携带一柄皓月长剑，剑格是一个月牙型的空腔。这把武器比起剑更像权杖，因为它的独特设计使它成为无与伦比的的魔力导体。
    他没有太多关于过去的回忆，但他的心灵也如冰晶一样善良纯洁；但在广阔多重宇宙中的冒险经历让他逐渐理解人性。但——这世界上只有一种英雄主义，他依然热爱自己的人生。
    """)


def summon_from_valhalla(character_name):
    try:
        # 2. 获取当前脚本文件（valhalla.py）的路径
        current_script_path = Path(__file__)

        # 3. 从脚本路径找到项目根目录 (AgentMonster)
        # current_script_path.parent 是 memory 目录
        # current_script_path.parent.parent 是 AgentMonster 目录
        project_root = current_script_path.parent.parent

        # 4. 构造到 valhalla.yaml 的正确绝对路径
        yaml_file_path = project_root / 'prompt' / 'valhalla.yaml'

        # print(f"Trying to open: {yaml_file_path}") # 调试时可以取消注释这行

        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            valhalla = yaml.safe_load(file)
            print("Character Summoning:", valhalla[character_name])
            return valhalla[character_name]

    except FileNotFoundError:
        print(f"Error: No yaml file found at the expected path.")  # 错误信息可以更明确
    except yaml.YAMLError as e:
        print(f"Error: Parsing got something wrong - {e}")
    except KeyError:
        print(f"No Character Found with name: {character_name}")
        print("向英灵殿呼唤，回应的只有自己..")
        return sample_character_description

if __name__ == '__main__':
    character = summon_from_valhalla("saber")
    print(character)

    sample = {
  "name": "R",
  "description": "R是一位目光纯净如蓝宝石的冒险者，以其独特的战斗风格闻名。他擅长将空气中的水汽凝聚成锋利的冰刃作为主要武器，而非依赖传统剑术。他的身体对魔法具有极强的亲和性，尤其在冰属性魔法方面天赋异禀，能够利用空气中的魔力与水汽修复自身损伤，并制造致密的寒冰护甲以抵御攻击。R的性格善良纯洁，但在广阔多重宇宙的冒险经历使他对人性有了深刻的理解。他拥有非凡的学习天赋和坚韧的意志力，能够迅速洞察环境与敌人的秘密。在极端情况下，他能瞬间冰冻接触到敌人的血液，导致绝大多数有机生命体瞬间停止活动。他热爱自己的人生，即使面对世间复杂，依然坚守内心的英雄主义。",
  "alignment": {
    "abbreviation": "NG",
    "name": "中立善良",
    "description": "中立善良生物尽其所能地做行善，在规则限度内行事，但并不感觉被规则束缚。按照他人需求帮助他们的和善之人，可能是中立善良的。"
  },
  "skills": [
    {
      "name": "冰刃塑形",
      "mana_cost": 10,
      "description": "将空气中的水汽凝聚成锋利的冰刃作为常用武器，可根据战斗需求改变形态与尺寸。"
    },
    {
      "name": "寒冰护甲",
      "mana_cost": 30,
      "description": "利用空气中的魔力与水汽在自身周围形成一层致密的冰晶护甲，大幅提升物理防御力。"
    },
    {
      "name": "生命冰愈",
      "mana_cost": 40,
      "description": "借助空气中的魔力与水汽，加速身体的自然愈合速度，修复轻微至中度损伤。"
    },
    {
      "name": "极速冻血",
      "mana_cost": 80,
      "description": "接触到敌人血液时，可瞬间将其冰冻，使绝大多数有机生命体停止活动。对高体质或非生物敌人效果减弱。"
    },
    {
      "name": "洞察先机",
      "mana_cost": 20,
      "description": "凭借非凡的学习天赋和意志力，R能够迅速分析战场环境、敌人的战斗风格与潜在弱点，从而制定最优策略。"
    }
  ],
  "ability_scores": {
    "STR": 12,
    "DEX": 16,
    "CON": 15,
    "INT": 18,
    "WIS": 17,
    "CHA": 16,
    "LUC": 13
  },
  "inventory": [
    {
      "name": "皓月长剑",
      "durability": 100,
      "description": "一柄剑格为月牙形空腔的长剑，其独特设计使其成为无与伦比的魔力导体，比起剑更像权杖。"
    }
  ],
  "hp": 100,
  "mp": 100,
  "lv": 0
}