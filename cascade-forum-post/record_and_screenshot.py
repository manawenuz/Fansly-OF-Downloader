import asyncio
import os
import shutil
import subprocess
from PIL import Image
from playwright.async_api import async_playwright

SCREENSHOT_DIR = "/Users/manwe/CascadeProjects/Fansly-OF-Downloader/cascade-forum-post/screenshots"
TEMP_VIDEO_DIR = "/Users/manwe/CascadeProjects/Fansly-OF-Downloader/cascade-forum-post/screenshots/temp_video"
URL = "https://of.tbs.manko.yoga/creator/cherrylovebombb"
CHROMIUM_EXEC = "/Users/manwe/Library/Caches/ms-playwright/chromium-1228/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(TEMP_VIDEO_DIR, exist_ok=True)

LIGHTBOX_NATIVE_CSS = """
#lightbox {
  position: fixed !important;
  inset: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  background: rgba(0, 0, 0, 0.96) !important;
  z-index: 9999 !important;
  display: none !important;
  align-items: center !important;
  justify-content: center !important;
  flex-direction: column !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
}
#lightbox.open {
  display: flex !important;
}
#lb-content {
  width: 100% !important;
  height: 100% !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 60px 16px 70px 16px !important;
  box-sizing: border-box !important;
}
#lb-content img, #lb-content video {
  max-width: 100% !important;
  max-height: 100% !important;
  width: auto !important;
  height: auto !important;
  object-fit: contain !important;
  border-radius: 12px !important;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6) !important;
  margin: auto !important;
}
.lb-close {
  position: absolute !important;
  top: 20px !important;
  right: 20px !important;
  width: 38px !important;
  height: 38px !important;
  border-radius: 50% !important;
  background: rgba(40, 40, 40, 0.75) !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: #fff !important;
  font-size: 18px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  cursor: pointer !important;
  z-index: 10001 !important;
}
.lb-nav {
  position: absolute !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  width: 44px !important;
  height: 44px !important;
  border-radius: 50% !important;
  background: rgba(40, 40, 40, 0.65) !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: #fff !important;
  font-size: 22px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  cursor: pointer !important;
  z-index: 10001 !important;
}
.lb-prev { left: 14px !important; }
.lb-next { right: 14px !important; }
.lb-counter {
  position: absolute !important;
  bottom: 24px !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
  background: rgba(40, 40, 40, 0.75) !important;
  backdrop-filter: blur(12px) !important;
  padding: 6px 18px !important;
  border-radius: 20px !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  color: #f0f0f0 !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
  z-index: 10001 !important;
  letter-spacing: 0.5px !important;
}
"""

async def smooth_scroll(page, distance, steps=25, delay=0.03):
    step_dist = distance / steps
    for _ in range(steps):
        await page.evaluate(f"window.scrollBy(0, {step_dist})")
        await asyncio.sleep(delay)

async def take_screenshots(page):
    await page.add_style_tag(content=LIGHTBOX_NATIVE_CSS)
    
    print("Capturing 07_mobile.jpg (Profile / Feed Top)...")
    await page.evaluate("window.scrollTo(0, 0)")
    await page.evaluate("if (typeof switchTab === 'function') switchTab('posts', document.getElementById('nav-posts'))")
    await asyncio.sleep(1)
    await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "07_mobile.jpg"), quality=90, type="jpeg")

    print("Capturing 08_mobile2.jpg (Mobile Drawer Navigation)...")
    await page.click(".mobile-menu-btn")
    await asyncio.sleep(0.6)
    await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "08_mobile2.jpg"), quality=90, type="jpeg")
    # Close sidebar
    await page.evaluate("if (typeof closeSidebar === 'function') closeSidebar()")
    await asyncio.sleep(0.4)

    print("Capturing 01_grid.jpg (Media Justified Gallery)...")
    await page.evaluate("switchTab('media', document.getElementById('nav-media'))")
    await asyncio.sleep(1)
    # Scroll slightly past the profile header directly to the gallery filter bar
    await page.evaluate("window.scrollTo(0, 580)")
    await asyncio.sleep(0.8)
    await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_grid.jpg"), quality=90, type="jpeg")

    print("Capturing 02_grid2.jpg (Media Justified Gallery Scrolled)...")
    await page.evaluate("window.scrollTo(0, 1200)")
    await asyncio.sleep(0.8)
    await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_grid2.jpg"), quality=90, type="jpeg")

    print("Capturing 05_lightbox.jpg (Native Centered Lightbox Photo)...")
    await page.evaluate("openGalleryLightbox(0)")
    await asyncio.sleep(0.8)
    await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "05_lightbox.jpg"), quality=90, type="jpeg")

    print("Capturing 06_lightbox2.jpg (Lightbox Navigated Item)...")
    await page.evaluate("lbNav(1)")
    await asyncio.sleep(0.8)
    await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "06_lightbox2.jpg"), quality=90, type="jpeg")
    # Close lightbox
    await page.evaluate("closeLightbox()")
    await asyncio.sleep(0.5)

    print("Capturing 03_search.jpg (Search Active with Post Results)...")
    await page.evaluate("switchTab('posts', document.getElementById('nav-posts'))")
    await asyncio.sleep(0.8)
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(0.3)
    await page.evaluate("toggleSearch()")
    await asyncio.sleep(0.3)
    await page.fill("#search-input", "morning")
    await page.evaluate("onSearch('morning')")
    await asyncio.sleep(0.8)
    # Scroll to show search results card
    await page.evaluate("window.scrollTo(0, 420)")
    await asyncio.sleep(0.8)
    await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "03_search.jpg"), quality=90, type="jpeg")
    await page.evaluate("clearSearch()")
    await page.evaluate("toggleSearch()")
    await asyncio.sleep(0.3)

    print("Capturing 04_date.jpg (Date Navigation Picker Overlay)...")
    await page.evaluate("openDatePicker()")
    await asyncio.sleep(0.6)
    await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "04_date.jpg"), quality=90, type="jpeg")
    await page.evaluate("closeDatePicker()")
    await asyncio.sleep(0.4)

