from prog_files import controls
from prog_files import light_cam, temp_humid_sensor
import time
import datetime
import RPi.GPIO as GPIO 
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine, Column, Integer, Float, String, Identity, func, Boolean
import logging
import sys
import subprocess
import schedule
import os
from dotenv import load_dotenv


load_dotenv()

controls.heat_mat_output(False)
controls.led_output(False)


sys.dont_write_bytecode = True

logger = logging.getLogger(__name__)

def farm_app_logger():
    logging.basicConfig(filename='farm_app.log', level=logging.DEBUG,
                format='%(asctime)s %(levelname)s: %(message)s')

class Base(DeclarativeBase):
    pass

class Mushroomdb(Base):
    __tablename__ = 'farm_info'

    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    Temperature = Column(Float, nullable=False)
    Humidity = Column(Float, nullable=False)
    Box_Fan_State = Column(Boolean, unique=False, default=True)
    Mister_State = Column(Boolean, unique=False, default=True)
    Pump_State = Column(Boolean, unique=False, default=True)
    Inline_Fan = Column(Boolean, unique=False, default=True)
    LED_State = Column(Boolean, unique=False, default=True)
    created_at = Column(String, nullable=False)

engine = create_engine(os.getenv("DB"))
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

session = Session()



TARGET_TEMP = 18
TEMP_THRESHOLD = 1
TARGET_HUMID = 80
HUMID_THRESHOLD = 1
AIR_CYCLE_INTERVAL = 15 * 60 

backup_script=os.getenv("SCRIPT_LOCATION")
log_location=os.getenv("LOG_LOCATION")         
               
def backup_procedure():
    try:
        logger.info("Starting Backup Procedure")
        subprocess.run([backup_script], capture_output=True, text=True, check=True)
        logger.info("File Uploaded to Google Drive ")
        open([log_location],'w').close() #just opens and clears it
        logger.info('Log file is cleared')
        entries_to_keep = 10
        subquery = session.query(Mushroomdb.id).order_by(Mushroomdb.Created_At.desc()).limit(entries_to_keep).subquery()
        entries_to_remove = session.query(Mushroomdb).filter(~Mushroomdb.id.in_(subquery)).delete(synchronize_session=False)
        session.commit()
        logger.debug(f"Deleted {entries_to_remove} old entries")
    except Exception as e:
        logger.error(f"Error: {e}")
     

def main_menu():
    while True:
        try:
            print("Menu Items: 1 for main loop and 2 for testing menu")
            menu_choice = int(input("Choose menu option: "))
            if menu_choice == 1:
                print("Starting program")
                logger.info("Menu choice 1")
                logger.info("10 seconds till program starts")
                time.sleep(10) #change to 10
                program_loop()
            elif menu_choice == 2:
                while True:
                    print("(1) Heat Mat Test")
                    print("(2) Temp and Humid Sensor")
                    print("(3) Mister Test")
                    print("(4) Inline Fan Test")
                    print("(5) Webcam Test")
                    print("(6) Test Pump")
                    print("(7) LED Test")
                    print("(R) Return to Main Menu")
                    test_menu_choice = input("Pick an Option (1,2,3,4,5,6,R): ")
                    if test_menu_choice == "1":
                         controls.heat_mat_output_test()
                    elif test_menu_choice == "2":
                         temp_humid_sensor.test_temp_humid()
                    elif test_menu_choice == "3":
                         controls.test_mister()
                    elif test_menu_choice == "4":
                         controls.test_inline_fan()
                    elif test_menu_choice == "5":
                         controls.led_test()
                    elif test_menu_choice =="6":
                         controls.pump_test()
                    elif test_menu_choice =="7":
                         controls.led_test()
                    elif test_menu_choice == "R" or "r":
                            break
                    else: 
                        print("Unknown Option")
            else:
                print("Unkown Option....")
        except KeyboardInterrupt:
                    print("Recived Interupt - Turining everything off")
                    print("**Shutdown** inline fan ")
                    controls.inline_fan_output(False)
                    print("**Shutdown** box fan ")
                    controls.heat_mat_output(False)
                    print("**Shutdown** mister ")
                    controls.mister_output(False)
                    print("**Shutdown** pump ")
                    controls.pump_output(False)
                    print("**Shutdown** LED")
                    controls.led_output(False)
                    print("mat shutdown")
                    
                    print("Quit")
                    break
            

