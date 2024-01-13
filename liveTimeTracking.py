import time

class LiveTimeTracker:
    def __init__(self):
        self.start_time = None
        self.callback_function = None

    def start_timer(self, callback_function=None):
        if self.start_time is None:
            print("Timer started.")
            self.start_time = time.time()
            self.callback_function = callback_function
            self.update_timer()
        else:
            print("Timer is already running.")

    def stop_timer(self):
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            print(f"Timer stopped. Elapsed time: {self.format_time(elapsed_time)}")
            self.start_time = None
            self.callback_function = None
        else:
            print("Timer is not running.")

    def update_timer(self):
        while self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            formatted_time = self.format_time(elapsed_time)
            print(f"\rElapsed time: {formatted_time}", end="", flush=True)
            if self.callback_function:
                self.callback_function(formatted_time)
            time.sleep(1)

    def format_time(self, seconds):
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

# Function that receives the elapsed time
def process_elapsed_time(elapsed_time):
    # You can do something with the elapsed time here
    print("\nElapsed time received in another function:", elapsed_time)
