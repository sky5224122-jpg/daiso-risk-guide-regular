from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageEnhance, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUTPUT = ASSETS / "quick-guide-25s.mp4"
POSTER = ASSETS / "quick-guide-poster.jpg"

WIDTH = 1280
HEIGHT = 720
OUTPUT_WIDTH = 960
OUTPUT_HEIGHT = 540
FPS = 10
SLIDE_SECONDS = 5
FADE_FRAMES = 6

NAVY = "#0F2244"
BLUE = "#2B5EA7"
RED = "#D0272D"
WHITE = "#FFFFFF"
TEXT = "#111827"
MUTED = "#52627A"
SURFACE = "#F4F6FA"
BORDER = "#D8E0EB"

FONT_REGULAR = Path(r"C:\Windows\Fonts\malgun.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\malgunbd.ttf")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(str(path), size=size)


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255
    )
    return mask


def fit_image(image: Image.Image, box: tuple[int, int], portrait: bool = False) -> Image.Image:
    source = image.convert("RGB")
    if portrait:
        target = source.copy()
        target.thumbnail(box, Image.Resampling.LANCZOS)
        return target

    source_ratio = source.width / source.height
    box_ratio = box[0] / box[1]
    if source_ratio > box_ratio:
        crop_width = int(source.height * box_ratio)
        left = max(0, (source.width - crop_width) // 2)
        source = source.crop((left, 0, left + crop_width, source.height))
    else:
        crop_height = int(source.width / box_ratio)
        top = max(0, (source.height - crop_height) // 2)
        source = source.crop((0, top, source.width, top + crop_height))
    return source.resize(box, Image.Resampling.LANCZOS)


def make_slide(
    step: str,
    title: str,
    subtitle: str,
    image_name: str,
    portrait: bool = False,
    closing: bool = False,
) -> Image.Image:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), SURFACE)
    draw = ImageDraw.Draw(canvas)

    draw.rectangle((0, 0, WIDTH, 116), fill=NAVY)
    draw.rectangle((0, 112, WIDTH, 116), fill=RED)
    draw.text((54, 28), "아성다이소 정기 위험성평가", font=font(24, True), fill=WHITE)
    draw.text((54, 66), "25초 핵심 실행 가이드", font=font(17), fill="#C9D8F0")

    badge_box = (1015, 34, 1220, 84)
    draw.rounded_rectangle(badge_box, radius=25, fill=BLUE)
    badge_text = step
    badge_font = font(20, True)
    bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    draw.text(
        (
            (badge_box[0] + badge_box[2] - (bbox[2] - bbox[0])) / 2,
            (badge_box[1] + badge_box[3] - (bbox[3] - bbox[1])) / 2 - 2,
        ),
        badge_text,
        font=badge_font,
        fill=WHITE,
    )

    draw.text((54, 150), title, font=font(34, True), fill=TEXT)
    draw.text((56, 200), subtitle, font=font(20), fill=MUTED)

    card = (52, 252, 1228, 668)
    draw.rounded_rectangle(card, radius=22, fill=WHITE, outline=BORDER, width=2)

    source = Image.open(ASSETS / image_name)
    if portrait:
        target = fit_image(source, (310, 370), portrait=True)
        x = 120
        y = 274 + (370 - target.height) // 2
        canvas.paste(target, (x, y), rounded_mask(target.size, 14))

        draw.text((510, 318), "먼저 접속구분을 선택합니다.", font=font(26, True), fill=TEXT)
        bullets = [
            "본사 · 매장 · 오픈지원",
            "평가유형은 '정기' 선택",
            "영업부에 맞는 접속 주소(V2~V6) 확인",
        ]
        for index, item in enumerate(bullets):
            top = 385 + index * 67
            draw.ellipse((512, top + 7, 528, top + 23), fill=RED)
            draw.text((548, top), item, font=font(23), fill=MUTED)
    else:
        target = fit_image(source, (1110, 350))
        x = 85
        y = 285
        canvas.paste(target, (x, y), rounded_mask(target.size, 14))

    if closing:
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (15, 34, 68, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rounded_rectangle(
            (350, 462, 930, 620), radius=24, fill=(15, 34, 68, 235)
        )
        overlay_draw.text(
            (640, 504),
            "제출 전 필수항목과 서명을 확인하세요",
            font=font(27, True),
            fill=WHITE,
            anchor="mm",
        )
        overlay_draw.text(
            (640, 558),
            "임시저장 → 최종제출 → 승인 → 인쇄/PDF",
            font=font(20),
            fill="#D8E5F7",
            anchor="mm",
        )
        canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")

    return canvas


def blend(left: Image.Image, right: Image.Image, amount: float) -> Image.Image:
    return Image.blend(left, right, max(0.0, min(1.0, amount)))


def build_video() -> None:
    slides = [
        make_slide(
            "STEP 1",
            "접속구분과 평가유형 선택",
            "본인 업무에 맞는 화면과 평가기간을 먼저 확인합니다.",
            "shot-login.png",
            portrait=True,
        ),
        make_slide(
            "STEP 2",
            "기본정보 · 조직도 · 교육 입력",
            "매장정보와 근무인원, 참여근로자, 사전교육 사진을 등록합니다.",
            "shot-dashboard.png",
        ),
        make_slide(
            "STEP 3",
            "16개 공정 평가표 상·중·하 점검",
            "공정 순서 칩으로 이동하며 위험요인, 개선대책, 현장사진을 확인합니다.",
            "shot-table.png",
        ),
        make_slide(
            "STEP 4",
            "근로자 · 관리감독자 전자서명",
            "참여와 결과공유 서명을 각각 확인하여 증빙을 완성합니다.",
            "shot-signature.png",
            portrait=True,
        ),
        make_slide(
            "STEP 5",
            "최종제출 · 승인 · 인쇄/PDF",
            "제출 상태와 승인 흐름을 확인하고 전체 결과를 보관합니다.",
            "shot-approval-flow.png",
            closing=True,
        ),
    ]

    writer = imageio_ffmpeg.write_frames(
        str(OUTPUT),
        (OUTPUT_WIDTH, OUTPUT_HEIGHT),
        fps=FPS,
        codec="libx264",
        quality=7,
        pix_fmt_in="rgb24",
        pix_fmt_out="yuv420p",
        macro_block_size=1,
        output_params=["-movflags", "+faststart"],
    )
    writer.send(None)

    per_slide = SLIDE_SECONDS * FPS
    for index, slide in enumerate(slides):
        for frame_index in range(per_slide):
            frame = slide
            if index < len(slides) - 1 and frame_index >= per_slide - FADE_FRAMES:
                amount = (frame_index - (per_slide - FADE_FRAMES) + 1) / FADE_FRAMES
                frame = blend(slide, slides[index + 1], amount)
            encoded_frame = frame.resize(
                (OUTPUT_WIDTH, OUTPUT_HEIGHT), Image.Resampling.LANCZOS
            )
            writer.send(encoded_frame.tobytes())

    writer.close()
    slides[0].save(POSTER, "JPEG", quality=90, optimize=True)
    print(f"created: {OUTPUT}")
    print(f"poster: {POSTER}")
    print(f"duration: {len(slides) * SLIDE_SECONDS}s")


if __name__ == "__main__":
    build_video()
