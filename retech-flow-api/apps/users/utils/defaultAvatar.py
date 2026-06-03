import random


DEFAULT_AVATARS = [
    "avatars/default_avatar_01.png",
    "avatars/default_avatar_02.png",
    "avatars/default_avatar_03.png",
    "avatars/default_avatar_04.png",
    "avatars/default_avatar_05.png",
]


def random_default_avatar():
    return random.choice(DEFAULT_AVATARS)
