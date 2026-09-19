#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
partner-skill: Chat Log Parser & Positive Signal Extractor
专为情侣设计的聊天记录解析器：
1. 提取双方发言互动比与回复节奏
2. 捕获深层关怀、叮嘱、报备等正向爱意信号
3. 识别“情绪刹车保护机制”（如“去洗澡了/我睡了”，识别为克制而非单纯冷暴力）
4. 输出结构化 Markdown 分析报告
"""

import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any, Optional

# 解决 Windows 等平台终端输出 Unicode/Emoji 编码异常
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 正向关怀信号词典
POSITIVE_SIGNALS = {
    "care": [
        "早点睡", "多喝水", "别熬夜", "按时吃饭", "吃药", "胃痛", "多穿点",
        "带伞", "路上小心", "慢点开", "辛苦了", "累不累", "别太拼", "我来弄",
        "热牛奶", "给你点", "外套", "注意保暖"
    ],
    "reporting": [
        "到家了", "到公司了", "下班了", "刚开完会", "在地铁上", "吃过饭了",
        "醒了", "刚忙完", "准备睡了", "登机了", "落地了"
    ],
    "affection": [
        "想你", "抱抱", "宝贝", "小宝", "亲亲", "爱你", "乖乖", "好乖",
        "可爱", "贴贴", "真棒", "好想见你", "天下第一好"
    ],
    "sharing": [
        "你看这个", "今天遇到了", "笑死我了", "推荐你", "这个好好吃",
        "下次带你去", "想和你一起", "拍照给你看"
    ]
}

# 情绪刹车词典（避免更激烈言语伤害感情的主动冷却行为）
EMOTIONAL_BRAKE_KEYWORDS = [
    "去洗澡了", "洗澡去了", "先睡了", "我睡了", "不说了", "算了不说这个了",
    "累了", "冷静一下", "晚安了"
]


class ChatMessage:
    def __init__(self, sender: str, content: str, timestamp: Optional[str] = None):
        self.sender = sender.strip()
        self.content = content.strip()
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "content": self.content,
            "timestamp": self.timestamp
        }


class ChatParser:
    def __init__(self, partner_name: Optional[str] = None):
        self.partner_name = partner_name

    def parse_text(self, text: str) -> List[ChatMessage]:
        """解析文本行格式或微信/QQ导出格式"""
        messages: List[ChatMessage] = []
        lines = text.strip().splitlines()

        # 模式 1: 时间 昵称 [换行或冒号] 消息内容 (常见微信/QQ 导出)
        # 例如: 2026-05-20 13:14:00 小宝: 在干嘛呢
        pattern_timed = re.compile(
            r"^(\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}(?::\d{2})?)\s+([^:\n]+)[:：\s]\s*(.*)$"
        )
        # 模式 2: [男/女/昵称]: 消息内容
        pattern_simple = re.compile(r"^\[?([^:\n\]]{1,20})\]?[:：]\s*(.*)$")

        current_msg: Optional[ChatMessage] = None

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            timed_match = pattern_timed.match(line_str)
            if timed_match:
                ts, sender, content = timed_match.groups()
                current_msg = ChatMessage(sender=sender, content=content, timestamp=ts)
                messages.append(current_msg)
                continue

            simple_match = pattern_simple.match(line_str)
            if simple_match:
                sender, content = simple_match.groups()
                current_msg = ChatMessage(sender=sender, content=content)
                messages.append(current_msg)
                continue

            # 多行消息延续
            if current_msg is not None:
                current_msg.content += "\n" + line_str
            else:
                # 无法识别发送者时的默认归类
                current_msg = ChatMessage(sender="未知/伴侣", content=line_str)
                messages.append(current_msg)

        return messages

    def analyze(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        """对解析得到的消息列表进行正向与情感节律分析"""
        if not messages:
            return {"error": "无有效聊天记录"}

        sender_counts = defaultdict(int)
        sender_words = defaultdict(int)
        positive_matches = defaultdict(list)
        brakes_detected = []

        for idx, msg in enumerate(messages):
            sender = msg.sender
            content = msg.content
            sender_counts[sender] += 1
            sender_words[sender] += len(content)

            # 检索正向信号
            for category, keywords in POSITIVE_SIGNALS.items():
                for kw in keywords:
                    if kw in content:
                        positive_matches[sender].append({
                            "type": category,
                            "keyword": kw,
                            "content": content,
                            "timestamp": msg.timestamp,
                            "index": idx + 1
                        })
                        break

            # 检索情绪刹车
            for kw in EMOTIONAL_BRAKE_KEYWORDS:
                if kw in content:
                    brakes_detected.append({
                        "sender": sender,
                        "keyword": kw,
                        "content": content,
                        "timestamp": msg.timestamp,
                        "index": idx + 1
                    })
                    break

        total_msgs = len(messages)
        sender_stats = {}
        for sender, count in sender_counts.items():
            sender_stats[sender] = {
                "message_count": count,
                "percentage": round(count / total_msgs * 100, 1),
                "total_words": sender_words[sender],
                "avg_words_per_msg": round(sender_words[sender] / count, 1) if count else 0,
                "positive_count": len(positive_matches[sender])
            }

        return {
            "total_messages": total_msgs,
            "sender_stats": sender_stats,
            "positive_matches": dict(positive_matches),
            "brakes_detected": brakes_detected
        }

    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """生成面向情侣的高情商正向 Markdown 分析报告"""
        if "error" in analysis:
            return f"❌ 分析失败: {analysis['error']}"

        stats = analysis["sender_stats"]
        brakes = analysis["brakes_detected"]
        positives = analysis["positive_matches"]

        md = []
        md.append("# 📊 partner-skill 聊天记录正向解码报告\n")
        md.append("> **原则**：绝不挑拨、只看深情。透过数据看见彼此的奔赴与克制。\n")

        md.append("## 1. 互动节律与发言分析")
        for sender, stat in stats.items():
            md.append(f"- **{sender}**：发送 `{stat['message_count']}` 条消息（占比 `{stat['percentage']}%`），捕获正向爱意信号 `{stat['positive_count']}` 次。")
        md.append("")

        md.append("## 2. 🛡️ 情绪刹车与克制保护记录")
        if brakes:
            md.append("以下节点为伴侣在情绪波动时主动踩下的**“情绪刹车”**。ta 选择了克制沉默，避免了口出恶言伤害感情：")
            for b in brakes:
                ts_info = f" [{b['timestamp']}]" if b['timestamp'] else ""
                md.append(f"- **第 {b['index']} 句**{ts_info} **{b['sender']}**：“{b['content']}”（*关键词: {b['keyword']}*）")
        else:
            md.append("- 本次对话交流整体温和平稳，未检测到激烈情绪刹车。")
        md.append("")

        md.append("## 3. 💖 被看见的深情与付出细节")
        has_positive = False
        for sender, items in positives.items():
            if items:
                has_positive = True
                md.append(f"### 💌 {sender} 的闪光关怀：")
                # 最多展示代表性的 5 条
                for item in items[:5]:
                    category_names = {
                        "care": "生活细微关照",
                        "reporting": "安全感及时报备",
                        "affection": "爱意与依赖表达",
                        "sharing": "分享欲与生活联结"
                    }
                    cat_cn = category_names.get(item["type"], "正向互动")
                    md.append(f"- **[{cat_cn}]** “{item['content']}”")
        if not has_positive:
            md.append("- 记录中双方表达较为内敛，建议在后续日常中多说一句‘辛苦了’、多给一个拥抱。")

        return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(description="partner-skill 聊天记录解析与深情信号提取工具")
    parser.add_argument("input_file", help="聊天记录文本文件路径 (.txt / .csv)")
    parser.add_argument("--partner", help="伴侣名称（可选）", default=None)
    parser.add_argument("--output", help="输出 Markdown 报告路径", default=None)
    parser.add_argument("--json", help="输出原始 JSON 格式", action="store_true")

    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ 找不到文件: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text(encoding="utf-8", errors="ignore")
    chat_parser = ChatParser(partner_name=args.partner)
    messages = chat_parser.parse_text(text)
    analysis = chat_parser.analyze(messages)

    if args.json:
        out_str = json.dumps(analysis, ensure_ascii=False, indent=2)
    else:
        out_str = chat_parser.generate_report(analysis)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out_str, encoding="utf-8")
        print(f"✅ 分析报告已成功保存至: {args.output}")
    else:
        print(out_str)


if __name__ == "__main__":
    main()
