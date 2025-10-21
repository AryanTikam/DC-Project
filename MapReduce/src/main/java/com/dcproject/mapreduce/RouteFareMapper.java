package com.dcproject.mapreduce;

import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;

public class RouteFareMapper extends Mapper<LongWritable, Text, Text, DoubleWritable> {

    private Text route = new Text();
    private DoubleWritable fare = new DoubleWritable();

    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        // CSV format: ride_id,rider_name,pickup,destination,fare,driver_name,timestamp
        String line = value.toString();
        String[] fields = line.split(",");

        if (fields.length >= 5) {
            String pickup = fields[2].trim();
            String destination = fields[3].trim();
            String routeKey = pickup + "-" + destination;
            double fareValue = Double.parseDouble(fields[4].trim());

            route.set(routeKey);
            fare.set(fareValue);
            context.write(route, fare);
        }
    }
}