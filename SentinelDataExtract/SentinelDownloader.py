from sentinelhub import DataCollection, geometry, constants, SHConfig, SentinelHubRequest, MimeType, SentinelHubDownloadClient
import pandas as pd
import numpy as np

# Configure Sentinel Hub with your API key
config = SHConfig()
config.sh_client_id = '6b13237e-d289-4827-b8d9-5a90aaedb247'
config.sh_client_secret = 'CfLdUhR08nJGv7kxeA1DvieL0bdsc2Up'

config.save()

config.mask_no_data = True 

if not config.sh_client_id or not config.sh_client_secret:
    print("Warning! To use Process API, please provide the credentials (OAuth client ID and client secret).")


# #longitude_min = -64.693039
# longitude_min = -62.693039
# latitude_min = 45.894866
# #longitude_max = -61.969033
# latitude_max = 46.999324
# latitude_max = 46.5
    
    # SW Ontario
#Bounding box for SW Ontario: http://bboxfinder.com/#42.803462,-81.589966,44.257003,-80.134277
longitude_min = -81.589966
latitude_min = 42.803462
longitude_max = -80.134277
latitude_max = 44.257003

# Define the bounding box and time range for the satellite imagery - match it to the time range of the truth data

time_interval = ('2023-08-01', '2023-08-31')

# Define the spectral bands to retrieve (e.g., red, green, blue, near-infrared)
bands = ['B01','B02','B03','B04','B05','B06','B07','B08','B8A','B09','B10','B11','B12']  # Sentinel-2 bands for RGB and NIR

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
request = SentinelHubRequest(
    data_folder='C:/Users',  # Folder to save downloaded data
    evalscript=myEvalscript,
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
    size=(512, 512),  # Image size
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

# Save the DataFrame to a CSV file
df.to_csv('./sentinel2_rgb_values.csv', index=False)
