import json
from collections import defaultdict
from datetime import datetime
import os

def analyze_chat_history(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not data.get("success") or "data" not in data:
        raise ValueError("JSON 格式不符合预期，请检查文件结构。")

    all_messages = []
    total_conversations = len(data["data"])
    model_usage = defaultdict(int)
    user_messages = []
    assistant_messages = []

    for conv in data["data"]:
        chat = conv.get("chat", {})
        messages_dict = chat.get("history", {}).get("messages", {})
        messages = list(messages_dict.values())
        # 按 timestamp 排序（虽然通常有序，但保险起见）
        messages.sort(key=lambda x: x.get("timestamp") or 0)
        all_messages.extend(messages)

        # 统计用户和助手消息
        for msg in messages:
            role = msg.get("role")
            if role == "user":
                user_messages.append(msg)
            elif role == "assistant":
                assistant_messages.append(msg)

            # 统计模型（从 assistant 消息中提取）
            if role == "assistant":
                model = msg.get("model") or msg.get("modelName", "unknown")
                model_usage[model] += 1

    total_messages = len(all_messages)
    total_user = len(user_messages)
    total_assistant = len(assistant_messages)

    # 时间分析
    timestamps = [msg["timestamp"] for msg in all_messages if msg.get("timestamp") is not None]
    if not timestamps:
        print("未找到有效时间戳。")
        return

    dates = [datetime.fromtimestamp(ts) for ts in timestamps]
    years = [d.year for d in dates]
    months = [(d.year, d.month) for d in dates]
    days = [d.date() for d in dates]

    # 默认分析 2025 年（根据当前时间）
    target_year = 2025
    messages_2025 = [
        msg for msg in all_messages
        if msg.get("timestamp") is not None and datetime.fromtimestamp(msg["timestamp"]).year == target_year
    ]
    user_2025 = [m for m in messages_2025 if m.get("role") == "user"]
    assistant_2025 = [m for m in messages_2025 if m.get("role") == "assistant"]

    # 字数统计
    def count_words(msg_list):
        return sum(len(msg.get("content", "")) for msg in msg_list)

    user_words = count_words(user_messages)
    assistant_words = count_words(assistant_messages)
    user_words_2025 = count_words(user_2025)
    assistant_words_2025 = count_words(assistant_2025)

    # 每月活跃度
    month_counts = defaultdict(int)
    for d in dates:
        if d.year == target_year:
            month_counts[(d.year, d.month)] += 1

    # 输出结果
    print("=" * 60)
    print(f"🤖 AI 对话年度统计报告（{target_year}）")
    print("=" * 60)
    print(f"📁 总对话会话数（Conversations）: {total_conversations}")
    print(f"💬 总消息条数（Messages）: {len(messages_2025)}")
    print(f"  - 用户提问: {len(user_2025)} 条 ({user_words_2025} 字)")
    print(f"  - AI 回答: {len(assistant_2025)} 条 ({assistant_words_2025} 字)")
    print()
    print(f"📈 月度活跃度（{target_year}）:")
    for (year, month), count in sorted(month_counts.items()):
        month_name = datetime(year, month, 1).strftime("%B")
        print(f"  - {month_name} {year}: {count} 条消息")
    print()
    print("🧠 最常使用的模型:")
    for model, count in sorted(model_usage.items(), key=lambda x: -x[1]):
        print(f"  - {model}: {count} 次")
    print()
    if messages_2025:
        avg_per_conv = len(messages_2025) / total_conversations
        print(f"📊 平均每场对话消息数: {avg_per_conv:.1f}")
    print("=" * 60)

    # 可选：导出为 CSV 或 Markdown
    with open("ai_chat_summary_2025.md", "w", encoding="utf-8") as f:
        f.write(f"# AI 对话年度总结（{target_year}）\n\n")
        f.write(f"- 对话会话数: {total_conversations}\n")
        f.write(f"- 总消息数: {len(messages_2025)}\n")
        f.write(f"- 用户消息: {len(user_2025)} 条（{user_words_2025} 字）\n")
        f.write(f"- AI 消息: {len(assistant_2025)} 条（{assistant_words_2025} 字）\n\n")
        f.write("## 月度活跃度\n")
        for (year, month), count in sorted(month_counts.items()):
            month_name = datetime(year, month, 1).strftime("%B")
            f.write(f"- {month_name} {year}: {count} 条\n")
        f.write("\n## 模型使用情况\n")
        for model, count in model_usage.items():
            f.write(f"- {model}: {count} 次\n")

    print("✅ 报告已保存为: ai_chat_summary_2025.md")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="分析 AI 对话 JSON 记录")
    parser.add_argument("file", help="导出的 JSON 文件路径")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print("❌ 文件不存在:", args.file)
    else:
        analyze_chat_history(args.file)