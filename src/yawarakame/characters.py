from __future__ import annotations

from importlib.resources import files

import yaml

from yawarakame.models import CharacterSpec


def load_characters() -> dict[str, CharacterSpec]:
    character_dir = files("yawarakame").joinpath("data", "characters")
    loaded: dict[str, CharacterSpec] = {}
    for path in sorted(character_dir.iterdir(), key=lambda item: item.name):
        if not path.name.endswith(".yaml"):
            continue
        with path.open("r", encoding="utf-8") as stream:
            character = CharacterSpec.model_validate(yaml.safe_load(stream))
        if character.id in loaded:
            raise ValueError(f"キャラクターIDが重複しています: {character.id}")
        loaded[character.id] = character
    return loaded

