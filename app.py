import streamlit as st
import requests
import base64
import os
import io
import json
import time
from PIL import Image, ImageDraw, ImageFont
import textwrap

# ─────────────────────────────────────────────
#  Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="🎨 AI Comic Creator",
    page_icon="🦸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  Custom CSS – comic / pop-art look
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bangers&family=Comic+Neue:wght@700&display=swap');

  html, body, [class*="css"] {
      font-family: 'Comic Neue', cursive;
  }
  .main { background: #fff9e6; }

  /* Hero header */
  .comic-header {
      background: linear-gradient(135deg, #ff6b35, #f7c59f, #efefd0, #004e89);
      border: 5px solid #1a1a1a;
      border-radius: 12px;
      padding: 20px 30px;
      text-align: center;
      margin-bottom: 20px;
      box-shadow: 8px 8px 0 #1a1a1a;
  }
  .comic-header h1 {
      font-family: 'Bangers', cursive;
      font-size: 3.5rem;
      color: #1a1a1a;
      letter-spacing: 3px;
      text-shadow: 3px 3px 0 #fff, 5px 5px 0 #ff6b35;
      margin: 0;
  }
  .comic-header p {
      font-size: 1.1rem;
      color: #1a1a1a;
      margin: 5px 0 0 0;
  }

  /* Panel cards */
  .panel-card {
      border: 4px solid #1a1a1a;
      border-radius: 8px;
      background: white;
      padding: 12px;
      box-shadow: 6px 6px 0 #1a1a1a;
      margin-bottom: 20px;
  }
  .panel-number {
      font-family: 'Bangers', cursive;
      font-size: 1.8rem;
      color: #ff6b35;
      text-shadow: 2px 2px 0 #1a1a1a;
  }

  /* Speech bubble */
  .speech-bubble {
      background: white;
      border: 3px solid #1a1a1a;
      border-radius: 20px;
      padding: 10px 15px;
      position: relative;
      font-family: 'Comic Neue', cursive;
      font-weight: 700;
      font-size: 0.95rem;
      box-shadow: 3px 3px 0 #1a1a1a;
      margin-top: 8px;
  }

  /* Buttons */
  .stButton > button {
      font-family: 'Bangers', cursive !important;
      font-size: 1.3rem !important;
      letter-spacing: 2px !important;
      background: #ff6b35 !important;
      color: white !important;
      border: 3px solid #1a1a1a !important;
      border-radius: 8px !important;
      box-shadow: 4px 4px 0 #1a1a1a !important;
      padding: 8px 24px !important;
      transition: all 0.1s !important;
  }
  .stButton > button:hover {
      transform: translate(2px, 2px) !important;
      box-shadow: 2px 2px 0 #1a1a1a !important;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
      background: #004e89 !important;
      border-right: 4px solid #1a1a1a;
  }
  [data-testid="stSidebar"] * { color: white !important; }
  [data-testid="stSidebar"] .stTextArea textarea,
  [data-testid="stSidebar"] .stTextInput input,
  [data-testid="stSidebar"] .stSelectbox select {
      background: #fff9e6 !important;
      color: #1a1a1a !important;
      border: 2px solid #1a1a1a !important;
  }

  /* Progress */
  .generating-badge {
      background: #ffdc00;
      border: 3px solid #1a1a1a;
      border-radius: 8px;
      padding: 8px 16px;
      font-family: 'Bangers', cursive;
      font-size: 1.2rem;
      letter-spacing: 2px;
      display: inline-block;
      box-shadow: 3px 3px 0 #1a1a1a;
  }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Helper – add speech bubble overlay to image
# ─────────────────────────────────────────────
def add_speech_bubble(image: Image.Image, text: str, position: str = "top") -> Image.Image:
    """Draw a comic speech bubble on top of the PIL image."""
    img = image.copy().convert("RGBA")
    W, H = img.size
    bubble_h = max(80, int(H * 0.22))
    bubble_w = int(W * 0.9)

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    x0 = (W - bubble_w) // 2
    y0 = 10 if position == "top" else H - bubble_h - 10
    x1, y1 = x0 + bubble_w, y0 + bubble_h

    # Bubble body
    draw.rounded_rectangle([x0, y0, x1, y1], radius=20,
                            fill=(255, 255, 255, 230), outline=(0, 0, 0, 255), width=3)

    # Tail triangle
    mid_x = (x0 + x1) // 2
    if position == "top":
        tail = [(mid_x - 12, y1), (mid_x + 12, y1), (mid_x, y1 + 22)]
    else:
        tail = [(mid_x - 12, y0), (mid_x + 12, y0), (mid_x, y0 - 22)]
    draw.polygon(tail, fill=(255, 255, 255, 230), outline=(0, 0, 0, 255))

    # Text inside bubble
    try:
        font = ImageFont.truetype("arial.ttf", size=max(14, bubble_h // 4))
    except Exception:
        font = ImageFont.load_default()

    max_chars = max(20, int(bubble_w / (font.size * 0.6)))
    wrapped = textwrap.fill(text, width=max_chars)
    draw.text((x0 + 10, y0 + 10), wrapped, fill=(0, 0, 0, 255), font=font)

    img = Image.alpha_composite(img, overlay)
    return img.convert("RGB")


# ─────────────────────────────────────────────
#  Image generators (pluggable backends)
# ─────────────────────────────────────────────
def generate_with_pollinations(prompt: str, style: str, width: int = 512, height: int = 512) -> Image.Image | None:
    """Free – Pollinations.ai (no API key required)."""
    style_suffix = {
        "Comic Book": "comic book art style, bold outlines, vibrant colors, halftone dots",
        "Manga": "black and white manga art, detailed linework, screen tones",
        "American Superhero": "marvel comics style, dynamic pose, action, bold inks",
        "Cartoon": "cartoon style, thick outlines, bright flat colors, funny",
        "Watercolor": "watercolor comic illustration, soft colors, inked outlines",
    }.get(style, "comic book style")

    full_prompt = f"{prompt}, {style_suffix}, high quality"
    encoded = requests.utils.quote(full_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&seed={int(time.time())}"
    try:
        resp = requests.get(url, timeout=60)
        if resp.status_code == 200:
            return Image.open(io.BytesIO(resp.content))
    except Exception as e:
        st.warning(f"Pollinations error: {e}")
    return None


def generate_with_openai(prompt: str, style: str, api_key: str) -> Image.Image | None:
    """OpenAI DALL·E 3 backend."""
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        style_suffix = {
            "Comic Book": "comic book art style, bold outlines, halftone",
            "Manga": "manga black and white art style",
            "American Superhero": "marvel comics superhero art style",
            "Cartoon": "cartoon illustration thick outlines",
            "Watercolor": "watercolor comic illustration",
        }.get(style, "comic book style")
        full_prompt = f"{prompt}, {style_suffix}"
        response = client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        img_url = response.data[0].url
        img_data = requests.get(img_url, timeout=30).content
        return Image.open(io.BytesIO(img_data))
    except Exception as e:
        st.warning(f"OpenAI error: {e}")
    return None


def generate_with_stability(prompt: str, style: str, api_key: str) -> Image.Image | None:
    """Stability AI (Stable Diffusion) backend."""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        style_suffix = {
            "Comic Book": "comic book art, bold lines",
            "Manga": "manga style, black and white",
            "American Superhero": "superhero comic art",
            "Cartoon": "cartoon illustration",
            "Watercolor": "watercolor illustration",
        }.get(style, "comic book art")
        body = {
            "text_prompts": [{"text": f"{prompt}, {style_suffix}", "weight": 1}],
            "cfg_scale": 7,
            "height": 512,
            "width": 512,
            "steps": 30,
            "samples": 1,
        }
        resp = requests.post(
            "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
            headers=headers, json=body, timeout=60
        )
        if resp.status_code == 200:
            data = resp.json()
            img_bytes = base64.b64decode(data["artifacts"][0]["base64"])
            return Image.open(io.BytesIO(img_bytes))
        else:
            st.warning(f"Stability error {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        st.warning(f"Stability SDK error: {e}")
    return None


# ─────────────────────────────────────────────
#  Auto-split story into panels
# ─────────────────────────────────────────────
def split_story_into_panels(story: str, num_panels: int) -> list[dict]:
    """
    Split a story into panel descriptions automatically.
    Returns list of dicts: {scene, dialogue}
    """
    # Split by sentences / natural breaks
    import re
    sentences = re.split(r'(?<=[.!?])\s+', story.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    panels = []
    chunk_size = max(1, len(sentences) // num_panels)

    for i in range(num_panels):
        start = i * chunk_size
        end = start + chunk_size if i < num_panels - 1 else len(sentences)
        chunk = " ".join(sentences[start:end]) if start < len(sentences) else "..."

        # Extract likely dialogue (text in quotes) as speech bubble
        dialogue_match = re.search(r'["\'](.+?)["\']', chunk)
        dialogue = dialogue_match.group(1) if dialogue_match else ""
        # Scene description = chunk without quotes
        scene = re.sub(r'["\'].*?["\']', '', chunk).strip() or chunk

        panels.append({"scene": scene, "dialogue": dialogue, "full": chunk})

    return panels


# ─────────────────────────────────────────────
#  Comic strip layout builder
# ─────────────────────────────────────────────
def build_comic_strip(images: list[Image.Image], panel_size: tuple = (512, 512),
                       cols: int = 2, border: int = 8, gap: int = 16,
                       bg_color: tuple = (255, 249, 230)) -> Image.Image:
    """Combine panel images into a single comic strip image."""
    rows = (len(images) + cols - 1) // cols
    strip_w = cols * panel_size[0] + (cols + 1) * gap + 2 * border
    strip_h = rows * panel_size[1] + (rows + 1) * gap + 2 * border

    strip = Image.new("RGB", (strip_w, strip_h), bg_color)
    draw = ImageDraw.Draw(strip)
    draw.rectangle([0, 0, strip_w - 1, strip_h - 1], outline=(26, 26, 26), width=border)

    for idx, img in enumerate(images):
        row, col = divmod(idx, cols)
        x = border + gap + col * (panel_size[0] + gap)
        y = border + gap + row * (panel_size[1] + gap)
        resized = img.resize(panel_size, Image.LANCZOS)
        strip.paste(resized, (x, y))
        # Panel border
        draw.rectangle([x - 3, y - 3, x + panel_size[0] + 2, y + panel_size[1] + 2],
                        outline=(26, 26, 26), width=3)

    return strip


# ─────────────────────────────────────────────
#  Main app
# ─────────────────────────────────────────────
def main():
    # ── Header ──────────────────────────────
    st.markdown("""
    <div class="comic-header">
      <h1>💥 AI COMIC CREATOR 💥</h1>
      <p>Type your story → Watch it become a comic automatically!</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar settings ─────────────────────
    with st.sidebar:
        st.markdown("## ⚙️ SETTINGS")
        st.markdown("---")

        backend = st.selectbox(
            "🖼️ Image Engine",
            ["Pollinations (Free, No Key)", "OpenAI DALL·E 3", "Stability AI"],
        )

        api_key = ""
        if backend == "OpenAI DALL·E 3":
            api_key = st.text_input("🔑 OpenAI API Key", type="password",
                                     placeholder="sk-...")
        elif backend == "Stability AI":
            api_key = st.text_input("🔑 Stability API Key", type="password",
                                     placeholder="sk-...")

        st.markdown("---")
        art_style = st.selectbox(
            "🎨 Art Style",
            ["Comic Book", "Manga", "American Superhero", "Cartoon", "Watercolor"],
        )
        num_panels = st.slider("📄 Number of Panels", min_value=2, max_value=8, value=4)
        cols_layout = st.radio("📐 Panel Layout", ["2 columns", "3 columns", "4 columns"], index=0)
        cols = int(cols_layout[0])

        show_bubbles = st.toggle("💬 Show Speech Bubbles", value=True)
        bubble_pos = st.radio("Bubble Position", ["top", "bottom"], horizontal=True)

        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.markdown("""
- Write your story naturally  
- Include **dialogue in quotes**  
- Describe characters & actions  
- More panels = richer comic  
        """)

    # ── Story input ──────────────────────────
    col_left, col_right = st.columns([2, 1])
    with col_left:
        story = st.text_area(
            "📖 Your Comic Story",
            height=200,
            placeholder="""Example:
Spider-Man swings through New York City at night. "I love this city!" he shouts.
Suddenly, Doctor Octopus appears on the rooftop. "Prepare to meet your doom, Spider-Man!"
They clash in an epic battle. Spider-Man dodges the metal tentacles with agility.
Finally, Spider-Man webs up Doc Ock. "Justice is served!" he proclaims triumphantly.""",
            help="Write your story. It will be auto-split into comic panels.",
        )

    with col_right:
        st.markdown("### 🦸 Character Info (optional)")
        character = st.text_input("Main Character", placeholder="e.g. Spider-Man")
        setting = st.text_input("Setting", placeholder="e.g. New York City, night")
        genre = st.selectbox("Genre", ["Superhero", "Fantasy", "Sci-Fi", "Horror", "Comedy", "Romance"])

    # ── Generate button ──────────────────────
    st.markdown("---")
    generate_col, download_col = st.columns([3, 1])
    with generate_col:
        generate_btn = st.button("⚡ GENERATE MY COMIC!", use_container_width=True)

    # ── State management ─────────────────────
    if "panels" not in st.session_state:
        st.session_state.panels = []
    if "strip_image" not in st.session_state:
        st.session_state.strip_image = None

    # ── Generation flow ──────────────────────
    if generate_btn:
        if not story.strip():
            st.error("✏️ Please write your story first!")
        elif backend != "Pollinations (Free, No Key)" and not api_key:
            st.error(f"🔑 Please enter your {backend} API key in the sidebar!")
        else:
            st.session_state.panels = []
            st.session_state.strip_image = None

            panel_descriptions = split_story_into_panels(story, num_panels)

            st.markdown('<div class="generating-badge">⚡ GENERATING YOUR COMIC…</div>',
                        unsafe_allow_html=True)
            progress = st.progress(0)
            status_text = st.empty()

            generated_images: list[Image.Image] = []
            panel_data = []

            for i, panel in enumerate(panel_descriptions):
                pct = (i + 1) / num_panels
                status_text.markdown(f"🎨 Drawing panel **{i+1}** of **{num_panels}**…")

                # Build detailed prompt
                char_hint = f"featuring {character}" if character else ""
                setting_hint = f"in {setting}" if setting else ""
                img_prompt = (
                    f"{genre} comic panel {char_hint} {setting_hint}: {panel['scene']}"
                ).strip()

                # Generate image
                img: Image.Image | None = None
                if backend == "Pollinations (Free, No Key)":
                    img = generate_with_pollinations(img_prompt, art_style)
                elif backend == "OpenAI DALL·E 3":
                    img = generate_with_openai(img_prompt, art_style, api_key)
                elif backend == "Stability AI":
                    img = generate_with_stability(img_prompt, art_style, api_key)

                if img is None:
                    # Fallback placeholder
                    img = Image.new("RGB", (512, 512), color=(200, 200, 200))
                    d = ImageDraw.Draw(img)
                    d.text((20, 240), f"Panel {i+1}\n(Generation failed)", fill=(80, 80, 80))

                # Add speech bubble if dialogue found
                display_img = img
                if show_bubbles and panel.get("dialogue"):
                    display_img = add_speech_bubble(img, panel["dialogue"], bubble_pos)

                generated_images.append(display_img)
                panel_data.append({
                    "panel_num": i + 1,
                    "image": display_img,
                    "scene": panel["scene"],
                    "dialogue": panel.get("dialogue", ""),
                    "full": panel["full"],
                })
                progress.progress(pct)

            st.session_state.panels = panel_data

            # Build strip
            strip = build_comic_strip(
                [p["image"] for p in panel_data],
                panel_size=(512, 512),
                cols=cols,
                bg_color=(255, 249, 230),
            )
            st.session_state.strip_image = strip

            progress.progress(1.0)
            status_text.markdown("✅ **Your comic is ready!** Scroll down to see it.")

    # ── Display panels ───────────────────────
    if st.session_state.panels:
        st.markdown("---")
        st.markdown("## 🗞️ YOUR COMIC STRIP")

        # Full strip image
        if st.session_state.strip_image:
            st.image(st.session_state.strip_image, use_container_width=True,
                     caption="📰 Full Comic Strip")

            # Download strip
            buf = io.BytesIO()
            st.session_state.strip_image.save(buf, format="PNG")
            st.download_button(
                label="⬇️ Download Full Comic Strip (PNG)",
                data=buf.getvalue(),
                file_name="my_comic.png",
                mime="image/png",
                use_container_width=True,
            )

        # Individual panels
        st.markdown("---")
        st.markdown("## 🔍 Individual Panels")

        panel_cols_n = min(cols, len(st.session_state.panels))
        for row_start in range(0, len(st.session_state.panels), panel_cols_n):
            row_panels = st.session_state.panels[row_start: row_start + panel_cols_n]
            panel_cols = st.columns(panel_cols_n)
            for col_idx, panel in enumerate(row_panels):
                with panel_cols[col_idx]:
                    st.markdown(
                        f'<div class="panel-number">PANEL {panel["panel_num"]}</div>',
                        unsafe_allow_html=True,
                    )
                    st.image(panel["image"], use_container_width=True)
                    if panel["dialogue"]:
                        st.markdown(
                            f'<div class="speech-bubble">💬 "{panel["dialogue"]}"</div>',
                            unsafe_allow_html=True,
                        )
                    with st.expander("📝 Scene Description"):
                        st.write(panel["scene"])

                    # Per-panel download
                    buf = io.BytesIO()
                    panel["image"].save(buf, format="PNG")
                    st.download_button(
                        f"⬇️ Panel {panel['panel_num']}",
                        buf.getvalue(),
                        file_name=f"panel_{panel['panel_num']}.png",
                        mime="image/png",
                        key=f"dl_panel_{panel['panel_num']}",
                    )

    # ── Footer ───────────────────────────────
    st.markdown("---")
    st.markdown(
        "<center style='color:#888;font-size:0.8rem;'>🦸 AI Comic Creator • Built with Streamlit & Pollinations AI</center>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
