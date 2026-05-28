import os
import sys
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw, ImageFont
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ---------------------------------------------------------
# မြန်မာစံတော်ချိန် (UTC +6:30) ကို သတ်မှတ်ခြင်း (အချိန်ဇုန် ပြဿနာ ဖြေရှင်းရန်)
# ---------------------------------------------------------
MMT = timezone(timedelta(hours=6, minutes=30))

# ==========================================
# အပိုင်း (၁) - Thumbnail ပေါ်တွင် ရက်စွဲတပ်ခြင်း
# ==========================================
def add_date_to_thumbnail(input_path, output_path):
    print("[INFO] ပုံပေါ်တွင် ရက်စွဲ ထည့်သွင်းနေပါသည်...")
    try:
        # datetime.now() အစား datetime.now(MMT) ကို ပြောင်းသုံးထားပါသည်
        today_date = datetime.now(MMT).strftime("%d.%m.%Y")
        
        img = Image.open(input_path)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
        except IOError:
            font = ImageFont.load_default()
            
        bbox = draw.textbbox((0, 0), today_date, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = ((img.width - text_width) / 2) + 200
        y = img.height - text_height - 50
        
        outline_color = "black"
        outline_width = 3
        for i in range(-outline_width, outline_width+1):
            for j in range(-outline_width, outline_width+1):
                draw.text((x+i, y+j), today_date, font=font, fill=outline_color)
                
        draw.text((x, y), today_date, font=font, fill="white")
        
        img.convert("RGB").save(output_path)
        print(f"[SUCCESS] ရက်စွဲတပ်ပြီးသောပုံကို {output_path} အမည်ဖြင့် သိမ်းလိုက်ပါပြီ။")
    except Exception as e:
        print(f"[ERROR] ပုံပြင်ရာတွင် အမှားရှိနေပါသည်: {e}")

# ==========================================
# အပိုင်း (၂) - YouTube သို့ Video နှင့် Thumbnail တင်ခြင်း
# ==========================================
def upload_video_to_youtube(video_path, thumb_path, title_name, description_text, schedule_time_str):
    print("[INFO] YouTube သို့ ဗီဒီယိုတင်ရန် ပြင်ဆင်နေပါသည်...")
    try:
        with open('client_secrets.json', 'w') as f:
            f.write(os.environ.get('YOUTUBE_CLIENT_SECRETS_DATA', ''))
        with open('token.json', 'w') as f:
            f.write(os.environ.get('YOUTUBE_TOKEN_DATA', ''))
            
        credentials = Credentials.from_authorized_user_file('token.json')
        youtube = build('youtube', 'v3', credentials=credentials)
        
        body = {
            'snippet': {
                'title': title_name,
                'description': description_text,
                'categoryId': '22'
            },
            'status': {
                'privacyStatus': 'private', 
                'publishAt': schedule_time_str
            }
        }
        
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype='video/*')
        
        request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
        response = request.execute()
        video_id = response['id']
        print(f"[SUCCESS] ဗီဒီယို တင်ပြီးပါပြီ။ (Video ID: {video_id})")
        
        youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(thumb_path)).execute()
        print("[SUCCESS] Thumbnail ပုံ တင်ပြီးပါပြီ။")
        
    except Exception as e:
        print(f"[ERROR] YouTube သို့ တင်ရာတွင် အမှားဖြစ်နေပါသည်: {e}")

