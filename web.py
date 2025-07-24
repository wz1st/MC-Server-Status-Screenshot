from flask import Flask, send_file, jsonify
import re, io, base64
from mcstatus import JavaServer
from PIL import Image, ImageDraw, ImageFont

# ===== 配置区 =====
FONT_PATH = "mc.ttf"
FONT_SIZE = 13
FONT_SIZE_BIG = 16
IMG_BASE64 = "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"
TEMPLATE_IMG = io.BytesIO(base64.b64decode(IMG_BASE64))
ICON_SIZE = 46
COLOR_MAP = {
    "0": (0,0,0), "1": (0,0,170), "2": (0,170,0), "3": (0,170,170),
    "4": (170,0,0), "5": (170,0,170), "6": (255,170,0), "7": (170,170,170),
    "8": (85,85,85), "9": (85,85,255), "a": (85,255,85), "b": (85,255,255),
    "c": (255,85,85), "d": (255,85,255), "e": (255,255,85), "f": (255,255,255),
    "r": (180,180,180)
}
# ===================

def parse_motd(motd: str):
    parts = re.split(r"(§[0-9a-fr])", motd.rstrip("§r"))
    res, col = [], COLOR_MAP["r"]
    for p in parts:
        if p.startswith("§") and len(p) == 2:
            col = COLOR_MAP.get(p[1], col)
        elif p:
            res.append((p, col))
    return res

def extract_address(path: str):
    """
    从 /server/mc.qingh.xyz:25565、mc.qingh.xyz、/server/1.2.3.4:1234 等提取 host、port。若无端口，port 返回 None。
    """
    m = re.match(r"^(?:/server/)?(?P<host>[\w\.\-]+)(?::(?P<port>\d+))?$", path)
    if not m:
        raise ValueError(f"无法解析地址：{path!r}")
    h, p = m.group("host"), m.group("port")
    return h, int(p) if p else None

def generate_minecraft_status(host, port=None):
    addr = f"{host}:{port}" if port else host
    try:
        server = JavaServer.lookup(addr)
        status = server.status()
    except :
        return None
    # 处理图标
    if status.icon:
        raw = status.icon.split(",",1)[1]
        icon = Image.open(io.BytesIO(base64.b64decode(raw))).resize((ICON_SIZE, ICON_SIZE))
    else:
        icon = Image.new("RGB", (ICON_SIZE, ICON_SIZE), (100,100,100))
    # 加载模板
    
    img = Image.open(TEMPLATE_IMG).convert("RGBA")
    draw = ImageDraw.Draw(img)
    img.paste(icon, (6,7))
    # 字体
    try:
        f_big = ImageFont.truetype(FONT_PATH, FONT_SIZE_BIG)
        f_small = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except:
        f_big = f_small = ImageFont.load_default()
    # 写 server addr 和 motd
    draw.text((ICON_SIZE+12,10), addr, font=f_big, fill=(219,219,5))
    motd = status.description.get("text") if isinstance(status.description, dict) else str(status.description)
    x, y = ICON_SIZE+12, 10+23
    for txt, col in parse_motd(motd):
        draw.text((x, y), txt, font=f_small, fill=col)
        x += f_small.getlength(txt)
    # 写在线人数
    online = f"{status.players.online}/{status.players.max}"
    w_online = draw.textlength(online, font=f_small)
    draw.text((img.width - w_online - 10, 35), online, font=f_small, fill=(180,180,180))
    # 延迟条
    def draw_ping(lat):
        bars = 5
        if lat < 75: lvl = 5
        elif lat < 150: lvl = 4
        elif lat < 300: lvl = 3
        elif lat < 600: lvl = 2
        elif lat < 1000: lvl = 1
        else: lvl = 0
        for i in range(bars):
            h = 3 + i*3
            y0 = 10 + (15 - h)
            c = (0,255,0) if i < lvl else (50,50,50)
            draw.rectangle([img.width - 35 + i*4, y0, img.width - 35 + i*4 + 2, 10+15], fill=c)
    draw_ping(status.latency)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

app = Flask(__name__)

@app.route("/server/<path:addr>")
def status_img(addr):
    try:
        host, port = extract_address(addr)
    except ValueError:
        return jsonify({"success": False, "message": "地址格式错误"}), 400
    buf = generate_minecraft_status(host, port)
    if buf is None:
        return jsonify({"success": False, "message": "服务器状态获取失败"}), 400
    else:
        return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
