from sensor import SHT20
from time import sleep


sht = SHT20(1, 0x40)

if sht:
    def get_temperature():
        """Reads and returns the temperature in Celsius."""
        try:
            _, t = sht.all()
            return t.C
        except OSError:
            print("Sensor error. Check connections.")
            return None  # Indicate an error

    def get_humidity():
        """Reads and returns the relative humidity."""
        try:
            h, _ = sht.all()
            return h.RH
        except OSError:
            print("Sensor error. Check connections.")
            return None  # Indicate an error


 
def test_temp_humid():
    temp = get_temperature() 
    humidity = get_humidity() - 9

    if temp is not None and humidity is not None:
        print(f"Temperature: {temp:.2f} °C")
        print(f"Humidity: {humidity:.2f} %")
    else:
        print("Failed to read sensor data.")


if __name__ == "__main__":
    while True:  # Run the test continuously
        test_temp_humid()
        sleep(2)