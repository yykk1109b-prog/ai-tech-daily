#!/usr/bin/env python3
"""
AI Tech Daily - 記事生成スクリプト
Claude APIを使用してニュース記事を生成
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import anthropic
import yaml


# GLM API設定
GLM_BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://api.z.ai/api/anthropic")

# 使用量制限
MAX_TOKENS_PER_ARTICLE = 10_000
MAX_TOTAL_TOKENS = 1_500_000  # 月間目標


def load_news() -> dict:
    """ニュースデータを読み込む"""
    repo_root = Path(__file__).resolve().parent.parent
    news_file = repo_root / "_data" / "today_news.json"

    if not news_file.exists():
        print(f"Error: {news_file} not found. Run fetch_news.py first.", file=sys.stderr)
        sys.exit(1)

    with open(news_file, "r", encoding="utf-8") as f:
        return json.load(f)


def select_articles(news_data: dict, count: int = 5) -> list:
    """重要ニュースを選定"""
    articles = news_data.get("articles", [])

    if len(articles) == 0:
        return []

    # 選定基準に従ってスコアリング
    for article in articles:
        score = 0

        # 影響度: タイトルに重要キーワードが含まれる
        important_keywords = [
            "API", "launch", "release", "new", "AI", "model",
            "OpenAI", "Google", "Microsoft", "Amazon", "Meta",
            "規制", "発表", "リリース", "新", "AI", "モデル"
        ]
        for keyword in important_keywords:
            if keyword.lower() in article["title"].lower():
                score += 1

        # カテゴリ分散
        article["_score"] = score

    # スコア順にソート
    articles.sort(key=lambda x: x.get("_score", 0), reverse=True)

    # ソース分散（同一ソース最大2件）
    selected = []
    source_count = {}

    for article in articles:
        source = article["source"]
        if source_count.get(source, 0) >= 2:
            continue
        selected.append(article)
        source_count[source] = source_count.get(source, 0) + 1

        if len(selected) >= count:
            break

    return selected


def generate_article_content(
    article: dict, client: anthropic.Anthropic
) -> str:
    """1件のニュース記事を生成"""
    title = article["title"]
    url = article["url"]
    summary = article.get("summary", "")
    source = article["source"]

    # ニュースの性質に応じた深掘りセクションを選択
    keywords = article["title"].lower()
    if any(kw in keywords for kw in ["api", "tool", "code", "release"]):
        deep_dive = ["技術的なポイント", "今日からできること"]
    elif any(kw in keywords for kw in ["fund", "acquisition", "market", "business"]):
        deep_dive = ["ビジネスへの影響", "業界の反応"]
    elif any(kw in keywords for kw in ["regulation", "law", "ethic"]):
        deep_dive = ["そもそもこれは何？", "業界の反応"]
    else:
        deep_dive = ["技術的なポイント", "ビジネスへの影響"]

    prompt = f"""以下のニュースについて、日本語のブログ記事を生成してください。

# ニュース情報
タイトル: {title}
URL: {url}
要約: {summary}
ソース: {source}

# 記事構成
1. サブタイトル（ニュースの核心を一言で）
2. 要約（150〜300字、5W1H + 主要数字、評論は含めない）
3. 深掘りセクション（以下の2つのテーマで、各200〜400字）
   - {deep_dive[0]}
   - {deep_dive[1]}

# ライティングスタイル
- 段落は2〜4文に分割
- **太字**で重要キーワードや数字を強調
- 能動態を使用
- 専門用語は初出時に説明
- 具体的な数字や事実を含める

# 出力形式
## {title} — サブタイトル

（要約テキスト）

### {deep_dive[0]}

（深掘りテキスト）

### {deep_dive[1]}

（深掘りテキスト）
"""

    try:
        response = client.messages.create(
            model=os.environ.get("ANTHROPIC_DEFAULT_SONNET_MODEL", "glm-4.7"),
            max_tokens=MAX_TOKENS_PER_ARTICLE,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        print(f"Error generating article: {e}", file=sys.stderr)
        raise


def generate_full_article(
    articles: list, client: anthropic.Anthropic
) -> str:
    """完全な記事を生成"""
    if not articles:
        return None

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y年%m月%d日")

    # フック導入文の生成
    first_news = articles[0]
    hook_prompt = f"""以下のニュースを元に、記事の導入文（フック）を生成してください。

今日の注目ニュース: {first_news['title']}

