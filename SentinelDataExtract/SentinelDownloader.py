from sentinelhub import DataCollection, geometry, constants, SHConfig, SentinelHubRequest, MimeType, SentinelHubDownloadClient
import pandas as pd
import numpy as np

# Configure Sentinel Hub with your API key
config = SHConfig()
#config.sh_client_id = 'sh-0ff3049a-dffe-4c03-b3bc-aa3818ca95c3'
#config.sh_client_secret = 'LiPySb7k8WO5ZQVM1HWb80NiI99yo9As'
config.sh_client_id = '8bede36a-dd3d-46f0-87af-44d67956c880'
config.sh_client_secret = 'PKwHDIOtPbTXgBD6dvsF6Z2wf1sZntvm'

config.save()

if not config.sh_client_id or not config.sh_client_secret:
    print("Warning! To use Process API, please provide the credentials (OAuth client ID and client secret).")

# longitude_min = -64.484032
# latitude_min = 45.862321
# longitude_max = -61.776823
# latitude_max = 47.061006


#longitude_min = -64.693039
longitude_min = -61.9691
latitude_min = 45.890
longitude_max = -61.969033
#latitude_max = 46.999324
latitude_max = 45.895

# Define the bounding box and time range for the satellite imagery
myBBox = geometry.BBox((longitude_min, latitude_min, longitude_max, latitude_max), constants.CRS.WGS84)
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
    input: ["B02", "B08", "B11", "dataMask"],
    output: { bands: 4 }
};
}

function evaluatePixel(samples) {
let val = [samples.B11, samples.B08, samples.B02, samples.dataMask];
return viz.processList(val);
}
"""

# data_source='S2L1C',

# Create a Sentinel Hub request for satellite imagery
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
    bbox=myBBox,
    #size=(512, 512),  # Image size
    config=config

)

sampleData = request.get_data()

# Process the data to extract coordinates and RGB values
data = np.array(sampleData[0])  # Assuming the response contains the RGB image data

# Extract coordinates (lon, lat) for each pixel
lon_values = np.linspace(myBBox.min_x, myBBox.max_x, data.shape[1])
lat_values = np.linspace(myBBox.min_y, myBBox.max_y, data.shape[0])
lons, lats = np.meshgrid(lon_values, lat_values)

# Flatten the data and coordinates for each pixel into a DataFrame
df = pd.DataFrame({
    'Longitude': lons.flatten(),
    'Latitude': lats.flatten(),
    'R': data[:, :, 0].flatten(),  # Red channel
    'G': data[:, :, 1].flatten(),  # Green channel
    'B': data[:, :, 2].flatten()   # Blue channel
})

# Save the DataFrame to a CSV file
df.to_csv('C:/Users/andre/IdeaProjects/SentinelDataExtract/data/sentinel2_rgb_values.csv', index=False)
