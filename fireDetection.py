import cv2, datetime, threading, winsound, requests, os, time, shutil, serial, json
import numpy as np
from flask import Flask, Response, render_template, jsonify, redirect, request
from tensorflow.keras.preprocessing.image import load_img
from keras.models import load_model
import re
from urllib.parse import urlparse


# === Paths and Constants ===
MODEL_PATH   = r"D:\VstudioCode\fire_model_SEP1.keras"
CASCADE_PATH = r"D:\VstudioCode\fFIREhaarcascade1.xml"
SAVE_DIR     = r"D:\FIRE_MODULE_CNN_16_12_2024\capture_images_fire\Detected_Fire_VS"
MODE_FILE    = "mode_config.json"
# IMG_SIZE = (100, 100)
IMG_SIZE = (256,256)
FRAME_W, FRAME_H = 640, 480
SERIAL_PORT = "COM6"
ip= None
# === Flask Setup ===
app = Flask(__name__)
app.secret_key = 'fire_detection_secret_key'
os.makedirs(SAVE_DIR, exist_ok=True)

# === Globals ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)

model = load_model(MODEL_PATH)
cascade = cv2.CascadeClassifier(CASCADE_PATH)

alert_message = "System Normal"
alert_lock = threading.Lock()
fire_sent = False
fire_detected = False
UNO_FIRE_URL = None
streaming = False
serial_connected = False
ser = None

# === Mode Storage ===
def load_mode():
    if os.path.exists(MODE_FILE):
        with open(MODE_FILE, 'r') as f:
            return json.load(f).get("mode", "AUTO")
    return "AUTO"

def save_mode(mode):
    with open(MODE_FILE, 'w') as f:
        json.dump({"mode": mode}, f)

system_mode = load_mode()

# === Beep + Arduino Trigger ===
def _beep():
    global fire_sent
    if not fire_sent:
        try:
            if UNO_FIRE_URL:
                requests.get(UNO_FIRE_URL, timeout=2)
                print(f"IP: {UNO_FIRE_URL}")
                fire_sent = True
        except Exception:
            pass
        winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS | winsound.SND_ASYNC)

# === Serial Listener Thread ===
def serial_listener():
    global ser, alert_message, serial_connected, system_mode, fire_sent
    try:
        ser = serial.Serial(SERIAL_PORT, 115200, timeout=2)
        serial_connected = True
        print(f"[Python] Serial connected on {SERIAL_PORT}")
        time.sleep(2)

        while True:
            try:
                line = ser.readline().decode(errors='ignore').strip()
                if line.startswith("MESSAGE:"):
                    msg = line.split("MESSAGE:")[1].strip()
                    with alert_lock:
                        alert_message = msg
                        print("♾️  Arduino:", msg)
                        if "Reset" in msg:
                            alert_message = "🔄 FAS System Reset...!"
                            fire_sent= False
                        elif "Fire" in msg:  # ✅ only beep/send when fire is actually reporte
                            _beep()

                elif line.startswith("CONFIG:"):
                    mode = line.split("CONFIG:")[1].strip()
                    if mode in ["CNN Mode Selected", "Auto Mode Selected"]:
                        system_mode = mode
                        with alert_lock:
                            alert_message = mode
                        print(f"System Mode set to {system_mode}")
                        save_mode(mode)
                        fire_sent= False
                        
                  

            except Exception:
                pass

    except Exception:
        pass
    time.sleep(1)

# === Fire Classifier ===
def identify_fire(image_path):
    img = load_img(image_path, target_size=IMG_SIZE)
    img_array = np.expand_dims(np.asarray(img), axis=0)
    prediction = model.predict(img_array)
    label_index = np.argmax(prediction)
    confidence = round(100 * np.max(prediction[0]), 2)
    return label_index, confidence

