from datetime import datetime, timedelta
import requests
import logging

def round_to_nearest_5_minutes(time_str):
    # Convert the time string to a datetime object
    time_obj = datetime.strptime(time_str, '%H:%M')
    
    # Get the number of minutes since the start of the hour
    minutes = time_obj.minute
    
    # Calculate the remainder when dividing by 5
    remainder = minutes % 5
    
    # Round up or down based on the remainder
    if remainder >= 3:
        # Round up
        rounded_minutes = minutes + (5 - remainder)
    else:
        # Round down
        rounded_minutes = minutes - remainder
    
    # Create a new time object with the rounded minutes
    rounded_time = time_obj.replace(minute=rounded_minutes)

        # Return the rounded time as a string in HH:MM format
    return rounded_time.strftime('%H:%M')

def generate_time_lists(start_time_str, end_time_str, interval):
    # Convert start and end times from HH:MM format to datetime objects
    start_time = datetime.strptime(start_time_str, '%H:%M')
    end_time = datetime.strptime(end_time_str, '%H:%M')
    
    # Initialize empty lists for hours and minutes
    HourList = []
    MinutesList = []

    # Round the start time to the nearest 5 minutes
    current_time = start_time
    
    # Loop until we reach the end time
    while current_time <= end_time:
        # Extract hour and minute, append to lists
        HourList.append(current_time.strftime('%H'))
        MinutesList.append(current_time.strftime('%M'))
        
        # Move forward by 5 minutes
        current_time += timedelta(minutes=interval)
    
    return HourList, MinutesList

def generate_time_labels(hour_list, minutes_list):
    time_labels = [f"{hour}:{minute}" for hour, minute in zip(hour_list, minutes_list)]
    return time_labels
