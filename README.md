# FATESCROLL 命理推演 · fatescroll-divination

> 八字 / 紫微斗数 / 周易卦象的 **Agent 技能**（SKILL.md 格式）。排盘由确定性脚本精确计算（真节气分界、农历转换、起运天数均为程序运算），推演解读由宿主 Agent 自带的大模型完成——**零 API Key、零外部依赖**，装在哪个 Agent IDE 就用谁的模型。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 安装

### WorkBuddy（腾讯）
设置 → 技能 → **上传技能** → 选择 [fatescroll-divination-skill.zip](fatescroll-divination-skill.zip) 导入，自动完成配置。

### 其他支持 SKILL.md 的 Agent（ZCode / Claude Code / Qoder …）
```bash
# 用户级（示例：ZCode）
mkdir -p ~/.zcode/skills
cp -R skills/fatescroll-divination ~/.zcode/skills/
# 或 .agents 惯例目录
mkdir -p ~/.agents/skills
cp -R skills/fatescroll-divination ~/.agents/skills/
```
重启会话后生效。

## 使用

直接对话即可触发：

| 你说 | 它做 |
|---|---|
| 「帮我看个八字」 | 索要出生日期/时辰/性别 → 脚本排盘 → 命格解读 |
| 「我 2027 年运势如何」 | 流年推演（目标日期自动传参） |
| 「帮我合婚」 | 双方各自排盘 + 八字合婚框架 |
| 「今天卦象如何」 | 当日本卦/互卦（按文王卦序确定性获取） |
| 「紫微命盘」 | 十二宫 + 本命四化 + 格局（Node 运行时） |

**红线**：涉及自伤等危机内容会停止推演并提供心理援助热线；全部输出附「文化参考、非专业建议」免责声明。

## 引擎可信度

- 排盘引擎与 [FATESCROLL](https://fatescroll.ai)（iOS/Web 应用）**同源**，经锁定向量回归保护（如 `1990-01-01 → 己巳/丙子/丙寅/戊子`）。
- 双运行时：Node（首选，含紫微，自包含单文件）与 Python 3 标准库（兜底，内置 MIT 许可的 lunar_python 副本）；同输入输出逐字一致。
- 全部推演引用脚本既算事实（干支/十神/星曜），禁止模型凭记忆重排。

## 目录

```
skills/fatescroll-divination/
├── SKILL.md                  # 触发与工作流
├── references/               # 八字 8 框架 / 周易 8 框架 / 合婚 6 框架 / 报告格式 / 伦理
└── scripts/
    ├── fatescroll_calc.cjs   # Node 排盘引擎（esbuild 自包含）
    ├── fatescroll_calc.py    # Python 零依赖兜底
    ├── lunar_python/         # MIT 历法库内置副本
    └── claim_account.sh      # 可选：绑定 fatescroll.ai 账号（跨设备/存档案）
```

## 说明

- 完整体验（生辰档案、命盘可视化、七位 AI 命理师对话、精装命书/运书）：**https://fatescroll.ai**
- 本技能内容属传统文化娱乐/文化参考，不构成任何专业建议；请相信科学、理性看待。
- License: MIT（内置第三方库见各目录 LICENSE）
