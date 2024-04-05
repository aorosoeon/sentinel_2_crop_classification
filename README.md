# sentinel_2_crop_classification
Crop classification for Canadian fields using satellite data from Sentinel-2

## structuring_truth_data
EDA for the crop types ground truth data from here: https://open.canada.ca/data/en/dataset/503a3113-e435-49f4-850c-d70056788632. Understanding its inconsistencies, handling missing values, plotting distributions, and plotting these data points on folium maps. The result is a cleaned geojson with crop type for each data point

## ExtractTruthData
Java class to extract truth data located within a specified bouding box (xmin, ymin, xmax, ymax) from a file in geoJSON fomat and write to CSV

Usage: java GeoJSONFilter \<GeoJSONFilePath\> \<BoundingBoxJSON\> \<OutputCSVFilePath\> \<Optional: CSV list of include descriptions (exact match required!)\>

Note that crop types " " and "Abandoned Agriculture Land" are hard-coded excludes

Example arguments:
C:\Users\andre\IdeaProjects\MergeSatData\data\annual_crop_inventory_ground_truth_data_v1_2023.geojson "{\"xmin\": -64.693039, \"ymin\": 45.894866, \"xmax\": -61.969033, \"ymax\": 46.999324}" C:\Users\andre\IdeaProjects\MergeSatData\data\output.csv "Wheat - Winter, Timothy, Canola / Rapeseed"

## SentinelDataExtract
Python file to extract data from SentinelHub
Due to data request volume limitations, make requests in chunks
Retrieve 13 optical (visual and near-infra-read) bands

## MergeSatData
Java class to merge Sentinel data and truth data to create CSV file suitable for ML models 

Usage: java mergeCropData \<truthDataCSV\> \<satelliteDataCSV\> \<outputCSV\> \<minDistance\>


## Truth data from Agriculture Canada is here:
https://github.com/aorosoeon/sentinel_2_crop_classification/tree/main/MergeSatData/data/annual_crop_inventory_ground_truth_data_v1_2023.geojson

Source: https://open.canada.ca/data/en/dataset/503a3113-e435-49f4-850c-d70056788632

## Prince Edward Island - bounding box splitter

PrinceEdwardIsland-SentialDataExtract\large_area_utilities.ipynb, illustrates various ways of obtaining bounding boxes from polygons, e.g. Prince Edward Island.
These bounding can further be used to obtain sential data.

## CropClassficationPycaret.ipynb
Jupyter notebook which reads the data from the final dataset and performs machine learning with the pycare library. 
