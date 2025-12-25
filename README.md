# 🤖 AI Chat Analyzer

Analyze your **exported AI chat history** (e.g., from Qwen) to generate insightful reports:

- 📊 Total conversations & messages  
- 📅 Monthly activity trends (or all-time)  
- 💬 User vs. AI message & word counts  
- 🧠 Most-used AI models  
- 📝 Exportable summary (Markdown)

Perfect for your **"AI Year in Review"**!

> ✨ Supports JSON exports with message timestamps and roles (like Qwen's format).

---

## 🚀 Quick Start

### 1. Export your chat history
Save your conversations as a **JSON file** (e.g., `chat_export.json`).  
It must contain messages with:
- `role` (`"user"` or `"assistant"`)
- `timestamp` (Unix seconds, e.g., `1766656979`)

### 2. Run the analyzer
```bash
# Analyze all time
python ai_chat_analyzer.py chat_export.json

# Analyze specific year (e.g., 2025)
python ai_chat_analyzer.py chat_export.json 2025
```

> 🔍 The script will:
> - Parse all conversations and messages
> - Print a summary in the terminal
> - Save a detailed report as `ai_chat_summary_all.md` or `ai_chat_summary_2025.md`

💡 **Tip**: Make sure your JSON file follows the expected structure (see [Supported Data Format](#supported-data-format)).

---

## 📁 Example Output

```
============================================================
🤖 AI 对话统计报告（2025）
============================================================
📁 总对话会话数: 84
💬 总消息条数: 1,247
  - 用户提问: 623 条 (28,412 字)
  - AI 回答: 624 条 (152,890 字)

📈 月度活跃度:
  - January 2025: 42 条消息
  - February 2025: 38 条消息
  ...
  - December 2025: 156 条消息

🧠 最常使用的模型:
  - qwen3-max-2025-10-30: 84 次

📊 平均每场对话消息数: 14.8
============================================================
```

And `ai_chat_summary_2025.md`:
```markdown
# AI 对话统计报告（2025）

- 对话会话数: 84
- 总消息数: 1247
- 用户消息: 623 条（28412 字）
- AI 消息: 624 条（152890 字）

## 月度活跃度
- January 2025: 42 条
- February 2025: 38 条
...
```

---

## 📦 Supported Data Format

Your JSON should look like:

```json
{
  "success": true,
  "data": [
    {
      "title": "My Chat",
      "chat": {
        "history": {
          "messages": {
            "msg1": {
              "role": "user",
              "content": "Hello!",
              "timestamp": 1766656979
            },
            "msg2": {
              "role": "assistant",
              "content": "",
              "content_list": [
                {
                  "content": "Hi there!",
                  "role": "assistant"
                }
              ],
              "timestamp": 1766656985,
              "model": "qwen3-max-2025-10-30"
            }
          }
        }
      }
    }
  ]
}
```

> 🔧 Need support for another format? Open an issue!

---

## 🛠️ Requirements

- Python 3.7+
- No third-party dependencies (uses only standard library)

---

## 🤝 Contributing

Feel free to:
- 🐞 Report bugs
- 💡 Suggest new stats (e.g., word clouds, response time)
- 🌐 Add support for other AI platforms (ChatGPT, Claude, etc.)

---

## 🤖 AI-Generated Notice

This script was **written with the assistance of an AI** (Qwen). The logic, structure, and documentation were collaboratively designed to analyze personal AI chat exports responsibly and efficiently.