import json
import os
from main import AutoBooker
from datetime import datetime, timedelta
import asyncio

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")

def get_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config

async def task(auto_booker: AutoBooker, automation):
    id = automation.get('id', '??')
    activation_time = automation.get('activation_time', '??')
    
    print(f"Scheduling booking id={id} at activation_time={activation_time}")
    
    try:
        await auto_booker.run(automation=automation, activation_time=activation_time)
        
        print(f"Booking id={id} completed successfully.")
        return True
    except Exception as e:
        print(f"Booking id={id} failed with error: {e}")
        return False
    
async def schedule_bookings(auto_booker: AutoBooker, login_lead, headless: bool, update_interval: float):
    # config = get_config()
    
    triggered_today = set()
    last_date = None
    
    while True:  
        config = get_config()    
        time_now = datetime.now()
        current_day = datetime.now().strftime('%A').lower()
        
        # reset triggers each day
        if last_date != time_now.date():
            triggered_today.clear()
            last_date = time_now.date()
            
        for automation in config:
            auto_id = automation.get('id', '??')
            activation_day = automation.get('activation_day', '').lower()
            activation_time = automation.get('activation_time', '??')
            
            if not automation.get('enabled', True):
                continue
            
            if activation_day != current_day:
                continue
            
            try:
                hh, mm, ss = map(int, activation_time.split(':'))
            except ValueError:
                print(f"Invalid activation_time format for booking id={auto_id}: {activation_time}")
                continue
            
            activation_datetime = time_now.replace(hour=hh, minute=mm, second=ss, microsecond=0)
            
            if activation_datetime <= time_now:
                continue
            
            prelogin = activation_datetime - timedelta(minutes=login_lead)
            
            if prelogin <= time_now < activation_datetime:
                if auto_id in triggered_today:
                    continue
                
                print(f"Triggering booking id={auto_id} at {time_now.strftime('%Y-%m-%d %H:%M:%S')}")
                
                asyncio.create_task(task(auto_booker, automation))

                triggered_today.add(auto_id)
                    
                await asyncio.sleep(update_interval)

        await asyncio.sleep(1)
           
if __name__ == "__main__":
    auto_booker = AutoBooker()
    
    asyncio.run(schedule_bookings(auto_booker, login_lead=5, headless=False, update_interval=2))


# import json
# import asyncio
# from datetime import datetime, timedelta

# from main import AutoBooker

# def get_config():
#     with open("config.json", "r") as f:
#         return json.load(f)

# async def task(automations: list[dict], activation_time: str, headless: bool):
#     ids = [a.get("id", "??") for a in automations]
#     print(f"Starting run activation_time={activation_time} ids={ids}", flush=True)

#     booker = AutoBooker()  # NEW instance per task
#     await booker.run(automations=automations, activation_time=activation_time, headless=headless)

# async def schedule_bookings(login_lead_seconds: int, headless: bool, update_interval: float):
#     triggered_today = set()
#     last_date = None

#     while True:
#         now = datetime.now()
#         current_day = now.strftime("%A").lower()

#         if last_date != now.date():
#             triggered_today.clear()
#             last_date = now.date()

#         config = get_config()

#         # group enabled automations for today by activation_time
#         groups = {}
#         for a in config:
#             if not a.get("enabled", True):
#                 continue
#             if (a.get("activation_day") or "").lower() != current_day:
#                 continue

#             act_time = a.get("activation_time")
#             if not act_time:
#                 continue

#             groups.setdefault(act_time, []).append(a)

#         # trigger at most once per activation_time per day
#         for act_time, autos in groups.items():
#             try:
#                 hh, mm, ss = map(int, act_time.split(":"))
#             except ValueError:
#                 print(f"Invalid activation_time: {act_time}", flush=True)
#                 continue

#             activation_dt = now.replace(hour=hh, minute=mm, second=ss, microsecond=0)
#             if activation_dt <= now:
#                 continue

#             prelogin_dt = activation_dt - timedelta(seconds=login_lead_seconds)

#             key = (current_day, act_time)
#             if prelogin_dt <= now < activation_dt and key not in triggered_today:
#                 print(
#                     f"\nTriggering activation_time={act_time} "
#                     f"[window {prelogin_dt.strftime('%H:%M:%S')} → {activation_dt.strftime('%H:%M:%S')}] "
#                     f"count={len(autos)}",
#                     flush=True
#                 )
#                 asyncio.create_task(task(autos, act_time, headless))
#                 triggered_today.add(key)

#         await asyncio.sleep(update_interval)

# if __name__ == "__main__":
#     asyncio.run(schedule_bookings(login_lead_seconds=60, headless=False, update_interval=1.0))
