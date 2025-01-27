from datetime import datetime, timedelta
import os
import pandas as pd
from PullRainData import BuildRainDF
from PullWindData import BuildWindDF
from Plotting import MakeAnimation
from InputRequests import InputRequest

def main():
    DATE, START_TIME, END_TIME = InputRequest()
    RainDF = BuildRainDF(DATE, START_TIME, END_TIME)
    WindDF = BuildWindDF(DATE, START_TIME, END_TIME)

    anim = MakeAnimation(WindDF, RainDF)
    anim.save('../gifs/output.gif', fps=1)

if __name__ == '__main__':
    main()