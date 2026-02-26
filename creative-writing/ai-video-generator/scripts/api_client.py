"""
AI 视频生成器 - API 客户端
支持火山引擎和阿里云的 API 调用
"""

import os
import yaml
import requests
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get(self, key: str, default=None):
        """获取配置项（支持嵌套键，如 'image_to_video.model'）"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def get_api_key(self, provider: str) -> str:
        """获取 API Key（支持环境变量）"""
        api_key = self.get(f"api_keys.{provider}.api_key")
        if api_key and api_key.startswith("${") and api_key.endswith("}"):
            # 从环境变量读取
            env_var = api_key[2:-1]
            return os.getenv(env_var, "")
        return api_key

    def get_current_video_model(self) -> Dict:
        """获取当前使用的视频生成模型配置"""
        model_name = self.get("image_to_video.model")
        models = self.get("image_to_video.alternative_models", [])

        for model in models:
            if model["name"] == model_name:
                return model

        # 如果没找到，返回默认配置
        return {
            "name": model_name,
            "provider": self.get("image_to_video.provider"),
            "max_duration": self.get("image_to_video.capabilities.max_duration", 12),
            "has_audio": self.get("image_to_video.capabilities.has_audio", True),
        }


class VolcanoEngineClient:
    """火山引擎 API 客户端"""

    def __init__(self, api_key: str, endpoint: str):
        self.api_key = api_key
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )

    def text_to_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 768,
        height: int = 1365,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
    ) -> bytes:
        """
        文生图 API

        Args:
            prompt: 正面提示词
            negative_prompt: 负面提示词
            width: 图片宽度
            height: 图片高度
            num_inference_steps: 推理步数
            guidance_scale: 引导系数

        Returns:
            图片二进制数据
        """
        url = f"{self.endpoint}/text-to-image"
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
        }

        response = self.session.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        # 假设返回格式：{"image": "base64_encoded_image"}
        image_data = base64.b64decode(result["image"])
        return image_data

    def image_to_image_with_reference(
        self,
        prompt: str,
        reference_image_path: str,
        reference_weight: float = 0.75,
        negative_prompt: str = "",
        width: int = 768,
        height: int = 1365,
    ) -> bytes:
        """
        图生图（使用参考图，保持角色一致性）

        Args:
            prompt: 正面提示词
            reference_image_path: 参考图路径
            reference_weight: 参考图权重 0-1
            negative_prompt: 负面提示词
            width: 图片宽度
            height: 图片高度

        Returns:
            图片二进制数据
        """
        url = f"{self.endpoint}/image-to-image"

        # 读取参考图并转为 base64
        with open(reference_image_path, "rb") as f:
            reference_image_b64 = base64.b64encode(f.read()).decode()

        payload = {
            "prompt": prompt,
            "reference_image": reference_image_b64,
            "reference_strength": reference_weight,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
        }

        response = self.session.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        image_data = base64.b64decode(result["image"])
        return image_data

    def image_to_video(
        self,
        image_path: str,
        prompt: str,
        duration: int = 5,
        motion_strength: float = 0.7,
        fps: int = 24,
    ) -> str:
        """
        图生视频（Seaweed 2.0）

        Args:
            image_path: 关键帧图片路径
            prompt: 运动描述提示词
            duration: 视频时长（秒）
            motion_strength: 运动强度 0-1
            fps: 帧率

        Returns:
            任务ID（需要轮询获取结果）
        """
        url = f"{self.endpoint}/image-to-video"

        # 读取图片并转为 base64
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()

        payload = {
            "image": image_b64,
            "prompt": prompt,
            "duration": duration,
            "motion_strength": motion_strength,
            "fps": fps,
            "aspect_ratio": "9:16",  # 竖屏
        }

        response = self.session.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        # 返回任务 ID
        return result["task_id"]

    def get_video_result(self, task_id: str, max_wait: int = 300) -> bytes:
        """
        获取视频生成结果（轮询）

        Args:
            task_id: 任务ID
            max_wait: 最大等待时间（秒）

        Returns:
            视频二进制数据
        """
        url = f"{self.endpoint}/tasks/{task_id}"
        start_time = time.time()

        while time.time() - start_time < max_wait:
            response = self.session.get(url)
            response.raise_for_status()

            result = response.json()
            status = result["status"]

            if status == "completed":
                # 下载视频
                video_url = result["video_url"]
                video_response = requests.get(video_url)
                video_response.raise_for_status()
                return video_response.content

            elif status == "failed":
                raise Exception(f"视频生成失败: {result.get('error', 'Unknown error')}")

            # 等待后重试
            time.sleep(5)

        raise TimeoutError(f"视频生成超时（{max_wait}秒）")


class AliyunClient:
    """阿里云 API 客户端"""

    def __init__(self, api_key: str, endpoint: str):
        self.api_key = api_key
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )

    def text_to_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 768,
        height: int = 1365,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
    ) -> bytes:
        """
        文生图（阿里云通义万相）

        Args:
            prompt: 正面提示词
            negative_prompt: 负面提示词
            width: 图片宽度
            height: 图片高度
            num_inference_steps: 推理步数（阿里云可能不支持，仅保持接口一致）
            guidance_scale: 引导系数（阿里云可能不支持，仅保持接口一致）

        Returns:
            图片二进制数据
        """
        url = f"{self.endpoint}/services/aigc/text2image/image-synthesis"

        payload = {
            "model": "wanx-v1",
            "input": {"prompt": prompt},
            "parameters": {
                "size": f"{width}*{height}",  # 阿里云格式：宽*高
                "n": 1,
            },
        }

        # 如果有负面提示词，添加到参数中（如果API支持）
        if negative_prompt:
            payload["parameters"]["negative_prompt"] = negative_prompt

        response = self.session.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        image_url = result["output"]["results"][0]["url"]

        # 下载图片
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        return image_response.content

    def image_to_image_with_reference(
        self,
        prompt: str,
        reference_image_path: str,
        reference_weight: float = 0.75,
        negative_prompt: str = "",
        width: int = 768,
        height: int = 1365,
    ) -> bytes:
        """
        图生图（使用参考图，保持角色一致性）
        阿里云通义万相的图像编辑API

        Args:
            prompt: 正面提示词
            reference_image_path: 参考图路径
            reference_weight: 参考图权重 0-1
            negative_prompt: 负面提示词
            width: 图片宽度
            height: 图片高度

        Returns:
            图片二进制数据
        """
        url = f"{self.endpoint}/services/aigc/image2image/image-synthesis"

        # 读取参考图并转为 base64
        with open(reference_image_path, "rb") as f:
            reference_image_b64 = base64.b64encode(f.read()).decode()

        payload = {
            "model": "wanx-v1",
            "input": {
                "prompt": prompt,
                "image": reference_image_b64,  # 参考图
            },
            "parameters": {
                "size": f"{width}*{height}",
                "strength": 1.0 - reference_weight,  # 阿里云用 strength 控制（越低越接近原图）
                "n": 1,
            },
        }

        if negative_prompt:
            payload["parameters"]["negative_prompt"] = negative_prompt

        response = self.session.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        image_url = result["output"]["results"][0]["url"]

        # 下载图片
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        return image_response.content

    def image_to_video(
        self,
        image_path: str,
        prompt: str,
        duration: int = 5,
        motion_strength: float = 0.7,
        fps: int = 24,
    ) -> str:
        """
        图生视频（阿里云视频生成）

        Args:
            image_path: 关键帧图片路径
            prompt: 运动描述提示词
            duration: 视频时长（秒）
            motion_strength: 运动强度 0-1
            fps: 帧率

        Returns:
            任务ID（需要轮询获取结果）
        """
        url = f"{self.endpoint}/services/aigc/image2video/video-synthesis"

        # 读取图片并转为 base64
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()

        payload = {
            "model": "videocomposer-v1",  # 阿里云视频生成模型
            "input": {
                "image": image_b64,
                "prompt": prompt,
            },
            "parameters": {
                "duration": duration,
                "fps": fps,
                "motion_strength": motion_strength,
            },
        }

        response = self.session.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        # 返回任务 ID
        return result["output"]["task_id"]

    def get_video_result(self, task_id: str, max_wait: int = 300) -> bytes:
        """
        获取视频生成结果（轮询）

        Args:
            task_id: 任务ID
            max_wait: 最大等待时间（秒）

        Returns:
            视频二进制数据
        """
        url = f"{self.endpoint}/services/aigc/tasks/{task_id}"
        start_time = time.time()

        while time.time() - start_time < max_wait:
            response = self.session.get(url)
            response.raise_for_status()

            result = response.json()
            status = result["output"]["task_status"]

            if status == "SUCCEEDED":
                # 下载视频
                video_url = result["output"]["video_url"]
                video_response = requests.get(video_url)
                video_response.raise_for_status()
                return video_response.content

            elif status == "FAILED":
                error_msg = result["output"].get("message", "Unknown error")
                raise Exception(f"视频生成失败: {error_msg}")

            # 等待后重试
            time.sleep(5)

        raise TimeoutError(f"视频生成超时（{max_wait}秒）")


class APIClient:
    """统一 API 客户端（根据配置自动选择服务商）"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config = ConfigManager(config_path)
        self._clients = {}

    def _get_client(self, service_type: str):
        """获取对应服务的客户端"""
        provider = self.config.get(f"{service_type}.provider")

        if provider not in self._clients:
            api_key = self.config.get_api_key(provider)
            endpoint = self.config.get(f"api_keys.{provider}.endpoint")

            if provider == "volcano":
                self._clients[provider] = VolcanoEngineClient(api_key, endpoint)
            elif provider == "aliyun":
                self._clients[provider] = AliyunClient(api_key, endpoint)
            else:
                raise ValueError(f"不支持的服务商: {provider}")

        return self._clients[provider]

    def generate_character_image(
        self, prompt: str, negative_prompt: str = "", save_path: str = None
    ) -> bytes:
        """
        生成角色形象（文生图）

        Args:
            prompt: 角色描述提示词
            negative_prompt: 负面提示词
            save_path: 保存路径（可选）

        Returns:
            图片二进制数据
        """
        client = self._get_client("text_to_image")

        # 添加全局标签
        quality_tags = self.config.get("prompts.quality_tags", "")
        vertical_tags = self.config.get("prompts.vertical_tags", "")
        full_prompt = f"{quality_tags}, {prompt}, {vertical_tags}"

        # 添加全局负面提示词
        global_negative = self.config.get("prompts.negative_prompt", "")
        full_negative = f"{global_negative}, {negative_prompt}"

        # 生成图片
        image_data = client.text_to_image(
            prompt=full_prompt,
            negative_prompt=full_negative,
            width=self.config.get("text_to_image.default_params.width", 768),
            height=self.config.get("text_to_image.default_params.height", 1365),
        )

        # 保存图片
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(image_data)
            print(f"✅ 图片已保存: {save_path}")

        return image_data

    def generate_keyframe_with_reference(
        self,
        prompt: str,
        reference_image_path: str,
        reference_weight: float = None,
        save_path: str = None,
    ) -> bytes:
        """
        生成关键帧（使用参考图保持角色一致性）

        Args:
            prompt: 场景描述提示词
            reference_image_path: 角色参考图路径
            reference_weight: 参考图权重（None 则使用配置默认值）
            save_path: 保存路径

        Returns:
            图片二进制数据
        """
        client = self._get_client("image_to_image")

        if reference_weight is None:
            reference_weight = self.config.get(
                "image_to_image.ip_adapter.default_weight", 0.75
            )

        # 生成关键帧
        image_data = client.image_to_image_with_reference(
            prompt=prompt,
            reference_image_path=reference_image_path,
            reference_weight=reference_weight,
        )

        # 保存
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(image_data)
            print(f"✅ 关键帧已保存: {save_path}")

        return image_data

    def generate_video(
        self,
        keyframe_path: str,
        prompt: str,
        duration: int = None,
        save_path: str = None,
    ) -> bytes:
        """
        生成视频片段

        Args:
            keyframe_path: 关键帧图片路径
            prompt: 运动描述
            duration: 视频时长（None 则从配置读取）
            save_path: 保存路径

        Returns:
            视频二进制数据
        """
        client = self._get_client("image_to_video")

        # 获取当前模型配置
        model_config = self.config.get_current_video_model()
        max_duration = model_config["max_duration"]

        # 检查时长限制
        if duration is None:
            duration = min(5, max_duration)  # 默认 5 秒或模型最大值
        elif duration > max_duration:
            print(f"⚠️ 警告: 请求时长 {duration}秒 超过模型限制 {max_duration}秒，已调整")
            duration = max_duration

        print(f"🎬 开始生成视频: {duration}秒 (模型: {model_config['name']})")

        # 生成视频（异步任务）
        task_id = client.image_to_video(
            image_path=keyframe_path, prompt=prompt, duration=duration
        )

        print(f"⏳ 任务已提交: {task_id}，等待生成...")

        # 等待结果
        video_data = client.get_video_result(task_id)

        # 保存
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(video_data)
            print(f"✅ 视频已保存: {save_path}")

        return video_data


