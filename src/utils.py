import segno
from PIL import Image, ImageDraw, ImageFont
import io
from typing import Optional

import io
from typing import Optional
import segno
from PIL import Image, ImageDraw, ImageFont

import io
from typing import Optional
import segno
from PIL import Image, ImageDraw, ImageFont

def get_qrcode_buffer(url: str, start_time: Optional[str] = None, end_time: Optional[str] = None) -> io.BytesIO:
    """全新卡片式布局二维码（保持尺寸不变，风格更现代）(AI Generated)"""
    # 生成二维码
    qr = segno.make_qr(url, error='m')
    buffer = io.BytesIO()

    base_scale = 4
    qr.save(buffer, kind='png', scale=base_scale)
    buffer.seek(0)

    if not (start_time and end_time):
        # 不带日期：200×200（全新卡片样式，不再是纯二维码）
        qr_img = Image.open(buffer)
        qr_img = qr_img.convert('RGB')
        qr_img = qr_img.resize((180, 180), Image.Resampling.LANCZOS)

        # 创建卡片式背景（带圆角和阴影，更现代）
        bg = Image.new('RGB', (200, 200), color='#FFFFFF')
        draw = ImageDraw.Draw(bg)

        # 绘制卡片主体（圆角大卡片，包裹二维码）
        draw.rounded_rectangle(
            [10, 10, 190, 190],
            radius=16,
            fill='#F5F7FA',
            outline='#E4E7ED',
            width=1
        )

        # 粘贴二维码到卡片中央
        bg.paste(qr_img, (10, 10))

        # 保存返回
        buffer = io.BytesIO()
        bg.save(buffer, format='PNG', optimize=True, compress_level=9)
        buffer.seek(0)
        return buffer

    # ===== 带日期：250×300（全新上下分区布局，现代卡片风格）=====
    qr_img = Image.open(buffer)
    qr_img = qr_img.convert('RGB')

    # 1. 二维码区域配置（上半区：大尺寸二维码，居中展示）
    target_qr_size = 160
    qr_img = qr_img.resize((target_qr_size, target_qr_size), Image.Resampling.LANCZOS)
    total_width = 250
    total_height = 300

    # 2. 创建整体卡片背景（纯白底，带轻微圆角边框，现代感）
    bg = Image.new('RGB', (total_width, total_height), color='#FFFFFF')
    draw = ImageDraw.Draw(bg)

    # 绘制整体卡片外框（圆角大卡片，包裹所有内容）
    draw.rounded_rectangle(
        [5, 5, 245, 295],
        radius=20,
        fill='#F9FBFD',
        outline='#E6E9ED',
        width=1
    )

    # 3. 上半区：二维码（居中放置，无额外复杂背景，更简洁）
    qr_x = (total_width - target_qr_size) // 2
    qr_y = 30  # 上半区居中留白
    bg.paste(qr_img, (qr_x, qr_y))

    # 4. 下半区：有效期信息（全新分区，与二维码用分割线隔开，更清晰）
    # 分割线（分隔上下区，简洁精致）
    split_line_y = qr_y + target_qr_size + 25
    draw.line([(40, split_line_y), (210, split_line_y)], fill='#E6E9ED', width=2)

    # 有效期标题（简化样式，居中加粗，更醒目）
    font_paths = [
        "arial.ttf",
        "msyh.ttc",
        "simhei.ttf"
    ]

    # 标题样式（更大胆，无需下划线装饰）
    title_text = "VALID PERIOD"
    title_font_size = 12
    title_font = None
    for font_path in font_paths:
        try:
            title_font = ImageFont.truetype(font_path, title_font_size)
            break
        except:
            continue
    if title_font is None:
        title_font = ImageFont.load_default()

    # 标题位置（分割线下方，居中）
    if hasattr(draw, 'textbbox'):
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    else:
        title_size = draw.textsize(title_text, font=title_font)
        title_bbox = (0, 0, title_size[0], title_size[1])
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (total_width - title_width) // 2
    title_y = split_line_y + 15
    draw.text((title_x, title_y), title_text, fill='#1F75CB', font=title_font, align='center')

    # 5. 有效期内容（大字体，无额外背景框，更清爽）
    period_text = f"{start_time} - {end_time}"
    # 动态调整字体大小（更大胆，提升可读性）
    if len(period_text) <= 25:
        period_font_size = 14
    elif len(period_text) <= 30:
        period_font_size = 13
    else:
        period_font_size = 12

    period_font = None
    for font_path in font_paths:
        try:
            period_font = ImageFont.truetype(font_path, period_font_size)
            break
        except:
            continue
    if period_font is None:
        period_font = ImageFont.load_default()

    # 内容位置（标题下方，居中，无背景框）
    if hasattr(draw, 'textbbox'):
        period_bbox = draw.textbbox((0, 0), period_text, font=period_font)
    else:
        period_size = draw.textsize(period_text, font=period_font)
        period_bbox = (0, 0, period_size[0], period_size[1])
    period_width = period_bbox[2] - period_bbox[0]
    period_x = (total_width - period_width) // 2
    period_y = title_y + 25

    # 绘制有效期（深黑色，醒目易读，无背景干扰）
    draw.text((period_x, period_y), period_text, fill='#2D3436', font=period_font, align='center')

    # 6. 保存并压缩
    buffer = io.BytesIO()
    bg.save(buffer,
            format='PNG',
            optimize=True,
            compress_level=9)
    buffer.seek(0)

    return buffer

if __name__ == "__main__":
    res_buffer = get_qrcode_buffer('https://www.python.org',
                          "2026-01-26 18:04:41", "2026-01-26 18:04:41")
    # res_buffer = get_qrcode_buffer('https://www.python.org')
    img = Image.open(res_buffer)
    img.save('qrcode_test.png')