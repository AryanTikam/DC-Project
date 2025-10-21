# MapReduce Jobs for Cab Management System Analytics

This project demonstrates multiple MapReduce jobs using Apache Hadoop to analyze ride data from a distributed cab booking system.

## Prerequisites

- Java 8 or higher
- Apache Maven
- Apache Hadoop (for running the jobs)

## Project Structure

```
MapReduce/
├── pom.xml
├── sample_input.txt
├── src/main/java/com/dcproject/mapreduce/
│   ├── RideCountDriver.java          # Original: Count rides by pickup location
│   ├── RideCountMapper.java
│   ├── RideCountReducer.java
│   ├── DriverPerformanceDriver.java  # New: Count rides per driver
│   ├── DriverPerformanceMapper.java
│   ├── DriverPerformanceReducer.java
│   ├── RouteFareDriver.java          # New: Average fare per route
│   ├── RouteFareMapper.java
│   ├── RouteFareReducer.java
│   ├── TimeUsageDriver.java          # New: Count rides per hour
│   ├── TimeUsageMapper.java
│   ├── TimeUsageReducer.java
│   ├── UserBehaviorDriver.java       # New: Count rides per user
│   ├── UserBehaviorMapper.java
│   └── UserBehaviorReducer.java
└── README.md
```

## Input Data Format

All jobs use CSV format: `ride_id,rider_name,pickup,destination,fare,driver_name,timestamp`

Example:
```
RIDE_1001,user1,Delhi,Mumbai,500.0,driver1,2023-10-21T10:00:00
```

## Available MapReduce Jobs

### 1. Ride Count by Pickup Location (Original)
- **Purpose**: Count rides originating from each pickup location
- **Command**: `hadoop jar target/mapreduce-job-1.0-SNAPSHOT.jar sample_input.txt output_ride_count`
- **Output**: `location count`

### 2. Driver Performance Analysis
- **Purpose**: Count rides completed by each driver
- **Command**: `hadoop jar target/mapreduce-job-1.0-SNAPSHOT.jar com.dcproject.mapreduce.DriverPerformanceDriver sample_input.txt output_driver_perf`
- **Output**: `driver_name ride_count`

### 3. Route and Fare Optimization
- **Purpose**: Calculate average fare for each pickup-destination route
- **Command**: `hadoop jar target/mapreduce-job-1.0-SNAPSHOT.jar com.dcproject.mapreduce.RouteFareDriver sample_input.txt output_route_fare`
- **Output**: `pickup-destination average_fare`

### 4. Time-Based Usage Patterns
- **Purpose**: Count rides by hour of day
- **Command**: `hadoop jar target/mapreduce-job-1.0-SNAPSHOT.jar com.dcproject.mapreduce.TimeUsageDriver sample_input.txt output_time_usage`
- **Output**: `hour ride_count`

### 5. User Behavior Insights
- **Purpose**: Count rides booked by each user
- **Command**: `hadoop jar target/mapreduce-job-1.0-SNAPSHOT.jar com.dcproject.mapreduce.UserBehaviorDriver sample_input.txt output_user_behavior`
- **Output**: `user_name ride_count`

## Building the Project

```bash
cd MapReduce
mvn clean package
```

This creates a shaded JAR file in the `target` directory.

## Running Jobs

### Local Mode (for testing)

```bash
# Example: Run ride count by pickup location
hadoop jar target/mapreduce-job-1.0-SNAPSHOT.jar com.dcproject.mapreduce.RideCountDriver sample_input.txt output_ride_count

# Example: Run driver performance analysis
hadoop jar target/mapreduce-job-1.0-SNAPSHOT.jar com.dcproject.mapreduce.DriverPerformanceDriver sample_input.txt output_driver_perf

# Example: Run route and fare optimization
hadoop jar target/mapreduce-job-1.0-SNAPSHOT.jar com.dcproject.mapreduce.RouteFareDriver sample_input.txt output_route_fare

# Example: Run time-based usage patterns
hadoop jar target/mapreduce-job-1.0-SNAPSHOT.jar com.dcproject.mapreduce.TimeUsageDriver sample_input.txt output_time_usage

# Example: Run user behavior insights
hadoop jar target/mapreduce-job-1.0-SNAPSHOT.jar com.dcproject.mapreduce.UserBehaviorDriver sample_input.txt output_user_behavior
```

### On Hadoop Cluster

1. Upload input data to HDFS:
```bash
hdfs dfs -put sample_input.txt /input/
```

2. Run a job:
```bash
hadoop jar target/mapreduce-job-1.0-SNAPSHOT.jar com.dcproject.mapreduce.DriverPerformanceDriver /input/sample_input.txt /output/driver_perf
```

3. View results:
```bash
hdfs dfs -cat /output/driver_perf/part-r-00000
```

## Expected Outputs (Sample Data)

### Driver Performance
```
driver1	3
driver2	3
driver3	4
```

### Route and Fare
```
Bangalore-Delhi	750.0
Chennai-Delhi	720.0
Delhi-Bangalore	825.0
Delhi-Chennai	700.0
Delhi-Mumbai	525.0
Mumbai-Bangalore	600.0
Mumbai-Chennai	650.0
Mumbai-Delhi	450.0
```

### Time-Based Usage
```
10	1
11	1
12	1
13	1
14	1
15	1
16	1
17	1
18	1
19	1
```

### User Behavior
```
user1	3
user2	2
user3	2
user4	1
user5	1
user6	1
```

## Integration with Your Cab Management System

These MapReduce jobs can be scheduled to run periodically on your ride data exported from the RPC servers. Use the insights for:
- **Driver Performance**: Optimize assignments and incentives
- **Route/Fare**: Implement dynamic pricing and route recommendations
- **Time Usage**: Plan staffing and surge pricing
- **User Behavior**: Develop loyalty programs and targeted marketing

For production, integrate with tools like Apache Oozie for workflow scheduling or export data directly to HDFS from your distributed servers.