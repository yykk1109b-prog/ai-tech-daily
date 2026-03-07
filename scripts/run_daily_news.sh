#!/bin/bash

# AI Tech Daily - 自動実行スクリプト
# Cronジョブから呼び出され、generate-news スキルを実行します

# 作業ディレクトリへ移動
cd ~/claude-dev/ai-tech-daily || exit 1

# ログディレクトリ作成
mkdir -p logs

# ログファイル名（日付付き）
LOG_FILE="logs/news_$(date +%Y%m%d_%H%M%S).log"

# 実行開始
echo "===== AI Tech Daily News Generation =====" | tee -a "$LOG_FILE"
echo "Start: $(date)" | tee -a "$LOG_FILE"

# Claude Codeのスキルを実行
claude /generate-news 2>&1 | tee -a "$LOG_FILE"

# 終了
echo "End: $(date)" | tee -a "$LOG_FILE"
echo "===== ===== =====" | tee -a "$LOG_FILE"
