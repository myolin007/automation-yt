import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# =========================================================================
# အပိုင်း (၁) - ပုံပေါ်တွင် နေ့စဉ် ရက်စွဲအမှန်ကို အလိုအလျောက် ရေးပေးမည့် လုပ်ငန်းစဉ်
# =========================================================================
def add_date_to_thumbnail(input_path, output_path):
    print("[INFO] ပုံပေါ်တွင် ရက်စွဲ ထည့်သွင်းခြင်း လုပ်ငန်းစတင်ပါပြီ...")
    try:
        # လက်ရှိစက်၏ ရက်စွဲကို ယူသည် (ဥပမာ - 25.05.2026)
        today_date = datetime.now().strftime("%d.%m.%Y")
        
        # မူရင်း Thumbnail ပုံကို ဖွင့်သည်
        img = Image.open(input_path)
        draw = ImageDraw.Draw(img)
        
        # ဖောင့်သတ်မှတ်သည် (GitHub Linux စက်ထဲတွင် အသင့်ရှိသော ဖောင့်တစ်ခုကို သုံးထားသည်)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
        except IOError:
            font = ImageFont.load_default()
            
        # စာသား၏ အရွယ်အစားကို တိုင်းတာပြီး နေရာချသည်
        bbox = draw.textbbox((0, 0), today_date, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # အစ်ကို လိုချင်သလို ညာဘက်သို့ ၂၀၀ တိုး၊ အပေါ်သို့ ၁၀၀ တင်ထားသည်
        x = ((img.width - text_width) / 2) + 200
        y = img.height - text_height - 100
        
        # စာသား ပိုထင်ရှားစေရန် အနက်ရောင် Outline (အနားသတ်) အရင်ဆွဲသည်
        for i in range(-4, 5):
            for j in range(-4, 5):
                draw.text((x+i, y+j), today_date, font=font, fill="black")
                
        # အဖြူရောင် စာသားအစစ်ကို အပေါ်မှ ထပ်ရေးသည်
        draw.text((x, y), today_date, font=font, fill="white")
        
        # ပုံကို RGBA မှ RGB ပြောင်း၍ JPEG အဖြစ် သိမ်းသည် (Error မတက်စေရန်)
        img.convert("RGB").save(output_path)
        print(f"[SUCCESS] ရက်စွဲထည့်ပြီးသား Thumbnail ကို {output_path} အဖြစ် သိမ်းဆည်းပြီးပါပြီ။")
    except Exception as e:
        print(f"[ERROR] ပုံပြင်ရာတွင် အမှားပြပြင်ခဲ့သည်: {e}")

# =========================================================================
# အပိုင်း (၂) - YouTube API ကို သုံး၍ ဗီဒီယိုအား Schedule စနစ်ဖြင့် Upload တင်ခြင်း
# =========================================================================
def upload_video_to_youtube(video_path, thumb_path, title_name, schedule_time_str):
    print("[INFO] YouTube API ကို အသုံးပြု၍ ဗီဒီယိုတင်ရန် ပြင်ဆင်နေပါသည်...")
    try:
        # GitHub Secrets ထဲက ပို့ပေးလိုက်တဲ့ စာသားတွေကနေ ဖိုင်ပြန်ဆောက်ပြီး သုံးခြင်း
        # ၎င်းနည်းလမ်းကြောင့် ၇ ရက် သက်တမ်းကုန်ဆုံးခြင်း လုံးဝ မရှိတော့ပါ
        with open('client_secrets.json', 'w') as f:
            f.write(os.environ.get('YOUTUBE_CLIENT_SECRETS_DATA'))
        with open('token.json', 'w') as f:
            f.write(os.environ.get('YOUTUBE_TOKEN_DATA'))
            
        # Token ဖိုင်ကို သုံးပြီး Google Credential သတ်မှတ်ခြင်း
        credentials = Credentials.from_authorized_user_file('token.json')
        youtube = build('youtube', 'v3', credentials=credentials)
        
        # ဗီဒီယို၏ အချက်အလက် (Title, Description, Schedule Time) များ သတ်မှတ်ခြင်း
        body = {
            'snippet': {
                'title': title_name,
                'description': f'တရားတော်များ နေ့စဉ် နာယူနိုင်ရန် တင်ပေးထားပါသည်။ ရက်စွဲ - {datetime.now().strftime("%d.%m.%Y")}',
                'categoryId': '22' # 22 ဆိုသည်မှာ People & Blogs ဖြစ်သည်
            },
            'status': {
                'privacyStatus': 'private', # Schedule စနစ်သုံးရန် အရင်ဆုံး Private ထားရမည်
                'publishAt': schedule_time_str # ဤနေရာတွင် Schedule အချိန် ဝင်သွားမည်
            }
        }
        
        # ဗီဒီယိုဖိုင်အား လမ်းကြောင်းပြ၍ ဆွဲတင်ရန် ပြင်ဆင်ခြင်း
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype='video/*')
        
        # YouTube ပေါ်သို့ ဗီဒီယို စတင် Upload တင်ခြင်း
        print("[INFO] ဗီဒီယိုအား YouTube ဆာဗာသို့ ပို့ဆောင်နေပါသည်...")
        request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
        response = request.execute()
        video_id = response['id']
        print(f"[SUCCESS] ဗီဒီယို တင်ပြီးပါပြီ။ Video ID: {video_id}")
        
        # တင်ပြီးသွားသော ဗီဒီယိုပေါ်သို့ ရက်စွဲတပ်ထားသော Thumbnail ပုံအား လှမ်းတင်ခြင်း
        print("[INFO] Thumbnail ပုံအား တွဲတင်နေပါသည်...")
        youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(thumb_path)).execute()
        print("[SUCCESS] Thumbnail အောင်မြင်စွာ တင်ပြီးပါပြီ။")
        
    except Exception as e:
        print(f"[ERROR] YouTube သို့ ဗီဒီယိုတင်ရာတွင် အမှားဖြစ်ခဲ့သည်: {e}")

