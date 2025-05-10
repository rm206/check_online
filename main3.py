import time
import socket
import psycopg2
import os
from datetime import datetime


class DBWriter:
    def __init__(self, event_id, mode="prod"):
        self.event_id = event_id
        try:
            if mode == "dev":
                self.db = psycopg2.connect(
                    host="localhost",
                    user="root",
                    password="fatma",
                    dbname="factchecker_claimbuster",
                )
            elif mode == "prod":
                self.db = psycopg2.connect(
                    host="localhost",
                    user="claimbuster",
                    password="claimbuster",
                    dbname="claimbuster",
                )
            self.cursor = self.db.cursor()
            self.connected = True
        except Exception as e:
            self.connected = False
            log_message(f"Failed to connect to database: {e}")

    def writeSentence(self, text, sequence):
        if not self.connected:
            return False

        try:
            # Default score value since we don't care about scores
            score = 0.0
            # insert sentence to database
            query = (
                "INSERT INTO live_sentences(text, score, sequence, event_id) \
                VALUES ('%s', %.10f, %d, %d)"
                % (text.replace("'", "''"), score, sequence, self.event_id)
            )
            self.cursor.execute(query)
            self.db.commit()
            return True
        except Exception as e:
            log_message(f"Failed to insert into database: {e}")
            return False

    def close(self):
        if self.connected:
            try:
                self.db.close()
            except:
                pass


def log_message(message):
    """Write message to log file with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"

    log_file = "db_messages.txt"
    try:
        with open(log_file, "a") as file:
            file.write(log_entry + "\n")
    except Exception as e:
        # If we can't write to the log file, print to console as last resort
        print(f"Failed to write to log file: {e}")
        print(log_entry)


def is_connected():
    """Check if the computer is connected to the internet."""
    try:
        # Try to connect to a common website (e.g., Google's DNS)
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False


def db_message_logger():
    last_time = datetime.now()
    message_count = 0
    lost_connection_time = None  # Variable to store the time of connection loss
    event_id = 1  # Set your event ID here

    log_message("Database message logger started")

    while True:
        try:
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

            # Always log the message to file first
            log_message(f"Message: {message}")

            # Try to write to database
            db_writer = None
            try:
                db_writer = DBWriter(event_id, "prod")
                if db_writer.connected:
                    db_success = db_writer.writeSentence(message, message_count)
                    if db_success:
                        log_message("Successfully inserted message into database")
                    else:
                        log_message("Failed to insert message into database")
            except Exception as e:
                log_message(f"Database operation error: {e}")
            finally:
                if db_writer:
                    db_writer.close()

            # Update last_time for the next iteration
            last_time = current_time

            # Wait for 10 minutes before sending the next message
            # Using a loop with small sleeps allows for more graceful handling of interruptions
            for _ in range(60):  # 60 * 10 seconds = 10 minutes
                time.sleep(10)

        except Exception as e:
            log_message(f"Error in main loop: {e}")
            # Sleep for a short time before continuing to prevent tight loop if there's a persistent error
            time.sleep(30)


if __name__ == "__main__":
    print("Starting DB message logger...")
    log_message("Initializing DB message logger")
    time.sleep(10)  # Initial delay

    try:
        db_message_logger()
    except KeyboardInterrupt:
        log_message("Process terminated by user")
    except Exception as e:
        log_message(f"Fatal error: {e}")