async def record_usage_session(context):
    print("Starting recorded usage session for video...")
    page = await context.new_page()
    await page.goto(URL, wait_until="networkidle")
    await page.add_style_tag(content=LIGHTBOX_NATIVE_CSS)
    await asyncio.sleep(1)

    # 1. Feed browsing
    await smooth_scroll(page, 450, steps=20, delay=0.03)
    await asyncio.sleep(0.6)
    
    # Toggle comments on a post
    comment_btn = await page.query_selector(".comments-toggle")
    if comment_btn:
        await comment_btn.click()
        await asyncio.sleep(0.8)
        await smooth_scroll(page, 250, steps=15, delay=0.03)
        await asyncio.sleep(0.6)

    # 2. Open Mobile Drawer
    await page.click(".mobile-menu-btn")
    await asyncio.sleep(0.8)

    # 3. Switch to Media Gallery
    await page.evaluate("switchTab('media', document.getElementById('nav-media'))")
    await page.evaluate("closeSidebar()")
    await asyncio.sleep(1.2)

    # Scroll gallery
    await smooth_scroll(page, 700, steps=25, delay=0.03)
    await asyncio.sleep(0.8)
    await smooth_scroll(page, 700, steps=25, delay=0.03)
    await asyncio.sleep(0.8)

    # Filter media tabs: Videos
    await page.evaluate("filterMediaType('video', document.querySelector('.media-chip:nth-child(3)') || document.querySelector('.media-chip'))")
    await asyncio.sleep(1)
    await smooth_scroll(page, 400, steps=15, delay=0.03)
    await asyncio.sleep(0.6)

    # Filter media tabs: All
    await page.evaluate("filterMediaType('all', document.querySelector('.media-chip:first-child'))")
    await asyncio.sleep(0.8)

    # 4. Open Lightbox
    await page.evaluate("openGalleryLightbox(0)")
    await asyncio.sleep(1.2)
    await page.evaluate("lbNav(1)")
    await asyncio.sleep(1.2)
    await page.evaluate("lbNav(1)")
    await asyncio.sleep(1.2)
    await page.evaluate("closeLightbox()")
    await asyncio.sleep(0.8)

    # 5. Search feature
    await page.evaluate("switchTab('posts', document.getElementById('nav-posts'))")
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(0.6)
    await page.evaluate("toggleSearch()")
    await asyncio.sleep(0.4)
    
    # Type search query letter by letter
    search_term = "morning"
    for char in search_term:
        await page.type("#search-input", char, delay=100)
    await asyncio.sleep(1.2)
    await smooth_scroll(page, 350, steps=15, delay=0.03)
    await asyncio.sleep(0.8)
    await page.evaluate("clearSearch()")
    await asyncio.sleep(0.4)
    await page.evaluate("toggleSearch()")
    await asyncio.sleep(0.6)

    # 6. Date Picker
    await page.evaluate("openDatePicker()")
    await asyncio.sleep(1)
    await page.evaluate("""() => {
        const chip = document.querySelector('.date-day-chip');
        if (chip) chip.click();
        else closeDatePicker();
    }""")
    await asyncio.sleep(1.2)

    # 7. Sort & Filter Overlay
    await page.evaluate("openSort()")
    await asyncio.sleep(1)
    await page.evaluate("setSortKey('likes')")
    await asyncio.sleep(0.6)
    await page.evaluate("document.getElementById('sort-overlay').classList.remove('open')")
    await asyncio.sleep(0.8)
    await smooth_scroll(page, 500, steps=20, delay=0.03)
    await asyncio.sleep(0.8)

    # 8. Messages Tab
    await page.click(".mobile-menu-btn")
    await asyncio.sleep(0.6)
    await page.evaluate("switchTab('messages', document.getElementById('nav-messages'))")
    await page.evaluate("closeSidebar()")
    await asyncio.sleep(1)
    await smooth_scroll(page, 300, steps=15, delay=0.03)
    await asyncio.sleep(0.8)

    # 9. Stories Tab
    await page.click(".mobile-menu-btn")
    await asyncio.sleep(0.6)
    await page.evaluate("switchTab('stories', document.getElementById('nav-stories'))")
    await page.evaluate("closeSidebar()")
    await asyncio.sleep(1)
    await smooth_scroll(page, 300, steps=15, delay=0.03)
    await asyncio.sleep(0.8)

    # Scroll back to top
    await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
    await asyncio.sleep(1.2)

    await page.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=CHROMIUM_EXEC,
            headless=True
        )

        viewport_cfg = {"width": 393, "height": 852}
        user_agent_cfg = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"

        # 1. Take clean screenshots in standard context
        print("--- Step 1: Taking Screenshots ---")
        context_ss = await browser.new_context(
            viewport=viewport_cfg,
            user_agent=user_agent_cfg,
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2
        )
        page_ss = await context_ss.new_page()
        await page_ss.goto(URL, wait_until="networkidle")
        await take_screenshots(page_ss)
        await context_ss.close()

        # 2. Record video in matching viewport and video-size
        print("--- Step 2: Recording Video Session ---")
        shutil.rmtree(TEMP_VIDEO_DIR, ignore_errors=True)
        os.makedirs(TEMP_VIDEO_DIR, exist_ok=True)
        
        context_vid = await browser.new_context(
            viewport=viewport_cfg,
            user_agent=user_agent_cfg,
            is_mobile=True,
            has_touch=True,
            device_scale_factor=1,
            record_video_dir=TEMP_VIDEO_DIR,
            record_video_size=viewport_cfg
        )
        await record_usage_session(context_vid)
        await context_vid.close()
        await browser.close()

    # Convert recorded webm to webp and mp4
    print("--- Step 3: Converting Video to WebP and MP4 ---")
    video_files = [os.path.join(TEMP_VIDEO_DIR, f) for f in os.listdir(TEMP_VIDEO_DIR) if f.endswith(".webm")]
    if video_files:
        src_video = video_files[0]
        out_webp = os.path.join(SCREENSHOT_DIR, "usage_demo.webp")
        out_mp4 = os.path.join(SCREENSHOT_DIR, "usage_demo.mp4")
        frames_dir = os.path.join(TEMP_VIDEO_DIR, "frames")
        os.makedirs(frames_dir, exist_ok=True)

        print("Extracting frames with upgraded ffmpeg...")
        subprocess.run([
            "/opt/homebrew/bin/ffmpeg", "-y",
            "-i", src_video,
            "-vf", "fps=10,scale=360:-1:flags=lanczos",
            os.path.join(frames_dir, "frame_%05d.png")
        ], check=True)

        frame_paths = sorted([os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.startswith("frame_") and f.endswith(".png")])
        print(f"Total frames extracted: {len(frame_paths)}")

        print("Encoding animated WEBP using Pillow...")
        images = [Image.open(f) for f in frame_paths]
        if images:
            images[0].save(
                out_webp,
                format="WEBP",
                save_all=True,
                append_images=images[1:],
                duration=100,
                loop=0,
                quality=65,
                method=4
            )
            print("WebP video generated:", out_webp, "Size:", os.path.getsize(out_webp))
            shutil.copyfile(out_webp, os.path.join(SCREENSHOT_DIR, "demo.webp"))

        print("Encoding MP4 video with ffmpeg...")
        subprocess.run([
            "/opt/homebrew/bin/ffmpeg", "-y",
            "-i", src_video,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "slow",
            "-crf", "22",
            out_mp4
        ], check=True)
        print("MP4 video generated:", out_mp4, "Size:", os.path.getsize(out_mp4))
        
        # Clean up temp frames and webm
        shutil.rmtree(TEMP_VIDEO_DIR, ignore_errors=True)

if __name__ == "__main__":
    asyncio.run(main())
