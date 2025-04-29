#!/farm_app/bin/activate  
import time
import datetime
import logging
import os
import signal
import sys
import subprocess
import schedule
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Float, String, Identity, Boolean
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from prog_files import controls, light_cam, temp_humid_sensor
import RPi.GPIO as GPIO

load_dotenv()

# Configuration (move these to a config file or env variables)
TARGET_TEMP = float(os.getenv("TARGET_TEMP"))
TEMP_THRESHOLD = float(os.getenv("TEMP_THRESHOLD"))
TARGET_HUMID = float(os.getenv("TARGET_HUMID"))
HUMID_THRESHOLD = float(os.getenv("HUMID_THRESHOLD"))
AIR_CYCLE_INTERVAL = int(os.getenv("AIR_CYCLE_INTERVAL"))  # 1 hour
COLONIZATION_AIR_CYCLE_INTERVAL = int(os.getenv("COLONIZATION_AIR_CYCLE_INTERVAL"))  # 12 hours
BACKUP_SCRIPT = os.getenv("SCRIPT_LOCATION")
LOG_LOCATION = os.getenv("LOG_LOCATION")

# Database setup
engine = create_engine(os.getenv("DB"))

class Base(DeclarativeBase):
    pass

class Mushroomdb(Base):
    __tablename__ = 'farm_info'
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    heat_mat_state = Column(Boolean, unique=False, default=True)
    mister_state = Column(Boolean, unique=False, default=True)
    pump_state = Column(Boolean, unique=False, default=True)
    inline_fan_state = Column(Boolean, unique=False, default=True)
    led_state = Column(Boolean, unique=False, default=True)
    created_at = Column(String, nullable=False)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Logging setup
