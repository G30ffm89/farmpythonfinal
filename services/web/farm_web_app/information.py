import sqlite3
import os

db_path = 'farm_web_app/farm_data_database'


db_file = os.path.join(db_path, 'farm_data.db')
def get_latest_data():
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT date, time, Temperature, Humidity, heat_mat_state, Mister_State, Pump_State,
                   Inline_Fan_state, LED_State 
            FROM farm_info 
            ORDER BY ID DESC LIMIT 1
        ''')
        result = cursor.fetchone()
        if result:
            date, time, temperature, humidity, heat_mat_state, mister_state, \
            pump_state ,inline_fan_state, led_state = result
            heat_mat_state = "On" if heat_mat_state else "Off"
            mister_state = "On" if mister_state else "Off"
            inline_fan_state = "On" if inline_fan_state else "Off"
            pump_state = "On" if pump_state else "Off"
            led_state = "On" if led_state else "Off"
            return date, time, temperature, humidity, heat_mat_state, mister_state, pump_state ,inline_fan_state, led_state 
        else:
            return None, None, None, None, None, None, None, None, None

def get_last_10_data():
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, time, Temperature, Humidity 
                FROM farm_info 
                ORDER BY ID DESC LIMIT 10
            ''')
            results = cursor.fetchall()

        data_list = []
        for row in results:
            date, time, temperature, humidity = row
            data_list.append({
                'date': date,
                'time': time,
                'temperature': temperature,
                'humidity': humidity
            })
        return list(reversed(data_list))
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None 
        
