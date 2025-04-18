import smbus
import time
import threading
import math

# Inisialisasi alamat I2C dan register MPU6050
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
GYRO_CONFIG = 0x1B  # Register untuk konfigurasi gyro
GYRO_ZOUT_H = 0x47
GYRO_ZOUT_L = 0x48

# Inisialisasi untuk akeselerometer
ACCEL_CONFIG = 0x1C
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F

# Konfigurasi bus I2C
bus = smbus.SMBus(1)

# Variable global untuk menyimpan sudut rotasi z
rotation_angle_z = 0.0

# Variable global untuk menyimpan nilai offset yang dihasilkan dari kalibrasi
gyro_offset_z = 0.0

# Variabel global untuk menyimpan offset kalibrasi akselerometer
accel_offset_x = 0
accel_offset_y = 0
accel_offset_z = 0


def read_word_2c(addr):
    # Membaca nilai 2-byte dari register MPU6050
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
    val = (high << 8) + low
    if val >= 0x8000:
        return -((65535 - val) + 1)
    else:
        return val

def set_gyro_scale(scale):
    # Mengatur faktor skala (scale factor) gyro
    # Konfigurasi bit 3-4 di register GYRO_CONFIG
    bus.write_byte_data(MPU6050_ADDR, GYRO_CONFIG, scale << 3)
    
# def set_accel_fsr(fsr):
#     # Mengatur Full Scale Range (FSR) akselerometer
#     bus.write_byte_data(MPU6050_ADDR, ACCEL_CONFIG, fsr << 3)

def calibrate_gyro():
    # Mengkalibrasi gyro untuk menghitung nilai offset
    global gyro_offset_z
    gyro_data = []
    for _ in range(1000):  # Ambil 1000 bacaan untuk kalibrasi
        gyro_data.append(read_word_2c(GYRO_ZOUT_H))
        time.sleep(0.001)  # Delay 0.001 detik
    gyro_offset_z = sum(gyro_data) / len(gyro_data)

def get_pitch_and_roll():
    # Membaca data akselerometer dari MPU6050 dan menghitung pitch dan roll
    accel_x = read_word_2c(ACCEL_XOUT_H) - accel_offset_x
    accel_y = read_word_2c(ACCEL_YOUT_H) - accel_offset_y
    accel_z = read_word_2c(ACCEL_ZOUT_H) - accel_offset_z
    
    # Mengonversi nilai akselerometer menjadi g
    accel_scale = 16384.0  # Faktor skala untuk akselerometer (per dokumentasi MPU6050)
    accel_x_scaled = accel_x / accel_scale
    accel_y_scaled = accel_y / accel_scale
    accel_z_scaled = accel_z / accel_scale
    
    # Menghitung pitch dan roll dalam radian
    pitch = math.atan2(accel_x_scaled, math.sqrt(accel_y_scaled**2 + accel_z_scaled**2))
    roll = math.atan2(accel_y_scaled, math.sqrt(accel_x_scaled**2 + accel_z_scaled**2))
    
    # Mengonversi pitch dan roll dari radian ke derajat
    pitch = math.degrees(pitch)
    roll = math.degrees(roll)
    
    return pitch, roll

def get_rotation_angle():
    # Membaca data gyro z dari MPU6050 dan menghitung rotasi sudut z
    gyro_z = read_word_2c(GYRO_ZOUT_H)
    # Mengonversi ke satuan sudut (misalnya, radian)
    # Anda mungkin perlu mengkalibrasi data gyro sesuai dengan kebutuhan aplikasi Anda
    gyro_scale = 131 # Faktor skala untuk gyro z (per dokumentasi MPU6050)
    gyro_z_scaled = (gyro_z - gyro_offset_z) / gyro_scale
    return gyro_z_scaled

def apply_lowpass_filter(current_value, new_value):
    # Menggunakan filter eksponensial untuk menerapkan low-pass filter
    alpha = 0.98
    return alpha * new_value + (1 - alpha) * current_value

def integrate_gyro_data(dt):
    global rotation_angle_z
    current_angle = 0.0  # Nilai awal sudut rotasi
    while True:
        rotation_rate = get_rotation_angle()
        if rotation_rate is not None:  # Pastikan ada data yang diterima
            current_angle = apply_lowpass_filter(current_angle, rotation_rate * dt)
            rotation_angle_z += current_angle
        time.sleep(dt)

# def integrate_gyro_data(dt):
#     global rotation_angle_z
#     while True:
#         rotation_angle_z += get_rotation_angle() * dt  # Integrasi data gyro z
#         time.sleep(dt)

def continuous_measurement():
    global rotation_angle_z
    print("yaw,pitch,roll")
    while True:
        pitch, roll = get_pitch_and_roll()
        print(rotation_angle_z)
        #print(rotation_angle_z,",", pitch, ",", roll)
        time.sleep(0.1) 

# Inisialisasi MPU6050
bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)

# Konfigurasi gyro (misalnya, faktor skala 2000 DPS)
set_gyro_scale(0b00)  # 0b11 adalah untuk faktor skala 2000 DPS
# set_accel_fsr(0)  # 0 untuk skala +-2g

print("Kalibrasi...")
# Kalibrasi gyro
calibrate_gyro()
print("Kalibrasi selesai")

# Buat thread untuk mengukur sudut rotasi z secara kontinu
dt = 0.1  # Interval waktu untuk pengukuran (misalnya, 0.01 detik)
gyro_thread = threading.Thread(target=integrate_gyro_data, args=(dt,))
gyro_thread.daemon = True
gyro_thread.start()

# Mulai thread untuk mencetak sudut rotasi z secara kontinu
print_thread = threading.Thread(target=continuous_measurement)
print_thread.daemon = True
print_thread.start()

# Tetapkan program berjalan agar thread-thread di atas bisa bekerja
while True:
    time.sleep(1)