logger = logging.getLogger(__name__)
logging.basicConfig(filename='farm_app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

def signal_handler(sig, frame):
    logger.info(f"Received signal {sig}. Cleaning up...")
    try:
        controls.inline_fan_output(False)
        controls.heat_mat_output(False)
        controls.mister_output(False)
        controls.pump_output(False)
        controls.led_output(False)
        time.sleep(2)
    except InterruptedError:
        logger.info("Cleanup complete. Exiting.")
    sys.exit(0)

def backup_procedure():
    try:
        logger.info("Starting Backup Procedure")
        subprocess.run([BACKUP_SCRIPT], capture_output=True, text=True, check=True)
        logger.info("File Uploaded to Google Drive ")
        open([LOG_LOCATION], 'w').close()  # just opens and clears it
        logger.info('Log file is cleared')
        entries_to_keep = 10
        subquery = session.query(Mushroomdb.id).order_by(Mushroomdb.created_at.desc()).limit(entries_to_keep).subquery()
        entries_to_remove = session.query(Mushroomdb).filter(~Mushroomdb.id.in_(subquery)).delete(synchronize_session=False)
        session.commit()
        logger.debug(f"Deleted {entries_to_remove} old entries")
    except Exception as e:
        logger.error(f"Error: {e}")

def write_to_database(date, time, temp, humid, heat_mat, mister, pump, inline_fan, led):
    try:
        new_entry = Mushroomdb(date=date, time=time, temperature=temp, humidity=humid,
                                heat_mat_state=heat_mat,  # Corrected column name
                                mister_state=mister, pump_state=pump,
                                inline_fan_state=inline_fan, led_state=led,
                                created_at=datetime.datetime.now())
        session.add(new_entry)
        session.commit()
    except Exception as e:
        logger.error(f"Error writing to database: {e}")
        controls.inline_fan_output(False)
        controls.heat_mat_output(False)
        controls.mister_output(False)
        controls.pump_output(False)
        controls.led_output(False)

def control_devices(pump_on, mister_on, inline_fan_on, heat_mat_on):
    controls.pump_output(pump_on)
    controls.mister_output(mister_on)
    controls.inline_fan_output(inline_fan_on)
    controls.heat_mat_output(heat_mat_on)

def run_control_loop(air_cycle_interval):
    heat_mat = 0
    mister = 0
    inline_fan = 0
    pump = 0
    led_state = 0
    first_run = 1
    humidity_adjustment = 13
    temperature_adjustment = 0
    schedule.every().day.at("00:00").do(backup_procedure)
    last_air_cycle_time = time.time()

    while True:
        try:
            schedule.run_pending()
            light_cam.capture_and_save()
            temperature = temp_humid_sensor.get_temperature()
            humidity = temp_humid_sensor.get_humidity()
            controls.led_output(True)

            currentDateAndTime = datetime.datetime.now()
            current_hour = currentDateAndTime.hour
            if 9 <= current_hour < 21: 
                controls.led_output(True)
                led_state = 1
            else:
                controls.led_output(False)
                led_state = 0

            if temperature is None or humidity is None:
                logger.error("Temperature or Humidity is None")
                while temperature is None or humidity is None:
                    time.sleep(15)
                    temperature = temp_humid_sensor.get_temperature()
                    humidity = temp_humid_sensor.get_humidity()

            db_temp = float(f"{temperature:.2f}") - temperature_adjustment
            db_humid = float(f"{humidity:.2f}") - humidity_adjustment
            now = datetime.datetime.now()
            current_time = time.time()

            # Temperature control
            if temperature > TARGET_TEMP + TEMP_THRESHOLD:
                if not controls.is_pump_on():
                    logger.info("Too Hot, Turning Pump On")
                    control_devices(True, controls.is_mister_on(), controls.is_inline_fan_on(), controls.is_heat_mat_on())
                    pump = 1
            elif temperature < TARGET_TEMP - TEMP_THRESHOLD:
                if controls.is_pump_on():
                    logger.info("Turning Pump Off")
                    control_devices(False, controls.is_mister_on(), controls.is_inline_fan_on(), controls.is_heat_mat_on())
                    pump = 0

            # Humidity control
            if humidity < TARGET_HUMID - HUMID_THRESHOLD:
                if not controls.is_mister_on():
                    logger.info("Too Dry, Turning Mister On")
                    control_devices(controls.is_pump_on(), True, controls.is_inline_fan_on(), controls.is_heat_mat_on())
                    mister = 1
            elif humidity > TARGET_HUMID + HUMID_THRESHOLD:
                if controls.is_mister_on():
                    logger.info("Too Humid, Turning Mister Off")
                    control_devices(controls.is_pump_on(), False, controls.is_inline_fan_on(), controls.is_heat_mat_on())
                    mister = 0

            # Air cycling
            if current_time - last_air_cycle_time >= air_cycle_interval or first_run == 1:
                logger.info("Cycling Air")
                control_devices(controls.is_pump_on(), controls.is_mister_on(), True, controls.is_heat_mat_on())
                inline_fan = 1
                time.sleep(300)#change to 300
                write_to_database(now.strftime("%d/%m/%Y"), now.strftime("%H:%M:%S"), db_temp, db_humid, heat_mat, mister, pump, inline_fan, led_state)
                control_devices(controls.is_pump_on(), controls.is_mister_on(), False, controls.is_heat_mat_on())
                inline_fan = 0
                last_air_cycle_time = current_time
            else:
                write_to_database(now.strftime("%d/%m/%Y"), now.strftime("%H:%M:%S"), db_temp, db_humid, heat_mat, mister, pump, inline_fan, led_state)
            time.sleep(60)
            first_run = 0
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            control_devices(False, False, False, False)
            break
    session.close()
    exit()

def program_loop():
    state = os.getenv("STATE")
    if state == "1":
        run_control_loop(AIR_CYCLE_INTERVAL)
    else:
        run_control_loop(COLONIZATION_AIR_CYCLE_INTERVAL)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        logger.info("Program Started")
        program_loop()
    except Exception as e:
        logger.error(f"Error {e}")
        controls.inline_fan_output(False)
        controls.heat_mat_output(False)
        controls.mister_output(False)
        controls.pump_output(False)
    finally:
        GPIO.cleanup()
        logger.info('Finished')