# 要件
- 2〜3文
- 最もインパクトのある数字や事実から始める
- 読者の興味を引くように
"""

    try:
        hook_response = client.messages.create(
            model=os.environ.get("ANTHROPIC_DEFAULT_HAIKU_MODEL", "glm-4.5-air"),
            max_tokens=200,
            messages=[{"role": "user", "content": hook_prompt}],
        )
        hook = hook_response.content[0].text
    except Exception as e:
        print(f"Warning: Failed to generate hook: {e}", file=sys.stderr)
        hook = f"今日のAI業界で最も注目されたニュースをお届けします。"

    # タイトルとタグの生成
    title_prompt = f"""以下のニュース一覧から、記事のタイトルとタグを生成してください。

ニュース:
{chr(10).join([f"- {a['title']}" for a in articles])}

# 出力形式（JSON）
{{
  "title": "YYYY年M月D日のAIニュース — 最も注目のキーワードを含む副題",
  "tags": ["tag1", "tag2", "tag3"]
}}
"""

    try:
        title_response = client.messages.create(
            model=os.environ.get("ANTHROPIC_DEFAULT_HAIKU_MODEL", "glm-4.5-air"),
            max_tokens=200,
            messages=[{"role": "user", "content": title_prompt}],
        )
        title_data = json.loads(title_response.content[0].text)
        article_title = title_data.get("title", f"{date_str}のAIニュース")
        tags = title_data.get("tags", ["AI", "ニュース"])
    except Exception as e:
        print(f"Warning: Failed to generate title: {e}", file=sys.stderr)
        article_title = f"{date_str}のAIニュース"
        tags = ["AI", "ニュース"]

    # 要約の生成
    summary_prompt = f"""以下のニュース一覧から、記事の説明文（120〜180字）を生成してください。

ニュース:
{chr(10).join([f"- {a['title']}" for a in articles])}

# 要件
- 120〜180字
- 主要キーワードを含める
"""

    try:
        summary_response = client.messages.create(
            model=os.environ.get("ANTHROPIC_DEFAULT_HAIKU_MODEL", "glm-4.5-air"),
            max_tokens=200,
            messages=[{"role": "user", "content": summary_prompt}],
        )
        description = summary_response.content[0].text.strip()
    except Exception as e:
        print(f"Warning: Failed to generate summary: {e}", file=sys.stderr)
        description = f"{date_str}のAI関連ニュースをお届けします。"

    # 記事本体の構築
    content_parts = [hook]

    for article in articles:
        article_content = generate_article_content(article, client)
        content_parts.append(f"> 元記事: [{article['source']}]({article['url']})")
        content_parts.append(article_content)
        content_parts.append("---")

    # Front Matter
    front_matter = f"""---
layout: post
title: "{article_title}"
date: {now.strftime("%Y-%m-%d")}
description: "{description}"
categories: [ai, daily]
tags: {json.dumps(tags, ensure_ascii=False)}
---
"""

    return front_matter + "\n\n" + "\n\n".join(content_parts)


def validate_article(article_path: Path) -> bool:
    """記事のバリデーション"""
    with open(article_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Front Matterのチェック
    if "layout:" not in content or "title:" not in content:
        return False

    # 構造チェック
    if "## " not in content:
        return False

    # 禁止パターンチェック
    forbidden_patterns = [
        "速報まとめ", "開発者視点", "ビジネス視点", "初心者向け解説", "活用アイデア"
    ]
    for pattern in forbidden_patterns:
        if pattern in content:
            return False

    return True


def main() -> None:
    """メイン処理"""
    # APIキーの確認
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # クライアント初期化
    client = anthropic.Anthropic(api_key=api_key, base_url=GLM_BASE_URL)

    # ニュース読み込み
    print("Loading news data...")
    news_data = load_news()

    # 記事選定
    print("Selecting articles...")
    selected_articles = select_articles(news_data)

    if not selected_articles:
        print("No articles selected. Exiting.", file=sys.stderr)
        sys.exit(0)

    print(f"Selected {len(selected_articles)} articles")

    # 記事生成
    print("Generating article...")
    article_content = generate_full_article(selected_articles, client)

    if not article_content:
        print("Failed to generate article", file=sys.stderr)
        sys.exit(1)

    # ファイル保存
    repo_root = Path(__file__).resolve().parent.parent
    posts_dir = repo_root / "_posts"
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    article_file = posts_dir / f"{date_str}-daily-ai-news.md"

    with open(article_file, "w", encoding="utf-8") as f:
        f.write(article_content)

    # バリデーション
    if not validate_article(article_file):
        print("Article validation failed", file=sys.stderr)
        article_file.unlink()
        sys.exit(1)

    print(f"Article saved to {article_file}")


if __name__ == "__main__":
    main()
