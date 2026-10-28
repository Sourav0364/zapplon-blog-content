#!/usr/bin/env python3
"""
Write the next posts from the content plan into posts/<slug>.md

Replaces the Zapier automation. Run from the root of the zapplon-blog-content
repo; the GitHub Action commits whatever this writes.

Posts are buyer-intent SEO articles aimed at California / US small businesses —
the people who hire Zapplon — not industry news. Topics come in order from
scripts/content-plan.json; the first entry whose slug is not already published
is written next. When the plan runs out the model proposes its own topic in the
same style.

Env:
  ANTHROPIC_API_KEY  required
  POSTS_PER_RUN      default 2
  SKIP_IF_DONE_TODAY  "1" = exit without writing if today's quota already exists
  BLOG_MODEL         default claude-sonnet-5-5 (claude-opus-5-5 costs ~2x)
  BLOG_EFFORT        default medium (low | medium | high | xhigh | max)

Exits non-zero on any failure so the Action fails loudly instead of committing
a broken or duplicate post.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import re
import sys

import anthropic

POSTS_DIR = pathlib.Path("posts")
PLAN_FILE = pathlib.Path("scripts/content-plan.json")
MODEL = os.environ.get("BLOG_MODEL", "claude-sonnet-5-5")
EFFORT = os.environ.get("BLOG_EFFORT", "medium")
POSTS_PER_RUN = int(os.environ.get("POSTS_PER_RUN", "2"))
# Catch-up mode: do nothing if today already has its full quota. Lets a later
# cron cover for a scheduled run GitHub delayed or dropped, without doubling up.
SKIP_IF_DONE = os.environ.get("SKIP_IF_DONE_TODAY") == "1"
CATEGORY = "AI & Automation"
SITE = "https://www.zapplon.com"
MIN_WORDS = 1300

META_MARK = "<<<META>>>"
BODY_MARK = "<<<BODY>>>"

SYSTEM = f"""\
You write for the Zapplon blog. Zapplon is a performance growth marketing \
agency serving small and mid-sized businesses, mainly in California and the \
wider US. It sells: AI voice agents and AI receptionists, AI cold email \
outreach, inbound lead generation from Instagram, Google and Meta ads, local \
SEO, and Shopify growth.

Your reader is a BUSINESS OWNER or office manager who is actively deciding \
whether to buy something. They are not a marketer and not an engineer. They \
want a straight answer, a real number, and to know what to do next.

Every post must earn a search ranking and an enquiry. Follow all of this:

1. ANSWER THE TITLE IN THE FIRST 100 WORDS. If the title asks what something \
costs, give the price range in the opening paragraph. Never withhold the \
answer to keep people reading — it loses the click back to Google.
2. USE REAL NUMBERS. Prices, ranges, timeframes, percentages. Search the web \
to verify current figures and cite who published them. Never invent a \
statistic, a quote, a date or a source. If you cannot verify it, leave it out \
or say the figure varies and explain what drives it.
3. BE SPECIFIC TO THE READER'S SITUATION. Write about their industry, their \
staff, their phone, their budget — not about "businesses" in the abstract.
4. BE GENUINELY USEFUL AND HONEST. Say when the product is a poor fit, when a \
cheaper option is better, and what the limitations are. A post that only sells \
does not rank and does not convert.
5. COVER THE WHOLE QUESTION. Include what it costs, how it works, what to \
watch out for, and how to decide. Use the sections the reader actually needs.

Style:
- Plain, direct professional English. Short paragraphs, 2-4 sentences.
- Address the reader as "you". No first-person singular.
- No hype. Never use: unlock, game-changer, revolutionise, seamless, \
dive in, in today's fast-paced world, elevate, supercharge.
- No exclamation marks.
- 5 to 9 `##` sections with descriptive headings a reader would scan for. \
Use `-` bullet lists and `**bold**` where they genuinely help.
- Include a short FAQ of 2-3 `###` questions near the end where it fits \
naturally — these win featured snippets.
- Do not include a top-level `#` heading; the site renders the title itself.
- Do not write a frontmatter block; metadata is returned separately.
- Mention Zapplon at most twice, and only where it is genuinely relevant. \
The post must read as useful advice, not an advert.
"""


def existing_posts() -> tuple[set[str], list[str]]:
    """Return published slugs, and recent titles so we never repeat a topic."""
    if not POSTS_DIR.is_dir():
        sys.exit(f"error: {POSTS_DIR}/ not found — run this from the repo root")
    slugs: set[str] = set()
    dated: list[tuple[str, str]] = []
    for path in POSTS_DIR.glob("*.md"):
        slugs.add(path.stem)
        text = path.read_text(encoding="utf-8", errors="replace")[:2000]
        title = re.search(r"^title:\s*(.+)$", text, re.M)
        date = re.search(r"^date:\s*(.+)$", text, re.M)
        if title:
            dated.append((
                date.group(1).strip().strip('"\'') if date else "",
                title.group(1).strip().strip('"\''),
            ))
    dated.sort(reverse=True)
    return slugs, [t for _, t in dated[:40]]


def written_today(today: str) -> int:
    """How many posts already carry today's date."""
    count = 0
    for path in POSTS_DIR.glob("*.md"):
        head = path.read_text(encoding="utf-8", errors="replace")[:2000]
        date = re.search(r"^date:\s*(.+)$", head, re.M)
        if date and date.group(1).strip().strip('"\'') == today:
            count += 1
    return count