# ==========================================
# အပိုင်း (၃) - အလုပ်ခွဲခြား စေခိုင်းခြင်း (Main Logic)
# ==========================================
if __name__ == "__main__":
    job_type = sys.argv[1] if len(sys.argv) > 1 else "morning"
    
    base_title = "တရားတော်များ 2026 | (ဘေးရှင်းအန္တရာယ်ကင်းကံပွင့်လာဘ်ပွင့်)| Dhamma Garden"
    video_description = """#dhammachannel #buddhatayarchannel #တရား
တရားတော်များ | တရားတော်များ 2026 | tayar taw myanmar | buddha | (အန္တရာယ်ကင်း၍ ဘုန်းကြီးကံပွင့်လာဘ်ပွင့်စေရန်) | Dhamma Talk | Buddhist Chanting

ဤ တရားတော်များ ၂၀၂၆ အထူးစုစည်းမှုတွင် လူနတ်ဗြဟ္မာ အပေါင်း စိတ်အေးချမ်းသာစွာ နာကြားနိုင်ရန်အတွက် အစွမ်းထက် တရားတော်များကို စနစ်တကျ ပြန်လည် ဆူညံသံများဖယ်ထုတ်ကာ (Remaster) လုပ်၍ တင်ဆက်ထားပါသည်။ ဤ တရားတော်များ သည် ၂၀၂၆ ခုနှစ်အတွင်း ဘေးကင်းအန္တရာယ်ကင်းပြီး ကံပွင့်လာဘ်ပွင့်စေရန် ရည်ရွယ်ထုတ်လွှင့်ခြင်း ဖြစ်ပါသည်။

🔔 တရားတော်များ အမြဲနာကြားနိုင်ရန် Subscribe လုပ်ထားပေးပါ -

Like & Share လုပ်ပေးခြင်းဖြင့် ဓမ္မဒါနကုသိုလ် ပြုနိုင်ပါသည်ခင်ဗျာ။

--------------------------------------------------
ℹ️ COPYRIGHT DISCLAIMER & LEGAL POLICY (Fair Use)
--------------------------------------------------
• This content is created purely for educational, religious, and spiritual improvement purposes. It contains traditional Dhamma teachings aimed at promoting mindfulness, peace, and moral values. This channel strictly adheres to all YouTube Community Guidelines and safety standards regarding digital publishing.

• Under Section 107 of the Copyright Act 1976, allowance is made for "fair use" for purposes such as criticism, comment, news reporting, teaching, scholarship, education, and research. Fair use is a use permitted by copyright statute that might otherwise be infringing. Non-profit, educational, or personal use tips the balance in favor of fair use.

--------------------------------------------------
🎧 AUDIO & VISUAL PRODUCTION (Value Added)
--------------------------------------------------
• Audio Remastering: The original historical audio tracks are sourced from the authorized public domain (dhammadownload.com) for free religious distribution. Our team has performed extensive audio engineering, including professional noise reduction, frequency balancing, and audio restoration, to ensure a pristine and peaceful listening experience.

• Visual Creation & Editing: All background visuals, moving footages, and typography are meticulously custom-created, edited, and synchronized using KineMaster. This production provides high educational and spiritual value, fully transformed from the raw material and strictly compliant with YouTube's Reused/Repetitive Content Policies.

--------------------------------------------------
[ About This Dhamma Talk ]
--------------------------------------------------
Welcome to our Dhamma Talk and Buddhist Chanting collection, dedicated to the Myanmar community worldwide, including those in Thailand, USA, Singapore, Canada, and India. This video features peaceful Myanmar Dhamma talks and powerful Buddhist chanting designed for spiritual growth, daily protection, and mindfulness. This video includes the First Sermon of the Buddha (Dhammacakka) and the Maha Samaya Sutta for Angelic Protection, healing, and spiritual peace.

🏷️ Hashtags:
#တရားတော်များ #တရားတော်များ2026 #တရားတော်များ2025 #တရား‌တော်များ2024 #တရား #2026တရားတော်များ #tayartawmyanmar #buddha #tayartawmyanmar2025 #tayartaw #tayardhamma #buddhatayarchannel
#dhamma #dhammachannel #dhammatalk"""
    
    # ဤနေရာတွင်လည်း datetime.now(MMT) ကို ပြောင်းသုံးထားပါသည်
    today_str = datetime.now(MMT).strftime('%d.%m.%Y')
    final_title = f"{base_title} [{today_str}]"
    
    if job_type == "morning":
        print("--- မနက်ပိုင်း လုပ်ငန်းစဉ် ---")
        add_date_to_thumbnail("m_video_thumb_raw.jpg", "m_video_thumb.jpg")
        
        # Schedule သတ်မှတ်ချိန်ကိုပါ မြန်မာစံတော်ချိန်ဖြင့် အတိအကျ ယူပါသည်
        target_time = datetime.now(MMT).strftime("%Y-%m-%dT05:30:00+06:30")
        
        upload_video_to_youtube("m_video.mp4", "m_video_thumb.jpg", final_title, video_description, target_time)
        
    elif job_type == "evening":
        print("--- ညနေပိုင်း လုပ်ငန်းစဉ် ---")
        add_date_to_thumbnail("e_video_thumb_raw.jpg", "e_video_thumb.jpg")
        
        # Schedule သတ်မှတ်ချိန်ကိုပါ မြန်မာစံတော်ချိန်ဖြင့် အတိအကျ ယူပါသည်
        target_time = datetime.now(MMT).strftime("%Y-%m-%dT18:30:00+06:30")
        
        upload_video_to_youtube("e_video.mp4", "e_video_thumb.jpg", final_title, video_description, target_time)
