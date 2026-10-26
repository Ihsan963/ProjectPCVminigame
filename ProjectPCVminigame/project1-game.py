import os
import time
import random
import math
import ctypes

import cv2
import numpy as np

SUMBER_VIDEO = 0         
LEBAR, TINGGI = 640, 480  
TAB_H = 36               
NAMA_JENDELA = "Mini Game - Warna Tangan"

LOWER = np.array([105, 120, 50])
UPPER = np.array([130, 255, 255])

MIN_AREA = 800          
BG_PATH = "bg.jpg"       
JEDA_DI_TAB_KAMERA = True

PAPAN_W, PAPAN_H = 100, 14
PAPAN_Y = TINGGI - 40
RADIUS_BOLA = 10
KECEPATAN_AWAL = 300    
KECEPATAN_MAKS = 1000
NAIK_PAPAN = 1.12
NAIK_DINDING = 1.0
NYAWA_AWAL = 1

NAMA_TAB = ["1  Game", "2  Kamera & Mask"]


def deteksi_tangan(frame_bgr, lower, upper):
    blur = cv2.GaussianBlur(frame_bgr, (7, 7), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    kontur, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not kontur:
        return None, None, mask, None
    terbesar = max(kontur, key=cv2.contourArea)
    if cv2.contourArea(terbesar) < MIN_AREA:
        return None, None, mask, None

    m = cv2.moments(terbesar)
    cx = int(m["m10"] / m["m00"])
    cy = int(m["m01"] / m["m00"])
    return cx, cy, mask, cv2.boundingRect(terbesar)


def kalibrasi_warna(frame_bgr, ukuran=40):
    h, w = frame_bgr.shape[:2]
    x0, y0 = w // 2 - ukuran // 2, h // 2 - ukuran // 2
    roi = frame_bgr[y0:y0 + ukuran, x0:x0 + ukuran]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV).reshape(-1, 3)
    hh, ss, vv = np.median(hsv, axis=0).astype(int)
    lower = np.array([max(hh - 15, 0), max(ss - 70, 50), max(vv - 70, 40)])
    upper = np.array([min(hh + 15, 179), 255, 255])
    return lower, upper


class Game:

    def __init__(self):
        self.reset()

    def reset(self):
        self.skor = 0
        self.nyawa = NYAWA_AWAL
        self.papan_x = LEBAR / 2
        self.status = "siap"       
        self.vx = self.vy = 0.0
        self.reset_bola()

    def reset_bola(self):
        self.bx = LEBAR / 2
        self.by = 80
        self.kecepatan = KECEPATAN_AWAL if self.skor == 0 else max(
            KECEPATAN_AWAL, self.kecepatan_terakhir() * 0.8)
        sudut = math.radians(random.choice([-1, 1]) * random.uniform(20, 50))
        self.vx = self.kecepatan * math.sin(sudut)
        self.vy = self.kecepatan * math.cos(sudut)   

    def kecepatan_terakhir(self):
        return math.hypot(self.vx, self.vy)

    def gerak_papan(self, target_x):
        if target_x is None:
            return
        self.papan_x = 0.6 * self.papan_x + 0.4 * target_x
        setengah = PAPAN_W / 2
        self.papan_x = min(max(self.papan_x, setengah), LEBAR - setengah)

    def update(self, dt):
        if self.status != "main":
            return
        self.bx += self.vx * dt
        self.by += self.vy * dt

        if self.bx - RADIUS_BOLA < 0:
            self.bx = RADIUS_BOLA
            self.vx = abs(self.vx)
        elif self.bx + RADIUS_BOLA > LEBAR:
            self.bx = LEBAR - RADIUS_BOLA
            self.vx = -abs(self.vx)
        if self.by - RADIUS_BOLA < 0:
            self.by = RADIUS_BOLA
            self.vy = abs(self.vy)

        atas_papan = PAPAN_Y
        if (self.vy > 0
                and atas_papan - RADIUS_BOLA <= self.by <= atas_papan + PAPAN_H
                and abs(self.bx - self.papan_x) <= PAPAN_W / 2 + RADIUS_BOLA):
            self.skor += 1
            self.kecepatan = min(self.kecepatan_terakhir() * NAIK_PAPAN, KECEPATAN_MAKS)

            offset = (self.bx - self.papan_x) / (PAPAN_W / 2)      
            offset = max(-1, min(1, offset))
            sudut = offset * math.radians(60)
            self.vx = self.kecepatan * math.sin(sudut)
            self.vy = -self.kecepatan * math.cos(sudut)
            self.by = atas_papan - RADIUS_BOLA

        if self.by - RADIUS_BOLA > TINGGI:
            self.nyawa -= 1
            if self.nyawa <= 0:
                self.status = "selesai"
            else:
                self.reset_bola()

