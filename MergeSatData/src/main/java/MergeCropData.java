//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
import com.opencsv.CSVWriter;
import com.opencsv.CSVReader;
import com.opencsv.exceptions.CsvValidationException;

import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.BufferedReader;

import java.util.HashMap;
import java.util.Map;

public class MergeCropData {

    private static String[] record;

    public static void main(String[] args) {
        if (args.length != 4) {
            System.err.println("Usage: java mergeCropData <truthDataCSV> <satelliteDataCSV> <outputCSV> <minDistance>");
            System.exit(1);
        }

        String truthDataCSV = args[0];
        String satelliteDataCSV = args[1];
        String outputCSV = args[2];
        int minDistance = Integer.parseInt(args[3]);

        Map<Pair, String> truthDataMap = new HashMap<>();

        // Read truthCSVReader into memory - all of it

        try (BufferedReader br = new BufferedReader(new FileReader(truthDataCSV))) {
            String line;

            // Read the header row (optional)
            line = br.readLine();

            while ((line = br.readLine()) != null) {

                String[] parts = line.split(",");
                if (parts.length >= 3) {
                    double latitude = Double.parseDouble(parts[0].trim());
                    double longitude = Double.parseDouble(parts[1].trim());
                    String description = parts[2].trim();

                    // Create a Pair object for latitude and longitude
                    Pair coordinates = new Pair(latitude, longitude);

                    // Populate the map with the key-value pair
                    truthDataMap.put(coordinates, description);
                }
            }

        } catch (IOException e) {
            e.printStackTrace();
        }

        System.out.println("Truth data CSV file read successfully.");

        try (CSVReader satCSVReader = new CSVReader(new FileReader(satelliteDataCSV));
             CSVWriter csvWriter = new CSVWriter(new FileWriter(outputCSV),
                     CSVWriter.DEFAULT_SEPARATOR,
                     CSVWriter.NO_QUOTE_CHARACTER, // Remove extra quotes
                     CSVWriter.NO_ESCAPE_CHARACTER,
                     CSVWriter.DEFAULT_LINE_END)) {

            csvWriter.writeNext(new String[]{"Latitude", "Longitude", "CropType","B02", "B08", "B11"});

            String[] record;
            int lineNumber = 0;
            int matchCount = 0;
            double closestPoint = 1000000.0;

            // Read the header row (optional)
            String[] headerRow = satCSVReader.readNext();

            // Process each record incrementally
            while ((record = satCSVReader.readNext()) != null) {
                lineNumber++;
                if (lineNumber % 100 == 0) {
                    System.out.print("\rProcessing satellite data record " + lineNumber + " Matches: " + matchCount);
                    System.out.flush();
                }

                // Extract long and lat - note the order of columns
                double satLong = Double.parseDouble(record[0]);
                double satLat = Double.parseDouble(record[1]);

                // Iterate through every single truth record, and try to find a "close" record
                for (Map.Entry<Pair, String> truthDataItem : truthDataMap.entrySet()) {

                    double truthLat = truthDataItem.getKey().latitude;
                    double truthLong = truthDataItem.getKey().longitude;

                    double distance = calculateDistance(satLat, satLong, truthLat, truthLong);

                    if (distance <= minDistance) {
                        // Close enough! Output this record
                        matchCount++;

                        if (distance < closestPoint) closestPoint = distance;

                        String truthDescription = truthDataItem.getValue();
                        csvWriter.writeNext(
                                new String[]{
                                        String.valueOf(satLat),
                                        String.valueOf(satLong),
                                        String.valueOf(Math.round(distance)),
                                        truthDescription,
                                        record[2], // "B02", "B08", "B11"
                                        record[3],
                                        record[4]
                                        // TODO: write all of the other features from the sat data
                                });
                    }
                }
            }

            System.out.println("\nCSV file generated successfully: match count " + matchCount);
        } catch (IOException e) {
            e.printStackTrace();
        } catch (CsvValidationException e) {
            throw new RuntimeException(e);
        }
    }

    // Calculate the Euclidean distance in meters between two points
    public static double calculateDistance(double lat1, double lon1, double lat2, double lon2) {
        // Radius of the Earth in meters
        final double EARTH_RADIUS_METERS = 6371000.0;

        // Convert latitude and longitude to radians
        lat1 = Math.toRadians(lat1);
        lon1 = Math.toRadians(lon1);
        lat2 = Math.toRadians(lat2);
        lon2 = Math.toRadians(lon2);

        // Calculate differences
        double dLat = lat2 - lat1;
        double dLon = lon2 - lon1;

        return Math.sqrt(dLat * dLat + dLon * dLon) * EARTH_RADIUS_METERS;
    }

    // Record class for holding latitude and longitude together
    record Pair(double latitude, double longitude) {
        // No need to define getters as they are automatically generated by records
    }
}


