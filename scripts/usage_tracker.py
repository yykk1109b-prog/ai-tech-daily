#!/usr/bin/env python3
"""
AI Tech Daily - 使用量トラッカー
Claude APIの無料枠使用量を監視
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import anthropic


class UsageTracker:
    """API使用量トラッカー"""

    # 無料枠の設定（月間）
    FREE_TIER_LIMIT = 200_000  # 入力トークン
    FREE_TIER_OUTPUT_LIMIT = 100_000  # 出力トークン

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.usage_file = repo_root / "_data" / "usage.json"
        self.usage_data = self._load_usage()

    def _load_usage(self) -> dict:
        """使用量データを読み込む"""
        if self.usage_file.exists():
            with open(self.usage_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "start_date": datetime.now(timezone.utc).isoformat(),
            "input_tokens": 0,
            "output_tokens": 0,
            "requests": 0,
        }

    def _save_usage(self):
        """使用量データを保存"""
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.usage_file, "w", encoding="utf-8") as f:
            json.dump(self.usage_data, f, indent=2)

    def check_free_tier(self) -> tuple[bool, str]:
        """無料枠内かチェック"""
        input_remaining = self.FREE_TIER_LIMIT - self.usage_data["input_tokens"]
        output_remaining = self.FREE_TIER_OUTPUT_LIMIT - self.usage_data["output_tokens"]

        if input_remaining < 0 or output_remaining < 0:
            return False, "無料枠を超過しています"

        warning = None
        if input_remaining < 50_000 or output_remaining < 25_000:
            warning = f"無料枠が残り少ないです（入力: {input_remaining:,}、出力: {output_remaining:,}トークン）"

        return True, warning or "OK"

    def track_request(self, input_tokens: int, output_tokens: int):
        """リクエストを追跡"""
        self.usage_data["input_tokens"] += input_tokens
        self.usage_data["output_tokens"] += output_tokens
        self.usage_data["requests"] += 1
        self._save_usage()


def get_current_usage(api_key: str) -> dict:
    """現在の使用量を取得（Anthropic APIから）"""
    try:
        client = anthropic.Anthropic(api_key=api_key)
        # Note: 現在のAPIバージョンでは使用量取得エンドポイントが制限されています
        # ローカルトラッキングを優先使用
        return {
            "input_tokens": 0,
            "output_tokens": 0,
        }
    except Exception:
        return {
            "input_tokens": 0,
            "output_tokens": 0,
        }


def main() -> None:
    """メイン処理"""
    repo_root = Path(__file__).resolve().parent.parent
    tracker = UsageTracker(repo_root)

    is_ok, message = tracker.check_free_tier()
    print(f"Status: {message}")
    print(f"Usage: {tracker.usage_data}")


if __name__ == "__main__":
    main()
