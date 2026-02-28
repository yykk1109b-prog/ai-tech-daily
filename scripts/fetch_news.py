from __future__ import annotations

import json
import socket
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import yaml

# Set default timeout for all socket operations (including feedparser).
# This is safe here because fetch_news.py runs as a standalone CLI script,
# not as part of a long-running service or multi-threaded application.
socket.setdefaulttimeout(10)


def main() -> None:
    """Fetch news from RSS feeds and save to JSON file."""
    repo_root = Path(__file__).resolve().parent.parent
    sources_file = repo_root / "_data" / "sources.yml"
    output_file = repo_root / "_data" / "today_news.json"

    # Create _data directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Load sources
    try:
        with open(sources_file, "r", encoding="utf-8") as f:
            sources = yaml.safe_load(f) or []
    except FileNotFoundError:
        print(f"Error: sources file not found at {sources_file}", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        sys.exit(1)

    # Fetch articles
    articles = []
    seen_urls = set()
    failed_feeds = []
    now = datetime.now(timezone.utc)
    cutoff_time = now - timedelta(hours=24)

    for source in sources:
        source_name = source.get("name", "Unknown")
        source_url = source.get("url")
        source_category = source.get("category", "general")
        source_language = source.get("language", "en")

        if not source_url:
            print(f"Warning: No URL for source '{source_name}'", file=sys.stderr)
            continue

        try:
            feed = feedparser.parse(source_url)

            if feed.bozo:
                print(
                    f"Warning: Feed parsing issue for '{source_name}': {feed.bozo_exception}",
                    file=sys.stderr,
                )

            for entry in feed.entries:
                title = entry.get("title", "")
                link = entry.get("link", "")

                if not link or link in seen_urls:
                    continue

                seen_urls.add(link)

                # Extract published/updated date
                published_time = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published_time = datetime(*entry.published_parsed[:6]).replace(
                        tzinfo=timezone.utc
                    )
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published_time = datetime(*entry.updated_parsed[:6]).replace(
                        tzinfo=timezone.utc
                    )

                # Filter by 24-hour window, but include articles with unknown dates
                if published_time is None or published_time >= cutoff_time:
                    summary = entry.get("summary", "")
                    # Strip HTML tags from summary if present
                    if summary:
                        # Simple HTML tag removal
                        import re
                        summary = re.sub(r"<[^>]+>", "", summary).strip()

                    article = {
                        "title": title,
                        "url": link,
                        "source": source_name,
                        "category": source_category,
                        "language": source_language,
                        "published": (
                            published_time.isoformat()
                            if published_time
                            else None
                        ),
                        "summary": summary,
                    }
                    articles.append(article)

        except Exception as e:
            error_msg = str(e)
            print(
                f"Error fetching feed '{source_name}' from {source_url}: {error_msg}",
                file=sys.stderr,
            )
            failed_feeds.append({"name": source_name, "url": source_url, "error": error_msg})
            continue

    # Display summary of failed feeds
    if failed_feeds:
        print(f"\n{len(failed_feeds)} feed(s) failed to fetch:", file=sys.stderr)
        for failed in failed_feeds:
            print(f"  - {failed['name']}: {failed['error']}", file=sys.stderr)

    # Check if any articles were fetched
    if len(articles) == 0:
        print("\nNo articles fetched from any feed.", file=sys.stderr)
        print("This might indicate:", file=sys.stderr)
        print("  - All feeds are down or timing out", file=sys.stderr)
        print("  - No new articles in the last 24 hours", file=sys.stderr)
        print("  - Network connectivity issues", file=sys.stderr)
        sys.exit(2)

    # Sort by published date (newest first), with None dates at the end
    articles.sort(
        key=lambda x: (
            x["published"] is None,
            x["published"],
        ),
        reverse=True,
    )

    # Create output JSON
    output_data = {
        "fetched_at": now.isoformat(),
        "total_count": len(articles),
        "articles": articles,
    }

    # Write to JSON file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"Successfully saved {len(articles)} articles to {output_file}")
    except Exception as e:
        print(f"Error writing to output file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
