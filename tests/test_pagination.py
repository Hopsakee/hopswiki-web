"""Boundary tests for the windowing primitive in `app.components.pagination`.

These lock in the cases a browser check does not reliably reach: an exact
multiple of PAGE_SIZE, an out-of-range index, and an empty result set. All of
them are pure Python — no NiceGUI, no server, no wiki data.
"""

from __future__ import annotations

import pytest

from app.components.pagination import PAGE_SIZE, paginate


def items(n: int) -> list[int]:
    return list(range(n))


def test_empty_list_yields_empty_first_window():
    w = paginate([], 0)
    assert (w.items, w.index, w.total, w.paged) == ([], 0, 0, False)
    assert w.last_index == 0
    assert w.summary("pages") == "0 pages"


def test_shorter_than_one_window_is_unpaged():
    w = paginate(items(PAGE_SIZE - 1), 0)
    assert len(w.items) == PAGE_SIZE - 1
    assert w.paged is False
    assert w.summary("pages") == f"{PAGE_SIZE - 1} pages"


def test_exactly_one_window_is_unpaged_and_has_no_phantom_second_page():
    w = paginate(items(PAGE_SIZE), 0)
    assert len(w.items) == PAGE_SIZE
    assert w.paged is False
    assert w.last_index == 0
    assert paginate(items(PAGE_SIZE), 1).index == 0


@pytest.mark.parametrize("multiple", [2, 3])
def test_exact_multiple_has_no_trailing_empty_window(multiple: int):
    total = PAGE_SIZE * multiple
    w = paginate(items(total), multiple - 1)
    assert w.last_index == multiple - 1
    assert len(w.items) == PAGE_SIZE
    assert w.items[-1] == total - 1
    # One past the true last page clamps back onto it, not onto an empty window.
    assert paginate(items(total), multiple).index == multiple - 1


def test_partial_last_window_reports_true_total_and_short_slice():
    total = PAGE_SIZE * 2 + 7
    w = paginate(items(total), 2)
    assert len(w.items) == 7
    assert w.total == total
    assert w.first == PAGE_SIZE * 2
    assert w.summary("pages") == (
        f"{total} pages · showing {PAGE_SIZE * 2 + 1}–{total}"
    )


@pytest.mark.parametrize("requested", [-99, -1, 3, 999])
def test_out_of_range_index_clamps_into_range(requested: int):
    total = PAGE_SIZE * 2 + 1
    w = paginate(items(total), requested)
    assert 0 <= w.index <= w.last_index
    assert w.items, "a clamped window must never render empty for a non-empty list"


def test_windows_tile_the_full_list_exactly_once():
    total = 1383  # the real corpus size that motivated this module
    seen: list[int] = []
    index = 0
    while True:
        w = paginate(items(total), index)
        seen.extend(w.items)
        if index >= w.last_index:
            assert w.last_index == 27, "1383 items must span 28 windows"
            break
        index += 1
    assert seen == items(total), "every item appears exactly once, in order"


def test_summary_always_reports_the_full_total_not_the_window():
    w = paginate(items(1383), 0)
    assert w.summary("pages").startswith("1383 pages")
    assert w.summary("results") == "1383 results · showing 1–50"
