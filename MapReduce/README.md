# MapReduce Job for Ride Count by Pickup Location

This project demonstrates a simple MapReduce job using Apache Hadoop to count the number of rides originating from each pickup location.

## Prerequisites

- Java 8 or higher
- Apache Maven
- Apache Hadoop (for running the job)

## Project Structure

```
MapReduce/
├── pom.xml
├── sample_input.txt
├── src/main/java/com/dcproject/mapreduce/
│   ├── RideCountDriver.java
│   ├── RideCountMapper.java
│   └── RideCountReducer.java
└── README.md
```

## Components

### RideCountMapper
- Reads input lines in CSV format: `ride_id,pickup,destination,fare`
- Emits key-value pairs: `(pickup_location, 1)`

### RideCountReducer
- Aggregates counts for each pickup location
- Outputs: `(pickup_location, total_count)`

### RideCountDriver
- Configures and runs the MapReduce job
- Sets input and output paths

## Building the Project

```bash
cd MapReduce
mvn clean package
```

This will create a shaded JAR file in the `target` directory.

## Running the MapReduce Job

### Local Mode (for testing)

```bash
hadoop jar target/mapreduce-job-1.0-SNAPSHOT.jar com.dcproject.mapreduce.RideCountDriver sample_input.txt output
```

### On Hadoop Cluster

1. Upload input data to HDFS:
```bash
hdfs dfs -put sample_input.txt /input/
```

2. Run the job:
```bash
hadoop jar target/mapreduce-job-1.0-SNAPSHOT.jar com.dcproject.mapreduce.RideCountDriver /input/sample_input.txt /output/ride_counts
```

3. View results:
```bash
hdfs dfs -cat /output/ride_counts/part-r-00000
```

## Expected Output

For the sample input, you should see output like:
```
Bangalore	1
Chennai	1
Delhi	5
Mumbai	3
```

This shows the count of rides starting from each location.

## Customization

You can modify the input format or the logic by editing the Mapper and Reducer classes. For example:
- Change the CSV parsing logic
- Count by destination instead of pickup
- Calculate average fares per location

## Integration with Your Cab Management System

This MapReduce job can be used to analyze ride data from your distributed cab booking system. You could:
- Process logs to find popular pickup locations
- Analyze fare patterns
- Generate reports on system usage

To integrate, you would need to:
1. Export ride data to HDFS in the expected format
2. Schedule the job to run periodically
3. Use the output for analytics or decision making