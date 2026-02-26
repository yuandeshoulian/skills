"""
AI 视频生成器 - 主生成脚本
从剧本和分镜脚本生成完整视频
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional
import json
from api_client import APIClient, ConfigManager
import subprocess


class VideoGenerator:
    """视频生成器"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config = ConfigManager(config_path)
        self.api_client = APIClient(config_path)
        self.output_base = Path(self.config.get("output.base_dir", "./output/ai-video"))

    def generate_full_episode(
        self,
        project_name: str,
        episode_number: int,
        script_path: str,
        storyboard_path: str,
    ):
        """
        生成完整集数的视频

        Args:
            project_name: 项目名称（如"王者归来"）
            episode_number: 集数
            script_path: 剧本路径
            storyboard_path: 分镜脚本路径
        """
        print("=" * 60)
        print(f"🎬 开始生成《{project_name}》第 {episode_number} 集")
        print("=" * 60)

        # 创建输出目录
        project_dir = self.output_base / project_name
        characters_dir = project_dir / "characters"
        scenes_dir = project_dir / "scenes"
        keyframes_dir = project_dir / "keyframes" / f"episode-{episode_number:03d}"
        videos_dir = project_dir / "videos" / f"episode-{episode_number:03d}"
        final_dir = project_dir / "final"

        for d in [characters_dir, scenes_dir, keyframes_dir, videos_dir, final_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # 步骤1：分析剧本，提取角色
        print("\n" + "=" * 60)
        print("📝 步骤1：分析剧本，提取角色信息")
        print("=" * 60)

        characters = self._extract_characters(script_path)
        print(f"✅ 识别到 {len(characters)} 个角色")

        # 步骤2：生成角色形象
        print("\n" + "=" * 60)
        print("🎨 步骤2：生成角色形象")
        print("=" * 60)

        character_images = self._generate_character_images(characters, characters_dir)

        # 步骤3：分析分镜脚本，提取场景
        print("\n" + "=" * 60)
        print("🏞️ 步骤3：生成场景图片")
        print("=" * 60)

        scenes = self._extract_scenes(storyboard_path)
        scene_images = self._generate_scene_images(scenes, scenes_dir)

        # 步骤4：生成关键帧
        print("\n" + "=" * 60)
        print("🖼️ 步骤4：生成关键帧")
        print("=" * 60)

        shots = self._extract_shots(storyboard_path)
        keyframes = self._generate_keyframes(
            shots, character_images, scene_images, keyframes_dir
        )

        # 步骤5：生成视频片段
        print("\n" + "=" * 60)
        print("🎥 步骤5：生成视频片段")
        print("=" * 60)

        video_segments = self._generate_video_segments(shots, keyframes, videos_dir)

        # 步骤6：合成最终视频
        print("\n" + "=" * 60)
        print("🎬 步骤6：合成最终视频")
        print("=" * 60)

        final_video = self._merge_video_segments(
            video_segments, final_dir / f"episode-{episode_number:03d}.mp4"
        )

        print("\n" + "=" * 60)
        print(f"✅ 视频生成完成！")
        print(f"📁 输出路径: {final_video}")
        print("=" * 60)

        return final_video

    def _extract_characters(self, script_path: str) -> List[Dict]:
        """从剧本提取角色信息（简化版）"""
        # 实际应该解析剧本文件
        # 这里返回示例数据
        return [
            {
                "name": "林宇",
                "description": "male, 28 years old, business elite, angular face, sharp eyes",
                "angles": ["front", "side", "full"],
            },
            {
                "name": "张雪",
                "description": "female, mid-20s, elegant woman, long hair",
                "angles": ["front", "side"],
            },
        ]

    def _generate_character_images(
        self, characters: List[Dict], output_dir: Path
    ) -> Dict:
        """生成角色形象图"""
        character_images = {}

        for char in characters:
            char_name = char["name"]
            print(f"\n生成角色: {char_name}")

            char_images = {}
            for angle in char["angles"]:
                print(f"  - {angle} 角度...")

                prompt = f"{char['description']}, {angle} view"
                save_path = output_dir / f"{char_name}-{angle}.png"

                # 检查缓存
                if self.config.get("cost.optimization.enable_caching") and save_path.exists():
                    print(f"    ✅ 使用缓存: {save_path}")
                    char_images[angle] = str(save_path)
                    continue

                # 生成图片
                self.api_client.generate_character_image(
                    prompt=prompt, save_path=str(save_path)
                )
                char_images[angle] = str(save_path)

            character_images[char_name] = char_images

        return character_images

    def _extract_scenes(self, storyboard_path: str) -> List[Dict]:
        """从分镜脚本提取场景信息"""
        # 实际应该解析分镜文件
        return [
            {
                "name": "豪华酒店大堂-晚上",
                "description": "luxury hotel lobby, evening, warm lighting, elegant",
            },
            {"name": "酒店门外-晚上", "description": "hotel entrance, night, street lights"},
        ]

    def _generate_scene_images(self, scenes: List[Dict], output_dir: Path) -> Dict:
        """生成场景图片"""
        scene_images = {}

        for scene in scenes:
            scene_name = scene["name"]
            print(f"\n生成场景: {scene_name}")

            save_path = output_dir / f"{scene_name}.png"

            # 检查缓存
            if self.config.get("cost.optimization.enable_caching") and save_path.exists():
                print(f"  ✅ 使用缓存: {save_path}")
                scene_images[scene_name] = str(save_path)
                continue

            # 生成图片
            prompt = f"{scene['description']}, cinematic, vertical composition"
            self.api_client.generate_character_image(  # 使用同样的文生图 API
                prompt=prompt, save_path=str(save_path)
            )
            scene_images[scene_name] = str(save_path)

        return scene_images

    def _extract_shots(self, storyboard_path: str) -> List[Dict]:
        """从分镜脚本提取镜头信息"""
        # 实际应该解析分镜文件
        return [
            {
                "id": "S1-1",
                "scene": "豪华酒店大堂-晚上",
                "shot_type": "全景",
                "angle": "平视",
                "camera_movement": "固定",
                "description": "豪华酒店大堂，林宇站在门口",
                "duration": 2,
                "characters": ["林宇"],
            },
            {
                "id": "S1-2",
                "scene": "豪华酒店大堂-晚上",
                "shot_type": "中景",
                "angle": "平视",
                "camera_movement": "固定",
                "description": "保安走向林宇",
                "duration": 2,
                "characters": ["林宇", "保安"],
            },
        ]

    def _generate_keyframes(
        self,
        shots: List[Dict],
        character_images: Dict,
        scene_images: Dict,
        output_dir: Path,
    ) -> Dict:
        """生成关键帧"""
        keyframes = {}

        for shot in shots:
            shot_id = shot["id"]
            print(f"\n生成关键帧: {shot_id}")

            save_path = output_dir / f"{shot_id}.png"

            # 构建提示词
            prompt = f"{shot['description']}, {shot['shot_type']}, {shot['angle']} angle"

            # 获取参考图（如果有角色）
            reference_image = None
            if shot["characters"]:
                main_character = shot["characters"][0]
                if main_character in character_images:
                    reference_image = character_images[main_character]["front"]

            # 生成关键帧
            if reference_image:
                # 使用参考图生成（保持角色一致性）
                self.api_client.generate_keyframe_with_reference(
                    prompt=prompt,
                    reference_image_path=reference_image,
                    save_path=str(save_path),
                )
            else:
                # 无角色，直接文生图
                self.api_client.generate_character_image(
                    prompt=prompt, save_path=str(save_path)
                )

            keyframes[shot_id] = str(save_path)

        return keyframes

    def _generate_video_segments(
        self, shots: List[Dict], keyframes: Dict, output_dir: Path
    ) -> List[str]:
        """生成视频片段"""
        video_segments = []

        # 获取当前模型配置
        model_config = self.config.get_current_video_model()
        max_duration = model_config["max_duration"]

        for shot in shots:
            shot_id = shot["id"]
            duration = shot["duration"]

            print(f"\n生成视频: {shot_id} ({duration}秒)")

            # 检查时长限制
            if duration > max_duration:
                print(f"  ⚠️ 时长 {duration}秒 超过限制 {max_duration}秒，分段生成")
                # 分段生成（这里简化处理）
                duration = max_duration

            save_path = output_dir / f"{shot_id}.mp4"

            # 构建运动提示词
            movement = shot["camera_movement"]
            motion_prompt = self._get_motion_prompt(movement)

            # 生成视频
            keyframe_path = keyframes[shot_id]
            self.api_client.generate_video(
                keyframe_path=keyframe_path,
                prompt=motion_prompt,
                duration=duration,
                save_path=str(save_path),
            )

            video_segments.append(str(save_path))

        return video_segments

    def _get_motion_prompt(self, camera_movement: str) -> str:
        """根据运镜方式生成运动提示词"""
        motion_prompts = {
            "固定": "static shot, minimal movement",
            "推镜": "camera slowly pushes in, zoom in",
            "拉镜": "camera slowly pulls out, zoom out",
            "跟镜": "camera follows subject, tracking shot",
            "摇镜": "camera pans left to right",
            "移镜": "camera moves horizontally, dolly shot",
        }
        return motion_prompts.get(camera_movement, "static shot")

    def _merge_video_segments(
        self, video_segments: List[str], output_path: Path
    ) -> Path:
        """合并视频片段（使用 FFmpeg）"""
        print(f"\n合并 {len(video_segments)} 个视频片段...")

        # 创建文件列表
        filelist_path = output_path.parent / "filelist.txt"
        with open(filelist_path, "w") as f:
            for video in video_segments:
                f.write(f"file '{video}'\n")

        # 使用 FFmpeg 合并
        cmd = [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(filelist_path),
            "-c",
            "copy",
            str(output_path),
            "-y",  # 覆盖已存在的文件
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ 视频合并完成: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 视频合并失败: {e.stderr.decode()}")
            raise

        # 清理临时文件
        filelist_path.unlink()

        return output_path


# ===== 使用示例 =====

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI 视频生成器")
    parser.add_argument("--project", type=str, required=True, help="项目名称")
    parser.add_argument("--episode", type=int, required=True, help="集数")
    parser.add_argument("--script", type=str, required=True, help="剧本路径")
    parser.add_argument("--storyboard", type=str, required=True, help="分镜脚本路径")
    parser.add_argument("--config", type=str, default="config.yaml", help="配置文件路径")

    args = parser.parse_args()

    # 初始化生成器
    generator = VideoGenerator(args.config)

    # 生成视频
    generator.generate_full_episode(
        project_name=args.project,
        episode_number=args.episode,
        script_path=args.script,
        storyboard_path=args.storyboard,
    )

    print("\n🎉 完成！")
