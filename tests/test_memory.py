#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for partner-skill MemoryManager
"""

import sys
import shutil
import unittest
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.memory import MemoryManager


class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mgr = MemoryManager(base_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_and_get_profile(self):
        profile = self.mgr.init_profile(
            name="小美",
            nickname="美美",
            traits=["嘴硬心软", "重细节"],
            triggers=["讲大道理"],
            calming_switch="给一个大大的拥抱",
            build_mode="grill_me_interview"
        )
        self.assertEqual(profile["partner_name"], "小美")
        self.assertEqual(profile["nickname"], "美美")
        self.assertEqual(profile["build_mode"], "grill_me_interview")

        fetched = self.mgr.get_profile("小美")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["partner_name"], "小美")
        self.assertIn("嘴硬心软", fetched["personality_traits"])

    def test_add_and_list_highlights(self):
        self.mgr.add_highlight(
            name="小美",
            action="深夜送来养胃粥",
            hidden_love="刀子嘴豆腐心，行动力永远比言语诚实",
            tag="caring"
        )
        self.mgr.add_highlight(
            name="小美",
            action="偷偷记住我喜欢的球鞋并送我作为生日礼物",
            hidden_love="默默把我说过的每一句话都放在心上",
            tag="sweet"
        )

        highlights = self.mgr.list_highlights("小美")
        self.assertEqual(len(highlights), 2)
        self.assertEqual(highlights[0]["partner_action"], "深夜送来养胃粥")
        self.assertEqual(highlights[1]["tag"], "sweet")

    def test_store_and_search_corpus(self):
        msgs = [
            {"sender": "小美", "content": "今天记得吃早餐呀，笨蛋"},
            {"sender": "我", "content": "好啦知道啦"},
            {"sender": "小美", "content": "下班我去接你，想吃火锅吗"}
        ]
        count = self.mgr.store_corpus("小美", msgs)
        self.assertEqual(count, 3)

        results = self.mgr.search_corpus("小美", "火锅")
        self.assertEqual(len(results), 1)
        self.assertIn("想吃火锅吗", results[0]["content"])

    def test_add_and_list_corrections(self):
        self.mgr.add_correction(
            name="小美",
            context="被催着吃饭时",
            user_feedback="ta不会说严肃的话，只会发个生气的猫猫表情包然后说快去吃啦"
        )
        cors = self.mgr.list_corrections("小美")
        self.assertEqual(len(cors), 1)
        self.assertEqual(cors[0]["context"], "被催着吃饭时")
        self.assertIn("猫猫表情包", cors[0]["user_feedback"])

    def test_export_digest(self):
        self.mgr.init_profile(
            name="小美",
            nickname="美美",
            gender="女生",
            traits=["嘴硬心软"]
        )
        self.mgr.add_highlight(
            name="小美",
            action="下雨天送伞",
            hidden_love="默默把我说的话放在心上"
        )
        digest = self.mgr.export_digest("小美")
        self.assertIn("属于我们与【美美】的恋爱回忆录", digest)
        self.assertIn("下雨天送伞", digest)
        self.assertIn("女生", digest)


if __name__ == "__main__":
    unittest.main()
