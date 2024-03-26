# sentinel_2_crop_classification
Crop classification for Canadian fields using satellite data from Sentinel-2

# ExtractTruthData
Java class to extract truth data located within a specified bouding box (xmin, ymin, xmax, ymax) from a file in geoJSON fomat and write to CSV

Usage: java GeoJSONFilter <GeoJSONFilePath> <BoundingBoxJSON> <OutputCSVFilePath>
TODO: (Andrew) include/exclude specific crop types 

# SentinelDataExtract
Python file to extract data from SentinelHub

# MergeSatData
Java class to merge Sentinel data and truth data to create CSV file suitable for ML models 

Usage: java mergeCropData <truthDataCSV> <satelliteDataCSV> <outputCSV> <minDistance>
TODO: add more output columns, after SentinelDataExtract is modified

# Truth data from Agriculture Canada is here:
https://github.com/aorosoeon/sentinel_2_crop_classification/tree/main/MergeSatData/data/annual_crop_inventory_ground_truth_data_v1_2023.geojson
Source: https://open.canada.ca/data/en/dataset/503a3113-e435-49f4-850c-d70056788632
