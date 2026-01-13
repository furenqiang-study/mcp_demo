import json
import math
from io import BytesIO
import requests
from PIL import Image, ImageDraw, ImageFont
import ast

#图片标注

def start_tag(img_data, box_points, api_key, chat_id, agent_id, model='Qwen'):
    '''
    img_data:url_path
    box_points:JSON string
    api_key:agent api key
    chat_id: current chat id
    agent_id:agent id
    model:current inferenced visual-model (GLM,Qwen)
    '''
    IMAGE_FACTOR = 28
    MIN_PIXELS = 4 * 28 * 28
    MAX_PIXELS = 16384 * 28 * 28
    MAX_RATIO = 200

    def round_by_factor(number: int, factor: int) -> int:
        """Returns the closest integer to 'number' that is divisible by 'factor'."""
        return round(number / factor) * factor

    def floor_by_factor(number: int, factor: int) -> int:
        """Returns the largest integer less than or equal to 'number' that is divisible by 'factor'."""
        return math.floor(number / factor) * factor

    def ceil_by_factor(number: int, factor: int) -> int:
        """Returns the smallest integer greater than or equal to 'number' that is divisible by 'factor'."""
        return math.ceil(number / factor) * factor

    def smart_resize(
            height: int, width: int, factor: int = IMAGE_FACTOR, min_pixels: int = MIN_PIXELS,
            max_pixels: int = MAX_PIXELS
    ) -> tuple[int, int]:
        """
        Rescales the image so that the following conditions are met:

        1. Both dimensions (height and width) are divisible by 'factor'.

        2. The total number of pixels is within the range ['min_pixels', 'max_pixels'].

        3. The aspect ratio of the image is maintained as closely as possible.
        """
        if max(height, width) / min(height, width) > MAX_RATIO:
            raise ValueError(
                f"absolute aspect ratio must be smaller than {MAX_RATIO}, got {max(height, width) / min(height, width)}"
            )
        h_bar = max(factor, round_by_factor(height, factor))
        w_bar = max(factor, round_by_factor(width, factor))
        if h_bar * w_bar > max_pixels:
            beta = math.sqrt((height * width) / max_pixels)
            h_bar = max(factor, floor_by_factor(height / beta, factor))
            w_bar = max(factor, floor_by_factor(width / beta, factor))
        elif h_bar * w_bar < min_pixels:
            beta = math.sqrt(min_pixels / (height * width))
            h_bar = ceil_by_factor(height * beta, factor)
            w_bar = ceil_by_factor(width * beta, factor)
        return h_bar, w_bar

    # print(f"img_data 类型:{type(img_data)}")
    img_data_list = ast.literal_eval(img_data)
    urls = [item['url'] for item in img_data_list]
    img_url = 'https://llm.geosophon.com' + urls[0]
    response = requests.get(img_url)
    if response.status_code == 200:

        image = Image.open(BytesIO(response.content)).convert("RGB")
    else:
        print(f"❌ 图片下载失败，状态码: {response.status_code}")
        exit(1)

    width, height = image.size
    scale = 1
    if model.lower() == 'qwen':
        input_height, input_width = smart_resize(height, width, max_pixels=2048 * 28 * 28)
        if 1 - abs(input_height - height / height) < 0.95:
            scale = 1.2
    elif model.lower() == 'glm':
        input_height, input_width = 1024, 1024

    draw = ImageDraw.Draw(image)
    try:
        box_data = json.loads(box_points)
    except Exception as e:
        raise ValueError("❌ box_points 不是有效的 JSON 字符串") from e
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 40)
    except:
        font = None  # 如果加载失败就用默认字体
    for item in box_data.get("locations", []):
        if not all(k in item for k in ("box", "label")):
            continue
        x1, y1, x2, y2 = item["box"]
        label = item["label"]
        abs_y1 = int(y1 / input_height * height * scale)
        abs_x1 = int(x1 / input_width * width * scale)
        abs_y2 = int(y2 / input_height * height * scale)
        abs_x2 = int(x2 / input_width * width * scale)

        if abs_x1 > abs_x2:
            abs_x1, abs_x2 = abs_x2, abs_x1

        if abs_y1 > abs_y2:
            abs_y1, abs_y2 = abs_y2, abs_y1
        box = [
            (abs_x1, abs_y1),  # 左上
            (abs_x2, abs_y1),  # 右上
            (abs_x2, abs_y2),  # 右下
            (abs_x1, abs_y2)  # 左下
        ]
        draw.polygon(box, outline="red", width=2)
        draw.text((abs_x1 + 2, abs_y1 - 42), label, fill="#ffe723", font=font)

    output_buffer = BytesIO()
    image.save(output_buffer, format="JPEG")
    output_buffer.seek(0)

    upload_url = f'https://llm.geosophon.com/api/application/{agent_id}/chat/{chat_id}/upload_file'
    headers = {
        "Authorization": api_key,
    }
    files = {
        "file": ("output.jpg", output_buffer, "image/jpeg")
    }

    # 发起上传请求
    response = requests.post(upload_url, headers=headers, files=files)
    if response.status_code == 200:
        # print("✅ 上传成功:", response.json())
        print("✅ 上传成功")
        return response.json()
    else:
        # print(f"❌ 上传失败: {response.status_code}")
        print(f"❌ 上传失败")
        print(response.text)


# img_data= [{'name': '001.jpeg', 'percentage': 0, 'status': 'ready', 'size': 34816, 'raw': {'uid': 1767950728592}, 'uid': 1767950728592, 'url': '/api/file/2390fb74-ed3d-11f0-b24c-4269080de842', 'file_id': '2390fb74-ed3d-11f0-b24c-4269080de842'}]
# api_key = 'application-86e36744c0b4191eea811cd6091d350b'
# chat_id = '2378be56-ed3d-11f0-8137-4269080de842'
# agent_id = '90f137e0-468c-11f0-9cbd-e2bb3033b0f6'
# box_points = '{\n  "locations":[\n    {\n      "type":"漏液",\n      "box":[94,402,864,993],\n      "label":"漏液区域1"\n    }\n  ]\n}'
#
# start_tag(img_data,box_points,api_key,chat_id,agent_id,'Qwen')