# ===== 使用示例 =====

if __name__ == "__main__":
    # 初始化客户端（自动读取 config.yaml）
    client = APIClient("config.yaml")

    # 示例1：生成角色形象
    print("=" * 50)
    print("示例1：生成角色形象")
    print("=" * 50)

    character_prompt = """
    male, 28 years old, handsome business elite,
    angular face, sharp eyes, short black hair slicked back,
    wearing navy blue suit, white shirt,
    confident expression, front view
    """

    client.generate_character_image(
        prompt=character_prompt, save_path="./output/test/character-front.png"
    )

    # 示例2：生成关键帧（使用参考图）
    print("\n" + "=" * 50)
    print("示例2：生成关键帧")
    print("=" * 50)

    keyframe_prompt = """
    same character, in luxury hotel lobby,
    standing near entrance, confident posture
    """

    client.generate_keyframe_with_reference(
        prompt=keyframe_prompt,
        reference_image_path="./output/test/character-front.png",
        save_path="./output/test/keyframe-001.png",
    )

    # 示例3：生成视频
    print("\n" + "=" * 50)
    print("示例3：生成视频")
    print("=" * 50)

    video_prompt = "camera slowly pushes in, character stands still"

    client.generate_video(
        keyframe_path="./output/test/keyframe-001.png",
        prompt=video_prompt,
        duration=3,  # 3 秒
        save_path="./output/test/video-001.mp4",
    )

    print("\n" + "=" * 50)
    print("✅ 所有测试完成！")
    print("=" * 50)
