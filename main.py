import os, requests, random, textwrap
import moviepy.editor as mp
from PIL import Image

if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

import arabic_reshaper
from bidi.algorithm import get_display

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
FONT_PATH = "ArabicFont.ttf"

def process_ar(t):
    return get_display(arabic_reshaper.reshape(t))

def get_random_quran():
    try:
        s_id = random.randint(1, 114)
        res = requests.get(f"https://api.alquran.cloud/v1/surah/{s_id}/ar.alafasy", timeout=15).json()['data']
        ayah = random.choice(res['ayahs'])
        return res['name'], ayah['text'], ayah['audio']
    except:
        return "سورة الإخلاص", "قُلْ هُوَ اللَّهُ أَحَدٌ", "https://cdn.islamic.network/quran/audio/128/ar.alafasy/112.mp3"

def build_tiktok_video():
    print("🚀 جاري طبخ الفيديو الاحترافي...")
    s_name, text, audio_url = get_random_quran()
    
    with open("audio.mp3", "wb") as f: f.write(requests.get(audio_url).content)
    a_clip = mp.AudioFileClip("audio.mp3")
    
    # رابط فيديو طبيعة مباشر
    fallback_v = "https://v1.assets.pexels.com/video_files/4124032/4124032-sd_540_960_25fps.mp4"
    try:
        headers = {'Authorization': PEXELS_API_KEY}
        v_res = requests.get('https://api.pexels.com/videos/search?query=nature&orientation=portrait&per_page=1', headers=headers, timeout=10).json()
        v_url = v_res['videos'][0]['video_files'][0]['link']
    except:
        v_url = fallback_v

    with open("bg.mp4", "wb") as f: f.write(requests.get(v_url).content)

    bg = mp.VideoFileClip("bg.mp4")
    if bg.duration < a_clip.duration:
        bg = mp.vfx.loop(bg, duration=a_clip.duration)
    else:
        bg = bg.set_duration(a_clip.duration)

    bg = bg.resize(height=1280).crop(x1=0, y1=0, width=720, height=1280).fx(mp.vfx.colorx, 0.6)
    
    title = mp.TextClip(process_ar(f" سورة {s_name} "), fontsize=50, color='gold', font=FONT_PATH, method='label').set_position(('center', 150)).set_duration(a_clip.duration)
    
    wrapped = "\n".join(textwrap.wrap(text, width=28))
    txt = mp.TextClip(process_ar(wrapped), fontsize=60, color='white', font=FONT_PATH, method='caption', size=(650, None), align='Center').set_position('center').set_duration(a_clip.duration)

    final = mp.CompositeVideoClip([bg, title, txt]).set_audio(a_clip)
    final.write_videofile("tiktok_final.mp4", fps=24, codec="libx264", audio_codec="aac")
    
    with open("caption.txt", "w", encoding="utf-8") as f:
        f.write(f"سورة {s_name} ✨ #قرآن #islam #fyp")
    print("✅ الفيديو جاهز للمرحلة القادمة!")

if __name__ == "__main__":
    build_tiktok_video()
