import RPi.GPIO as GPIO
import time

# Tentukan pin GPIO untuk trigger dan echo
TRIG_PIN = 17
ECHO_PIN = 18

# Konstanta untuk lowpass filter
ALPHA = 0.9

# Inisialisasi variabel untuk lowpass filter
filtered_distance = 0

def setup():
    # Set mode GPIO ke BCM
    GPIO.setmode(GPIO.BCM)

    # Atur pin sebagai OUTPUT (TRIG) dan INPUT (ECHO)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)

def measure_distance():
    # Bersihkan trigger pin sebelum pengukuran
    GPIO.output(TRIG_PIN, GPIO.LOW)
    time.sleep(0.1)

    # Kirim sinyal ultrasonik dengan menyalakan trigger pin
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, GPIO.LOW)

    # Catat waktu awal ketika sinyal dikirim
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()

    # Catat waktu saat sinyal diterima kembali
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    # Hitung durasi sinyal perjalanan
    pulse_duration = pulse_end - pulse_start

    # Hitung jarak berdasarkan durasi sinyal dan kecepatan suara
    speed_of_sound = 34300  # Kecepatan suara dalam cm/s
    distance = (pulse_duration * speed_of_sound) / 2

    return distance

def lowpass_filter(value):
    global filtered_distance
    filtered_distance = (1 - ALPHA) * filtered_distance + ALPHA * value
    return filtered_distance

def cleanup():
    # Matikan GPIO
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        setup()

        while True:
            # Ukur jarak
            distance = measure_distance()

            # Terapkan lowpass filter
            filtered_distance = lowpass_filter(distance)

            # Cetak hasil yang difilter
            print(f"Jarak (Difilter): {filtered_distance:.2f} cm")

            # Tunggu sejenak sebelum mengukur lagi
            time.sleep(0.01)

    except KeyboardInterrupt:
        # Tangkap KeyboardInterrupt (Ctrl+C) untuk membersihkan GPIO
        cleanup()
