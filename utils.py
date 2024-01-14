from datetime import datetime
import threading


def start_study_session(duration, func):
    datetime_name = str(datetime.now().replace(microsecond=0))
    datetime_name = datetime_name.replace(" ", "-").replace(":", "-")

    with open("./logs/logs.txt", "a+") as f:
        f.write(datetime_name + "\n")
    with open(f"./logs/{datetime_name}.csv", "w+") as f:
        f.write("total_time,distracted_time,blink_count,yawn_count\n")

    t = threading.Thread(
        target=func,
        args=[datetime_name, duration],
    )
    t.start()
