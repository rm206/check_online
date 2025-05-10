import time
import pyautogui
from datetime import datetime


def send_message():
    last_time = datetime.now()
    message_count = 0
    while True:
        # Calculate current time and time passed since the last message
        current_time = datetime.now()
        time_passed = current_time - last_time
        last_time = current_time

        # Increment the message count
        message_count += 1

        # Format the message
        message = f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}, Time passed: {time_passed}, Message count: {message_count}"

        # Click and enter the message
        pyautogui.click()
        pyautogui.typewrite(message)
        pyautogui.press("enter")

        # Wait for 10 minutes before sending the next message
        time.sleep(10 * 60)


if __name__ == "__main__":
    time.sleep(10)
    send_message()
