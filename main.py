import os, requests, random, textwrap
import moviepy.editor as mp
from PIL import Image

# إصلاح مشكلة Pillow الجديدة
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
        res = requests.get(f"https://api.alquran.cloud/v1/surah/{s_id}/ar.alafasy", timeout=15).json()['data']
        ayah = random.choice(res['ayahs'])
        return res['name'], ayah['text'], ayah['audio']
    except:
        return "سورة الإخلاص", "قُلْ هُوَ اللَّهُ أَحَدٌ", "https://cdn.islamic.network/quran/audio/128/ar.alafasy/112.mp3"

def build_tiktok_video():
    print("🚀 جاري التحضير...")
    s_name, text, audio_url = get_random_quran()
    
    # 1. تحميل الصوت (تأكد من الرابط)
    audio_data = requests.get(audio_url).content
    with open("audio.mp3", "wb") as f: f.write(audio_data)
    a_clip = mp.AudioFileClip("audio.mp3")
    
    # 2. تحميل الفيديو (روابط مباشرة خام للمشاهد الطبيعية)
    video_ready = False
    # رابط مباشر لفيديو طبيعة (HD) لضمان العمل في حال فشل Pexels
    fallback_url = "https://v1.assets.pexels.com/video_files/4124032/4124032-sd_540_960_25fps.mp4"
    
    try:
        headers = {'Authorization': PEXELS_API_KEY}
        v_res = requests.get('https://api.pexels.com/videos/search?query=nature&orientation=portrait&per_page=5', headers=headers, timeout=15).json()
        v_url = random.choice(v_res['videos'])['video_files'][0]['link']
        print(f"📥 Downloading from Pexels...")
        v_data = requests.get(v_url).content
        with open("bg.mp4", "wb") as f: f.write(v_data)
        video_ready = True
    except Exception as e:
        print(f"⚠️ Pexels Failed, using static backup: {e}")
        v_data = requests.get(fallback_url).content
        with open("bg.mp4", "wb") as f: f.write(v_data)
        video_ready = True

    # 3. المونتاج الفعلي
    if video_ready:
        try:
            # فتح الفيديو والتأكد من جودته
            bg = mp.VideoFileClip("bg.mp4")
            # لو الفيديو أقصر من الصوت، نكرره
            if bg.duration < a_clip.duration:
                bg = mp.vfx.loop(bg, duration=a_clip.duration)
            else:
                bg = bg.set_duration(a_clip.duration)

            bg = bg.resize(height=1280).crop(x1=0, y1=0, width=720, height=1280)
            bg = bg.fx(mp.vfx.colorx, 0.6) # تعتيم 40%
            
            # النصوص
            title = mp.TextClip(process_ar(f" سورة {s_name} "), fontsize=50, color='gold', font=FONT_PATH, method='label').set_position(('center', 150)).set_duration(a_clip.duration)
            
            wrapped = "\n".join(textwrap.wrap(text, width=28))
            txt = mp.TextClip(process_ar(wrapped), fontsize=60, color='white', font=FONT_PATH, method='caption', size=(650, None), align='Center').set_position('center').set_duration(a_clip.duration)

            final = mp.CompositeVideoClip([bg, title, txt]).set_audio(a_clip)
            # تقليل الجودة قليلاً لضمان سرعة الرفع وعدم حدوث Error في الذاكرة
            final.write_videofile("tiktok_final.mp4", fps=24, codec="libx264", audio_codec="aac")
            
            caption = f"سورة {s_name} 🕋 #قرآن #islam #fyp"
            with open("caption.txt", "w", encoding="utf-8") as f: f.write(caption)
            print("✅ فيديو جاهز للرفع!")
        except Exception as e:
            print(f"❌ Montage Error: {e}")

if __name__ == "__main__":
    build_tiktok_video()
