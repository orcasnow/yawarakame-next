# Character definitions must remain loadable after installation or relocation.
from yawarakame.characters import load_characters


def test_all_initial_characters_load() -> None:
    characters = load_characters()
    assert set(characters) == {"reporter", "ninja", "samurai"}
    assert characters["reporter"].label == "記"
    assert characters["ninja"].label == "忍"
    assert characters["samurai"].label == "侍"


def test_relationships_match_available_characters() -> None:
    characters = load_characters()
    for character in characters.values():
        assert set(character.relationships).issubset(characters)