# === Camera Frame Generator ===
def gen_frames():
    global cap, fire_detected, alert_message, system_mode
    while streaming:
        # serial_listener()
        ret, frame = cap.read()
        if not ret:
            continue

        fires = cascade.detectMultiScale(frame, 1.1, 7)
        if len(fires) > 0:
            for (x, y, w, h) in fires:
                try:
                    timestamp = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    text1 = f"Fire{timestamp}"
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.5
                    color = (0, 255, 0)
                    thickness = 1
                    (text_width, text_height), _ = cv2.getTextSize(timestamp, font, font_scale, thickness)
                    text_x = frame.shape[1] - text_width - 8
                    text_y = frame.shape[0] - 7
                    cv2.putText(frame, text1, (text_x, text_y), font, font_scale, color, thickness)

                    filename = f"Fire_{len(os.listdir(SAVE_DIR))}.jpg"
                    filepath = os.path.join(SAVE_DIR, filename)
                    cv2.imwrite(filepath, frame)

                    label, conf = identify_fire(filepath)
                    box_color = (0, 0, 255) if label == 1 else (0, 255, 0)
                    label_text = f"FIRE: {conf}%" if label == 1 else f"SAFE: {conf}%"
                    cv2.rectangle(frame, (x, y), (x+w, y+h), box_color, 2)
                    cv2.putText(frame, label_text, (x, y-10), font, 0.6, box_color, 2)

                    shutil.copy(filepath, os.path.join('static', 'last_fire.jpg'))

                    if label == 1 and conf >= 80:
                        fire_detected = True
                        _beep()
                        with alert_lock:
                            alert_message = "🔥 Fire Detected!"
                except Exception as e:
                    print(f"🔥 Detection error: {e}")

        ret, buffer = cv2.imencode('.jpg', cv2.resize(frame, (FRAME_W, FRAME_H)))
        if not ret:
            continue
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# === Flask Routes ===
@app.route('/')
def index():
    return render_template('index.html', mode=system_mode, alert_message=alert_message)

@app.route("/get_alert")
def get_alert():
    with alert_lock:
        # print(f"🔔http:// alert_send- {alert_message}")
        return jsonify({"alert": alert_message})

@app.route('/video_feed')
def video_feed():
    if streaming:
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(b"", mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start', methods=['POST'])
def start():
    global streaming
    streaming = True
    print("✅ Camera stream started.")
    return redirect('/')

@app.route('/stop', methods=['POST'])
def stop():
    global streaming, fire_sent
    streaming = False
    fire_sent = False
    print("🛑 Camera stream stopped.")
    return redirect('/')


def sanitize_ip(raw: str) -> str:
    """
    Accepts things like 'http://192.168.1.5', '192.168.1.5/', ' https://192.168.1.5  '
    and returns just '192.168.1.5'.
    """
    if not raw:
        return None
    raw = raw.strip()
    if raw.startswith("http://") or raw.startswith("https://"):
        parsed = urlparse(raw)
        host = parsed.netloc or parsed.path  # netloc holds host for normal urls, path for weird ones
    else:
        # strip any accidental leading slashes
        host = raw.lstrip("/")

    # remove trailing path if present
    host = host.split("/")[0]

    # very light validation (IPv4)
    if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host):
        return None
    return host

def arduino_url(ip: str, path: str) -> str:
    """Build a proper Arduino URL."""
    ip = sanitize_ip(ip)
    if not ip:
        return None
    if not path.startswith("/"):
        path = "/" + path
    return f"http://{ip}{path}"

@app.route("/update_ip", methods=["POST"])
def update_ip():
    global UNO_FIRE_URL, ip
    data = request.get_json()
    raw = data.get("ip")
    cleaned = sanitize_ip(raw)
    if not cleaned:
        return jsonify({"status": "error", "message": "Invalid IP"}), 400

    ip = cleaned                         # store raw IP only (e.g., '192.168.1.5')
    UNO_FIRE_URL = arduino_url(ip, "/fire")
    print(f"✅ UNO_FIRE_URL updated to: {UNO_FIRE_URL}")
    return jsonify({"status": "success", "url": UNO_FIRE_URL})



@app.route('/reset_fire', methods=['POST'])
def reset_fire():
    global alert_message, fire_detected, fire_sent, ip
    try:
        reset_url = arduino_url(ip, "/reset_fire") if ip else None
        if reset_url:
            try:
                resp = requests.get(reset_url, timeout=3)
                if resp.status_code == 200:
                    print("✅ Flask + Arduino system reset successful.")
                else:
                    print(f"⚠️ Arduino reset failed, status: {resp.status_code}")
            except Exception as e:
                print(f"⚠️ Could not contact Arduino for reset: {e}")
        else:
            print("⚠️ Arduino IP not set yet. Please update IP first.")

        # Clear saved fire images
        for f in os.listdir(SAVE_DIR):
            if f.lower().endswith(".jpg"):
                try:
                    os.remove(os.path.join(SAVE_DIR, f))
                except Exception:
                    pass

        # Replace last fire with healthy image
        healthy_img = os.path.join("static", "system_healthy.png")
        last_fire = os.path.join("static", "last_fire.jpg")
        if os.path.exists(healthy_img):
            try:
                shutil.copy(healthy_img, last_fire)
            except Exception:
                pass

        # Reset local vars
        cap.grab()
        fire_sent = False
        with alert_lock:
            alert_message = "System Normal"
        fire_detected = False
        print("✅ Flask system reset done.")
    except Exception as e:
        print(f"⚠️ Reset route error: {e}")

    return redirect("/")


