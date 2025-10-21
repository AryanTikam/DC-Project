package com.dcproject.mapreduce;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;

public class UserBehaviorMapper extends Mapper<LongWritable, Text, Text, IntWritable> {

    private final static IntWritable one = new IntWritable(1);
    private Text userName = new Text();

    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        // CSV format: ride_id,rider_name,pickup,destination,fare,driver_name,timestamp
        String line = value.toString();
        String[] fields = line.split(",");

        if (fields.length >= 2) {
            String user = fields[1].trim(); // rider_name is the 2nd field
            userName.set(user);
            context.write(userName, one);
        }
    }
}