import os, requests, random, textwrap
import moviepy.editor as mp
from PIL import Image, ImageFont, ImageDraw
import arabic_reshaper
from bidi.algorithm import get_display

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
FONT_PATH = "ArabicFont.ttf"

def process_ar(t):
    reshaped = arabic_reshaper.reshape(t)
    return get_display(reshaped)

def build_tiktok_video():
    print("🎬 Starting...")
    s_id = random.randint(1, 114)
    res = requests.get(f"http://api.alquran.cloud/v1/surah/{s_id}/ar.alafasy").json()['data']
    s_name = res['name']
    ayah = random.choice(res['ayahs'])
    text = ayah['text']
    
    # تحميل الصوت
    with open("audio.mp3", "wb") as f:
        f.write(requests.get(ayah['audio']).content)
    
    a_clip = mp.AudioFileClip("audio.mp3")
    
    # جلب فيديو من Pexels
    headers = {'Authorization': PEXELS_API_KEY}
    v_res = requests.get('https://api.pexels.com/videos/search?query=nature&orientation=portrait&per_page=10', headers=headers).json()
    v_url = random.choice(v_res['videos'])['video_files'][0]['link']
    with open("bg.mp4", "wb") as f: f.write(requests.get(v_url).content)

    # تجهيز الفيديو الأساسي
    bg = mp.VideoFileClip("bg.mp4").resize(height=1280).crop(x1=0, y1=0, width=720, height=1280).set_duration(a_clip.duration)
    
    # كتابة النص بوضعية بسيطة
    txt = mp.TextClip(process_ar(text), fontsize=50, color='white', font=FONT_PATH, method='caption', size=(600, None)).set_duration(a_clip.duration).set_position('center')
    title = mp.TextClip(process_ar(s_name), fontsize=70, color='gold', font=FONT_PATH).set_duration(a_clip.duration).set_position(('center', 200))

    final = mp.CompositeVideoClip([bg, title, txt]).set_audio(a_clip)
    final.write_videofile("tiktok_final.mp4", fps=24, codec="libx264", audio_codec="aac")
    print("✅ Done!")

if __name__ == "__main__":
    build_tiktok_video()
