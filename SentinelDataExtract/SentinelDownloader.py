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


longitude_min = -62.415
latitude_min = 46.27
longitude_max = -62.24
latitude_max = 46.44

# Define time range for the satellite imagery - match it to the time range of the truth data
time_interval = ('2023-08-01', '2023-08-31')

# Define the spectral bands to retrieve (e.g., red, green, blue, near-infrared)
bands = ['B04', 'B03', 'B02', 'B08']  # Sentinel-2 bands for RGB and NIR

# define evalscript
myEvalscript = """
//VERSION=3
let minVal = 0.0;
let maxVal = 0.4;

let viz = new HighlightCompressVisualizer(minVal, maxVal);

function setup() {
return {
    input: ["B04", "B03", "B02", "dataMask"],
    output: { bands: 4 }
};
}

function evaluatePixel(samples) {
let val = [samples.B04, samples.B03, samples.B02, samples.dataMask];
return viz.processList(val);
}
"""

# data_source='S2L1C',

# Create a Sentinel Hub request for satellite imagery
# Because of limitations in the volume of data in each SentinelHubRequest,
# break down the input bounding box into small chunks and iterate through them

chunk_long = longitude_min
chunk_lat = latitude_min

chunk_size = 0.01

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
            'B04': data[:, :, 0].flatten(),
            'B03': data[:, :, 1].flatten(),
            'B02': data[:, :, 2].flatten()
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
cumulative_df.to_csv('C:/Users/andre/IdeaProjects/SentinelDataExtract/data/sentinel2_rgb_values.csv', index=False)
print("Done!")
