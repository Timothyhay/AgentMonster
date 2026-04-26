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
    from main import create_monster
    from ui.stage import BattleStage
    
    # 召唤 Saber
    saber_desc = summon_from_valhalla("saber")
    saber = create_monster(saber_desc)
    
    print(f"正在为 {saber.name} 生成头像...")
    saber.generate_avatar()
    print("头像生成完成:")
    print(saber.avatar)

    # 召唤 R
    r_desc = summon_from_valhalla("r")
    r = create_monster(r_desc)
    
    print(f"正在为 {r.name} 生成头像...")
    r.generate_avatar()
    print("头像生成完成:")
    print(r.avatar)

    # 测试战斗舞台
    print("\n进入战斗舞台演示...")
    stage = BattleStage(saber, r)
    stage.animate_idle()
    
    print("\nSaber 发动攻击!")
    stage.animate_attack(1)
    
    print("\nR 释放法术!")
    stage.animate_spell(2)