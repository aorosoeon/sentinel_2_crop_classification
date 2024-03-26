//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.opencsv.CSVWriter;

import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

public class GeoJSONFilter {
    public static void main(String[] args) {
        if (args.length < 3) {
            System.err.println("Usage: java GeoJSONFilter <GeoJSONFilePath> <BoundingBoxJSON> <OutputCSVFilePath> <Optional: CSV list of include descriptions (exact match required!)>");
            System.exit(1);
        }

        String geoJsonFilePath = args[0];
        String boundingBoxJson = args[1];
        String outputCsvFilePath = args[2];
        List<String> includeList = new ArrayList<>();

        // If provided, convert the 4th arg to a List of CropTypes to include, and trim spaces
        // Wrap each item in double quotes to match geoJSON contents
        if (args.length == 4) {
            includeList = Stream.of(args[3].split(","))
                    .map(item -> "\"" + item.trim() + "\"")
                    .toList();
        }

        // Hard-coded list of crop types to exclude, if include list is NOT provided
        // Note double quotes to match contents of geoJSON file
        List<String> excludeList = List.of("\" \"", "\"Abandoned Agricultural Land\"");

        try {
            ObjectMapper objectMapper = new ObjectMapper();
            JsonNode boundingBoxNode = objectMapper.readTree(boundingBoxJson);

            // This is the bounding box for the truth/fact data

            double xmin = boundingBoxNode.get("xmin").asDouble();
            double ymin = boundingBoxNode.get("ymin").asDouble();
            double xmax = boundingBoxNode.get("xmax").asDouble();
            double ymax = boundingBoxNode.get("ymax").asDouble();

            // Read the goeJSON truth data file, and extract relevant entries

            try (FileReader fileReader = new FileReader(geoJsonFilePath);
                 FileWriter fileWriter = new FileWriter(outputCsvFilePath);
                 CSVWriter csvWriter = new CSVWriter(fileWriter,
                         CSVWriter.DEFAULT_SEPARATOR,
                         CSVWriter.NO_QUOTE_CHARACTER, // Remove extra quotes
                         CSVWriter.NO_ESCAPE_CHARACTER,
                         CSVWriter.DEFAULT_LINE_END
                         )
            ) {

                // Write a header row
                csvWriter.writeNext(new String[]{"Latitude", "Longitude", "CropType"});

                JsonNode geoJsonNode = objectMapper.readTree(fileReader);
                JsonNode featureNodes = geoJsonNode.get("features");
                int totalFeatures = featureNodes.size();
                int processedCount = 0;

                // Extract the coordinates and crop type description
                // Note that there is an integer code available in attribute CROP_TYP_1,
                // but we have chosen to use the description for convenience
                // If processing time/memory is big concern, we could use CROP_TYP_1 instead

                for (JsonNode featureNode : featureNodes) {
                    JsonNode geometryNode = featureNode.get("geometry");
                    JsonNode coordinatesNode = geometryNode.get("coordinates");

                    double longitude = coordinatesNode.get(0).asDouble();
                    double latitude = coordinatesNode.get(1).asDouble();

                    // Ignore any truth data points outside the bounding box

                    if (longitude >= xmin && longitude <= xmax && latitude >= ymin && latitude <= ymax) {

                        JsonNode propertiesNode = featureNode.get("properties");
                        String description = String.valueOf(propertiesNode.get("DESCRIPT_1"));

                        // If Include list is provided, check if this description is in the list
                        // Otherwise, check if this description is in the Exclude list

                        if ((!includeList.isEmpty() && includeList.contains(description)) ||
                                (includeList.isEmpty() && !excludeList.contains(description))) {
                            //Found a useful entry, write it to CSV
                            csvWriter.writeNext(
                                    new String[]{
                                            String.valueOf(latitude),
                                            String.valueOf(longitude),
                                            description
                                    });
                        }
                    }

                    processedCount++;
                    printProgress(processedCount, totalFeatures);
                }

                System.out.println("CSV file generated successfully.");
            } catch (IOException e) {
                e.printStackTrace();
            }
        } catch (IOException e) {
            System.err.println("Error reading bounding box JSON: " + e.getMessage());
            System.exit(1);
        }
    }

    private static void printProgress(int processedCount, int totalFeatures) {
        int progress = (int) Math.round((double) processedCount / totalFeatures * 100);
        System.out.print("\rProcessing " + processedCount + " of " + totalFeatures);
        System.out.flush();

        if (processedCount == totalFeatures) {
            System.out.println(); // Move to the next line after completion
        }
    }
}

