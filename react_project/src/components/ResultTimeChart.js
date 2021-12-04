
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
    //new TimeRange(date.setFullYear( date.getFullYear() - 1 ) , new Date())
    const [timerange, setTimerange] = useState(new TimeRange(new Date('2020-01-03T08:00:00'), new Date('2020-01-03T09:00:00')));
    const [data, setData] = React.useState({"items":[], "aggregation": "1m", "totalItems": 0});
    const [tracker, setTracker] = React.useState({tracker: null, trackerEvent: null, trackerX: null});
    const [activeDelay, setActiveDelay] = useState(false)
    const [activeQuery, setActiveQuery] = useState(false)
    // const user_id = props.user_id;
    // const hive_id = props.hive_id;
    //let series = {}

    useEffect( () => {
        if (activeDelay) 
        // do not access server until delay in progress
            return;
        console.log('Effect invoked');
        setActiveQuery(true);
        getSamples(hive_id, timerange).then((retData) => {
            //updataData = false;
            setData(retData.data.data);
            setActiveQuery(false);
        }).catch(err => {
            console.log({location: "ResultTimeChart; getSamples return", error: err});
            setData(null);
            setActiveQuery(false);
        })
      }, [hive_id, activeDelay, timerange]);

    if (! data || data.length === 0)
        return (<h2>No data</h2>);

    //console.log(JSON.stringify(data));

    const series = new TimeSeries({
        name: "Bio Unit statistics",
        columns: ["index", "temp_low", "temp_high", "heat_pwr", "temp_out"],
        points: data.items.map((rec) => [
            Index.getIndexString(data.aggregation, new Date(rec.sample_time)),
            rec.temp_low,
            rec.temp_high,
            rec.heat_pwr,
            rec.temp_out,
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

    const markerStyle = {
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        color: "#AAA",
        marginLeft: "5px"
    }

    return (
        <React.Fragment>
        <Typography variant="h6">
            Time period:{timerange.begin().toLocaleString()} - {timerange.end().toLocaleString()}
        </Typography>
        <Typography variant="h6">
            Granularity: {data.aggregation}, Samples: {data.totalItems} {tracker.tracker ? ", Marker: "+tracker.tracker.toLocaleString() : ""}
        </Typography>
        { tracker.trackerEvent ?
            <div style={{position: 'relative'}}>
                <div style={{position: 'absolute', left: tracker.trackerX, top: '30px'}}>
                    <div style={markerStyle}>Temp low: {Number(tracker.trackerEvent.get('temp_low')).toFixed(2)}</div>
                </div>
                <div style={{position: 'absolute', left: tracker.trackerX, top: '160px' }}>
                    <div style={markerStyle}>Temp high: {Number(tracker.trackerEvent.get('temp_high')).toFixed(2)}</div>
                </div>
                <div style={{position: 'absolute', left: tracker.trackerX, top: '290px' }}>
                    <div style={markerStyle}>Power: {Number(tracker.trackerEvent.get('heat_pwr')).toFixed(2)}</div>
                </div>
                <div style={{position: 'absolute', left: tracker.trackerX, top: '420px' }}>
                    <div style={markerStyle}>Temp out: {Number(tracker.trackerEvent.get('temp_out')).toFixed(2)}</div>
                </div>
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
            title="Temperature statistics over the past month" 
            //format="day" 
            utc={false}
            //padding ={0}
            enablePanZoom={true}
            onTimeRangeChanged={handleTimeRangeChange}
            >
            <ChartRow height="130">
                <YAxis
                    id="temp_low"
                    label="deg"
                    min={series.min("temp_low")}
                    max={series.max("temp_low")}
                    format=".2f"
                    width="70"
                    type="linear"
                />
                <Charts>
                    <LineChart
                        axis="temp_low"
                        //style={{success: {normal: {fill: "#e34d7d"}}}}
                        spacing={5}
                        columns={["temp_low"]}
                        series={series}
                        //radius={5.0}
                    />
                </Charts>
            </ChartRow>            
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
                    {/* <LineChart
                        axis="heat_power"
                        //style={{success: {normal: {fill: "#e34d7d"}}}}
                        spacing={5}
                        columns={["heat_pwr"]}
                        series={series}
                        //radius={5.0}
                    /> */}
                    <BarChart
                        axis="heat_power"
                        style={{heat_pwr: {normal: {fill: "#e34d7d"}}}}
                        spacing={5}
                        columns={["heat_pwr"]}
                        //style={upDownStyle}
                        series={series}
                        //radius={5.0}
                    />
                </Charts>
            </ChartRow>        
            <ChartRow height="130">
                <YAxis
                    id="temp_out"
                    label="deg"
                    min={series.min("temp_out")}
                    max={series.max("temp_out")}
                    format=".2f"
                    width="70"
                    type="linear"
                />
                <Charts>
                    <LineChart
                        axis="temp_out"
                        //style={{success: {normal: {fill: "#e34d7d"}}}}
                        spacing={5}
                        columns={["temp_out"]}
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