def teks(img, s, pos, skala=0.7, warna=(255, 255, 255), tebal=2):
    cv2.putText(img, s, pos, cv2.FONT_HERSHEY_SIMPLEX, skala, (0, 0, 0), tebal + 2, cv2.LINE_AA)
    cv2.putText(img, s, pos, cv2.FONT_HERSHEY_SIMPLEX, skala, warna, tebal, cv2.LINE_AA)


def teks_tengah(img, s, y, skala=0.9, warna=(255, 255, 255)):
    lebar = img.shape[1]
    (w, _), _ = cv2.getTextSize(s, cv2.FONT_HERSHEY_SIMPLEX, skala, 2)
    teks(img, s, ((lebar - w) // 2, y), skala, warna)


def buat_background():
    if os.path.exists(BG_PATH):
        bg = cv2.imread(BG_PATH)
        if bg is not None:
            bg = cv2.resize(bg, (LEBAR, TINGGI))
            return (bg * 0.6).astype(np.uint8)      
    atas = np.array([60, 35, 25], dtype=np.float64)   
    bawah = np.array([20, 12, 10], dtype=np.float64)
    t = np.linspace(0, 1, TINGGI)[:, None, None]
    grad = atas * (1 - t) + bawah * t
    return np.repeat(grad, LEBAR, axis=1).astype(np.uint8)


def gambar_game(bg, game, tangan_terdeteksi):
    tampilan = bg.copy()

    x1 = int(game.papan_x - PAPAN_W / 2)
    x2 = int(game.papan_x + PAPAN_W / 2)
    cv2.rectangle(tampilan, (x1, PAPAN_Y), (x2, PAPAN_Y + PAPAN_H), (255, 200, 0), -1)
    cv2.rectangle(tampilan, (x1, PAPAN_Y), (x2, PAPAN_Y + PAPAN_H), (255, 255, 255), 2)
 
    cv2.circle(tampilan, (int(game.bx), int(game.by)), RADIUS_BOLA, (0, 80, 255), -1)
    cv2.circle(tampilan, (int(game.bx), int(game.by)), RADIUS_BOLA, (255, 255, 255), 2)

    teks(tampilan, f"Skor: {game.skor}", (10, 28))

    if game.status == "siap":
        teks_tengah(tampilan, "TEKAN SPASI UNTUK MULAI", 170)
    elif game.status == "selesai":
        teks_tengah(tampilan, "GAME OVER", 180, 1.4, (80, 80, 255))
        teks_tengah(tampilan, f"Skor akhir: {game.skor}", 225)
        teks_tengah(tampilan, "SPASI = main lagi   Q = keluar", 265, 0.6)
    elif not tangan_terdeteksi:
        teks_tengah(tampilan, "Tangan tidak terdeteksi", 120, 0.7, (80, 200, 255))
    return tampilan


def gambar_kamera(frame, mask, cx, cy, bbox, lower, upper, game):
    half_w, half_h = LEBAR // 2, TINGGI // 2
    skala = half_w / LEBAR

    kam = frame.copy()
    cv2.rectangle(kam, (LEBAR // 2 - 20, TINGGI // 2 - 20),
                  (LEBAR // 2 + 20, TINGGI // 2 + 20), (0, 255, 255), 2)
    if bbox is not None:
        x, y, w, h = bbox
        cv2.rectangle(kam, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(kam, (cx, cy), 10, (0, 0, 255), -1)
    kam = cv2.resize(kam, (half_w, half_h))

    msk = cv2.cvtColor(cv2.resize(mask, (half_w, half_h)), cv2.COLOR_GRAY2BGR)
    teks(kam, "Kamera", (8, 22), 0.55)
    teks(msk, "Mask (putih = terdeteksi)", (8, 22), 0.5)

    atas = np.hstack([kam, msk])
    panel = np.full((TINGGI - half_h, LEBAR, 3), (35, 28, 28), np.uint8)

    if cx is not None:
        teks(panel, f"TANGAN TERDETEKSI   x={cx}  y={cy}", (14, 32), 0.65, (120, 255, 120))
    else:
        teks(panel, "TANGAN TIDAK TERDETEKSI", (14, 32), 0.65, (90, 90, 255))
    return np.vstack([atas, panel])


def tambah_tab(konten, tab_aktif):
    bar = np.full((TAB_H, LEBAR, 3), (28, 22, 22), np.uint8)
    lebar_tab = LEBAR // len(NAMA_TAB)
    for i, nama in enumerate(NAMA_TAB):
        x0, x1 = i * lebar_tab, (i + 1) * lebar_tab
        aktif = (i == tab_aktif)
        warna_bg = (110, 70, 30) if aktif else (50, 42, 42)
        cv2.rectangle(bar, (x0 + 2, 4), (x1 - 2, TAB_H), warna_bg, -1)
        if aktif:
            cv2.rectangle(bar, (x0 + 2, 4), (x1 - 2, 8), (255, 200, 0), -1)
        (w, _), _ = cv2.getTextSize(nama, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.putText(bar, nama, (x0 + (lebar_tab - w) // 2, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (255, 255, 255) if aktif else (170, 170, 170), 1, cv2.LINE_AA)
    return np.vstack([bar, konten])


def tab_dari_klik(x, y):
    if 0 <= y < TAB_H and 0 <= x < LEBAR:
        return min(x // (LEBAR // len(NAMA_TAB)), len(NAMA_TAB) - 1)
    return None

def ukuran_layar():
    try:                                  
        ctypes.windll.user32.SetProcessDPIAware()
        u = ctypes.windll.user32
        return u.GetSystemMetrics(0), u.GetSystemMetrics(1)
    except Exception:                    
        return 1920, 1080

def main():
    global LOWER, UPPER
    cap = cv2.VideoCapture(SUMBER_VIDEO)
    if not cap.isOpened():
        print("Kamera / video tidak bisa dibuka. Cek SUMBER_VIDEO.")
        return

    game = Game()
    bg = buat_background()
    state = {"tab": 0}

    def saat_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            t = tab_dari_klik(x, y)
            if t is not None:
                state["tab"] = t

    cv2.namedWindow(NAMA_JENDELA)
    cv2.setMouseCallback(NAMA_JENDELA, saat_mouse)

    waktu_lalu = time.time()
    print("Mini game dimulai. Spasi=mulai, TAB=ganti tab, C=kalibrasi, Q=keluar")
    
    sw, sh = ukuran_layar()
    lw = sw // 2                     
    lh = int(lw * TINGGI / LEBAR)    

    cv2.namedWindow("Game", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Game", lw, lh)
    cv2.moveWindow("Game", 0, 0)                 

    cv2.namedWindow("Kamera & Mask", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Kamera & Mask", lw, lh)
    cv2.moveWindow("Kamera & Mask", lw, 0)       

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)                      
        frame = cv2.resize(frame, (LEBAR, TINGGI))

        cx, cy, mask, bbox = deteksi_tangan(frame, LOWER, UPPER)
        game.gerak_papan(cx)

        sekarang = time.time()
        dt = min(sekarang - waktu_lalu, 0.05)
        waktu_lalu = sekarang
        if not (JEDA_DI_TAB_KAMERA and state["tab"] == 1):
            game.update(dt)

        cv2.imshow("Game", gambar_game(bg, game, cx is not None))
        cv2.imshow("Kamera & Mask", gambar_kamera(frame, mask, cx, cy, bbox, LOWER, UPPER, game))

        tombol = cv2.waitKey(1) & 0xFF
        if tombol == ord("q"):
            break
        elif tombol == 9:                                
            state["tab"] = 1 - state["tab"]
        elif tombol == ord("1"):
            state["tab"] = 0
        elif tombol == ord("2"):
            state["tab"] = 1
        elif tombol == ord(" "):
            if game.status in ("siap", "selesai"):
                game.reset()
                game.status = "main"
                state["tab"] = 0
        elif tombol == ord("c"):
            LOWER, UPPER = kalibrasi_warna(frame)
            print("Kalibrasi baru -> LOWER:", LOWER, "UPPER:", UPPER)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
