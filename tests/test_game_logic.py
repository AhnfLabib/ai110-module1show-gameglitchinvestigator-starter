"""
Pytest cases that target the specific bugs detected in the game logic.

These tests encode the *correct* expected behavior; they fail when the
known bugs are present and pass once the bugs are fixed.
"""
import sys
from pathlib import Path

# Add project root so "app" can be imported when running tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from unittest.mock import MagicMock

# Mock streamlit before importing app so we don't need a display
_st = MagicMock()
_st.sidebar.selectbox.return_value = "Normal"
_st.sidebar.caption.return_value = None
_st.session_state = MagicMock()  # allow attribute assignment (secret, attempts, etc.)
_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
_st.expander.return_value.__enter__ = MagicMock(return_value=MagicMock())
_st.expander.return_value.__exit__ = MagicMock(return_value=False)
sys.modules["streamlit"] = _st

from app import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
)


# ---------------------------------------------------------------------------
# Bug: UI always says "Guess a number between 1 and 100" but Easy/Hard use
#      different ranges. Correct behavior: Easy = 1–20, so range is NOT 1–100.
# ---------------------------------------------------------------------------
def test_get_range_easy_is_not_1_to_100():
    """Easy difficulty should be 1–20; if UI hardcodes 1–100 it's wrong."""
    low, high = get_range_for_difficulty("Easy")
    assert (low, high) == (1, 20)
    assert high != 100  # documents bug: UI must not always say "1 and 100"


def test_get_range_normal_is_1_to_100():
    """Normal difficulty should be 1–100."""
    low, high = get_range_for_difficulty("Normal")
    assert (low, high) == (1, 100)


# ---------------------------------------------------------------------------
# Bug: "Hard" had smaller range (1–50) than "Normal" (1–100), so Hard was
#      actually easier. Correct behavior: Hard range size >= Normal range size.
# ---------------------------------------------------------------------------
def test_hard_difficulty_should_not_be_easier_than_normal():
    """Hard should not have a smaller range than Normal (Hard must be harder)."""
    normal_low, normal_high = get_range_for_difficulty("Normal")
    hard_low, hard_high = get_range_for_difficulty("Hard")

    normal_size = normal_high - normal_low
    hard_size = hard_high - hard_low
    assert hard_size >= normal_size, (
        "Bug: Hard range should not be smaller than Normal (Hard was 1–50, Normal 1–100)"
    )


# ---------------------------------------------------------------------------
# Bug: On even attempts the app passed secret as str(), so check_guess compared
#      int to str → TypeError then string comparison (e.g. 9 vs "100" → "9" > "100").
#      Correct behavior: comparison must be numeric; 9 < 100 → "Too Low".
# ---------------------------------------------------------------------------
def test_check_guess_returns_tuple_outcome_message():
    """check_guess returns (outcome, message)."""
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"
    assert isinstance(message, str)


def test_check_guess_numeric_comparison_with_int_secret():
    """Correct hint when guess is 9 and secret is 100 (both numeric)."""
    outcome, _ = check_guess(9, 100)
    assert outcome == "Too Low"


def test_check_guess_string_secret_should_compare_numerically():
    """
    When secret is passed as string (e.g. on even attempts), comparison must
    still be numeric. 9 < 100 so outcome must be 'Too Low', not 'Too High'.
    Bug: int vs str comparison raises TypeError, or string comparison gives wrong hint.
    """
    outcome_int, _ = check_guess(9, 100)
    assert outcome_int == "Too Low"
    try:
        outcome_str, _ = check_guess(9, "100")
    except TypeError:
        pytest.fail(
            "Bug: check_guess(guess_int, secret_str) raises TypeError; "
            "secret must be normalized to int or comparison must support str"
        )
    assert outcome_str == outcome_int, (
        "Bug: secret as str causes wrong comparison (e.g. string '9' > '100')"
    )
    assert outcome_str == "Too Low"


# ---------------------------------------------------------------------------
# Bug: "Too High" on even attempt_number adds 5 to score; on odd subtracts 5.
#      Correct behavior: wrong guess (Too High) should not reward points.
# ---------------------------------------------------------------------------
def test_update_score_too_high_should_not_increase_score():
    """
    A 'Too High' wrong guess should not increase score.
    Bug: on even attempt_number the code adds 5.
    """
    score_after = update_score(0, "Too High", attempt_number=2)
    assert score_after <= 0, (
        "Bug: 'Too High' on even attempt should not add 5 points"
    )


def test_update_score_too_high_odd_attempt_decreases():
    """'Too High' on odd attempt decreases score by 5."""
    assert update_score(10, "Too High", attempt_number=1) == 5


def test_update_score_too_low_decreases():
    """'Too Low' always decreases score by 5."""
    assert update_score(10, "Too Low", attempt_number=1) == 5


# ---------------------------------------------------------------------------
# Bug: New Game uses random.randint(1, 100) and ignores difficulty range.
#      We can't call that from here; we test that range exists per difficulty
#      so a correct "new game" would pick secret in [low, high].
# ---------------------------------------------------------------------------
def test_range_per_difficulty_for_new_game_secret():
    """
    For a correct 'New Game', secret should be in [low, high] for the selected
    difficulty. This documents the bug: app uses randint(1, 100) for new game
    instead of get_range_for_difficulty(difficulty).
    """
    for difficulty in ("Easy", "Normal", "Hard"):
        low, high = get_range_for_difficulty(difficulty)
        assert low <= high
        assert low >= 1
        # Any secret for this difficulty must be in [low, high]
        # (We can't call the app's new-game logic; we just assert ranges are valid.)
        assert high >= 20  # at least Easy's high
