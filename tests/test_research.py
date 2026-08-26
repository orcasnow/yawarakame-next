# Search-decision tests keep current topics separate from timeless analysis.
from yawarakame.research import decide_web_search


def test_current_topic_enables_search() -> None:
    required, reason = decide_web_search("現在のグランパスの順位を評価する")
    assert required is True
    assert "現在" in reason


def test_general_tactics_does_not_enable_search() -> None:
    required, _ = decide_web_search("4バックのビルドアップを考える")
    assert required is False
