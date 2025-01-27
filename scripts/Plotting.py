from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime, timedelta
import geopandas as gpd
import numpy as np
import logging  
import pandas as pd

from PullRainData import BuildRainDF
from PullWindData import BuildWindDF

def MakeAnimation(WindDF: pd.DataFrame, RainDF: pd.DataFrame) -> None:
    logging.info('Plotting and saving animation as a gif')

    # Reading of the SG geojson file
    singapore_map = gpd.read_file('../NationalMapPolygonKML.geojson')

    # Prepare the data for the heatmap animation
    time_groups = RainDF.groupby('timestamp')

    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Set color normalization based on the min and max rainfall intensity in your dataset
    norm_precip = Normalize(vmin=RainDF['value'].min(), vmax=RainDF['value'].max())
    cmap_precip = plt.cm.plasma  # Other colormaps that can be tried are 'viridis' or 'coolwarm'

    # Set color normalization based on the min and max rainfall intensity in your dataset
    norm_wind = Normalize(vmin=WindDF['WindSpeed'].min(), vmax=WindDF['WindSpeed'].max())
    cmap_wind = plt.cm.plasma  # Other colormaps that can be tried are 'viridis' or 'coolwarm'

    # Create a ScalarMappable object for the colorbar
    sm1 = ScalarMappable(cmap=cmap_precip, norm=norm_precip)
    sm1.set_array([])  # We set an empty array since we will pass data to the colorbar later

    sm2 = ScalarMappable(cmap=cmap_wind, norm=norm_wind)
    sm2.set_array([])

    # Add the colorbar
    cbar1 = fig.colorbar(sm1, ax=ax)
    cbar1.set_label("Precipitation (mm)")

    # cbar2 = fig.colorbar(sm2, ax=ax)
    # cbar2.set_label('Wind Speed (m/s)')

    # Define the update function for each frame
    def update(frame):
        ax.clear()  # Clear the axis for the new frame
        
        timestamp, precip_slice = frame
        values = np.array(precip_slice['value'], dtype=float)
        values = np.nan_to_num(values, nan=0.0)
        # Plot the Singapore map
        singapore_map.plot(ax=ax, color='lightgray', edgecolor='lightgray')
        
        # Plot precipitation as a scatter plot (no interpolation needed)
        ax.scatter(
            precip_slice['longitude'], 
            precip_slice['latitude'], 
            c=values,  # Color based on rainfall intensity
            s=values * 30,  # Adjust size of the dots
            cmap=cmap_precip, 
            norm=norm_precip,  # Use the normalization set earlier
            alpha=0.7
        )
        wind_slice = WindDF[WindDF['timestamp'] == timestamp]
        u = wind_slice['WindSpeed'] * np.cos(np.radians(wind_slice['WindDirection']))
        v = wind_slice['WindSpeed'] * np.sin(np.radians(wind_slice['WindDirection']))
        
        ax.barbs(
            wind_slice['longitude'], 
            wind_slice['latitude'], 
            u, 
            v, 
            # color=cmap_wind(norm_wind(wind_slice['Wind Speed'])),
            length=7  # Optional: Adjust length of the barbs
        )
        
        # Set the title with the current timestamp
        ax.set_title(f"Precipitation and winds at {timestamp}")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.set_xlim([103.58, 104.05])
        ax.set_ylim([1.15, 1.50])
        
        # The colorbar remains fixed with the same range across all frames

    # Prepare the frames (grouped by timestamp)
    frames = [(timestamp, precip_slice) for timestamp, precip_slice in time_groups]
    # print(frames)

    # Create the animation
    ani = animation.FuncAnimation(fig, update, frames=frames, repeat=False)
    return ani
    
if __name__ == '__main__':
    DATE = input('Date in yyyy-mm-dd format \n')
    START_TIME = input('Starting time in HH:MM format \n')
    END_TIME = input('Ending time in HH:MM format \n')
    
    RainDF = BuildRainDF(DATE, START_TIME, END_TIME)
    WindDF = BuildWindDF(DATE, START_TIME, END_TIME)
    anim = MakeAnimation(WindDF, RainDF)
    anim.save('anim.gif', writer='imagemagick',fps=1)
    plt.show()

