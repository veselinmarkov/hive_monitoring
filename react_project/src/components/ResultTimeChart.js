
import { makeStyles } from '@material-ui/core/styles';
import { TimeSeries, Index, TimeRange } from 'pondjs';
import React, { useState, useEffect } from 'react';
import { LinearProgress, Typography, Box } from '@material-ui/core';
import {
    Charts,
    ChartContainer,
    ChartRow,
    YAxis,
    BarChart,
    Resizable, 
    LineChart,
} from "react-timeseries-charts";
import { getSamples } from '../api/hivedb';
import { TimeRangeBar } from './TimeRangeBar';
 
// Metrics "temp_low", "temp_high", "temp_out", "heat_pwr", "temp_hot", "humi_in", "humi_out"
const customColorsList = {
    "temp_low": "#1f77b4", 
    "temp_high": "#ff7f0e",
    "temp_out": "#aec7e8",
    "heat_pwr": "#d62728", 
    "temp_hot": "#ffbb78",
    "humi_in": "#2ca02c",
    "humi_out": "#98df8a", 
    /*"#d62728", "#ff9896", "#9467bd", "#c5b0d5",
    "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f",
    "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5"
    */
};

const useStyles = makeStyles((theme) => ({
    rootContainer: {
        border: "1px solid #ccc", 
        paddingTop: "0px", 
        paddingBottom: "0px",
    }
}));

// let timerange = new TimeRange(new Date('2020-01-03T08:00:00'), new Date('2020-01-03T09:00:00'));

