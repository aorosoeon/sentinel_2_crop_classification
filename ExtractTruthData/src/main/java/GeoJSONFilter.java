//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.opencsv.CSVWriter;

import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

public class GeoJSONFilter {
    public static void main(String[] args) {
        if (args.length != 3) {
            System.err.println("Usage: java GeoJSONFilter <GeoJSONFilePath> <BoundingBoxJSON> <OutputCSVFilePath>");
            System.exit(1);
        }

        String geoJsonFilePath = args[0];
        String boundingBoxJson = args[1];
        String outputCsvFilePath = args[2];

        try {
            ObjectMapper objectMapper = new ObjectMapper();
            JsonNode boundingBoxNode = objectMapper.readTree(boundingBoxJson);

            double xmin = boundingBoxNode.get("xmin").asDouble();
            double ymin = boundingBoxNode.get("ymin").asDouble();
            double xmax = boundingBoxNode.get("xmax").asDouble();
            double ymax = boundingBoxNode.get("ymax").asDouble();

            try (FileReader fileReader = new FileReader(geoJsonFilePath);
                 FileWriter fileWriter = new FileWriter(outputCsvFilePath);
                 CSVWriter csvWriter = new CSVWriter(fileWriter,
                         CSVWriter.DEFAULT_SEPARATOR,
                         CSVWriter.NO_QUOTE_CHARACTER, // Remove extra quotes
                         CSVWriter.NO_ESCAPE_CHARACTER,
                         CSVWriter.DEFAULT_LINE_END
                         )
            ) {

                csvWriter.writeNext(new String[]{"Latitude", "Longitude", "CropType"});

                JsonNode geoJsonNode = objectMapper.readTree(fileReader);
                JsonNode featureNodes = geoJsonNode.get("features");
                int totalFeatures = featureNodes.size();
                int processedCount = 0;

                for (JsonNode featureNode : featureNodes) {
                    JsonNode geometryNode = featureNode.get("geometry");
                    JsonNode coordinatesNode = geometryNode.get("coordinates");

                    double longitude = coordinatesNode.get(0).asDouble();
                    double latitude = coordinatesNode.get(1).asDouble();

                    if (longitude >= xmin && longitude <= xmax && latitude >= ymin && latitude <= ymax) {
                        JsonNode propertiesNode = featureNode.get("properties");
                        String description = String.valueOf(propertiesNode.get("DESCRIPT_1"));

                        csvWriter.writeNext(
                                new String[]{
                                        String.valueOf(latitude),
                                        String.valueOf(longitude),
                                        description
                                });
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

