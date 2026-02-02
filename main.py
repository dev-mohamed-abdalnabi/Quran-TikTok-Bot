import os, requests, random, textwrap
import moviepy.editor as mp
from PIL import Image, ImageFont, ImageDraw

# سطر الإصلاح لمشكلة ANTIALIAS
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

import arabic_reshaper
from bidi.algorithm import get_display

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
FONT_PATH = "ArabicFont.ttf"

def process_ar(t):
    reshaped = arabic_reshaper.reshape(t)
    return get_display(reshaped)

def get_random_quran():
    try:
        s_id = random.randint(1, 114)
        res = requests.get(f"http://api.alquran.cloud/v1/surah/{s_id}/ar.alafasy").json()['data']
        s_name = res['name']
        ayah = random.choice(res['ayahs'])
        return s_name, ayah['text'], ayah['audio']
    except:
        return "الفاتحة", "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ", "https://cdn.islamic.network/quran/audio/128/ar.alafasy/1.mp3"

def build_tiktok_video():
    print("🚀 جاري صناعة فيديو احترافي...")
    s_name, text, audio_url = get_random_quran()
    
    # 1. تحميل الصوت
    with open("audio.mp3", "wb") as f: f.write(requests.get(audio_url).content)
    a_clip = mp.AudioFileClip("audio.mp3")
    
    # 2. جلب الفيديو مع معالجة الخطأ
    try:
        headers = {'Authorization': PEXELS_API_KEY}
        queries = ['nature', 'mountains', 'galaxy', 'ocean', 'rain']
        v_res = requests.get(f'https://api.pexels.com/videos/search?query={random.choice(queries)}&orientation=portrait&per_page=15', headers=headers).json()
        v_url = random.choice(v_res['videos'])['video_files'][0]['link']
        with open("bg.mp4", "wb") as f: f.write(requests.get(v_url).content)
    except Exception as e:
        print(f"⚠️ Pexels Error: {e}. Using fallback background.")
        # لو فشل، بيحمل فيديو طبيعة عام (رابط مباشر احتياطي)
        fallback_url = "https://player.vimeo.com/external/370374926.sd.mp4?s=2318629938e2f89f7f4e9126d40c6a83602492f2&profile_id=164"
        with open("bg.mp4", "wb") as f: f.write(requests.get(fallback_url).content)

    # 3. المونتاج
    bg = mp.VideoFileClip("bg.mp4").resize(height=1280).crop(x1=0, y1=0, width=720, height=1280).set_duration(a_clip.duration)
    bg = bg.fx(mp.vfx.colorx, 0.6) 
    
    title_fixed = process_ar(f" سورة {s_name} ")
    title_clip = mp.TextClip(title_fixed, fontsize=55, color='gold', font=FONT_PATH, method='label').set_position(('center', 150)).set_duration(a_clip.duration)

    wrapped_text = "\n".join(textwrap.wrap(text, width=25))
    ayah_fixed = process_ar(wrapped_text)
    txt_clip = mp.TextClip(ayah_fixed, fontsize=65, color='white', font=FONT_PATH, method='caption', size=(650, None), align='Center').set_position('center').set_duration(a_clip.duration)

    final = mp.CompositeVideoClip([bg, title_clip, txt_clip]).set_audio(a_clip)
    final.write_videofile("tiktok_final.mp4", fps=24, codec="libx264", audio_codec="aac")
    
    # 4. وصف الفيديو
    hashtags = ["#قرآن", "#راحة_نفسية", "#islam", "#fyp", "#foryou"]
    caption = f"سورة {s_name} 🕊️ { ' '.join(hashtags) }"
    with open("caption.txt", "w", encoding="utf-8") as f: f.write(caption)
    print(f"✅ Done: {caption}")

if __name__ == "__main__":
    build_tiktok_video()
