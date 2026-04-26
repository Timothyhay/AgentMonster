# Cute ASCII Art Character Candidates
AVATARS = {
    "slime": r"""
      .--.
     / @ @ \
    |   ^   |
     \  -  /
      '---'
    """,
    "cat": r"""
     |\__/,|   (`\
   _.|o o  |_   ) )
 -(((---(((---'(_/
    """,
    "fox": r"""
      /\   /\
     //\\_//\\
     \_     _/
      / * * \
      \__^__/
    """,
    "robot": r"""
     [#####]
     [o- -o]
     [  V  ]
     [#####]
    """,
    "ghost": r"""
     .-"-.
    / o o \
    |  V  |
    \  -  /
     '---'
    """
}

# Spell & Attack Effects
EFFECTS = {
    "fire": [
        "  (  ",
        " ( ) ",
        "(()))",
        " ( ) ",
        "  )  "
    ],
    "ice": [
        "  *  ",
        " *#* ",
        "*###*",
        " *#* ",
        "  *  "
    ],
    "spark": [
        "  |  ",
        "- o -",
        "  |  "
    ],
    "slash": [
        "  /  ",
        " /   ",
        "/    "
    ],
    "hit": [
        " (X) ",
        "  !  "
    ]
}

def get_avatar(name: str) -> str:
    return AVATARS.get(name.lower(), AVATARS["slime"])

def get_effect(name: str) -> list:
    return EFFECTS.get(name.lower(), EFFECTS["spark"])
