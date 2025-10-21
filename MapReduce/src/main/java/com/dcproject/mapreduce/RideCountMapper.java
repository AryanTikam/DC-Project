package com.dcproject.mapreduce;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;

public class RideCountMapper extends Mapper<LongWritable, Text, Text, IntWritable> {

    private final static IntWritable one = new IntWritable(1);
    private Text pickupLocation = new Text();

    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        // Assuming CSV format: ride_id,pickup,destination,fare
        String line = value.toString();
        String[] fields = line.split(",");

        if (fields.length >= 2) {
            String pickup = fields[1].trim(); // pickup location is the second field
            pickupLocation.set(pickup);
            context.write(pickupLocation, one);
        }
    }
}