export function ResultTimeChart({hive_id}) {    // user_id, hive_id, 
    const classes = useStyles();
    let date = new Date();
    date.setDate( date.getDate() - 3 );
    const [timerange, setTimerange] = useState(new TimeRange(date , new Date()));
    //let date = new Date('2020-02-15T09:00:00');
    //date.setDate( date.getDate() - 365 );
    //const [timerange, setTimerange] = useState(new TimeRange(date , new Date('2020-02-15T09:00:00')));
    //const [timerange, setTimerange] = useState(new TimeRange(new Date('2020-01-03T08:00:00'), new Date('2020-01-03T09:00:00')));
    const [data, setData] = React.useState({"items":[], "aggregation": "1m", "totalItems": 0});
    const [tracker, setTracker] = React.useState({tracker: null, trackerEvent: null, trackerX: null});
    const [activeDelay, setActiveDelay] = useState(false)
    const [activeQuery, setActiveQuery] = useState(false)
    // const user_id = props.user_id;
    // const hive_id = props.hive_id;
    //let series = {}

    useEffect( () => {
        if (activeDelay || ! hive_id) 
        // do not access server until delay in progress
            return;
        console.log('Charts Effect invoked');
        setActiveQuery(true);
        getSamples(hive_id, timerange).then((retData) => {
            //updataData = false;
            setData(retData.data.data);
            setActiveQuery(false);
        }).catch(err => {
            console.log({location: "ResultTimeChart; getSamples return", error: err});
            //setData({"items":[], "aggregation": "1m", "totalItems": 0});
            setActiveQuery(false);
        })
      }, [hive_id, activeDelay, timerange]);

    if (! hive_id )
      return (<h2>Please, choose a unit to display statistics</h2>);

    if (! data || data.length === 0)
        return (<h2>No data</h2>);

    //console.log(JSON.stringify(data));

    function show_bad_date(date_str) {
        try {
            return new Date(date_str)
        } catch (error) {
            console.log('Invalid date:', date_str)
            throw error
        }
    }
    const series = new TimeSeries({
        name: "Bio Unit statistics",
        columns: ["index", "temp_low", "temp_high", "temp_out", "heat_pwr", "temp_hot", "humi_in", "humi_out"],
        points: data.items.map((rec) => [
//            Index.getIndexString(data.aggregation, new Date(rec.sample_time)),
            Index.getIndexString(data.aggregation, show_bad_date(rec.sample_time)),
            rec.temp_low,
            rec.temp_high,
            rec.temp_out,
            rec.heat_pwr,
            rec.temp_hot,
            rec.humi_in,
            rec.humi_out,
        ])
    });
   
    /* if (! timerange)
        setTimerange(new TimeRange(new Date('01/01/2020'), new Date('02/01/2020')))
 */

    /* const series = new TimeSeries({
        name: "Bio Unit statistics",
        columns: ["time", "temp_low", "temp_high", "heat_pwr"],
        points: data.map((rec) => [
            new Date(rec.sample_time),
            rec.temp_low,
            rec.temp_high,
            rec.heat_pwr
        ])
    }); */
    
    /* let dailySeries = series.dailyRollup({
        aggregation: {success: {success: avg()}},
        toTimeEvents: false 
    }) */

    //console.log(JSON.stringify(series));

    //console.log(series.min("temp_high"), series.max("temp_high"));

    const handleTimeRangeChange = newTimerange => {
        setTimerange(newTimerange);
        //timerange = newTimerange;
        if (! activeDelay) {
            // console.log('Set Active delay true and start the timer');
            setActiveDelay(true);
            setTimeout(() => { setActiveDelay(false)}, 1000)
        }
        //console.log(timerange);
    };

    const handleTrackerChanged = (t, scale) => {
        setTracker({
            tracker: t,
            trackerEvent: t && series.at(series.bisect(t)),
            trackerX: t && scale(t)
        });
    };

    
    // create LineChart styles for every temperature color
    const line_styles = Object.assign({}, ...Object.entries(customColorsList).map(([k, v])=> (
        { 
            [k]: {
                [k]: { 
                    normal: {
                        stroke: v,
                        strokeWidth: 2,
                        opacity: 0.5
                    }
                }
            }
        }
    )));

    /*
    const markerStyle = {
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        color: "#AAA",
        marginLeft: "5px"
    }
    */
    // create marker color styles for every temperature color, using example markerStyle above
    const markerStyle = Object.assign({}, ...Object.entries(customColorsList).map(([k, v])=> (
        { 
            [k]: {
                backgroundColor: 'rgba(255, 255, 255, 0.8)',
                color: v,
                marginLeft: "5px"
            }
        }
    )));

    function my_min(arr) {
        let min_val = Number.MAX_VALUE
        for (const v of arr) {
            if (! isNaN(v) && (v < min_val))
                min_val = v;
        }
        return min_val
    }

    function my_max(arr) {
        let max_val = Number.MIN_VALUE
        for (const v of arr) {
            if (! isNaN(v) && (v > max_val))
                max_val = v;
        }
        return max_val
    }

    const updateLastDays = (event, days) => {
        console.log("In updateLastDays:", days);
        let date = new Date();
        date.setDate( date.getDate() - days );
        setTimerange(new TimeRange(date , new Date()));
    }

    return (
        <React.Fragment>
        <Typography variant="subtitle1">
            Time period:{timerange.begin().toLocaleString()} - {timerange.end().toLocaleString()}
        </Typography>
        <Typography variant="subtitle1">
            Granularity: {data.aggregation}, Samples: {data.totalItems} {tracker.tracker ? ", Marker: "+tracker.tracker.toLocaleString() : ""}
        </Typography>
        <TimeRangeBar handleRangeChange = {updateLastDays}/>
        { tracker.trackerEvent ?
            <div style={{position: 'relative'}}>
                <div style={{position: 'absolute', left: tracker.trackerX, top: '30px'}}>
                    <div style={markerStyle["temp_low"]}>Temp low: {Number(tracker.trackerEvent.get('temp_low')).toFixed(2)}</div>
                    <div style={markerStyle["temp_high"]}>Temp high: {Number(tracker.trackerEvent.get('temp_high')).toFixed(2)}</div>
                    <div style={markerStyle["temp_out"]}>Temp out: {Number(tracker.trackerEvent.get('temp_out')).toFixed(2)}</div>
                </div>
                <div style={{position: 'absolute', left: tracker.trackerX, top: '160px' }}>
                    <div style={markerStyle["heat_pwr"]}>Heat pwr: {Number(tracker.trackerEvent.get('heat_pwr')).toFixed(2)}</div>
                </div>
                <div style={{position: 'absolute', left: tracker.trackerX, top: '290px' }}>
                    <div style={markerStyle["temp_hot"]}>Temp hot: {Number(tracker.trackerEvent.get('temp_hot')).toFixed(2)}</div>
                </div>
                <div style={{position: 'absolute', left: tracker.trackerX, top: '420px' }}>
                    <div style={markerStyle["humi_in"]}>Humi in: {Number(tracker.trackerEvent.get('humi_in')).toFixed(2)}</div>
                    <div style={markerStyle["humi_out"]}>Humi out: {Number(tracker.trackerEvent.get('humi_out')).toFixed(2)}</div>
                </div>
                {/*
                <div style={{position: 'absolute', left: tracker.trackerX, top: '550px' }}>
                    <div style={markerStyle["temp_low"]}>Hot air: {Number(tracker.trackerEvent.get('temp_hot')).toFixed(2)}</div>
                </div>
                <div style={{position: 'absolute', left: tracker.trackerX, top: '680px' }}>
                    <div style={markerStyle["temp_low"]}>Humi in: {Number(tracker.trackerEvent.get('humi_in')).toFixed(2)}</div>
                </div>
                <div style={{position: 'absolute', left: tracker.trackerX, top: '810px' }}>
                    <div style={markerStyle["temp_low"]}>Humi out: {Number(tracker.trackerEvent.get('humi_out')).toFixed(2)}</div>
                </div>
                */}
            </div>
        : null }
        <Box sx={{minHeight:5}}>
            { activeQuery && <LinearProgress/>}
        </Box>
        <Resizable className={classes.rootContainer}>
        {/* <Button disabled={activeQuery}/>    */}
        <ChartContainer timeRange={series ? timerange: null} 
            trackerPosition={tracker.tracker}
            onTrackerChanged={handleTrackerChanged}
            title="Hive Metrics" 
            //format="day" 
            utc={false}
            //padding ={0}
            enablePanZoom={true}
            onTimeRangeChanged={handleTimeRangeChange}
            >
            <ChartRow height="130">
                <YAxis
                    id="temp_all"
                    label="deg"
                    min={my_min([series.min("temp_out"), series.min("temp_low"), series.min("temp_high")])}
                    max={my_max([series.max("temp_out"), series.max("temp_low"), series.max("temp_high")])}
                    format=".2f"
                    width="70"
                    type="linear"
                />
                <Charts>
                    <LineChart
                        axis="temp_all"
                        //style={{success: {normal: {fill: "#e34d7d"}}}}
                        style = {line_styles["temp_low"]}
                        spacing={5}
                        columns={["temp_low"]}
                        series={series}
                        //radius={5.0}
                    />
                    <LineChart
                        axis="temp_all"
                        //style={{success: {normal: {fill: "#e34d7d"}}}}
                        style = {line_styles["temp_high"]}
                        spacing={5}
                        columns={["temp_high"]}
                        series={series}
                        radius={5.0}
                    />
                    <LineChart
                        axis="temp_all"
                        //style={{success: {normal: {fill: "#e34d7d"}}}}
                        style = {line_styles["temp_out"]}
                        spacing={5}
                        columns={["temp_out"]}
                        series={series}
                        radius={5.0}
                    />
                </Charts>
            </ChartRow>     
            {/*       
            <ChartRow height="130">
                <YAxis
                    id="temp_high"
                    label="deg"
                    min={series.min("temp_high")}
                    max={series.max("temp_high")}
                    format=".2f"
                    width="70"
                    type="linear"
                />
                <Charts>
                    <LineChart
                        axis="temp_high"
                        //style={{success: {normal: {fill: "#e34d7d"}}}}
                        spacing={5}
                        columns={["temp_high"]}
                        series={series}
                        radius={5.0}
                    />
                </Charts>
            </ChartRow>
        */}
            <ChartRow height="130">
                <YAxis
                    id="heat_power"
                    label="power %"
                    min={0}
                    max={series.max("heat_pwr")}
                    format=".2f"
                    width="70"
                    type="linear"
                />
                <Charts>
                    <BarChart
                        axis="heat_power"
                        //style={{heat_pwr: {normal: {fill: "#e34d7d"}}}}
                        style = {line_styles["heat_pwr"]}
                        spacing={5}
                        columns={["heat_pwr"]}
                        series={series}
                        //radius={5.0}
                    />
                </Charts>
            </ChartRow>        
            <ChartRow height="130">
                <YAxis
                    id="temp_hot"
                    label="deg"
                    min={series.min("temp_hot")}
                    max={series.max("temp_hot")}
                    format=".2f"
                    width="70"
                    type="linear"
                />
                <Charts>
                    <LineChart
                        axis="temp_hot"
                        style={line_styles["temp_hot"]}
                        spacing={5}
                        columns={["temp_hot"]}
                        series={series}
                        radius={5.0}
                    />
                </Charts>
            </ChartRow>
            <ChartRow height="130">
                <YAxis
                    id="humi_in"
                    label="%"
                    min={my_min([series.min("humi_in"), series.min("humi_out")])}
                    max={my_max([series.max("humi_in"), series.max("humi_out")])}
                    format=".2f"
                    width="70"
                    type="linear"
                />
                <Charts>
                    <LineChart
                        axis="humi_in"
                        style={line_styles["humi_in"]}
                        spacing={5}
                        columns={["humi_in"]}
                        series={series}
                        radius={5.0}
                    />
                    <LineChart
                        axis="humi_in"
                        style={line_styles["humi_out"]}
                        spacing={5}
                        columns={["humi_out"]}
                        series={series}
                        radius={5.0}
                    />
                </Charts>
            </ChartRow>
        </ChartContainer>
        </Resizable>
        </React.Fragment>
    );
}