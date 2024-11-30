from datetime import datetime, timedelta
import requests
import logging
import pandas as pd
from PullRainData import BuildRainDF
from PullWindData import BuildWindDF
from Plotting import MakeAnimation


def main():
    DATE = input('Date in yyyy-mm-dd format \n')
    START_TIME = input('Starting time in HH:MM format \n')
    END_TIME = input('Ending time in HH:MM format \n')

    RainDF = BuildRainDF(DATE, START_TIME, END_TIME)
    WindDF = BuildWindDF(DATE, START_TIME, END_TIME)
    anim = MakeAnimation(WindDF, RainDF)
    anim.save('anim.gif',fps=1)
if __name__ == '__main__':
    main()