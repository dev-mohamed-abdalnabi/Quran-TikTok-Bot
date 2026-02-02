import os, requests, random, json, base64, textwrap
import numpy as np
import moviepy.editor as mp
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageFont, ImageDraw

# --- الإعدادات ---
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
FONT_PATH = "ArabicFont.ttf" 

def process_ar(t):
    reshaped = arabic_reshaper.reshape(t)
    return get_display(reshaped)[::-1]

def build_tiktok_video():
    print("🎬 جاري تحضير فيديو التيك توك...")
    
    # اختيار سورة عشوائية
    s_id = random.randint(1, 114)
    res = requests.get(f"http://api.alquran.cloud/v1/surah/{s_id}/ar.alafasy").json()['data']
    s_name = res['name']
    
    # اختيار آية عشوائية (التيك توك يحب المقاطع القصيرة المركزة)
    ayah = random.choice(res['ayahs'])
    audio_url = ayah['audio']
    text = ayah['text']
    
    # تحميل الصوت
    with open("audio.mp3", "wb") as f:
        f.write(requests.get(audio_url).content)
    
    a_clip = mp.AudioFileClip("audio.mp3")
    dur = a_clip.duration
    
    # جلب خلفية سينمائية من Pexels
    headers = {'Authorization': PEXELS_API_KEY}
    v_res = requests.get('https://api.pexels.com/videos/search?query=nature&orientation=portrait&per_page=15', headers=headers).json()
    v_url = random.choice(v_res['videos'])['video_files'][0]['link']
    with open("bg.mp4", "wb") as f: f.write(requests.get(v_url).content)

    # معالجة الخلفية (Zoom-in Effect)
    bg = mp.VideoFileClip("bg.mp4").resize(height=1280).crop(x1=0, y1=0, width=720, height=1280).set_duration(dur)
    bg = bg.resize(lambda t: 1 + 0.04*t) 
    
    # طبقة تظليل لزيادة وضوح الكلام
    dark = mp.ColorClip(size=(720, 1280), color=(0,0,0), duration=dur).set_opacity(0.4)

    # رسم النص الاحترافي
    img = Image.new('RGBA', (720, 1280), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # اسم السورة فوق
    f_sura = ImageFont.truetype(FONT_PATH, 75)
    draw.text((360, 200), process_ar(s_name), font=f_sura, fill="#FFD700", anchor="mm")
    
    # نص الآية في المنتصف
    f_ayah = ImageFont.truetype(FONT_PATH, 65)
    lines = textwrap.wrap(text, width=22)
    y_pos = 640 - (len(lines) * 45)
    for line in lines:
        draw.text((360, y_pos), process_ar(line), font=f_ayah, fill="white", anchor="mm", stroke_width=2, stroke_fill="black")
        y_pos += 110

    txt_clip = mp.ImageClip(np.array(img)).set_duration(dur).set_position('center')

    # تجميع الفيديو
    final = mp.CompositeVideoClip([bg, dark, txt_clip]).set_audio(a_clip)
    final.write_videofile("tiktok_final.mp4", fps=30, codec="libx264", logger=None)
    print(f"✅ تم الانتهاء من فيديو سورة {s_name}")

if __name__ == "__main__":
    build_tiktok_video()
