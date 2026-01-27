import segno
from PIL import Image, ImageDraw, ImageFont
from typing import Optional
import io


def get_qrcode_buffer(url: str, start_time: Optional[str] = None, end_time: Optional[str] = None):
    """现代化风格的二维码生成 (generate by AI)"""
    # 生成二维码
    qr = segno.make_qr(url, error='m')
    buffer = io.BytesIO()
    qr.save(buffer, kind='png', scale=7)  # 更小的比例
    buffer.seek(0)

    if not (start_time and end_time):
        return buffer

    # 打开二维码
    qr_img = Image.open(buffer)
    qr_img = qr_img.convert('RGB')
    qr_width, qr_height = qr_img.size

    # 计算新图片尺寸（添加圆角和边距）
    padding = 40
    text_height = 60
    corner_radius = 20
    new_width = qr_width + padding * 2
    new_height = qr_height + padding * 2 + text_height

    # 创建带圆角的背景
    from PIL import ImageOps
    bg = Image.new('RGB', (new_width, new_height), color='#F8F9FA')

    # 创建圆角遮罩
    mask = Image.new('L', (new_width, new_height), 0)
    draw_mask = ImageDraw.Draw(mask)

    # 绘制圆角矩形
    def round_rect(x1, y1, x2, y2, r):
        draw_mask.rectangle([x1 + r, y1, x2 - r, y2], fill=255)
        draw_mask.rectangle([x1, y1 + r, x2, y2 - r], fill=255)
        draw_mask.pieslice([x1, y1, x1 + 2 * r, y1 + 2 * r], 180, 270, fill=255)
        draw_mask.pieslice([x2 - 2 * r, y1, x2, y1 + 2 * r], 270, 360, fill=255)
        draw_mask.pieslice([x1, y2 - 2 * r, x1 + 2 * r, y2], 90, 180, fill=255)
        draw_mask.pieslice([x2 - 2 * r, y2 - 2 * r, x2, y2], 0, 90, fill=255)

    round_rect(0, 0, new_width - 1, new_height - 1, corner_radius)

    # 应用圆角
    bg.putalpha(mask)

    # 粘贴二维码（居中）
    qr_x = (new_width - qr_width) // 2
    qr_y = padding
    bg.paste(qr_img, (qr_x, qr_y))

    draw = ImageDraw.Draw(bg)

    # 添加分隔线
    line_y = qr_y + qr_height + 15
    draw.line([(qr_x, line_y), (qr_x + qr_width, line_y)],
              fill='#E9ECEF', width=2)

    # 添加日期
    try:
        font = ImageFont.truetype("arial.ttf", 12) or ImageFont.truetype("msyh.ttf", 12)
    except:
        font = ImageFont.load_default()

    period_text = f"Valid Period: {start_time} - {end_time}"
    text_bbox = draw.textbbox((0, 0), period_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (new_width - text_width) // 2
    text_y = line_y + 20

    # 添加文字背景
    text_padding = 8
    draw.rounded_rectangle(
        [text_x - text_padding, text_y - text_padding,
         text_x + text_width + text_padding, text_y + (text_bbox[3] - text_bbox[1]) + text_padding],
        radius=6,
        fill='#E7F5FF',
        outline='#339AF0',
        width=1
    )

    draw.text((text_x, text_y), period_text, fill='#1864AB', font=font)

    # 保存
    buffer = io.BytesIO()
    bg.save(buffer, format='PNG', optimize=True)
    buffer.seek(0)

    return buffer

if __name__ == "__main__":
    res_buffer = get_qrcode_buffer('https://www.python.org',
                          "2026-01-26 18:04:41", "2026-01-26 18:04:41")
    # res_buffer = get_qrcode_buffer('https://www.python.org')
    img = Image.open(res_buffer)
    img.save('qrcode_test.png')