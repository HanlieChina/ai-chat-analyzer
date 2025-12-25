import json
import os
from collections import defaultdict
from datetime import datetime
import argparse

def get_message_content(msg):
    """安全提取消息文本内容，兼容 user 和 assistant 消息"""
    role = msg.get("role", "")
    if role == "assistant":
        # 优先从 content_list 提取（Qwen 结构）
        content_list = msg.get("content_list")
        if isinstance(content_list, list) and content_list:
            texts = []
            for item in content_list:
                text = item.get("content")
                if isinstance(text, str):
                    texts.append(text)
            return "".join(texts)
    # 所有角色 fallback 到 content 字段
    content = msg.get("content")
    return content if isinstance(content, str) else ""

def count_words(msg_list):
    """计算消息列表总字数（字符数）"""
    return sum(len(get_message_content(msg)) for msg in msg_list)

def analyze_chat_history(json_path):
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

        # 安全排序：处理 timestamp 为 None 或缺失
        messages.sort(key=lambda x: x.get("timestamp") or 0)
        
        # 过滤掉无有效 timestamp 的消息（避免后续崩溃）
        valid_messages = [m for m in messages if m.get("timestamp") is not None]
        all_messages.extend(valid_messages)

        # 统计模型（从 assistant 消息中）
        for msg in valid_messages:
            if msg.get("role") == "assistant":
                model = msg.get("model") or msg.get("modelName") or "unknown"
                model_usage[model] += 1

    # 分离用户和 AI 消息
    user_messages = [m for m in all_messages if m.get("role") == "user"]
    assistant_messages = [m for m in all_messages if m.get("role") == "assistant"]

    total_messages = len(all_messages)
    if total_messages == 0:
        print("⚠️ 没有找到任何有效消息。")
        return

    # ===== 年度分析（默认 2025）=====
    target_year = 2025

    # 安全筛选 2025 年消息
    messages_2025 = [
        msg for msg in all_messages
        if msg.get("timestamp") is not None and
        datetime.fromtimestamp(msg["timestamp"]).year == target_year
    ]
    user_2025 = [m for m in messages_2025 if m.get("role") == "user"]
    assistant_2025 = [m for m in messages_2025 if m.get("role") == "assistant"]

    # 字数统计
    user_words_2025 = count_words(user_2025)
    assistant_words_2025 = count_words(assistant_2025)

    # 月度活跃度
    month_counts = defaultdict(int)
    for msg in messages_2025:
        dt = datetime.fromtimestamp(msg["timestamp"])
        month_counts[(dt.year, dt.month)] += 1

    # ===== 输出结果 =====
    print("=" * 60)
    print(f"🤖 AI 对话年度统计报告（{target_year}）")
    print("=" * 60)
    print(f"📁 总对话会话数（Conversations）: {total_conversations}")
    print(f"💬 {target_year} 年总消息条数: {len(messages_2025)}")
    print(f"  - 用户提问: {len(user_2025)} 条 ({user_words_2025:,} 字)")
    print(f"  - AI 回答: {len(assistant_2025)} 条 ({assistant_words_2025:,} 字)")
    print()
    
    if month_counts:
        print(f"📈 月度活跃度（{target_year}）:")
        for (year, month), count in sorted(month_counts.items()):
            month_name = datetime(year, month, 1).strftime("%B")
            print(f"  - {month_name} {year}: {count} 条消息")
    else:
        print(f"📅 {target_year} 年无对话记录。")
    print()
    
    if model_usage:
        print("🧠 最常使用的模型:")
        for model, count in sorted(model_usage.items(), key=lambda x: -x[1]):
            print(f"  - {model}: {count} 次")
    print()

    if messages_2025 and total_conversations > 0:
        avg_per_conv = len(messages_2025) / total_conversations
        print(f"📊 平均每场对话消息数: {avg_per_conv:.1f}")
    print("=" * 60)

    # ===== 生成 Markdown 报告 =====
    report_md = f"""# AI 对话年度总结（{target_year}）

- **对话会话数**: {total_conversations}
- **总消息数**: {len(messages_2025)}
- **用户消息**: {len(user_2025)} 条（{user_words_2025:,} 字）
- **AI 消息**: {len(assistant_2025)} 条（{assistant_words_2025:,} 字）

## 月度活跃度
"""
    if month_counts:
        for (year, month), count in sorted(month_counts.items()):
            month_name = datetime(year, month, 1).strftime("%B")
            report_md += f"- {month_name} {year}: {count} 条\n"
    else:
        report_md += "无记录。\n"

    report_md += "\n## 模型使用情况\n"
    for model, count in model_usage.items():
        report_md += f"- {model}: {count} 次\n"

    output_file = "ai_chat_summary_2025.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"✅ 报告已保存为: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="分析 AI 对话 JSON 记录（支持 Qwen 导出格式）")
    parser.add_argument("file", help="导出的 JSON 文件路径")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"❌ 文件不存在: {args.file}")
        exit(1)

    try:
        analyze_chat_history(args.file)
    except Exception as e:
        print(f"💥 分析失败: {e}")
        raise