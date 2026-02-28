#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct ModelScope API Image Generation
No MCP server required, direct HTTP requests

Usage:
    python generate_image.py "a cute cat playing in sunlight"
    python generate_image.py "prompt" --size 1024x1024 --steps 30
    python generate_image.py "prompt" --api-key YOUR_KEY

Environment:
    MODELSCOPE_API_KEY - ModelScope API Token (optional, can use --api-key instead)
"""

import os
import sys
import time
import argparse
import requests

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = 'https://api-inference.modelscope.cn/'
DEFAULT_MODEL = 'Tongyi-MAI/Z-Image-Turbo'


def generate_image(api_key, prompt, model=DEFAULT_MODEL, negative_prompt=None, size='1024x1024',
                   seed=None, steps=None, guidance=None, image_url=None):
    """
    生成图片的异步函数（内部处理轮询）

    Args:
        api_key: ModelScope API Key
        prompt: 正向提示词（必需）
        model: 模型名称
        negative_prompt: 负向提示词
        size: 图片尺寸（如 '1024x1024'）
        seed: 随机种子
        steps: 采样步数
        guidance: 引导系数
        image_url: 待编辑图片URL

    Returns:
        str: 图片 URL

    Raises:
        ValueError: API Key 未设置
        Exception: 图片生成失败
    """
    if not api_key:
        raise ValueError('API Key is required. Use --api-key or set MODELSCOPE_API_KEY environment variable')

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    # 构建请求参数
    params = {
        'model': model,
        'prompt': prompt,
    }

    if negative_prompt:
        params['negative_prompt'] = negative_prompt
    if size:
        params['size'] = size
    if seed is not None:
        params['seed'] = seed
    if steps is not None:
        params['steps'] = steps
    if guidance is not None:
        params['guidance'] = guidance
    if image_url:
        params['image_url'] = image_url

    # 提交图片生成任务
    submit_headers = {**headers, 'X-ModelScope-Async-Mode': 'true'}
    response = requests.post(
        f'{BASE_URL}v1/images/generations',
        json=params,
        headers=submit_headers
    )

    if response.status_code != 200:
        raise Exception(f'Failed to submit task: {response.status_code} - {response.text}')

    task_id = response.json().get('task_id')
    if not task_id:
        raise Exception('No task_id in response')

    # 轮询任务状态，直到完成
    poll_count = 0
    max_polls = 60  # 最多轮询 60 次（3分钟）
    while poll_count < max_polls:
        poll_count += 1
        time.sleep(3)  # 等待 3 秒

        status_headers = {**headers, 'X-ModelScope-Task-Type': 'image_generation'}
        status_response = requests.get(
            f'{BASE_URL}v1/tasks/{task_id}',
            headers=status_headers
        )

        if status_response.status_code != 200:
            raise Exception(f'Failed to get task status: {status_response.status_code}')

        status_data = status_response.json()
        task_status = status_data.get('task_status')

        # 显示进度
        print('.', end='', file=sys.stderr, flush=True)

        if task_status == 'SUCCEED':
            print('', file=sys.stderr)  # 换行
            output_images = status_data.get('output_images', [])
            if output_images and len(output_images) > 0:
                return output_images[0]
            else:
                raise Exception('Image generation succeeded but no output images found')
        elif task_status == 'FAILED':
            print('', file=sys.stderr)  # 换行
            error_msg = status_data.get('error_message', 'Unknown error')
            raise Exception(f'Image generation failed: {error_msg}')
        # 继续轮询（PENDING 或 RUNNING 状态）

    raise Exception('Image generation timed out after 3 minutes')


def main():
    parser = argparse.ArgumentParser(
        description='使用魔搭社区 API 生成图片',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s "a cute cat" --api-key YOUR_KEY
  %(prog)s "a cute cat" --api-key YOUR_KEY --size 1024x1024 --steps 30
  %(prog)s "A landscape" --api-key YOUR_KEY --negative "blurry" --guidance 7.5

  或设置环境变量后省略 --api-key:
  $env:MODELSCOPE_API_KEY="YOUR_KEY"
  %(prog)s "a cute cat"
        '''
    )

    parser.add_argument('prompt', help='正向提示词（必需）')
    parser.add_argument('--api-key', help='ModelScope API Key（可省略，使用环境变量 MODELSCOPE_API_KEY）')
    parser.add_argument('--model', default=DEFAULT_MODEL,
                        help=f'模型名称（默认: {DEFAULT_MODEL}）')
    parser.add_argument('--negative', help='负向提示词')
    parser.add_argument('--size', default='1024x1024', help='图片尺寸（默认: 1024x1024）')
    parser.add_argument('--seed', type=int, help='随机种子')
    parser.add_argument('--steps', type=int, help='采样步数（1-100）')
    parser.add_argument('--guidance', type=float, help='引导系数（1.5-20）')

    args = parser.parse_args()

    # 获取 API Key：优先使用命令行参数，其次环境变量
    api_key = args.api_key or os.environ.get('MODELSCOPE_API_KEY', '')

    if not args.prompt:
        parser.print_help()
        sys.exit(1)

    try:
        print(f'Generating image using {args.model}...', file=sys.stderr)
        image_url = generate_image(
            api_key=api_key,
            prompt=args.prompt,
            model=args.model,
            negative_prompt=args.negative,
            size=args.size,
            seed=args.seed,
            steps=args.steps,
            guidance=args.guidance
        )
        print(image_url)
    except Exception as e:
        print(f'\nError: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