def next_from_plan(slugs: set[str], taken: set[str]) -> dict | None:
    """First planned post not already published and not claimed this run."""
    if not PLAN_FILE.is_file():
        print(f"note: {PLAN_FILE} not found — the model will choose a topic")
        return None
    try:
        plan = json.loads(PLAN_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"error: {PLAN_FILE} is not valid JSON: {exc}")
    for entry in plan.get("posts", []):
        slug = entry.get("slug")
        if slug and slug not in slugs and slug not in taken:
            return entry
    return None


def build_prompt(entry: dict | None, titles: list[str], today: str) -> str:
    recent = "\n".join(f"- {t}" for t in titles) or "- (none yet)"
    if entry:
        brief = f"""\
Write this planned post:

  Title:          {entry['title']}
  Target keyword: {entry['keyword']}
  Slug:           {entry['slug']}

Use the exact slug above. You may refine the title for clarity, but keep the \
target keyword in it. Link naturally to {SITE}{entry['linkTo']} once in the \
first third of the post, using descriptive anchor text — never "click here".
"""
    else:
        brief = f"""\
The content plan is finished, so choose the topic yourself.

Pick one question a California small business owner would type into Google \
when they are close to buying one of Zapplon's services — a cost question, a \
comparison, a "best X for Y", or a specific problem. Favour a narrow, \
specific topic (an industry, a city, a budget) over a broad one. Avoid \
industry news: nobody searching for news is going to hire an agency. Do not \
name or compare a specific competitor company.

Link naturally to the most relevant page once in the first third, using \
descriptive anchor text. The pages are {SITE}/ai-agents (AI receptionists and \
voice agents), /email-agents (cold email), /lead-agents (Instagram lead \
generation), /services (ads, SEO, Shopify), /results (case studies and the \
Growth Audit), /approach (how we work).
"""

    return f"""\
Today is {today}.

{brief}
Research the topic with web search first and verify any figure you use.

Write 1,500 to 2,000 words. Longer and genuinely complete beats short.

Do not duplicate any of these already-published posts:
{recent}

Return your answer in exactly this shape and nothing else:

{META_MARK}
{{
  "slug": "kebab-case-slug",
  "title": "Headline, under 70 characters, containing the target keyword",
  "metaTitle": "SEO title, under 60 characters",
  "description": "Meta description, 140-158 characters, with the target keyword",
  "keywords": ["target keyword", "related keyword", "third keyword"],
  "excerpt": "Two sentences summarising the post for the blog listing.",
  "readMins": 8
}}
{BODY_MARK}
## First section heading

The article body in Markdown...
"""


def call_claude(client: anthropic.Anthropic, prompt: str) -> str:
    messages: list[dict] = [{"role": "user", "content": prompt}]

    # Server-side web search can return pause_turn on a long turn; resume by
    # echoing the assistant content back and continuing the same conversation.
    for _ in range(6):
        with client.messages.stream(
            model=MODEL,
            max_tokens=32000,
            system=SYSTEM,
            output_config={"effort": EFFORT},
            tools=[{
                "type": "web_search_20260209",
                "name": "web_search",
                "max_uses": 6,
            }],
            messages=messages,
        ) as stream:
            response = stream.get_final_message()

        if response.stop_reason == "refusal":
            detail = getattr(response.stop_details, "category", None)
            sys.exit(f"error: model declined the request (category: {detail})")
        if response.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": response.content})
            continue
        if response.stop_reason == "max_tokens":
            sys.exit("error: hit max_tokens before finishing the post")

        usage = response.usage
        print(f"    tokens in/out: {usage.input_tokens}/{usage.output_tokens}")
        text = "".join(b.text for b in response.content if b.type == "text")
        if not text.strip():
            sys.exit("error: model returned no text")
        return text

    sys.exit("error: web search did not settle after 6 resumes")


