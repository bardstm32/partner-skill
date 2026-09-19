#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
partner-skill: Local Memory & Highlights Storage Manager
管理伴侣人设档案 (profile.json) 与相爱高光时刻记录 (highlights.jsonl)。
完全运行于用户本地，严守情侣隐私。
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# 解决 Windows 等平台终端输出 Unicode/Emoji 编码异常
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


class MemoryManager:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = Path("partners")
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_partner_dir(self, name: str) -> Path:
        slug = "".join(c if c.isalnum() else "_" for c in name.strip().lower())
        pdir = self.base_dir / slug
        pdir.mkdir(parents=True, exist_ok=True)
        return pdir

    def init_profile(
        self,
        name: str,
        nickname: Optional[str] = None,
        gender: Optional[str] = None,
        traits: Optional[List[str]] = None,
        triggers: Optional[List[str]] = None,
        calming_switch: Optional[str] = None,
        build_mode: str = "grill_me_interview"
    ) -> Dict[str, Any]:
        """初始化或更新伴侣画像档案"""
        pdir = self._get_partner_dir(name)
        profile_file = pdir / "profile.json"

        data = {
            "partner_name": name,
            "nickname": nickname or name,
            "gender": gender or "未指定",
            "build_mode": build_mode,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "personality_traits": traits or [],
            "triggers": triggers or [],
            "calming_switch": calming_switch or "给予充满安全感的拥抱与温和认错",
            "relationship_stage": "in_relationship"
        }

        profile_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data

    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """获取伴侣档案"""
        pdir = self._get_partner_dir(name)
        profile_file = pdir / "profile.json"
        if not profile_file.exists():
            return None
        return json.loads(profile_file.read_text(encoding="utf-8"))

    def add_highlight(
        self,
        name: str,
        action: str,
        hidden_love: str,
        tag: str = "caring"
    ) -> Dict[str, Any]:
        """追加一条相爱高光时刻 / 闪光付出记忆"""
        pdir = self._get_partner_dir(name)
        hl_file = pdir / "highlights.jsonl"

        entry = {
            "timestamp": datetime.now().isoformat(),
            "partner_action": action,
            "hidden_love": hidden_love,
            "tag": tag
        }

        with open(hl_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return entry

    def list_highlights(self, name: str) -> List[Dict[str, Any]]:
        """列出该伴侣的所有高光瞬间"""
        pdir = self._get_partner_dir(name)
        hl_file = pdir / "highlights.jsonl"
        if not hl_file.exists():
            return []

        entries = []
        with open(hl_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line.strip()))
        return entries

    def store_corpus(self, name: str, messages: List[Dict[str, Any]]) -> int:
        """全量留存真实聊天语料库，用于后续相似场景检索与语言习惯复刻"""
        pdir = self._get_partner_dir(name)
        corpus_file = pdir / "corpus.jsonl"
        count = 0
        with open(corpus_file, "a", encoding="utf-8") as f:
            for msg in messages:
                entry = {
                    "timestamp": msg.get("timestamp") or datetime.now().isoformat(),
                    "sender": msg.get("sender", ""),
                    "content": msg.get("content", "")
                }
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                count += 1
        return count

    def search_corpus(self, name: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """在语料库中检索包含关键词的相似对话"""
        pdir = self._get_partner_dir(name)
        corpus_file = pdir / "corpus.jsonl"
        if not corpus_file.exists():
            return []
        matches = []
        with open(corpus_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line.strip())
                    if query in item.get("content", ""):
                        matches.append(item)
                        if len(matches) >= limit:
                            break
        return matches

    def add_correction(self, name: str, context: str, user_feedback: str) -> Dict[str, Any]:
        """记录用户反馈‘ta不会这样’时的场景与修正建议"""
        pdir = self._get_partner_dir(name)
        cor_file = pdir / "corrections.jsonl"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "user_feedback": user_feedback
        }
        with open(cor_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def list_corrections(self, name: str) -> List[Dict[str, Any]]:
        """查看用户的所有纠偏记录"""
        pdir = self._get_partner_dir(name)
        cor_file = pdir / "corrections.jsonl"
        if not cor_file.exists():
            return []
        entries = []
        with open(cor_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line.strip()))
        return entries

    def export_digest(self, name: str, output_path: Optional[str] = None) -> str:
        """导出恋爱回忆录 / 高光纪念册 Markdown 文档"""
        prof = self.get_profile(name) or {}
        highlights = self.list_highlights(name)
        partner_name = prof.get("partner_name", name)
        nickname = prof.get("nickname", partner_name)
        gender = prof.get("gender", "伴侣")
        traits = prof.get("personality_traits", [])

        md = []
        md.append(f"# 💌 属于我们与【{nickname}】的恋爱回忆录\n")
        md.append("> “时间在流逝，但每一次被你认真爱着的瞬间，都被时光温柔定格。”\n")
        md.append("## 🌟 伴侣画像与相爱基调")
        md.append(f"- **伴侣称呼**：{partner_name}（昵称: {nickname}）")
        md.append(f"- **角色设定**：{gender}")
        if traits:
            md.append(f"- **闪光特质**：{'、'.join(traits)}")
        md.append("")

        md.append("## 💖 被认真深爱着的高光时刻")
        if not highlights:
            md.append("- 还没有记录高光瞬间，快去捕捉一次 ta 的关怀吧。")
        else:
            for idx, h in enumerate(highlights, 1):
                ts = h.get("timestamp", "")[:10]
                action = h.get("partner_action", "")
                love = h.get("hidden_love", "")
                tag = h.get("tag", "caring")
                md.append(f"### {idx}. [{ts}] 关于爱的细节（{tag}）")
                md.append(f"- **真实付出**：{action}")
                md.append(f"- **深层爱意**：{love}\n")

        md.append("## 🕊️ 爱的箴言与未来寄语")
        md.append("“相爱是一场长跑。愿无论未来遇到多少风雨，我们都能翻开这本回忆录，重温最初的坚定。”\n")

        content = "\n".join(md)
        if output_path:
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(content, encoding="utf-8")
        return content