@app.route("/exit", methods=["POST"])
def exit_app():
    def _bye():
        time.sleep(1)
        cap.release()
        cv2.destroyAllWindows()
        os._exit(0)
    threading.Thread(target=_bye, daemon=True).start()
    return "Shutting down..."

@app.route("/set_mode", methods=["POST"])
def set_mode():
    global system_mode, UNO_FIRE_URL, ip
    data = request.get_json()
    mode = data.get("mode")
    if mode in ["AUTO", "CNN"]:
        system_mode = mode
        save_mode(mode)
        endpoint = "/auto_mode" if mode == "AUTO" else "/cnn_mode"
        url = arduino_url(ip, endpoint)
        if url:
            try:
                requests.get(url, timeout=2)
                print(f"→ {mode} Mode Activated on Arduino")
            except Exception as e:
                print(f"⚠️ {mode} Mode Activation Failed: {e}")
        return jsonify({"status": "success", "mode": system_mode})
    return jsonify({"status": "error", "message": "Invalid mode"}), 400

# === Start Flask App ===
if __name__ == "__main__":
    threading.Thread(target=serial_listener, daemon=True).start()
    app.run(debug=False, threaded=True)




# import cv2, datetime, threading, winsound, requests, os, time, shutil, serial
# import numpy as np
# from flask import Flask, Response, render_template, jsonify, redirect, request
# from tensorflow.keras.preprocessing.image import load_img
# from keras.models import load_model

# # === Paths and Constants ===
# MODEL_PATH   = r"D:\VstudioCode\CNN552025best_2_model.keras"
# CASCADE_PATH = r"D:\finalFIREhaarcascade.xml"
# SAVE_DIR     = r"D:\FIRE_MODULE_CNN_16_12_2024\capture_images_fire\Detected_Fire_VS"
# IMG_SIZE = (100, 100)
# FRAME_W, FRAME_H = 640, 480
# SERIAL_PORT = "COM4"

# # === Flask Setup ===
# app = Flask(__name__)
# app.secret_key = 'fire_detection_secret_key'
# os.makedirs(SAVE_DIR, exist_ok=True)
# fire_sent = False
# # === Globals ===
# cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_W)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)

# model = load_model(MODEL_PATH)
# cascade = cv2.CascadeClassifier(CASCADE_PATH)

# alert_message = "System Normal"
# alert_lock = threading.Lock()
# fire_detected = False
# UNO_FIRE_URL = None
# streaming = False
# serial_connected = False
# ser = None
# system_mode = "AUTO"  # or "CNN"

# # === Beep + Arduino Trigger ===

# def _beep():
#     global fire_sent
#     if not fire_sent:
#         try:
#             if UNO_FIRE_URL:
#                 requests.get(UNO_FIRE_URL, timeout=2)
#                 print(f"IP: {UNO_FIRE_URL}")
#                 fire_sent = True
#         except Exception:
#             pass
#         winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS | winsound.SND_ASYNC)

# # === Serial Listener Thread ===
# def serial_listener():
#     global ser, alert_message, serial_connected, system_mode, fire_sent
#     try:
#         ser = serial.Serial(SERIAL_PORT, 115200, timeout=2)
#         serial_connected = True
#         print(f"[Python] Serial connected on {SERIAL_PORT}")
#         time.sleep(2)

#         while True:
#             try:
#                 line = ser.readline().decode(errors='ignore').strip()
#                 if line.startswith("MESSAGE:"):
#                     msg = line.split("MESSAGE:")[1].strip()
#                     with alert_lock:
#                         alert_message = msg
#                         print("🔔 Arduino:", msg)
#                         if "Reset" in msg:
#                             alert_message = "🔄 FAS System Reset...!"
#                             fire_sent= False
#                         _beep()

