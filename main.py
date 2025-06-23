import logging
from datetime import datetime
import requests
import base64
import json
import os
from pydub import AudioSegment

from notion import create_idea, create_task

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 开启日志输出
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 设置你希望保存文件的目录
SAVE_DIR = "saved_voice"
os.makedirs(SAVE_DIR, exist_ok=True)


# 处理语音消息
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("start handle_voice ============================")
    user = update.effective_user.first_name or "unknown_user"
    voice = update.message.voice

    # 获取语音文件信息并下载
    file = await context.bot.get_file(voice.file_id)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user}_{timestamp}.ogg"
    filepath = os.path.join(SAVE_DIR, filename)

    await file.download_to_drive(filepath)
    print(f"✅ 已保存语音文件: {filepath}")

    # 对语音进行识别，获得文字信息
    message = convert_ogg_to_text(filepath)

    save_message(message)

    # 合成语音回复
    reply_text = message

    await update.message.reply_text(reply_text)


# 调用外部语音识别服务，将语音转为文字
def convert_ogg_to_text(filepath):
    return main_convert_ogg_to_text_google(filepath)


def save_message(text):
    if text.startswith("灵感"):
        create_idea(
            content=text[2:],
            ptype="灵感",
            create_date=datetime.today().strftime('%Y-%m-%d')
        )
    elif text.startswith("任务"):
        create_task(
            name=text[2:],
            status="Not Started",
            # tags=["API", "Documentation"],
            # catalog_group="catalog_group",
            # catalog="catalog",
            # due_date=datetime.today().strftime('%Y-%m-%d'),
        )
    else:
        create_idea(
            content=text[2:],
            ptype="未识别",
            create_date=datetime.today().strftime('%Y-%m-%d')
        )

# google 语音转文字服务
def main_convert_ogg_to_text_google(filepath):
    api_key = 'AIzaSyCvl-xbsY1yXrQ92I90CSN4wdkngRujs6s'

    # 1. 加载音频并转为 base64 编码
    with open(os.path.join(filepath), "rb") as audio_file:
        audio_content = base64.b64encode(audio_file.read()).decode("utf-8")

    # 2. 构造请求体
    url = f'https://speech.googleapis.com/v1/speech:recognize?key={api_key}'

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "config": {
            "encoding": "OGG_OPUS",  # 必须指定 OGG_OPUS
            "sampleRateHertz": 48000,  # Telegram 通常是 48000 Hz
            "languageCode": "zh-CN",  # 普通话
            "enableAutomaticPunctuation": True  # 自动加标点
        },
        "audio": {
            "content": audio_content
        }
    }

    # 3. 发送 POST 请求
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # 4. 处理结果
    if response.status_code == 200:
        result = response.json()
        if "results" in result:
            for r in result['results']:
                print("识别结果:", r['alternatives'][0]['transcript'])
                return r['alternatives'][0]['transcript']
        else:
            print("没有识别结果")
    else:
        print("请求失败:", response.status_code)
        print(response.text)


# 百度语音转文字服务
def main_convert_ogg_to_text_baidu(filepath):
    # ========== Step 0: 用户参数 ==========
    API_KEY = '0z66mckoqABo8n4WgJMC3ZIV'
    SECRET_KEY = '1NVP1bo9H4dIf456cefSnfbtghh42U2y'
    OGG_FILE = filepath
    WAV_FILE = 'voice.wav'

    # 转换音频
    convert_ogg_to_wav_baidu(OGG_FILE, WAV_FILE)

    # 获取token
    token = get_token_baidu(API_KEY, SECRET_KEY)

    # 调用识别接口
    result = recognize_baidu(WAV_FILE, token)

    # 输出结果
    if result.get("err_no") == 0:
        print("识别结果：", result["result"][0])
    else:
        print("识别失败：", result)

    # 可选：删除中间文件
    os.remove(WAV_FILE)


# ========== Step 1: 转换 OGG 到 WAV ==========
def convert_ogg_to_wav_baidu(ogg_path, wav_path):
    audio = AudioSegment.from_ogg(ogg_path)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)  # 16kHz, mono, 16bit
    audio.export(wav_path, format='wav')


# ========== Step 2: 获取 access_token ==========
def get_token_baidu(api_key, secret_key):
    token_url = 'https://openapi.baidu.com/oauth/2.0/token'
    params = {
        'grant_type': 'client_credentials',
        'client_id': api_key,
        'client_secret': secret_key
    }
    res = requests.get(token_url, params=params)
    return res.json().get("access_token")


# ========== Step 3: 调用百度语音识别 API ==========
def recognize_baidu(wav_path, token):
    with open(wav_path, 'rb') as f:
        speech_data = f.read()

    speech_base64 = base64.b64encode(speech_data).decode('utf-8')
    length = len(speech_data)

    data = {
        "format": "wav",
        "rate": 16000,
        "channel": 1,
        "cuid": "telegram-bot-device",
        "token": token,
        "speech": speech_base64,
        "len": length,
        "dev_pid": 1537  # 普通话输入法模型
    }

    url = "https://vop.baidu.com/server_api"
    headers = {"Content-Type": "application/json"}
    res = requests.post(url, headers=headers, data=json.dumps(data))
    return res.json()


# 启动 bot
def main():
    TELEGRAM_BOT_TOKEN = "8033385245:AAEy7yv2HAAhOhpoJxVz1ZN2ISd5VIP3PwQ"
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    print("✅ Bot started...")
    app.run_polling()


if __name__ == '__main__':
    main()