def main():
    parser = argparse.ArgumentParser(description="partner-skill 本地记忆与高光沉淀管理器")
    subparsers = parser.add_subparsers(dest="command")

    # init 子命令
    init_cmd = subparsers.add_parser("init", help="初始化伴侣档案")
    init_cmd.add_argument("name", help="伴侣称呼")
    init_cmd.add_argument("--nickname", help="亲昵称呼", default=None)
    init_cmd.add_argument("--gender", help="性别与角色 (女生/男生)", default="未指定")
    init_cmd.add_argument("--traits", help="性格标签(逗号分隔)", default="")
    init_cmd.add_argument("--triggers", help="情绪雷区(逗号分隔)", default="")
    init_cmd.add_argument("--calm", help="专属哄好开关", default=None)
    init_cmd.add_argument("--mode", help="建档方式 (chat/interview)", default="interview")

    # get 子命令
    get_cmd = subparsers.add_parser("get", help="查看伴侣档案")
    get_cmd.add_argument("name", help="伴侣称呼")

    # add-highlight 子命令
    add_hl = subparsers.add_parser("add-highlight", help="沉淀一条感动付出高光时刻")
    add_hl.add_argument("name", help="伴侣称呼")
    add_hl.add_argument("--action", required=True, help="ta 做出的具体付出或关怀举动")
    add_hl.add_argument("--love", required=True, help="其背后的深层爱意解读")
    add_hl.add_argument("--tag", default="caring", help="标签 (caring/sacrifice/sweet)")

    # list-highlights 子命令
    list_hl = subparsers.add_parser("list-highlights", help="查看所有高光记录")
    list_hl.add_argument("name", help="伴侣称呼")

    # correct 子命令 (ta不会这样纠错)
    cor_cmd = subparsers.add_parser("correct", help="记录‘ta不会这样’的纠错反馈")
    cor_cmd.add_argument("name", help="伴侣称呼")
    cor_cmd.add_argument("--context", required=True, help="发生偏差的情境或话题")
    cor_cmd.add_argument("--feedback", required=True, help="真实 ta 的回复习惯或反应")

    # list-corrections 子命令
    list_cor = subparsers.add_parser("list-corrections", help="查看历史纠偏记录")
    list_cor.add_argument("name", help="伴侣称呼")

    # search-corpus 子命令
    search_cp = subparsers.add_parser("search-corpus", help="检索真实语料库")
    search_cp.add_argument("name", help="伴侣称呼")
    search_cp.add_argument("query", help="关键词")

    # export 子命令 (导出恋爱回忆录)
    export_cmd = subparsers.add_parser("export", help="导出恋爱回忆录")
    export_cmd.add_argument("name", help="伴侣称呼")
    export_cmd.add_argument("--output", help="输出 Markdown 文件路径", default=None)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    mgr = MemoryManager()

    if args.command == "init":
        traits_list = [t.strip() for t in args.traits.split(",") if t.strip()]
        triggers_list = [t.strip() for t in args.triggers.split(",") if t.strip()]
        res = mgr.init_profile(
            name=args.name,
            nickname=args.nickname,
            gender=args.gender,
            traits=traits_list,
            triggers=triggers_list,
            calming_switch=args.calm,
            build_mode=args.mode
        )
        print(f"✅ 成功初始化【{args.name}】的情侣档案：\n{json.dumps(res, ensure_ascii=False, indent=2)}")

    elif args.command == "get":
        prof = mgr.get_profile(args.name)
        if prof:
            print(json.dumps(prof, ensure_ascii=False, indent=2))
        else:
            print(f"⚠️ 未找到【{args.name}】的档案，请先使用 init 命令创建。")

    elif args.command == "add-highlight":
        hl = mgr.add_highlight(name=args.name, action=args.action, hidden_love=args.love, tag=args.tag)
        print(f"💖 高光时刻已沉淀：\n{json.dumps(hl, ensure_ascii=False, indent=2)}")

    elif args.command == "list-highlights":
        items = mgr.list_highlights(args.name)
        if not items:
            print(f"目前还没有记录【{args.name}】的高光时刻，快去捕捉一次吧！")
        else:
            print(f"🌟 【{args.name}】的相爱高光时刻总数: {len(items)}\n")
            for idx, item in enumerate(items, 1):
                print(f"{idx}. [{item['timestamp'][:10]}] 付出: {item['partner_action']} -> 爱意: {item['hidden_love']}")

    elif args.command == "correct":
        cor = mgr.add_correction(name=args.name, context=args.context, user_feedback=args.feedback)
        print(f"📝 已记录【{args.name}】的习惯纠偏：\n{json.dumps(cor, ensure_ascii=False, indent=2)}")

    elif args.command == "list-corrections":
        items = mgr.list_corrections(args.name)
        if not items:
            print(f"目前还没有关于【{args.name}】的纠偏记录~")
        else:
            print(f"📝 【{args.name}】的习惯纠偏记录总数: {len(items)}\n")
            for idx, item in enumerate(items, 1):
                print(f"{idx}. 情境: {item['context']} -> 真实习惯: {item['user_feedback']}")

    elif args.command == "search-corpus":
        results = mgr.search_corpus(args.name, args.query)
        if not results:
            print(f"在【{args.name}】的语料库中未找到包含‘{args.query}’的记录~")
        else:
            print(f"🔍 找到 {len(results)} 条匹配的真实语料：\n")
            for item in results:
                print(f"[{item.get('sender', '未知')}]: {item.get('content', '')}")

    elif args.command == "export":
        digest = mgr.export_digest(args.name, args.output)
        if args.output:
            print(f"📖 恋爱回忆录已成功导出至: {args.output}")
        else:
            print(digest)


if __name__ == "__main__":
    main()