#                 elif line.startswith("CONFIG:"):
#                     mode = line.split("CONFIG:")[1].strip()
#                     if mode in ["AUTO", "CNN"]:
#                         system_mode = mode
#                         fire_sent= False
#                         print(f"System Mode set to {system_mode}")
                        

#             except Exception as e:
#                 pass
#                 # time.sleep(1)
                
#     except Exception as e:
#         pass
#         # print("⚠️ Serial error:", e)

# # === Fire Classifier ===
# def identify_fire(image_path):
#     img = load_img(image_path, target_size=IMG_SIZE)
#     img_array = np.expand_dims(np.asarray(img), axis=0)
#     prediction = model.predict(img_array)
#     label_index = np.argmax(prediction)
#     confidence = round(100 * np.max(prediction[0]), 2)
#     return label_index, confidence

# # === Camera Frame Generator ===
# def gen_frames():
#     global cap, fire_detected, alert_message, system_mode
#     while streaming:
#         serial_listener()
#         ret, frame = cap.read()
        
#         if not ret:
#             continue

#         fires = cascade.detectMultiScale(frame, 1.1, 7)
#         if len(fires) > 0:
#             for (x, y, w, h) in fires:
#                 try:
#                     timestamp = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
#                     text1 = f"🔥 {timestamp}"
#                     font = cv2.FONT_HERSHEY_SIMPLEX
#                     font_scale = 0.5
#                     color = (0, 255, 0)
#                     thickness = 1
#                     (text_width, text_height), _ = cv2.getTextSize(timestamp, font, font_scale, thickness)
#                     text_x = frame.shape[1] - text_width - 8
#                     text_y = frame.shape[0] - 7
#                     cv2.putText(frame, text1, (text_x, text_y), font, font_scale, color, thickness)

#                     filename = f"Fire_{len(os.listdir(SAVE_DIR))}.jpg"
#                     filepath = os.path.join(SAVE_DIR, filename)
#                     cv2.imwrite(filepath, frame)

#                     label, conf = identify_fire(filepath)
#                     box_color = (0, 0, 255) if label == 1 else (0, 255, 0)
#                     label_text = f"FIRE: {conf}%" if label == 1 else f"SAFE: {conf}%"
#                     cv2.rectangle(frame, (x, y), (x+w, y+h), box_color, 2)
#                     cv2.putText(frame, label_text, (x, y-10), font, 0.6, box_color, 2)

#                     shutil.copy(filepath, os.path.join('static', 'last_fire.jpg'))

#                     # FIRE ACTION
#                     if label == 1 and conf >= 80:
#                         if system_mode == "AUTO":
#                             fire_detected = True
#                             _beep()
#                             with alert_lock:
#                                 alert_message = "🔥 Fire Detected!"
#                         elif system_mode == "CNN":
#                             fire_detected = True
#                             _beep()
#                             with alert_lock:
#                                 alert_message = "🔥 Fire Detected!"
#                 except Exception as e:
#                     print(f"🔥 Detection error: {e}")

#         ret, buffer = cv2.imencode('.jpg', cv2.resize(frame, (FRAME_W, FRAME_H)))
#         if not ret:
#             continue
#         yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# # === Flask Routes ===
# @app.route('/')
# def index():
#     return render_template('index.html', mode=system_mode, alert_message=alert_message)


# @app.route("/get_alert")
# def get_alert():
#     with alert_lock:
#         return jsonify({"alert": alert_message})

# @app.route('/video_feed')
# def video_feed():
#     if streaming:
#         return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
#     else:
#         return Response(b"", mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/start', methods=['POST'])
# def start():
#     global streaming
#     streaming = True
#     print("✅ Camera stream started.")
#     return redirect('/')

# @app.route('/stop', methods=['POST'])
# def stop():
#     global streaming,fire_sent
#     streaming = False
#     fire_sent= False
#     print("🛑 Camera stream stopped.")
#     return redirect('/')

# @app.route("/update_ip", methods=["POST"])
# def update_ip():
#     global UNO_FIRE_URL
#     data = request.get_json()
#     ip = data.get("ip")
#     if ip:
#         UNO_FIRE_URL = f"http://{ip}/fire"
#         print(f"✅ UNO_FIRE_URL updated to: {UNO_FIRE_URL}")
#         return jsonify({"status": "success", "url": UNO_FIRE_URL}), 200
#     else:
#         return jsonify({"status": "error", "message": "IP not provided"}), 400