# =========================================================================
# အပိုင်း (၃) - မနက်/ညနေ အချိန်နှင့် အလုပ်ဇယား ခွဲခြားခြင်း ကဏ္ဍ
# =========================================================================
if __name__ == "__main__":
    job_type = sys.argv[1] if len(sys.argv) > 1 else "morning"
    
    # ---------------------------------------------------------------------
    # ⚠️ အချိန်ပြောင်းလိုလျှင် ပြင်ရမည့်နေရာ (မနက်ပိုင်း)
    # ---------------------------------------------------------------------
    if job_type == "morning":
        print("--- မနက်ပိုင်း လုပ်ငန်းစဉ် စတင်နေပါသည် ---")
        add_date_to_thumbnail("m_video_thumb_raw.jpg", "m_video_thumb.jpg")
        add_date_to_thumbnail("m_live_thumb_raw.jpg", "m_live_thumb.jpg")
        
        # ဗီဒီယိုခေါင်းစဉ် ပေးရန်နေရာ
        video_title = f"မနက်ခင်း နာယူရန် တရားတော်များ - {datetime.now().strftime('%d.%m.%Y')}"
        
        # 💡 ဗီဒီယို Schedule ပြသလိုသည့် အချိန်ကို ဤနေရာတွင် ပြင်ပါ (လက်ရှိ မနက် ၀၅:၃၀)
        target_schedule = datetime.now().strftime("%Y-%m-%dT05:30:00+06:30")
        
        upload_video_to_youtube("m_video.mp4", "m_video_thumb.jpg", video_title, target_schedule)
        
    # ---------------------------------------------------------------------
    # ⚠️ အချိန်ပြောင်းလိုလျှင် ပြင်ရမည့်နေရာ (ညနေပိုင်း)
    # ---------------------------------------------------------------------
    elif job_type == "evening":
        print("--- ညနေပိုင်း လုပ်ငန်းစဉ် စတင်နေပါသည် ---")
        add_date_to_thumbnail("e_video_thumb_raw.jpg", "e_video_thumb.jpg")
        add_date_to_thumbnail("e_live_thumb_raw.jpg", "e_live_thumb.jpg")
        
        # ဗီဒီယိုခေါင်းစဉ် ပေးရန်နေရာ
        video_title = f"ညနေခင်း နာယူရန် တရားတော်များ - {datetime.now().strftime('%d.%m.%Y')}"
        
        # 💡 ဗီဒီယို Schedule ပြသလိုသည့် အချိန်ကို ဤနေရာတွင် ပြင်ပါ (လက်ရှိ ညနေ ၁၈:၃၀)
        target_schedule = datetime.now().strftime("%Y-%m-%dT18:30:00+06:30")
        
        upload_video_to_youtube("e_video.mp4", "e_video_thumb.jpg", video_title, target_schedule)
