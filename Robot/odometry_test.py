import RPi.GPIO as GPIO
import time

# Tentukan konstanta untuk konversi
keliling_roda_cm = 8.6
jumlah_lubang_encoder = 20
faktor_konversi = keliling_roda_cm / jumlah_lubang_encoder

# Tentukan pin GPIO yang digunakan
sensor_pin = 17  # Ganti dengan pin GPIO yang Anda gunakan

# Inisialisasi GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Variabel untuk menghitung odometri
count = 0
prev_state = GPIO.input(sensor_pin)

try:
    print("Odometri Motor DC (Tekan Ctrl+C untuk keluar)")
    while True:
        # Pemeriksaan polling nilai pin GPIO
        current_state = GPIO.input(sensor_pin)

        # Deteksi perubahan pada pin
        if current_state != prev_state:
            count += 1
            jarak_cm = count * faktor_konversi
            print(f"Jarak yang Ditempuh: {jarak_cm:.2f} cm")
            prev_state = current_state

        # Tunggu selama 1 detik sebelum mengukur kembali
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nProgram dihentikan")
    GPIO.cleanup()
