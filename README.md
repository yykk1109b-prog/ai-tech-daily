# AI Tech Daily

毎日のテックニュースをAIが分析・記事化するサイト

**公開サイト:** https://yykk1109b-prog.github.io/ai-tech-daily/

---

## 概要

AI Tech Dailyは、複数のRSSソースから最新のテックニュースを自動収集し、5つの異なる視点から分析・記事化してGitHub Pagesで公開するプロジェクトです。毎日1回の手動実行により、最新のAI関連ニュースをお届けします。

---

## 技術スタック

- **ホスティング:** GitHub Pages（無料）
- **サイト生成:** Jekyll
- **記事形式:** Markdown
- **RSS取得:** Python + feedparser
- **記事生成:** Claude Code generate-news スキル
- **SEO対応:** jekyll-seo-tag, jekyll-sitemap, jekyll-feed
- **デザイン:** カスタムCSS

---

## 記事の5つの視点

各ニュース記事は、以下の5つの視点から分析されます：

1. **⚡ 速報まとめ** （300字）
   - ニュースの要点を素早く把握できるサマリー

2. **💻 開発者視点** （500字）
   - エンジニアにとって重要な技術的側面

3. **📊 ビジネス視点** （500字）
   - 市場トレンドや企業戦略の観点

4. **📖 初心者向け解説** （400字）
   - AI未経験者でも理解できる説明

5. **💡 活用アイデア** （400字）
   - 実務での応用可能性を紹介

---

## RSSソース

以下のメディアから最新ニュースを取得：

- Hacker News
- TechCrunch AI
- The Verge AI
- MIT Technology Review
- GIGAZINE
- ITmedia AI+

---

## セットアップ

### 前提条件

- Ruby 2.7以上
- Python 3.9以上
- Git

### インストール手順

1. リポジトリをクローン：
   ```bash
   git clone https://github.com/yykk1109b-prog/ai-tech-daily.git
   cd ai-tech-daily
   ```

2. Jekyll依存関係をインストール：
   ```bash
   bundle install
   ```

3. Python環境を構築：
   ```bash
   cd scripts
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. ローカルサーバーで確認：
   ```bash
   cd ..
   bundle exec jekyll serve
   ```

   ブラウザで http://localhost:4000 にアクセスしてください

---

## 日次運用

### 記事生成

毎日の記事生成は、Claude Codeで以下のコマンドを実行：

```
/generate-news
```

このコマンドは以下の処理を自動実行：

1. RSSソースから最新ニュースを取得
2. AIがニュースの重要度を判定
3. 5つの視点から分析記事を生成
4. Markdownファイルを作成
5. GitHubへ自動プッシュ
6. GitHub Pagesで自動公開

### 手動での記事作成

記事を手動で作成する場合：

1. `_posts/` ディレクトリに `YYYY-MM-DD-title.md` 形式で作成
2. YAMLフロントマターを含める：
   ```yaml
   ---
   layout: post
   title: "記事タイトル"
   date: YYYY-MM-DD HH:MM:SS
   categories: news
   ---
   ```

---

## ディレクトリ構造

```
ai-tech-daily/
├── _posts/                 # 記事ファイル（Markdown）
├── _layouts/               # Jekyll レイアウト
├── assets/                 # CSS、画像など
├── scripts/                # Python スクリプト
│   ├── requirements.txt     # Python依存関係
│   └── fetch_news.py        # RSS取得スクリプト
├── _config.yml             # Jekyll設定
├── Gemfile                 # Ruby依存関係
└── README.md               # このファイル
```

---

## 設定

### Jekyll設定（`_config.yml`）

基本的な設定はJekyllで行います。プラグインとテーマはこのファイルで管理されます。

### Python設定（`scripts/requirements.txt`）

RSSフィード取得に必要なライブラリを管理：

- `feedparser` - RSS/Atomフィード解析
- `pyyaml` - YAML設定ファイル読み込み

---

## 貢献

プロジェクトへの改善提案やバグ報告は、GitHubのIssuesでお願いします。

---

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

## トラブルシューティング

### Jekyll が起動しない場合

```bash
bundle install --redownload
```

### Python スクリプトでエラーが出る場合

1. 仮想環境が有効か確認
2. 依存関係を再インストール：
   ```bash
   pip install --upgrade -r requirements.txt
   ```

### GitHub Pages が更新されない場合

1. `git push` が成功しているか確認
2. リポジトリの Pages 設定を確認
3. 10分程度待機（キャッシュ反映の時間）

---

## サポート

問題が発生した場合は、GitHub Issuesで報告してください。
