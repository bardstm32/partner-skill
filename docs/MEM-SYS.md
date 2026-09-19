# 🧠 partner-skill 记忆与高光沉淀系统 (MEM-SYS)

为了让 `partner-skill` 具备长期记忆与越来越懂你们关系的能力，系统设计了本地轻量化的数据沉淀机制。

---

## 1. 目录结构

所有记忆与档案存储于本地工作目录（默认在 `.gitignore` 中受到隐私保护）：

```
partners/
└── {partner_slug}/
    ├── profile.json            # 伴侣与情侣关系基础档案
    ├── corpus.jsonl            # 真实原始聊天语料库（供场景匹配与语气习惯复刻）
    ├── corrections.jsonl       # 用户“ta不会这样”的纠错沉淀记录
    ├── highlights.jsonl        # 闪光时刻与感动点滴记忆流水
    ├── conflicts.jsonl         # 历次冲突解码与和解复盘
    └── chats/                  # 导入的原始聊天记录文件归档
```

---

## 2. 数据结构规范

### 2.1 伴侣基础档案 (`profile.json`)

```json
{
  "partner_name": "小晴",
  "nickname": "晴宝",
  "gender": "female",
  "relationship_stage": "in_relationship",
  "anniversary": "2023-05-20",
  "mbti": "ISFJ",
  "love_languages": ["words_of_affirmation", "quality_time"],
  "comfort_foods": ["热奶茶", "草莓蛋糕", "火锅"],
  "triggers": ["被敷衍", "长时间失联", "不听解释直接讲道理"],
  "calming_methods": ["紧紧抱住不撒手", "轻声认错说我一直在", "递上一杯温水"]
}
```

### 2.2 闪光时刻记录 (`highlights.jsonl`)

每当从聊天记录或日常互动中捕捉到对方深爱你的细节时沉淀一条：

```json
{
  "timestamp": "2026-09-18T22:30:00",
  "context": "深夜加班胃痛",
  "partner_action": "嘴上埋怨我不按时吃饭，但半小时后外卖送来了热粥和养胃冲剂",
  "hidden_love": "刀子嘴豆腐心，行动力永远比言语诚实",
  "tag": "caring"
}
```

---

## 3. 记忆检索与动态注入

当用户执行 `/partner decode` 或 `/partner reflect` 时，系统自动读取伴侣 profile 与历史高光细节：
- 提取对方过去的温柔举动作为反思证据；
- 结合对方的情感雷区与平复方式（`calming_methods`），生成量身定制的破冰文案。
- 检索 `corpus.jsonl` 中相似情境的对话，提取语言习惯用于习惯复刻回复~
