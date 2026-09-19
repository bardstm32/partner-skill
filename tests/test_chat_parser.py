#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for partner-skill ChatParser
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.chat_parser import ChatParser, ChatMessage


class TestChatParser(unittest.TestCase):
    def setUp(self):
        self.parser = ChatParser(partner_name="小晴")

    def test_parse_simple_format(self):
        text = """
        小宝: 随便你吧，反正你每次都觉得自己对
        大头: 我只是在跟你讲道理啊
        小宝: 行行行，你跟道理过一辈子去吧，去洗澡了
        """
        msgs = self.parser.parse_text(text)
        self.assertEqual(len(msgs), 3)
        self.assertEqual(msgs[0].sender, "小宝")
        self.assertIn("随便你吧", msgs[0].content)
        self.assertEqual(msgs[1].sender, "大头")
        self.assertEqual(msgs[2].sender, "小宝")

    def test_parse_timed_format(self):
        text = """
        2026-05-20 13:14:00 小宝: 宝宝到家了吗，路上小心点带伞没
        2026-05-20 13:15:30 大头: 已经到了，放心吧
        """
        msgs = self.parser.parse_text(text)
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0].sender, "小宝")
        self.assertEqual(msgs[0].timestamp, "2026-05-20 13:14:00")
        self.assertIn("路上小心", msgs[0].content)

    def test_analyze_positive_signals_and_brakes(self):
        text = """
        [女]: 今天加班好累啊
        [男]: 辛苦了宝贝，按时吃饭，下班我去接你
        [女]: 行行行你道理最大，我不说了，去洗澡了
        """
        msgs = self.parser.parse_text(text)
        analysis = self.parser.analyze(msgs)

        self.assertEqual(analysis["total_messages"], 3)
        self.assertIn("男", analysis["sender_stats"])
        # Check positive signal detected for 男 (辛苦了, 宝贝, 按时吃饭)
        self.assertGreater(analysis["sender_stats"]["男"]["positive_count"], 0)

        # Check emotional brake detected for 女 (去洗澡了)
        self.assertEqual(len(analysis["brakes_detected"]), 1)
        self.assertEqual(analysis["brakes_detected"][0]["sender"], "女")
        self.assertEqual(analysis["brakes_detected"][0]["keyword"], "去洗澡了")

    def test_generate_report(self):
        text = """
        [小美]: 路上小心，多穿点
        [大明]: 知道啦，想你
        """
        msgs = self.parser.parse_text(text)
        analysis = self.parser.analyze(msgs)
        report = self.parser.generate_report(analysis)

        self.assertIn("partner-skill 聊天记录正向解码报告", report)
        self.assertIn("小美", report)
        self.assertIn("生活细微关照", report)


if __name__ == "__main__":
    unittest.main()