# @app.route('/reset_fire', methods=['POST'])
# def reset_fire():
#     global alert_message, fire_detected, fire_sent
#     try:
#         for f in os.listdir(SAVE_DIR):
#             if f.lower().endswith(".jpg"):
#                 os.remove(os.path.join(SAVE_DIR, f))

#         healthy_img = os.path.join("static", "system_healthy.png")
#         last_fire = os.path.join("static", "last_fire.jpg")
#         if os.path.exists(healthy_img):
#             shutil.copy(healthy_img, last_fire)

#         cap.grab()
#         fire_sent= False
#         with alert_lock:
#             alert_message = "System Normal"
#         fire_detected = False
#         print("✅ System reset.")
#     except Exception as e:
#         print(f"⚠️ Reset error: {e}")
#     return redirect("/")

# @app.route("/exit", methods=["POST"])
# def exit_app():
#     def _bye():
#         time.sleep(1)
#         cap.release()
#         cv2.destroyAllWindows()
#         os._exit(0)
#     threading.Thread(target=_bye, daemon=True).start()
#     return "Shutting down..."

# @app.route("/set_mode", methods=["POST"])
# def set_mode():
#     global system_mode, UNO_FIRE_URL
#     data = request.get_json()
#     mode = data.get("mode")

#     if mode == "AUTO":
#         system_mode = "AUTO"
#         if UNO_FIRE_URL:
#             try:
#                 r = requests.get(UNO_FIRE_URL.replace("/fire", "/auto_mode"), timeout=2)
#                 print("→ AUTO Mode Activated")
#             except Exception as e:
#                 print(f"⚠️ AUTO Mode Activated Failed: {e}")
#     elif mode == "CNN":
#         system_mode = "CNN"
#         if UNO_FIRE_URL:
#             try:
#                 r = requests.get(UNO_FIRE_URL.replace("/fire", "/cnn_mode"), timeout=2)
#                 print("→ CNN Mode Activated")
#             except Exception as e:
#                 print(f"⚠️ CNN Mode Activated Failed: {e}")
#     else:
#         return jsonify({"status": "error", "message": "Invalid mode"}), 400

#     return jsonify({"status": "success", "mode": system_mode})

# # === Start App ===
# if __name__ == "__main__":
#     threading.Thread(daemon=True).start()
#     app.run(debug=True, threaded=True)


# # === Start Flask App ===
# if __name__ == "__main__":
#     threading.Thread(target=serial_listener, daemon=True).start()
#     app.run(debug=True, threaded=True)





# import cv2, datetime, threading, winsound, requests, os, time, shutil, serial, serial.tools.list_ports
# import numpy as np
# from flask import Flask, Response, render_template, jsonify, redirect, request
# from tensorflow.keras.preprocessing.image import load_img
# from keras.models import load_model

# # === Paths and Constants ===
# MODEL_PATH   = r"D:\VstudioCode\CNN552025best_2_model.keras"
# CASCADE_PATH = r"D:\finalFIREhaarcascade.xml"
# SAVE_DIR     = r"D:\FIRE_MODULE_CNN_16_12_2024\capture_images_fire\Detected_Fire_VS"
# FRAME_W, FRAME_H = 640, 480
# IMG_SIZE = (100, 100)
# SERIAL_PORT = "COM4"

# # === Flask Setup ===
# app = Flask(__name__)
# app.secret_key = 'fire_detection_secret_key'
# os.makedirs(SAVE_DIR, exist_ok=True)

# # === Globals ===
# cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_W)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)

# model = load_model(MODEL_PATH)
# cascade = cv2.CascadeClassifier(CASCADE_PATH)

# alert_message = "System Normal"
# alert_lock = threading.Lock()
# fire_detected = False
# UNO_FIRE_URL = None
# streaming = False
# serial_connected = False
# ser = None


# # === Beep + Arduino Trigger ===
# def _beep():
#     try:
#         if UNO_FIRE_URL:
#             requests.get(UNO_FIRE_URL, timeout=1)
#     except Exception:
#         pass
#     winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS | winsound.SND_ASYNC)