def program_loop():
    box_fan = 0
    mister = 0
    inline_fan = 0
    pump = 0
    _time = 0
    _date = 0
    led_state = 0
    first_run = 1
    humidity_adjustment = 13
    temperature_adjustment = 0
    schedule.every().day.at("00:00").do(backup_procedure)

    last_air_cycle_time = time.time()

    while True:
                try:
                    
                    schedule.run_pending()
                    led_state = 0
                    logger.info("loop started")
                    logger.info("taking picture")
                    light_cam.capture_and_save()
                    logger.info("picture taken")
                    logger.info("getting temperature/humidity")
                    temperature = temp_humid_sensor.get_temperature()
                    humidity = temp_humid_sensor.get_humidity()
                    db_temp = float(f"{temperature:.2f}") - temperature_adjustment
                    db_humid = float(f"{humidity:.2f}") - humidity_adjustment #humidity is out a bit
                    
                    if temperature is None or humidity is None:
                        logger.error("Temperature or Humidity is None")
                        while temperature is None or humidity is None:
                            time.sleep(15)
                            logger.info("Trying Again")
                            temperature = temp_humid_sensor.get_temperature()
                            humidity = humidity = temp_humid_sensor.get_humidity()

                    logger.debug(f"Humidity {humidity:.2f}")
                    logger.debug(f"Temperature {temperature:.2f}")

                    # get current time 
                    now = datetime.datetime.now()
                    logger.debug(f"Current time to be saved {now}")

                    _time = now.strftime("%H:%M:%S")
                    _date = now.strftime("%d/%m/%Y")
                    

                    
                    logger.info(f"Starting Checks")
                    time.sleep(5)
                    logger.info(f"Temperature Checks")
                    if temperature > TARGET_TEMP + TEMP_THRESHOLD:
                        if not controls.is_pump_on():  
                            logger.info("Too Hot, Turning Pump On")
                            controls.pump_output(True)
                            pump = 1
                        else:
                            logger.info("Still Too Hot Pump Already On")
                        time.sleep(5)
                    elif temperature < TARGET_TEMP - TEMP_THRESHOLD:
                        if controls.is_pump_on():
                            controls.pump_output(False)
                            pump = 0
                            logger.info("Turning Pump Off")
                        else:
                            logger.info("Pump Already Off")
                        time.sleep(5)
                    
                    logger.info("Starting Humidity")
                    if humidity < TARGET_HUMID - HUMID_THRESHOLD:
                        if not controls.is_mister_on():  
                            logger.info("Too Dry, Turning Mister On")
                            controls.mister_output(True)
                            mister = 1
                        else:
                            logger.info("Still Too Dry Mister Already On")
                        time.sleep(30)
                        
                    elif humidity > TARGET_HUMID + HUMID_THRESHOLD:
                        if controls.is_mister_on():  
                            logger.info("Too Humid, Turning Mister Off")
                            controls.mister_output(False)
                            mister = 0
                        else:
                            logger.info("Humidity is Good Mister Staying Off")
                        time.sleep(30)

                    # Air cycling
                    current_time = time.time()
                    logger.debug(f"current time: {current_time}")
                    if current_time - last_air_cycle_time >= AIR_CYCLE_INTERVAL or first_run == 1:  # 15 minutes in seconds
                        logger.info("Cycling Air")
                        controls.inline_fan_output(True)
                        inline_fan = 1
                        logger.info("Cycling air fan switched on")
                    
                    if inline_fan == 1:
                        logger.info("writing to db")
                        logger.debug(f"Date: {_date}, "
                                    f"Time: {_time}, "
                                    f"Temperature: {db_temp}, "
                                    f"Humidity: {db_humid}, "
                                    f"Box_Fan_State: {box_fan}, "
                                    f"Mister_State: {mister}, "
                                    f"Pump_State: {pump}, "
                                    f"Inline_Fan: {inline_fan}, "
                                    f"LED_State: {led_state}")
                        try:
                            new_entry = Mushroomdb(
                                date=_date, 
                                time=_time,
                                Temperature=db_temp,
                                Humidity=db_humid,
                                Box_Fan_State=box_fan,
                                Mister_State=mister,
                                Pump_State=pump,
                                Inline_Fan=inline_fan,
                                LED_State = led_state,
                                created_at = now
                                    )
                            
                            session.add(new_entry)
                            session.commit()
                        except Exception as e:
                            logger.error(f"Error writing to database: {e}")
                            controls.inline_fan_output(False)
                            controls.mister_output(False)
                            controls.pump_output(False)

                        logger.info("Inline fan if statement written to db")
                        time.sleep(300) #5 min air cycle CHANGE BACK TO 300
                        controls.inline_fan_output(False)
                        logger.info("Turning air fan off")
                        inline_fan = 0
                        last_air_cycle_time = current_time

                    else:
                        logger.info("writing to db")
                        logger.debug(f"Date: {_date}, "
                                    f"Time: {_time}, "
                                    f"Temperature: {db_temp}, "
                                    f"Humidity: {db_humid}, "
                                    f"Box_Fan_State: {box_fan}, "
                                    f"Mister_State: {mister}, "
                                    f"Pump_State: {pump}, "
                                    f"Inline_Fan: {inline_fan}, "
                                    f"LED_State: {led_state}")
                        last_air_cycle_time = current_time

                        try:
                            new_entry = Mushroomdb(
                                date=_date, 
                                time=_time,
                                Temperature=db_temp,
                                Humidity=db_humid,
                                Box_Fan_State=box_fan,
                                Mister_State=mister,
                                Pump_State=pump,
                                Inline_Fan=inline_fan,
                                LED_State = led_state,
                                created_at = now
                                    )
                            session.add(new_entry)
                            session.commit() 
                        except Exception as e:
                                logger.error(f"Error writing to database: {e}")
                                controls.inline_fan_output(False)
                                controls.heat_mat_output(False)
                                controls.mister_output(False)
                                controls.pump_output(False)
                
                    logger.info("Else statement writtem to db")
                    

                    time.sleep(60) #CHANGE BACK TO 60
                    first_run = 0
                    logger.info("Loop restarting....") 

                    

                except KeyboardInterrupt:
                    print("Recived Interupt - Turining everything off")
                    print("**Shutdown** inline fan ")
                    controls.inline_fan_output(False)
                    print("**Shutdown** box fan ")
                    controls.heat_mat_output(False)
                    print("**Shutdown** mister ")
                    controls.mister_output(False)
                    print("**Shutdown** pump ")
                    controls.pump_output(False)
                    print("**Shutdown** LED")
                    controls.led_output(False)
                    print("Quit")
                    break 
                except Exception as e: 
                    logger.error("turning stuff off")
                    print("**Shutdown** inline fan ")
                    controls.inline_fan_output(False)
                    print("**Shutdown** box fan ")
                    controls.heat_mat_output(False)
                    print("**Shutdown** mister ")
                    controls.mister_output(False)
                    print("**Shutdown** pump ")
                    controls.pump_output(False)
                    print("**Shutdown** LED")
                    controls.led_output(False)
                    print("Quit")
                    break 
                    logger.info("turned off")
                    logger.warning(f"An error occurred: {e}")  
                    break 
    session.close()
    exit()


if __name__ == '__main__':
    farm_app_logger()
    try:
        logger.info("Main menu started")
        main_menu()
    finally:
        GPIO.cleanup()
        logger.info('Finished')          

