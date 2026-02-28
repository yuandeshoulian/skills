#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Official Account API - Direct HTTP calls
No MCP server required

Usage:
    python wechat.py upload_image <image_path> --app-id <appid> --app-secret <secret> [--proxy <proxy_url>]
    python wechat.py create_draft <title> <content> <thumb_media_id> --app-id <appid> --app-secret <secret> [--proxy <proxy_url>]
    python wechat.py publish <media_id> --app-id <appid> --app-secret <secret> [--proxy <proxy_url>]
    python wechat.py get_status <publish_id> --app-id <appid> --app-secret <secret> [--proxy <proxy_url>]

Environment:
    WECHAT_APP_ID - WeChat AppID
    WECHAT_APP_SECRET - WeChat AppSecret
    WECHAT_PROXY_URL - Optional proxy URL for requests (e.g., https://proxy.example.com:8080)
"""

import os
import sys
import time
import json
import argparse
import requests

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "https://api.weixin.qq.com/cgi-bin"


class WeChatClient:
    """WeChat Official Account API Client"""

    def __init__(self, app_id, app_secret, proxy_url=None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expires_at = 0

        # Setup proxy if provided
        if proxy_url:
            self.session = requests.Session()
            # 如果代理 URL 包含 /wechat/ 路径，使用 BASE_URL 替换
            # 否则使用标准代理
            if '/wechat/' in proxy_url:
                # 使用代理服务器的 BASE URL
                # 格式: http://wxpublish.jasion.top/wechat/ -> http://wxpublish.jasion.top
                proxy_base = proxy_url.split('/wechat/')[0]
                self.proxy_base_url = proxy_url.rstrip('/')  # 保留完整代理 URL
                self.session.proxies = {
                    'http': proxy_base,
                    'https': proxy_base
                }
            else:
                self.session.proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                self.proxy_base_url = None
        else:
            self.session = requests
            self.proxy_base_url = None

    def get_access_token(self):
        """Get access_token (auto-refresh if expired)"""
        # Check if token is still valid
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        # Fetch new token
        # 如果使用带路径的代理，替换 BASE_URL
        base = self.proxy_base_url if hasattr(self, 'proxy_base_url') and self.proxy_base_url else BASE_URL
        url = f"{base}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }

        response = self.session.get(url, params=params)
        data = response.json()

        if "access_token" not in data:
            raise Exception(f"Failed to get access_token: {data}")

        self.access_token = data["access_token"]
        # Set expiry to 5 minutes early (7200 - 300 = 6900 seconds)
        self.token_expires_at = time.time() + 6900

        return self.access_token

    def upload_image(self, image_path):
        """Upload image to WeChat material library

        Args:
            image_path: Local image file path or HTTP URL or base64 data URL

        Returns:
            dict: Response with media_id and url
        """
        token = self.get_access_token()
        base = self.proxy_base_url if hasattr(self, 'proxy_base_url') and self.proxy_base_url else BASE_URL
        url = f"{base}/material/add_material?access_token={token}&type=image"

        # Check if image_path is a URL or base64
        if image_path.startswith('http://') or image_path.startswith('https://'):
            # Download image from URL
            img_response = self.session.get(image_path)
            img_data = img_response.content
            filename = image_path.split('/')[-1].split('?')[0] or 'image.jpg'
        elif image_path.startswith('data:image'):
            # Base64 data URL
            import base64
            from io import BytesIO

            header, data = image_path.split(',', 1)
            img_data = base64.b64decode(data)
            filename = 'image.png' if 'png' in header else 'image.jpg'
        else:
            # Local file path
            with open(image_path, 'rb') as f:
                img_data = f.read()
            filename = os.path.basename(image_path)

        # Upload as multipart/form-data
        files = {
            'media': (filename, img_data)
        }

        response = self.session.post(url, files=files)
        result = response.json()

        if "media_id" not in result:
            raise Exception(f"Upload failed: {result}")

        return result

    def create_draft(self, title, content, thumb_media_id, author="", digest="",
                     content_source_url="", need_open_comment=0, only_fans_can_comment=0):
        """Create WeChat article draft

        Args:
            title: Article title
            content: Article content (HTML format)
            thumb_media_id: Cover image media ID
            author: Author name (optional)
            digest: Article summary (optional)
            content_source_url: Original article URL (optional)
            need_open_comment: Open comments (0/1)
            only_fans_can_comment: Fans only comments (0/1)

        Returns:
            dict: Response with media_id
        """
        token = self.get_access_token()
        base = self.proxy_base_url if hasattr(self, 'proxy_base_url') and self.proxy_base_url else BASE_URL
        url = f"{base}/draft/add?access_token={token}"

        payload = {
            "articles": [{
                "title": title,
                "author": author,
                "content": content,
                "digest": digest,
                "thumb_media_id": thumb_media_id,
                "content_source_url": content_source_url,
                "need_open_comment": need_open_comment,
                "only_fans_can_comment": only_fans_can_comment
            }]
        }

        # 手动序列化 JSON，确保中文不被转义
        import json
        response = self.session.post(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
            headers={'Content-Type': 'application/json; charset=utf-8'}
        )
        result = response.json()

        if "media_id" not in result:
            raise Exception(f"Create draft failed: {result}")

        return result

    def publish(self, media_id):
        """Publish article

        Args:
            media_id: Draft media ID

        Returns:
            dict: Response with publish_id
        """
        token = self.get_access_token()
        base = self.proxy_base_url if hasattr(self, 'proxy_base_url') and self.proxy_base_url else BASE_URL
        url = f"{base}/freepublish/submit?access_token={token}"

        payload = {
            "media_id": media_id
        }

        response = self.session.post(url, json=payload)
        result = response.json()

        if "publish_id" not in result:
            raise Exception(f"Publish failed: {result}")

        return result

    def get_publish_status(self, publish_id):
        """Get publish status

        Args:
            publish_id: Publish task ID

        Returns:
            dict: Status information
        """
        token = self.get_access_token()
        base = self.proxy_base_url if hasattr(self, 'proxy_base_url') and self.proxy_base_url else BASE_URL
        url = f"{base}/freepublish/get?access_token={token}"

        payload = {
            "publish_id": publish_id
        }

        response = self.session.post(url, json=payload)
        result = response.json()

        status_map = {
            0: "发布成功",
            1: "发布中",
            2: "原创失败",
            3: "常规失败",
            4: "平台审核不通过",
            5: "成功后用户删除"
        }

        if "publish_id" in result:
            result["status_text"] = status_map.get(result.get("publish_status"), "未知状态")

        return result

    def delete_draft(self, media_id):
        """Delete draft

        Args:
            media_id: Draft media ID

        Returns:
            dict: Response
        """
        token = self.get_access_token()
        base = self.proxy_base_url if hasattr(self, 'proxy_base_url') and self.proxy_base_url else BASE_URL
        url = f"{base}/draft/delete?access_token={token}"

        payload = {
            "media_id": media_id
        }

        response = self.session.post(url, json=payload)
        result = response.json()

        if result.get("errcode") != 0:
            raise Exception(f"Delete draft failed: {result}")

        return result


def main():
    parser = argparse.ArgumentParser(
        description='微信公众号 API 直接调用',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 上传图片
  %(prog)s upload_image image.jpg --app-id wx123 --app-secret secret123

  # 创建草稿
  %(prog)s create_draft "标题" "<html>...</html>" "media_id" --app-id wx123 --app-secret secret123

  # 发布文章
  %(prog)s publish "media_id" --app-id wx123 --app-secret secret123

  # 查询发布状态
  %(prog)s get_status "publish_id" --app-id wx123 --app-secret secret123

  # 使用代理（适用于没有固定IP的情况）
  %(prog)s upload_image image.jpg --app-id wx123 --app-secret secret123 --proxy https://proxy.example.com:8080

  或设置环境变量后省略参数:
  $env:WECHAT_APP_ID="wx123"
  $env:WECHAT_APP_SECRET="secret123"
  $env:WECHAT_PROXY_URL="https://proxy.example.com:8080"
  %(prog)s upload_image image.jpg
        '''
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # Common arguments
    def add_common_args(p):
        p.add_argument('--app-id', help='微信公众号 AppID')
        p.add_argument('--app-secret', help='微信公众号 AppSecret')
        p.add_argument('--proxy', help='代理服务器 URL（如 https://proxy.example.com:8080 或 http://your-domain.com/wechat/）')

    # upload_image command
    upload_parser = subparsers.add_parser('upload_image', help='上传图片到素材库')
    add_common_args(upload_parser)
    upload_parser.add_argument('image_path', help='图片路径（本地文件或HTTP URL或base64）')

    # create_draft command
    draft_parser = subparsers.add_parser('create_draft', help='创建草稿')
    add_common_args(draft_parser)
    draft_parser.add_argument('title', help='文章标题')
    draft_parser.add_argument('content', help='文章内容（HTML格式）或使用 --content-file 指定文件')
    draft_parser.add_argument('thumb_media_id', help='封面图片MediaID')
    draft_parser.add_argument('--content-file', help='从文件读取文章内容（UTF-8编码），避免命令行编码问题')
    draft_parser.add_argument('--author', default='', help='作者名称')
    draft_parser.add_argument('--digest', default='', help='文章摘要')
    draft_parser.add_argument('--content-source-url', default='', help='原文链接')
    draft_parser.add_argument('--open-comment', type=int, choices=[0, 1], default=0, help='是否打开评论')
    draft_parser.add_argument('--fans-only', type=int, choices=[0, 1], default=0, help='是否仅粉丝可评论')

    # publish command
    publish_parser = subparsers.add_parser('publish', help='发布文章')
    add_common_args(publish_parser)
    publish_parser.add_argument('media_id', help='草稿MediaID')

    # get_status command
    status_parser = subparsers.add_parser('get_status', help='查询发布状态')
    add_common_args(status_parser)
    status_parser.add_argument('publish_id', help='发布任务ID')

    # delete_draft command
    delete_parser = subparsers.add_parser('delete_draft', help='删除草稿')
    add_common_args(delete_parser)
    delete_parser.add_argument('media_id', help='草稿MediaID')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Get credentials from args or environment
    app_id = args.app_id or os.environ.get('WECHAT_APP_ID', '')
    app_secret = args.app_secret or os.environ.get('WECHAT_APP_SECRET', '')
    proxy_url = getattr(args, 'proxy', None) or os.environ.get('WECHAT_PROXY_URL', '')

    if not app_id or not app_secret:
        print('Error: Missing WECHAT_APP_ID or WECHAT_APP_SECRET', file=sys.stderr)
        print('Use --app-id and --app-secret, or set environment variables', file=sys.stderr)
        sys.exit(1)

    # Create client
    client = WeChatClient(app_id, app_secret, proxy_url=proxy_url if proxy_url else None)

    # Print proxy info if using proxy
    if proxy_url:
        print(f'使用代理: {proxy_url}', file=sys.stderr)

    try:
        if args.command == 'upload_image':
            result = client.upload_image(args.image_path)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == 'create_draft':
            # 优先从文件读取内容，避免命令行编码问题
            content = args.content
            if hasattr(args, 'content_file') and args.content_file:
                with open(args.content_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            result = client.create_draft(
                title=args.title,
                content=content,
                thumb_media_id=args.thumb_media_id,
                author=args.author,
                digest=args.digest,
                content_source_url=args.content_source_url,
                need_open_comment=args.open_comment,
                only_fans_can_comment=args.fans_only
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == 'publish':
            result = client.publish(args.media_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == 'get_status':
            result = client.get_publish_status(args.publish_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == 'delete_draft':
            result = client.delete_draft(args.media_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
