import math

from sentinelhub import DataCollection, geometry, constants, SHConfig, SentinelHubRequest, MimeType, SentinelHubDownloadClient
import pandas as pd
import numpy as np

# Configure Sentinel Hub with your API key - see https://apps.sentinel-hub.com/dashboard/#/account/settings
config = SHConfig()
config.sh_client_id = '6b13237e-d289-4827-b8d9-5a90aaedb247'
config.sh_client_secret = 'CfLdUhR08nJGv7kxeA1DvieL0bdsc2Up'
#config.sh_client_id = '8bede36a-dd3d-46f0-87af-44d67956c880'
#config.sh_client_secret = 'PKwHDIOtPbTXgBD6dvsF6Z2wf1sZntvm'

config.mask_no_data = True  # Set mask_no_data to True to mask rows with no data measurements

config.save()

if not config.sh_client_id or not config.sh_client_secret:
    print("Warning! To use Process API, please provide the credentials (OAuth client ID and client secret).")

# longitude_min = -64.484032
# latitude_min = 45.862321
# longitude_max = -61.776823
# latitude_max = 47.061006

# PEI
#longitude_min = -62.415
#latitude_min = 46.27
#longitude_max = -62.24
#latitude_max = 46.44

# SW Ontario
#Bounding box for SW Ontario: http://bboxfinder.com/#42.803462,-81.589966,44.257003,-80.134277
longitude_min = -81.589966
latitude_min = 42.803462
longitude_max = -80.134277
latitude_max = 44.257003

# Define time range for the satellite imagery - match it to the time range of the truth data
time_interval = ('2023-08-01', '2023-08-31')

# Define the spectral bands to retrieve (e.g., red, green, blue, near-infrared)
bands = ['B01','B02','B03','B04','B05','B06','B07','B08','B8A','B09','B10','B11','B12']

# define evalscript
myEvalscript = """
//VERSION=3
let minVal = 0.0;
let maxVal = 0.4;

let viz = new HighlightCompressVisualizer(minVal, maxVal);

function setup() {
return {
    input: ["B01","B02","B03", "B04","B05", "B06", "B07", "B08","B8A","B09","B10","B11","B12"],
    output: { bands: 13 }
};
}

function evaluatePixel(samples) {
let val = [samples.B01,samples.B02,samples.B03,samples.B04,samples.B05, samples.B06,samples.B07,samples.B08,samples.B8A,samples.B09,samples.B10,samples.B11, samples.B12];
return viz.processList(val);
}
"""

# data_source='S2L1C',

# Create a Sentinel Hub request for satellite imagery
# Because of limitations in the volume of data in each SentinelHubRequest,
# break down the input bounding box into small chunks and iterate through them

chunk_long = longitude_min
chunk_lat = latitude_min

chunk_size = 0.07

cumulative_df = pd.DataFrame()

chunk_count = 0
total_chunks = math.ceil((longitude_max - longitude_min) / chunk_size) * \
               math.ceil((longitude_max - longitude_min) / chunk_size)

print(f"Progress: {chunk_count}/{total_chunks}", end='\r')

while chunk_long < longitude_max:
    while chunk_lat < latitude_max:

        # Define the bounding box for this chunk
        chunk_BBox = geometry.BBox((chunk_long, chunk_lat, chunk_long + chunk_size, chunk_lat + chunk_size), constants.CRS.WGS84)

        request = SentinelHubRequest(
            data_folder='C:/Users/andre/IdeaProjects/SentinelDataExtract/data',  # Folder to save downloaded data
            evalscript=myEvalscript,
            # resolution=[10,10],
            input_data=[
                SentinelHubRequest.input_data (
                    time_interval=time_interval,
                    maxcc=0.5,  # Maximum cloud coverage
                    mosaicking_order='leastCC',  # Mosaicking order,
                    data_collection=DataCollection.SENTINEL2_L1C
                )
            ],
            responses=[
                SentinelHubRequest.output_response('default', MimeType.TIFF)
            ],
            bbox=chunk_BBox,
            #size=(512, 512),  # Image size
            config=config
        )

        sampleData = request.get_data()

        # Process the data to extract coordinates and RGB values
        data = np.array(sampleData[0])  # Assuming the response contains the RGB image data

        # Extract coordinates (lon, lat) for each pixel
        lon_values = np.linspace(chunk_BBox.min_x, chunk_BBox.max_x, data.shape[1])
        lat_values = np.linspace(chunk_BBox.min_y, chunk_BBox.max_y, data.shape[0])
        lons, lats = np.meshgrid(lon_values, lat_values)

        # Flatten the data and coordinates for each pixel into a DataFrame
        chunk_df = pd.DataFrame({
            'Longitude': lons.flatten(),
            'Latitude': lats.flatten(),
            'B01': data[:, :, 0].flatten(),
            'B02': data[:, :, 1].flatten(),
            'B03': data[:, :, 2].flatten(),
            'B04': data[:, :, 3].flatten(),
            'B05': data[:, :, 4].flatten(),
            'B06': data[:, :, 5].flatten(),
            'B07': data[:, :, 6].flatten(),
            'B08': data[:, :, 7].flatten(),
            'B8A': data[:, :, 8].flatten(),
            'B09': data[:, :, 9].flatten(),
            'B10': data[:, :, 10].flatten(),
            'B11': data[:, :, 11].flatten(),
            'B12': data[:, :, 12].flatten()
        })

        cumulative_df = pd.concat([cumulative_df, chunk_df], ignore_index=True)

        chunk_lat += chunk_size

        chunk_count += 1
        print(f"Progress: {chunk_count}/{total_chunks}", end='\r')

    chunk_long += chunk_size
    chunk_lat = latitude_min

# After looping through all chunks, save the DataFrame to a CSV file.
# This can take a few seconds if there are millions of rows

print("Writing CSV file...")
cumulative_df.to_csv('C:/Users/andre/IdeaProjects/SentinelDataExtract/data/sentinel2_rgb_values.csv.zip', index=False)
print("Done!")
