import RPi.GPIO as GPIO
import time

# Tentukan pin GPIO untuk masing-masing sensor
SENSORS = {
    "Sensor_1": {"TRIG": 17, "ECHO": 18},
    #"Sensor_2": {"TRIG": 27, "ECHO": 22},
    #"Sensor_3": {"TRIG": 23, "ECHO": 24},
    #"Sensor_4": {"TRIG": 10, "ECHO": 9}
}

# Konstanta untuk lowpass filter
ALPHA = 0.9

def setup():
    # Set mode GPIO ke BCM
    GPIO.setmode(GPIO.BCM)

    # Atur pin sebagai OUTPUT (TRIG) dan INPUT (ECHO) untuk setiap sensor
    for sensor, pins in SENSORS.items():
        GPIO.setup(pins["TRIG"], GPIO.OUT)
        GPIO.setup(pins["ECHO"], GPIO.IN)

def measure_distance(trig_pin, echo_pin):
    # Bersihkan trigger pin sebelum pengukuran
    GPIO.output(trig_pin, GPIO.LOW)
    time.sleep(0.1)

    # Kirim sinyal ultrasonik dengan menyalakan trigger pin
    GPIO.output(trig_pin, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trig_pin, GPIO.LOW)

    # Catat waktu awal ketika sinyal dikirim
    while GPIO.input(echo_pin) == 0:
        pulse_start = time.time()

    # Catat waktu saat sinyal diterima kembali
    while GPIO.input(echo_pin) == 1:
        pulse_end = time.time()

    # Hitung durasi sinyal perjalanan
    pulse_duration = pulse_end - pulse_start

    # Hitung jarak berdasarkan durasi sinyal dan kecepatan suara
    speed_of_sound = 34300  # Kecepatan suara dalam cm/s
    distance = (pulse_duration * speed_of_sound) / 2

    return distance

def lowpass_filter(current_value, previous_value):
    # Implementasi digital lowpass filter
    filtered_value = (1 - ALPHA) * previous_value + ALPHA * current_value
    return filtered_value

def cleanup():
    # Matikan GPIO
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        setup()

        # Nilai awal untuk digital lowpass filter
        filtered_distances = {sensor: 0 for sensor in SENSORS}

        while True:
            # Ukur jarak untuk setiap sensor
            for sensor, pins in SENSORS.items():
                distance = measure_distance(pins["TRIG"], pins["ECHO"])
                filtered_distances[sensor] = lowpass_filter(distance, filtered_distances[sensor])
                print(f"{filtered_distances[sensor]:.2f}")

            # Tunggu sejenak sebelum mengukur lagi
            time.sleep(0.01)

    except KeyboardInterrupt:
        # Tangkap KeyboardInterrupt (Ctrl+C) untuk membersihkan GPIO
        cleanup()