def parse(raw: str) -> tuple[dict, str]:
    if META_MARK not in raw or BODY_MARK not in raw:
        sys.exit(f"error: response missing {META_MARK}/{BODY_MARK} markers")
    meta_part, body = raw.split(BODY_MARK, 1)
    meta_part = meta_part.split(META_MARK, 1)[1]
    meta_part = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", meta_part.strip())
    try:
        meta = json.loads(meta_part)
    except json.JSONDecodeError as exc:
        sys.exit(f"error: metadata is not valid JSON: {exc}")
    return meta, body.strip()


def validate(meta: dict, body: str, slugs: set[str], entry: dict | None) -> None:
    required = ["slug", "title", "metaTitle", "description", "keywords", "excerpt"]
    missing = [k for k in required if not meta.get(k)]
    if missing:
        sys.exit(f"error: metadata missing fields: {', '.join(missing)}")

    slug = meta["slug"]
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        sys.exit(f"error: slug is not kebab-case: {slug!r}")
    if slug in slugs:
        sys.exit(f"error: slug already exists, refusing to overwrite: {slug}")

    if not isinstance(meta["keywords"], list) or not all(
        isinstance(k, str) and k for k in meta["keywords"]
    ):
        sys.exit("error: keywords must be a non-empty list of strings")

    words = len(body.split())
    if words < MIN_WORDS:
        sys.exit(f"error: body too short ({words} words, minimum {MIN_WORDS})")
    if body.lstrip().startswith("# "):
        sys.exit("error: body starts with an H1; the site renders the title")
    if "##" not in body:
        sys.exit("error: body has no ## section headings")

    # A post that never links to a service page cannot produce an enquiry.
    if entry and entry.get("linkTo") and entry["linkTo"] not in body:
        sys.exit(f"error: body never links to {entry['linkTo']}")


def q(value: str) -> str:
    """
    Quote a frontmatter string value for the site's parser.

    lib/remotePosts.ts strips the surrounding quotes but does NOT unescape, so
    a backslash-escaped quote would render literally as \\" on the page. Embedded
    double quotes become typographic ones instead (which the existing posts
    already use), and newlines are flattened since the parser is line-based.
    """
    text = re.sub(r"\s+", " ", str(value)).strip()
    out, open_quote = [], True
    for ch in text:
        if ch == '"':
            out.append("“" if open_quote else "”")
            open_quote = not open_quote
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def write_post(meta: dict, body: str, today: str) -> pathlib.Path:
    read_mins = meta.get("readMins")
    if not isinstance(read_mins, int) or not 3 <= read_mins <= 20:
        read_mins = max(3, round(len(body.split()) / 200))
    frontmatter = "\n".join([
        "---",
        f"slug: {meta['slug']}",
        f"title: {q(meta['title'])}",
        f"metaTitle: {q(meta['metaTitle'])}",
        f"description: {q(meta['description'])}",
        f"keywords: {json.dumps(meta['keywords'], ensure_ascii=False)}",
        f"category: {q(CATEGORY)}",
        f"date: {q(today)}",
        f"readMins: {read_mins}",
        f"excerpt: {q(meta['excerpt'])}",
        "---",
        "",
    ])
    path = POSTS_DIR / f"{meta['slug']}.md"
    path.write_text(frontmatter + "\n" + body + "\n", encoding="utf-8")
    return path


def emit_slugs(written: list[str]) -> None:
    """Hand the slugs to the workflow so it can publish and submit these URLs."""
    if out := os.environ.get("GITHUB_OUTPUT"):
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(f"slugs={','.join(written)}\n")


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("error: ANTHROPIC_API_KEY is not set")

    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    slugs, titles = existing_posts()

    if SKIP_IF_DONE:
        done = written_today(today)
        if done >= POSTS_PER_RUN:
            print(f"{done} post(s) already dated {today}; nothing to do")
            emit_slugs([])
            return
        print(f"catch-up: {done}/{POSTS_PER_RUN} posts exist for {today}")

    client = anthropic.Anthropic()
    print(f"{len(slugs)} published; writing {POSTS_PER_RUN} with {MODEL} (effort={EFFORT})")

    written: list[str] = []
    taken: set[str] = set()
    for n in range(1, POSTS_PER_RUN + 1):
        entry = next_from_plan(slugs, taken)
        label = entry["title"] if entry else "(model picks the topic)"
        print(f"\n[{n}/{POSTS_PER_RUN}] {label}")

        meta, body = parse(call_claude(client, build_prompt(entry, titles, today)))
        validate(meta, body, slugs, entry)
        path = write_post(meta, body, today)

        slugs.add(meta["slug"])
        taken.add(entry["slug"] if entry else meta["slug"])
        titles.insert(0, meta["title"])
        written.append(meta["slug"])
        print(f"    wrote {path} ({len(body.split())} words)")

    print(f"\ndone: {len(written)} post(s)")
    emit_slugs(written)


if __name__ == "__main__":
    main()
