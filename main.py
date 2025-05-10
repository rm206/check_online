import time
import socket
from datetime import datetime


def is_connected():
    """Check if the computer is connected to the internet."""
    try:
        # Try to connect to a common website (e.g., Google's DNS)
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False


def send_message():
    last_time = datetime.now()
    message_count = 0
    lost_connection_time = None  # Variable to store the time of connection loss
    while True:
        current_time = datetime.now()

        # If there is no connection, store the time of disconnection and use it for subsequent messages
        if not is_connected():
            if lost_connection_time is None:
                lost_connection_time = (
                    current_time  # Store the time when the connection was lost
                )
            message = f"Lost connection at {lost_connection_time.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            # If the connection is restored, reset the lost connection time and use the current time
            if lost_connection_time is not None:
                lost_connection_time = None  # Reset the lost connection time

            # Calculate time passed since last message
            time_passed = current_time - last_time
            message_count += 1
            message = f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}, Time passed: {time_passed}, Message count: {message_count}"

        # Write the message to a file
        with open("messages.log", "a") as file:
            file.write(message + "\n")

        # Update last_time for the next iteration
        last_time = current_time

        # Wait for 10 minutes before sending the next message
        time.sleep(10 * 60)


if __name__ == "__main__":
    time.sleep(10)
    send_message()
