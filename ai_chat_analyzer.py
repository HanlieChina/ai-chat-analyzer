import json
import os
from collections import defaultdict
from datetime import datetime
import argparse

def get_message_content(msg):
    """安全提取消息文本内容，兼容 user 和 assistant 消息"""
    role = msg.get("role", "")
    if role == "assistant":
        content_list = msg.get("content_list")
        if isinstance(content_list, list) and content_list:
            texts = []
            for item in content_list:
                text = item.get("content")
                if isinstance(text, str):
                    texts.append(text)
            return "".join(texts)
    content = msg.get("content")
    return content if isinstance(content, str) else ""

def count_words(msg_list):
    return sum(len(get_message_content(msg)) for msg in msg_list)

def analyze_chat_history(json_path, target_year=None):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not data.get("success") or "data" not in data:
        raise ValueError("❌ JSON 格式不符合预期：缺少 data 字段或 success != true")

    all_messages = []
    total_conversations = len(data["data"])
    model_usage = defaultdict(int)

    for conv in data["data"]:
        chat = conv.get("chat", {})
        messages_dict = chat.get("history", {}).get("messages", {})
        messages = list(messages_dict.values())
        messages.sort(key=lambda x: x.get("timestamp") or 0)
        valid_messages = [m for m in messages if m.get("timestamp") is not None]
        all_messages.extend(valid_messages)

        for msg in valid_messages:
            if msg.get("role") == "assistant":
                model = msg.get("model") or msg.get("modelName") or "unknown"
                model_usage[model] += 1

    if not all_messages:
        print("⚠️ 没有找到任何有效消息。")
        return

    # ===== 筛选目标时间范围 =====
    if target_year is not None:
        messages_filtered = [
            msg for msg in all_messages
            if datetime.fromtimestamp(msg["timestamp"]).year == target_year
        ]
        title_year = str(target_year)
        output_file = f"ai_chat_summary_{target_year}.md"
    else:
        messages_filtered = all_messages
        title_year = "全部时间"
        output_file = "ai_chat_summary_all.md"

    user_filtered = [m for m in messages_filtered if m.get("role") == "user"]
    assistant_filtered = [m for m in messages_filtered if m.get("role") == "assistant"]

    # 字数统计
    user_words = count_words(user_filtered)
    assistant_words = count_words(assistant_filtered)

    # 月度统计（仅当年或全部）
    month_counts = defaultdict(int)
    for msg in messages_filtered:
        dt = datetime.fromtimestamp(msg["timestamp"])
        key = (dt.year, dt.month) if target_year is None else dt.month  # 全部时间显示年月，单年只显示月
        month_counts[key] += 1

    # ===== 输出报告 =====
    print("=" * 60)
    print(f"🤖 AI 对话统计报告（{title_year}）")
    print("=" * 60)
    print(f"📁 总对话会话数: {total_conversations}")
    print(f"💬 总消息条数: {len(messages_filtered)}")
    print(f"  - 用户提问: {len(user_filtered)} 条 ({user_words:,} 字)")
    print(f"  - AI 回答: {len(assistant_filtered)} 条 ({assistant_words:,} 字)")
    print()

    if month_counts:
        print("📈 月度活跃度:")
        if target_year is not None:
            for month in sorted(month_counts.keys()):
                month_name = datetime(target_year, month, 1).strftime("%B")
                print(f"  - {month_name} {target_year}: {month_counts[month]} 条消息")
        else:
            for (year, month) in sorted(month_counts.keys()):
                month_name = datetime(year, month, 1).strftime("%B")
                print(f"  - {month_name} {year}: {month_counts[(year, month)]} 条消息")
    else:
        print("📅 无消息记录。")
    print()

    if model_usage:
        print("🧠 最常使用的模型:")
        for model, count in sorted(model_usage.items(), key=lambda x: -x[1]):
            print(f"  - {model}: {count} 次")
    print()

    if messages_filtered and total_conversations > 0:
        avg_per_conv = len(messages_filtered) / total_conversations
        print(f"📊 平均每场对话消息数: {avg_per_conv:.1f}")
    print("=" * 60)

    # ===== 生成 Markdown =====
    report_md = f"""# AI 对话统计报告（{title_year}）

- **对话会话数**: {total_conversations}
- **总消息数**: {len(messages_filtered)}
- **用户消息**: {len(user_filtered)} 条（{user_words:,} 字）
- **AI 消息**: {len(assistant_filtered)} 条（{assistant_words:,} 字）

## 月度活跃度
"""
    if month_counts:
        if target_year is not None:
            for month in sorted(month_counts.keys()):
                month_name = datetime(target_year, month, 1).strftime("%B")
                report_md += f"- {month_name} {target_year}: {month_counts[month]} 条\n"
        else:
            for (year, month) in sorted(month_counts.keys()):
                month_name = datetime(year, month, 1).strftime("%B")
                report_md += f"- {month_name} {year}: {month_counts[(year, month)]} 条\n"
    else:
        report_md += "无记录。\n"

    report_md += "\n## 模型使用情况\n"
    for model, count in model_usage.items():
        report_md += f"- {model}: {count} 次\n"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"✅ 报告已保存为: {output_file}")

if __name__ == "__main__":
    script_name = os.path.basename(__file__)
    parser = argparse.ArgumentParser(
        description="分析 AI 对话 JSON 记录（支持 Qwen 导出格式）",
        usage=f"python {script_name} <json_file> [year]"
    )
    parser.add_argument("file", help="导出的 JSON 文件路径")
    parser.add_argument(
        "year",
        nargs="?",  # 可选
        type=int,
        help="可选：指定年份（如 2025），不填则分析全部时间"
    )
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"❌ 文件不存在: {args.file}")
        exit(1)

    try:
        analyze_chat_history(args.file, target_year=args.year)
    except Exception as e:
        print(f"💥 分析失败: {e}")
        raise