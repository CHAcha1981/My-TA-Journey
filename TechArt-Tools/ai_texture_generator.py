"""Generate tileable textures via Stable Diffusion and save for Unity."""

from io import BytesIO
import json
import os
import sys
import time
from base64 import b64decode
from binascii import Error as BinasciiError
from urllib.parse import urlparse

import requests
from PIL import Image

# 配置
DEFAULT_SD_API = "http://localhost:7860/sdapi/v1/txt2img"
STABLE_DIFFUSION_API = os.getenv("STABLE_DIFFUSION_API", DEFAULT_SD_API).strip()
UNITY_TEXTURE_FOLDER = r'E:\unityproject\My project (6)\Assets\Ai_Textures'#unity贴图路径
OUTPUT_SIZE = 1024  # 最终图片的分辨率，2的幂

CONFIG_OUTPUT_PATH = os.path.join(UNITY_TEXTURE_FOLDER, "ai_texture_config.json")


def ensure_folder(path):
    """Create output folder when it does not exist."""
    if not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            print(f"创建目录失败: {path}，错误: {e}")
            sys.exit(1)


def check_sd_api_available(api_url):
    """Check SD WebUI endpoint before starting batch generation."""
    parsed = urlparse(api_url)
    if not parsed.scheme or not parsed.netloc:
        print(f"STABLE_DIFFUSION_API 配置无效: {api_url}")
        return False
    health_url = f"{parsed.scheme}://{parsed.netloc}/sdapi/v1/options"
    try:
        response = requests.get(health_url, timeout=8)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print("Stable Diffusion API 不可用。")
        print(f"- 当前地址: {api_url}")
        print("- 请确认 A1111/Forge 已启动并开启 API (--api)。")
        print("- 也可以通过环境变量 STABLE_DIFFUSION_API 指定地址。")
        print(f"- 连通性检查失败: {e}")
        return False


def post_sd_request(prompt, seed=None, size=OUTPUT_SIZE, negative_prompt=None):
    """Call txt2img API and return a PIL image."""
    payload = {
        "prompt": prompt,
        "width": size,
        "height": size,
        "steps": 25,
        "seed": seed if seed is not None else -1,
        "enable_hr": False,
        "negative_prompt": negative_prompt or "",
        "sampler_index": "Euler"
    }
    try:
        response = requests.post(STABLE_DIFFUSION_API, json=payload, timeout=300)
        response.raise_for_status()
        res = response.json()
        images = res.get("images", [])
        if not images:
            print(f"API 未返回图片，prompt: {prompt}")
            return None
        # “images”返回的是base64编码的图片
        img_data = images[0]
        img = Image.open(BytesIO(b64decode(img_data)))
        return img
    except (requests.RequestException, ValueError, OSError, BinasciiError) as e:
        print(f"生成图片失败，prompt: {prompt}，错误信息: {e}")
        return None

def resize_to_power_of_two(img, size=OUTPUT_SIZE):
    """Resize image to a square power-of-two texture."""
    if img.size != (size, size):
        return img.resize((size, size), Image.Resampling.LANCZOS)
    return img

def save_texture(img, base_name, folder, index=0):
    """Save texture image and return file name."""
    file_name = f"{base_name}_{index}.png" if index > 0 else f"{base_name}.png"
    save_path = os.path.join(folder, file_name)
    try:
        img.save(save_path)
        return file_name
    except OSError as e:
        print(f"保存图片失败: {save_path}，错误: {e}")
        return None

def import_to_unity(asset_path):
    """Emit a log showing where the texture was saved."""
    # 简单方案：修改Assets目录下文件，Unity自动检测并导入，一般无需额外操作
    # 可以后续扩展为调用Unity编辑器命令或脚本
    print(f"已保存到Unity Assets: {asset_path}")

def batch_generate(prompts_dict, out_folder=UNITY_TEXTURE_FOLDER, size=OUTPUT_SIZE):
    """Generate all prompts, save textures, and write config mapping."""
    ensure_folder(out_folder)
    if not check_sd_api_available(STABLE_DIFFUSION_API):
        print("终止批量生成。")
        return
    result_config = {}

    total = len(prompts_dict)
    count = 0
    for mat_name, prompt in prompts_dict.items():
        count += 1
        print(f"[{count}/{total}] 生成贴图: {mat_name}，提示词: {prompt}")
        img = post_sd_request(prompt, size=size)
        if img is None:
            print(f"跳过 {mat_name}")
            continue
        img = resize_to_power_of_two(img, size=size)
        fname = save_texture(img, mat_name, out_folder)
        if fname:
            import_to_unity(os.path.join(out_folder, fname))
            result_config[fname] = prompt
        time.sleep(1)
    # 写配置文件
    try:
        with open(CONFIG_OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(result_config, f, ensure_ascii=False, indent=2)
        print(f"已写入配置文件: {CONFIG_OUTPUT_PATH}")
    except (OSError, TypeError, ValueError) as e:
        print(f"写配置文件失败: {e}")

def main():
    """Entry point with sample prompts."""
    # 示例批量生成配置
    prompts = {
        "brick_wall": "brick wall seamless pattern, high-res texture, photorealistic",
        "metal": "metal seamless texture, brushed steel, PBR, tileable, clean",
        "fabric": "cloth seamless texture, woven, fabric, high detail, tileable",
    }
    batch_generate(prompts)

if __name__ == "__main__":
    main()
