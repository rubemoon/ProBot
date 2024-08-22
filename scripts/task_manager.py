import serial
import time
import csv
import yaml
from gtts import gTTS
from playsound import playsound
import os
import random
from datetime import datetime, timedelta

def load_config():
    """Load configuration from config.yaml."""
    with open("config/config.yaml", 'r') as config_file:
        return yaml.safe_load(config_file)

def initialize_serial(port, baud_rate, timeout=5):
    """Initialize the serial connection to Arduino."""
    print("[INFO] Initializing serial connection...")
    arduino = serial.Serial(port, baud_rate, timeout=timeout)
    time.sleep(2)  # Allow time for the connection to initialize
    print("[INFO] Serial connection established.")
    return arduino

def read_tasks(task_file):
    """Read tasks from the CSV file."""
    tasks = []
    with open(task_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if len(row) == 2:
                tasks.append({'task': row[0], 'status': row[1]})
    print(f"[INFO] {len(tasks)} tasks loaded.")
    return tasks

def save_tasks(task_file, tasks):
    """Save tasks to the CSV file."""
    with open(task_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Task', 'Status'])  # Write header
        for task in tasks:
            writer.writerow([task['task'], task['status']])
    print(f"[INFO] Tasks saved successfully.")

def speak(message):
    """Convert text to speech and play it."""
    try:
        tts = gTTS(message)
        tts.save("temp.mp3")
        playsound("temp.mp3")
        os.remove("temp.mp3")
    except Exception as e:
        print(f"[ERROR] Failed to play message: {e}")

def get_time_of_day():
    """Determine the current time of day."""
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "morning"
    elif 12 <= current_hour < 18:
        return "afternoon"
    else:
        return "evening"

def greet_user(config):
    """Greet the user with a friendly message based on the time of day."""
    time_of_day = get_time_of_day()
    greetings = config['greetings'][time_of_day]
    speak(random.choice(greetings))

def announce_task(task):
    """Announce the current task with instructions."""
    message = (
        f"Your next task is: {task['task']}. It's currently {task['status']}. "
        "If you're working on this task, press 1 to mark it as completed. "
        "If you'd like to skip this task, press 2. "
        "To hear the task again, press 3. "
        "To hear all pending tasks, press 4."
    )
    speak(message)

def announce_completion(config):
    """Announce task completion with a friendly message."""
    completion_messages = config['completion_messages']['general']
    speak(random.choice(completion_messages))

def announce_pending(tasks):
    """Announce all pending tasks with a friendly tone."""
    pending_tasks = [task['task'] for task in tasks if task['status'] == 'Not Started']
    if pending_tasks:
        message = "Here are your pending tasks: " + ', '.join(pending_tasks) + "."
    else:
        message = "You've completed all your tasks! What's next?"
    speak(message)

def announce_all_tasks(tasks):
    """Announce all tasks and their statuses."""
    message = "Here's a summary of all your tasks:"
    for task in tasks:
        message += f" {task['task']} is currently {task['status']}. "
    speak(message)

def handle_button_press(button_pressed, current_task_index, tasks, config):
    """Handle the button press logic with a friendly, conversational tone."""
    if button_pressed == 1:  # Mark task as complete
        tasks[current_task_index]['status'] = 'Completed'
        announce_completion(config)
        current_task_index = move_to_next_task(current_task_index, tasks)
    elif button_pressed == 2:  # Skip to the next task
        speak("Alright, let's skip to the next task.")
        current_task_index = move_to_next_task(current_task_index, tasks)
    elif button_pressed == 3:  # Repeat current task
        announce_task(tasks[current_task_index])
        # Announce all tasks and exit after repeating the task
        time.sleep(2)  # Brief pause before announcing all tasks
        announce_all_tasks(tasks)
        time.sleep(5)  # Wait for 5 seconds before exiting (adjust as needed)
        speak("I'll give you some time to work on this. See you later!")
        print("[INFO] Exiting the program after task repeat.")
        exit(0)
    elif button_pressed == 4:  # Announce all pending tasks
        announce_pending(tasks)
    elif button_pressed == 14:  # Exit program
        announce_all_tasks(tasks)
        exit_message = random.choice(config['exit_messages']['general'])
        speak(exit_message)
        print("[INFO] Exiting the program. Have a productive day!")
        exit(0)
    else:
        speak("I'm not sure what that means. Could you try again?")
        print(f"[WARNING] Unknown button code: {button_pressed}")
    
    return current_task_index

def move_to_next_task(current_task_index, tasks):
    """Move to the next uncompleted task, or finish if all tasks are completed."""
    while current_task_index < len(tasks) and tasks[current_task_index]['status'] == 'Completed':
        current_task_index += 1
    
    if current_task_index >= len(tasks):
        announce_all_tasks(tasks)
        speak("You've completed all your tasks for the day. Great job, Rubens!")
        print("[INFO] All tasks completed.")
        exit(0)
    else:
        announce_task(tasks[current_task_index])
    
    return current_task_index

def main():
    config = load_config()
    arduino = initialize_serial(config['serial_port'], config['baud_rate'])

    tasks = read_tasks(config['task_file_path'])
    current_task_index = 0

    greet_user(config)  # Initial greeting when the script starts

    current_task_index = move_to_next_task(current_task_index, tasks)

    while True:
        if arduino.in_waiting > 0:
            raw_data = arduino.readline().decode().strip()
            print(f"[DEBUG] Raw data received: '{raw_data}'")
            if raw_data.isdigit():
                button_pressed = int(raw_data)
                speak(f"Button {button_pressed} pressed.")
                print(f"[INFO] Button pressed: {button_pressed}")
                current_task_index = handle_button_press(button_pressed, current_task_index, tasks, config)
                save_tasks(config['task_file_path'], tasks)

if __name__ == "__main__":
    main()

