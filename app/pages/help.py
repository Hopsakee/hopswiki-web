"""Help page: short, opinionated intro to Hopswiki for myself and future readers."""

from nicegui import ui

from app.components.layout import page_layout
from app.config import Settings
from app.wiki import WikiStore

HELP_HTML = """
<h1>What is Hopswiki?</h1>

<p>Hopswiki is my personal cross-domain wiki. It spans three Library areas — my
private reading (<em>d1 Prive</em>), my work at WDODelta (<em>d5 WDODelta</em>),
and software / AI / development (<em>d6 Programming en Development</em>) — and
turns the underlying archive into a single navigable knowledge graph.</p>

<h2>Why it exists</h2>

<p>The Library archive holds the source documents: PDFs, YouTube transcripts,
clipped articles, the lot. The vault holds my own working notes. Neither of
those is a wiki. Hopswiki is the layer where the documents become connected — a
summary per source, a page per concept, comparisons where two sources disagree,
syntheses where they combine into something larger.</p>

<p>The point is not to re-read the documents. The point is to remember what
they said and how they relate.</p>

<h2>What is in here</h2>

<ul>
  <li><strong>Sources</strong> — one summary page per archived document, with key takeaways and outbound links.</li>
  <li><strong>Concepts</strong> — ideas, frameworks, recurring themes. Each concept gathers every mention across sources.</li>
  <li><strong>Entities</strong> — people, organizations, tools that appear repeatedly across the archive.</li>
  <li><strong>Comparisons</strong> — side-by-side analyses where two sources cover the same territory differently.</li>
  <li><strong>Syntheses</strong> — cross-source arguments and big-picture takes. The reason the wiki exists.</li>
</ul>

<h2>How to use it</h2>

<ol>
  <li><strong>Browse a folder</strong> — pick Sources / Concepts / Entities / Comparisons / Syntheses from the header.</li>
  <li><strong>Search</strong> — substring match across titles, body, and tags.</li>
  <li><strong>Follow the links</strong> — every page lists its backlinks (who points here) and outlinks (where it points).</li>
  <li><strong>Sort by link-density</strong> — the pages with the most inbound or outbound links are the connective tissue of the graph.</li>
</ol>

<h2>How it is maintained</h2>

<p>The wiki is written by the Librarian skill (<code>_PKW_LIBRARIAN</code>) — not
by hand. Pages are markdown with YAML frontmatter; wikilinks resolve at render
time; backlinks are computed at boot. This browser is read-only. To add a
source, the source goes into the Library archive and the Librarian runs.</p>

<h2>Important to know</h2>

<ul>
  <li>This is a personal tool — not a publication, not a shared editing surface.</li>
  <li>Summaries are AI-assisted and may be wrong; the original document always wins.</li>
  <li>Wikilinks shown as struck-through point at pages that have not been written yet — that is a feature, not a bug.</li>
</ul>
"""


def register(store: WikiStore, settings: Settings) -> None:

    @ui.page("/help")
    def help_page() -> None:
        with page_layout("Help"):
            with ui.element("div").classes("wiki-content"):
                ui.html(HELP_HTML)
