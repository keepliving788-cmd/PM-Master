#!/usr/bin/env python3
"""
飞书机器人后端服务
接收飞书消息，查询离线知识库，返回答案
"""
from flask import Flask, request, jsonify
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.config import Config
from retriever.simple_search import SimpleSearchEngine

app = Flask(__name__)

# 初始化检索引擎
config = Config.load()
search_engine = SimpleSearchEngine(config)

print("✅ 飞书机器人后端启动")
print(f"   检索引擎已加载")


@app.route('/webhook', methods=['POST'])
def webhook():
    """接收飞书消息webhook"""
    data = request.json

    # URL验证（飞书首次配置时）
    if data.get('type') == 'url_verification':
        return jsonify({'challenge': data['challenge']})

    # 处理消息事件
    if data.get('header', {}).get('event_type') == 'im.message.receive_v1':
        return handle_message(data)

    return jsonify({'msg': 'ok'})


def handle_message(data):
    """处理收到的消息"""
    try:
        event = data['event']
        message = json.loads(event['message']['content'])
        text = message.get('text', '').strip()

        # 提取查询内容（去掉@机器人）
        query = text.split(' ', 1)[-1] if ' ' in text else text

        if not query:
            return jsonify({'msg': 'empty query'})

        print(f"\n收到查询: {query}")

        # 查询离线知识库
        results = search_engine.search(
            query=query,
            top_k=5,
            mode='hybrid'
        )

        # 图片增强（v1.2.0新增）
        results = search_engine.enrich_with_images(results, enable_images=True)

        # 构建回复
        reply = format_reply(query, results)

        # 发送回复到飞书
        send_reply(event['sender']['sender_id']['open_id'],
                   event['message']['message_id'],
                   reply)

        return jsonify({'msg': 'success'})

    except Exception as e:
        print(f"❌ 处理消息失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'msg': 'error', 'error': str(e)})


def format_reply(query, results):
    """格式化回复内容"""
    if not results:
        return f"未找到关于「{query}」的相关内容"

    # 构建回复
    lines = [f"📚 关于「{query}」的搜索结果：\n"]

    for i, result in enumerate(results[:3], 1):
        score = result.get('score', 0)
        content = result['content'][:200]  # 限制长度
        has_images = result.get('has_images', False)
        image_count = result.get('image_count', 0)

        lines.append(f"{i}. 【相关度: {score:.2f}】")
        lines.append(f"{content}...")

        # 显示图片信息（v1.2.0新增）
        if has_images:
            lines.append(f"🖼️ 包含 {image_count} 张图片")

        lines.append("")

    if len(results) > 3:
        lines.append(f"还有 {len(results)-3} 条相关结果")

    return '\n'.join(lines)


def send_reply(user_id, message_id, text):
    """发送回复到飞书"""
    import os
    import lark_oapi as lark
    from lark_oapi.api.im.v1 import ReplyMessageRequest, ReplyMessageRequestBody

    # 读取凭证
    env_path = Path(__file__).parent / '.env'
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

    client = lark.Client.builder() \
        .app_id(os.environ['FEISHU_APP_ID']) \
        .app_secret(os.environ['FEISHU_APP_SECRET']) \
        .build()

    # 构建消息
    content = json.dumps({"text": text}, ensure_ascii=False)

    request = ReplyMessageRequest.builder() \
        .message_id(message_id) \
        .request_body(ReplyMessageRequestBody.builder()
                      .content(content)
                      .msg_type("text")
                      .build()) \
        .build()

    response = client.im.v1.message.reply(request)

    if response.success():
        print(f"✅ 回复成功")
    else:
        print(f"❌ 回复失败: {response.msg}")


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'search_engine': 'ready'
    })


@app.route('/test', methods=['POST'])
def test():
    """测试接口"""
    query = request.json.get('query', '')

    if not query:
        return jsonify({'error': 'query required'})

    results = search_engine.search(
        query=query,
        top_k=5,
        mode='hybrid'
    )

    return jsonify({
        'query': query,
        'results': results
    })


if __name__ == '__main__':
    # 开发模式
    app.run(host='0.0.0.0', port=8080, debug=True)
