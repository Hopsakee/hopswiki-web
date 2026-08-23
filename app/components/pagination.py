"""Bounded rendering: window a long list so element construction stays constant.

NiceGUI serialises the entire element tree into the initial HTTP response, so a
page's cost scales with the number of elements *constructed*, not with what the
viewport shows. Rendering all 1383 wiki pages took 12.4 s and 3.08 MB before a
browser saw a byte; one 50-row window takes 0.5 s and 0.14 MB.

Sort and filter always run over the full dataset — only the window is rendered —
so ordering and counts stay globally correct at any page size.

NiceGUI does ship `ui.pagination` (a wrapper around Quasar's `q-pagination`).
It is deliberately not used here: it renders Quasar's own numbered-page chrome,
which would have to be fought with CSS overrides to match this app's theme,
whereas the control below reuses the flat/dense/accent button idiom the rest of
the components already use.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from nicegui import ui

#: Items rendered per window. The single tuning knob for bounded rendering.
PAGE_SIZE = 50

_NAV_STYLE = "color: var(--accent); font-size: 0.8rem"
_META_STYLE = "color: var(--text-muted); font-size: 0.8rem; white-space: nowrap"


@dataclass(frozen=True)
class Window[T]:
    """One rendered slice of a longer list, plus the numbers that describe it.

    `total` is always the length of the *full* list, never of `items` — every
    count shown to the user is the true total.
    """

    items: list[T]
    index: int
    total: int

    @property
    def first(self) -> int:
        """0-based offset of this window's first item within the full list."""
        return self.index * PAGE_SIZE

    @property
    def last_index(self) -> int:
        return max(0, (self.total - 1) // PAGE_SIZE)

    @property
    def paged(self) -> bool:
        """True when the full list does not fit in a single window."""
        return self.total > PAGE_SIZE

    def summary(self, noun: str) -> str:
        """e.g. `1383 pages · showing 1–50`, or just `45 pages` when unpaged."""
        if not self.paged:
            return f"{self.total} {noun}"
        return (
            f"{self.total} {noun} · "
            f"showing {self.first + 1}–{self.first + len(self.items)}"
        )


def paginate[T](items: list[T], page: int) -> Window[T]:
    """Slice `items` to the `page`-th window, clamping `page` into range.

    The clamp matters because `total` can shrink under a live page index:
    `search.py` re-runs its query on every paging click, so a `/_reload` that
    drops pages between two clicks would otherwise render an out-of-range
    window. The list views additionally reset to page 0 on any sort or filter
    change, so their own narrowing case never reaches the clamp — the clamp is
    the backstop, the reset is the UX rule, and neither makes the other
    redundant.
    """
    last = max(0, (len(items) - 1) // PAGE_SIZE)
    index = max(0, min(page, last))
    return Window(items[index * PAGE_SIZE:(index + 1) * PAGE_SIZE], index, len(items))


def pagination_controls(window: Window, on_page: Callable[[int], None]) -> None:
    """First / Prev / position / Next / Last. Renders nothing for a single window.

    First and Last exist because 1383 pages is 28 windows: without them the far
    end of the list costs 27 clicks, which is the same as unreachable.
    """
    if not window.paged:
        return
    index, last = window.index, window.last_index

    def nav(label: str, icon: str, target: int, enabled: bool) -> None:
        # Icon plus label, matching the filter button's idiom — the label keeps
        # the control legible before the Material Icons font has painted.
        ui.button(label, icon=icon, on_click=lambda: on_page(target)) \
            .props("flat dense size=sm").style(_NAV_STYLE).set_enabled(enabled)

    with ui.row().classes("items-center gap-2 flex-wrap").style("margin-top: 0.5rem"):
        nav("First", "first_page", 0, index > 0)
        nav("Prev", "chevron_left", index - 1, index > 0)
        ui.label(f"Page {index + 1} of {last + 1}").style(_META_STYLE)
        nav("Next", "chevron_right", index + 1, index < last)
        nav("Last", "last_page", last, index < last)
