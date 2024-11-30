from datetime import datetime
import re

def DateInputRequest() -> str:
    while True: # Prompts user for a date until a valid date is supplied
        date = input('Date in yyyy-mm-dd format \n')
        try: 
            datetime.strptime(date, '%Y-%m-%d')
            break
        except ValueError:
            print('Input does not match required format! Try again.')
    return date

def StartTimeInputRequest() -> str:
    while True: # Prompts user for a start time until a valid start time date is supplied
        start_time = input('Start time in HH:MM format \n')
        try:
            datetime.strptime(start_time, '%H:%M')
            break
        except ValueError:
            print('Input does not match required format! Try again.')
    return start_time

def EndTimeInputRequest() -> str:
    while True: # Prompts user for a start time until a valid start time date is supplied
        end_time = input('End time in HH:MM format \n')
        try:
            datetime.strptime(end_time, '%H:%M')
            break
        except ValueError:
            print('Input does not match required format! Try again.')
    return end_time

def InputRequest():
    while True:
        date = DateInputRequest()
        start_time = StartTimeInputRequest()
        end_time = EndTimeInputRequest()
        if datetime.strptime(start_time, '%H:%M') < datetime.strptime(end_time, '%H:%M'):
            break
        else:
            print('Start time must be earlier than end time! Try again.')

    return date, start_time, end_time
