import smbus            
from time import sleep, time
import math
import RPi.GPIO as GPIO
import sys
 
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47
bus = smbus.SMBus(1)
 
def MPU_Init():
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
    bus.write_byte_data(Device_Address, CONFIG, 0)
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)
 
def read_raw_data(addr):
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
        value = ((high << 8) | low)
        if(value > 32768):
                value = value - 65536
        return value
 
 
def dist(a, b):
    return math.sqrt((a*a) + (b*b))
 
 
def get_y_rotation(x, y, z):
    radians = math.atan2(y, dist(x, z))
    return -(radians * (180.0 / math.pi))
  
def get_x_rotation(x, y, z):
    radians = math.atan2(x, dist(y, z))
    return -(radians * (180.0 / math.pi))

def get_z_rotation(x, y, z):
    radians = math.atan2(z, dist(x, z))
    return -(radians * (180.0 / math.pi))

if __name__ == "__main__":
         
    z_angle = 0
    preinterval = 0
    Device_Address = 0x68   
    MPU_Init()
     
    print("Reading MPU6050...")
    try:
        while True:
            acc_x = read_raw_data(ACCEL_XOUT_H)
            acc_y = read_raw_data(ACCEL_YOUT_H)
            acc_z = read_raw_data(ACCEL_ZOUT_H)
            
            gyro_x = read_raw_data(GYRO_XOUT_H)
            gyro_y = read_raw_data(GYRO_YOUT_H)
            gyro_z = read_raw_data(GYRO_ZOUT_H)
            
            gyro_x_scaled = gyro_x/131.0
            gyro_y_scaled = gyro_y/131.0
            gyro_z_scaled = gyro_z/131.0
             
            acclX_scaled = acc_x * .000061 * 9.80665
            acclY_scaled = acc_y * .000061 * 9.80665
            acclZ_scaled = acc_z * .000061 * 9.80665
             
            x_angle = get_x_rotation(acclX_scaled, acclY_scaled, acclZ_scaled)
            y_angle = get_y_rotation(acclX_scaled, acclY_scaled, acclZ_scaled)
            
            t_new = time()
            dt = (t_new - preinterval)
            preinterval = t_new
            
            z_angle += gyro_z*dt 
            
            print("gyro z: ", gyro_z, " angle z : ", z_angle)
            #print("X rotation: ", x_angle," Y rotation: ",y_angle, " Z rotation: ",z_angle)
            sleep(0.05)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(e)
        sys.exit(0)