# # === Serial Listener Thread ===
# def serial_listener():
#     global ser, alert_message, serial_connected
#     try:
#         ser = serial.Serial(SERIAL_PORT, 115200, timeout=2)
#         serial_connected = True
#         print(f"[Python] Serial port {SERIAL_PORT} opened successfully.")
#         time.sleep(2)  # Arduino boot delay

#         while True:
#             try:
#                 line = ser.readline().decode(errors='ignore').strip()
#                 if line.startswith("MESSAGE:"):
#                     with alert_lock:
#                         alert_message = line.split("MESSAGE:")[1].strip()
#                         print("🚨 Received from Arduino:", alert_message)
#                         _beep()

#             except Exception as e:
#                 pass
#                 time.sleep(1)

#     except Exception as e:
#         pass


# # === Fire Classifier ===
# def identify_fire(image_path):
#     img = load_img(image_path, target_size=IMG_SIZE)
#     img_array = np.expand_dims(np.asarray(img), axis=0)
#     prediction = model.predict(img_array)
#     label_index = np.argmax(prediction)
#     confidence = round(100 * np.max(prediction[0]), 2)
#     return label_index, confidence

# # === Camera Frame Generator ===
# def gen_frames():
#     global cap, fire_detected, alert_message
#     while streaming:
#         serial_listener()
#         ret, frame = cap.read()
#         if not ret:
#             continue

#         fires = cascade.detectMultiScale(frame, 1.1, 7)
#         if len(fires) > 0:
#             for (x, y, w, h) in fires:
#                 try:
#                     timestamp = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
#                     text1 = f"🔥 {timestamp}"
#                     font = cv2.FONT_HERSHEY_SIMPLEX
#                     font_scale = 0.5
#                     color = (0, 255, 0)
#                     thickness = 1
#                     (text_width, text_height), _ = cv2.getTextSize(timestamp, font, font_scale, thickness)
#                     text_x = frame.shape[1] - text_width - 8
#                     text_y = frame.shape[0] - 7
#                     cv2.putText(frame, text1, (text_x, text_y), font, font_scale, color, thickness)

#                     filename = f"Fire_{len(os.listdir(SAVE_DIR))}.jpg"
#                     filepath = os.path.join(SAVE_DIR, filename)
#                     cv2.imwrite(filepath, frame)

#                     label, conf = identify_fire(filepath)
#                     box_color = (0, 0, 255) if label == 1 else (0, 255, 0)
#                     label_text = f"FIRE: {conf}%" if label == 1 else f"SAFE: {conf}%"
#                     cv2.rectangle(frame, (x, y), (x+w, y+h), box_color, 2)
#                     cv2.putText(frame, label_text, (x, y-10), font, 0.6, box_color, 2)

#                     shutil.copy(filepath, os.path.join('static', 'last_fire.jpg'))

#                     if label == 1 and conf >= 80:
#                         fire_detected = True
#                         _beep()
#                         with alert_lock:
#                             alert_message = "🔥 Fire Detected!"
#                     # else:
#                     #     with alert_lock:
#                     #         alert_message = "Safe - Low Confidence"
#                 except Exception as e:
#                     print(f"🔥 Detection error: {e}")

#         ret, buffer = cv2.imencode('.jpg', cv2.resize(frame, (FRAME_W, FRAME_H)))
#         if not ret:
#             continue
#         yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# # === Routes ===
# @app.route("/")
# def index():
#     return render_template("index.html", alert=alert_message)

# @app.route("/get_alert")
# def get_alert():
#     with alert_lock:
#         print("📤 Sending to HTML:", alert_message)
#         return jsonify({"alert": alert_message})

# @app.route('/video_feed')
# def video_feed():
#     if streaming:
#         return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
#     else:
#         return Response(b"", mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/start', methods=['POST'])
# def start():
#     global streaming
#     streaming = True
#     print("✅ Streaming started.")
#     return redirect('/')

# @app.route('/stop', methods=['POST'])
# def stop():
#     global streaming
#     streaming = False
#     print("🛑 Streaming stopped.")
#     return redirect('/')

# @app.route("/update_ip", methods=["POST"])
# def update_ip():
#     global UNO_FIRE_URL
#     data = request.get_json()
#     ip = data.get("ip")
#     if ip:
#         UNO_FIRE_URL = f"http://{ip}/fire"
#         print(f"✅ UNO_FIRE_URL updated to: {UNO_FIRE_URL}")
#         return jsonify({"status": "success", "url": UNO_FIRE_URL}), 200
#     else:
#         return jsonify({"status": "error", "message": "IP not provided"}), 400

