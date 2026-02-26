#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动上传文章到微信公众号草稿箱

用法:
    python auto_upload.py <html_file> <title> <cover_image> [options]

示例:
    python auto_upload.py article.html "文章标题" cover.jpg
    python auto_upload.py article.html "文章标题" cover.jpg --author "张三" --digest "摘要"
"""

import os
import sys
import json
import argparse
from wechat import WeChatClient


def auto_upload(html_file, title, cover_image, author="", digest="", content_source_url="",
                 open_comment=0, fans_only=0):
    """
    自动上传文章到微信公众号草稿箱

    Args:
        html_file: HTML 文件路径
        title: 文章标题
        cover_image: 封面图片路径
        author: 作者名称
        digest: 文章摘要
        content_source_url: 原文链接
        open_comment: 是否打开评论 (0/1)
        fans_only: 是否仅粉丝可评论 (0/1)

    Returns:
        dict: 包含 media_id 和上传结果
    """
    # 从环境变量获取配置
    app_id = os.environ.get('WECHAT_APP_ID', '')
    app_secret = os.environ.get('WECHAT_APP_SECRET', '')
    proxy_url = os.environ.get('WECHAT_PROXY_URL', '')

    if not app_id or not app_secret:
        raise Exception("缺少 WECHAT_APP_ID 或 WECHAT_APP_SECRET 环境变量")

    print(f"📝 正在上传文章: {title}")
    print(f"🔧 使用代理: {proxy_url if proxy_url else '无'}")
    print()

    # 创建客户端
    client = WeChatClient(app_id, app_secret, proxy_url=proxy_url if proxy_url else None)

    # 1. 上传封面图
    print("📸 步骤 1/2: 上传封面图...")
    upload_result = client.upload_image(cover_image)
    media_id = upload_result.get('media_id')

    if not media_id:
        raise Exception(f"上传封面图失败: {upload_result}")

    print(f"✅ 封面图上传成功!")
    print(f"   Media ID: {media_id}")
    print(f"   URL: {upload_result.get('url', '')}")
    print()

    # 2. 读取 HTML 内容
    print("📄 步骤 2/2: 读取文章内容...")
    if not os.path.exists(html_file):
        raise Exception(f"HTML 文件不存在: {html_file}")

    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print(f"✅ 已读取 {len(html_content)} 个字符")
    print()

    # 3. 创建草稿
    print("📤 步骤 3/3: 创建草稿...")
    draft_result = client.create_draft(
        title=title,
        content=html_content,
        thumb_media_id=media_id,
        author=author,
        digest=digest,
        content_source_url=content_source_url,
        need_open_comment=open_comment,
        only_fans_can_comment=fans_only
    )

    if 'media_id' not in draft_result:
        raise Exception(f"创建草稿失败: {draft_result}")

    print(f"✅ 草稿创建成功!")
    print(f"   Media ID: {draft_result.get('media_id')}")
    print()

    return {
        'success': True,
        'cover_media_id': media_id,
        'draft_media_id': draft_result.get('media_id'),
        'upload_result': upload_result,
        'draft_result': draft_result
    }


def main():
    parser = argparse.ArgumentParser(
        description='自动上传文章到微信公众号草稿箱',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 基础用法
  %(prog)s article.html "文章标题" cover.jpg

  # 完整参数
  %(prog)s article.html "文章标题" cover.jpg \\
    --author "张三" \\
    --digest "这是一篇关于..." \\
    --content-source-url "https://..." \\
    --open-comment 1

  # 使用环境变量配置 AppID/AppSecret
  export WECHAT_APP_ID="wx123"
  export WECHAT_APP_SECRET="secret123"
  export WECHAT_PROXY_URL="http://proxy.com/wechat/"
  %(prog)s article.html "标题" cover.jpg
        '''
    )

    parser.add_argument('html_file', help='HTML 文件路径')
    parser.add_argument('title', help='文章标题')
    parser.add_argument('cover_image', help='封面图片路径')
    parser.add_argument('--author', default='', help='作者名称')
    parser.add_argument('--digest', default='', help='文章摘要')
    parser.add_argument('--content-source-url', default='', help='原文链接')
    parser.add_argument('--open-comment', type=int, choices=[0, 1], default=0,
                        help='是否打开评论 (默认: 0)')
    parser.add_argument('--fans-only', type=int, choices=[0, 1], default=0,
                        help='是否仅粉丝可评论 (默认: 0)')

    args = parser.parse_args()

    try:
        result = auto_upload(
            html_file=args.html_file,
            title=args.title,
            cover_image=args.cover_image,
            author=args.author,
            digest=args.digest,
            content_source_url=args.content_source_url,
            open_comment=args.open_comment,
            fans_only=args.fans_only
        )

        print("=" * 50)
        print("🎉 上传完成!")
        print("=" * 50)
        print(f"\n封面图 Media ID: {result['cover_media_id']}")
        print(f"草稿 Media ID: {result['draft_media_id']}")
        print(f"\n你可以在微信公众号后台的草稿箱中查看这篇文章。")

    except Exception as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
