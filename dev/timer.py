import threading
import time


# Function to be called when the timer expires
def timer_expired():
    print("Timer expired! Performing the scheduled action.")


# Function to start the timer
def start_timer(seconds):
    timer = threading.Timer(seconds, timer_expired)
    timer.start()
    return timer


# Main function to demonstrate the timer
def main():
    print("Starting the timer for 5 seconds...")

    # Start a 5-second timer
    timer = start_timer(5)

    # Simulate doing other tasks
    for i in range(1, 1):
        print(f"Doing task {i}...")
        time.sleep(2)  # Simulate a task taking some time

    print("Main program continues to run...")

    # Optional: Wait for the timer to expire before exiting
    # Uncomment the next line if you want to wait for the timer
    timer.join()


if __name__ == "__main__":
    main()