# @app.route('/reset_fire', methods=['POST'])
# def reset_fire():
#     global alert_message, fire_detected
#     try:
#         for f in os.listdir(SAVE_DIR):
#             if f.lower().endswith(".jpg"):
#                 os.remove(os.path.join(SAVE_DIR, f))

#         healthy_img = os.path.join("static", "system_healthy.png")
#         last_fire = os.path.join("static", "last_fire.jpg")
#         if os.path.exists(healthy_img):
#             shutil.copy(healthy_img, last_fire)

#         cap.grab()
#         with alert_lock:
#             alert_message = "System Normal"
#         fire_detected = False
#         print("✅ System reset.")
#     except Exception as e:
#         print(f"⚠️ Reset error: {e}")
#     return redirect("/")

# @app.route("/exit", methods=["POST"])
# def exit_app():
#     def _bye():
#         time.sleep(1)
#         cap.release()
#         cv2.destroyAllWindows()
#         os._exit(0)
#     threading.Thread(target=_bye, daemon=True).start()
#     return "Shutting down..."

# # === Start App ===
# if __name__ == "__main__":
#     threading.Thread(daemon=True).start()
#     app.run(debug=True, threaded=True)




























# import cv2, datetime, threading, winsound, requests, os, time, shutil
# import numpy as np
# from flask import Flask, Response, render_template, jsonify, redirect, request
# from tensorflow.keras.preprocessing.image import load_img
# from keras.models import load_model
# from threading import Lock

# # === Paths and Constants ===
# MODEL_PATH   = r"D:\VstudioCode\CNN552025best_2_model.keras"
# CASCADE_PATH = r"D:\finalFIREhaarcascade.xml"
# SAVE_DIR     = r"D:\FIRE_MODULE_CNN_16_12_2024\capture_images_fire\Detected_Fire_VS"
# FRAME_W, FRAME_H = 640, 480
# IMG_SIZE = (100, 100)

# # === Flask App Setup ===
# app = Flask(__name__, static_url_path='/static')
# app.secret_key = 'fire_detection_secret_key'
# os.makedirs(SAVE_DIR, exist_ok=True)

# # === Global State ===
# alert_message = "System Normal"
# fire_detected = False
# alert_lock = Lock()
# streaming = False
# model = load_model(MODEL_PATH)
# cascade = cv2.CascadeClassifier(CASCADE_PATH)
# UNO_FIRE_URL = None
# # === Camera Setup ===
# cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_W)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)

# # === Alarm + UNO Trigger ===
# # Fire Beep Function
# def _beep():
#     try:
#         requests.get(UNO_FIRE_URL, timeout=1)
#     except Exception:
#         pass
#     winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS | winsound.SND_ASYNC)


# # === CNN Prediction ===
# def identify_fire(image_path):
#     img = load_img(image_path, target_size=IMG_SIZE)
#     img_array = np.expand_dims(np.asarray(img), axis=0)
#     prediction = model.predict(img_array)
#     label_index = np.argmax(prediction)
#     confidence = round(100 * np.max(prediction[0]), 2)
#     return label_index, confidence

# # === Streaming Frames ===
# def gen_frames():
#     global cap, alert_message, fire_detected
#     while streaming:
#         ret, frame = cap.read()
#         if not ret:
#             continue

#         fires = cascade.detectMultiScale(frame, 1.1, 7)
#         if len(fires) == 0:
#             if not fire_detected:
#                 with alert_lock:
#                     alert_message = "System Normal"
#         else:
#             for (x, y, w, h) in fires:
#                 try:
#                     # Timestamp watermark
#                     timestamp = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
#                     text1 = f"🔥 {timestamp}"
#                     font = cv2.FONT_HERSHEY_SIMPLEX
#                     font_scale = 0.5
#                     color = (0, 255, 0)
#                     thickness = 1
#                     (text_width, text_height), _ = cv2.getTextSize(timestamp, font, font_scale, thickness)
#                     text_x = frame.shape[1] - text_width - 8
#                     text_y = frame.shape[0] - 7
#                     cv2.putText(frame, text1, (text_x, text_y), font, font_scale, color, thickness)

#                     # Save fire image
#                     filename = f"Fire_{len(os.listdir(SAVE_DIR))}.jpg"
#                     filepath = os.path.join(SAVE_DIR, filename)
#                     cv2.imwrite(filepath, frame)

#                     # CNN prediction
#                     label, conf = identify_fire(filepath)
#                     box_color = (0, 0, 255) if label == 1 else (0, 255, 0)
#                     label_text = f"FIRE: {conf}%" if label == 1 else f"SAFE: {conf}%"
#                     cv2.rectangle(frame, (x, y), (x+w, y+h), box_color, 2)
#                     cv2.putText(frame, label_text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

#                     # Save for UI display
#                     shutil.copy(filepath, os.path.join('static', 'last_fire.jpg'))

#                     if label == 1 and conf >= 80:
#                         fire_detected = True
#                         _beep()
#                         with alert_lock:
#                             alert_message = "🔥 Fire Detected!"
#                     else:
#                         with alert_lock:
#                             alert_message = "Safe - Low Confidence"

#                 except Exception as e:
#                     print(f"🔥 Error during detection: {e}")

#         ret, buffer = cv2.imencode('.jpg', cv2.resize(frame, (FRAME_W, FRAME_H)))
#         if not ret:
#             continue
#         yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')



# # === Flask Routes ===
# @app.route("/")
# def index():
#     return render_template("index.html", alert_message=alert_message)

# @app.route("/get_alert")
# def get_alert():
#     return jsonify({"alert": alert_message})

# @app.route('/video_feed')
# def video_feed():
#     if streaming:
#         return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
#     else:
#         return Response(b"", mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/start', methods=['POST'])
# def start():
#     global streaming
#     streaming = True
#     print("[✔] Streaming started.")
#     return redirect('/')

# @app.route('/stop', methods=['POST'])
# def stop():
#     global streaming
#     streaming = False
#     print("[🛑] Streaming stopped.")
#     return redirect('/')

# @app.route("/update_ip", methods=["POST"])
# def update_ip():
#     global UNO_FIRE_URL
#     data = request.get_json()
#     ip = data.get("ip")

#     if ip:
#         UNO_FIRE_URL = f"http://{ip}/fire"
#         print(f"[✔] UNO_FIRE_URL updated to: {UNO_FIRE_URL}")
#         return jsonify({"status": "success", "url": UNO_FIRE_URL}), 200
#     else:
#         return jsonify({"status": "error", "message": "IP not provided"}), 400

# @app.route("/arduino_alert", methods=["POST"])
# def arduino_alert():
#     global alert_message
#     data = request.form.get("alert")
#     if data:
#         alert_message = data
#         print(f"[🔥 ALERT RECEIVED] {alert_message}")
#         return jsonify({"status": "success", "message": alert_message}), 200
#     else:
#         return jsonify({"status": "error", "message": "No alert received"}), 400
    
# @app.route('/reset_fire', methods=['POST'])
# def reset_fire():
#     global alert_message, fire_detected
#     try:
#         for f in os.listdir(SAVE_DIR):
#             if f.lower().endswith(".jpg"):
#                 os.remove(os.path.join(SAVE_DIR, f))

#         healthy_img = os.path.join("static", "system_healthy.png")
#         last_fire = os.path.join("static", "last_fire.jpg")
#         if os.path.exists(healthy_img):
#             shutil.copy(healthy_img, last_fire)

#         cap.grab()
#         with alert_lock:
#             alert_message = "System Normal"
#         fire_detected = False

#         print("✅ Fire images cleared. System healthy image loaded.")
#     except Exception as e:
#         print(f"⚠️ Reset error: {e}")
#     return redirect("/")
    
# @app.route("/exit", methods=["POST"])
# def exit_app():
#     def _bye():
#         time.sleep(1)
#         cap.release()
#         cv2.destroyAllWindows()
#         os._exit(0)
#     threading.Thread(target=_bye, daemon=True).start() serial_listener()
#     return "Shutting down…"

# # === Run the App ===
# if __name__ == "__main__":
#     # server_IP = input("🔧 Enter Of UNO-IP: ").strip()
#     # UNO_FIRE_URL = f"http://{server_IP}/fire"
#     app.run(debug=True, threaded=True)
# # else:
# #     server_IP = "0.0.0.0"  # Placeholder for reloader; won't be used
# #     UNO_FIRE_URL = f"http://{server_IP}/fire"







