import React from 'react';
import {Container, Grid, Paper, CssBaseline, 
  Typography, Divider } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import Control from './components/Control';
import { ResultTimeChart } from './components/ResultTimeChart';

const useStyles = makeStyles((theme) => ({
  rootContainer: {
    paddingTop: "0", 
    border: "2px solid #e34d7d", 
    borderRadius: "7px",
    marginTop: "60px",
    //height: "100vh"
  },
  container: {
    alignItems: "stretch",
    margin: "5px 0px 5px",
    flexWrap: "nowrap",
    height:"100%",
  },
  main: {
    flexGrow: 1,
  },
  mainPaper: {
    height: "100%",
    display: "flex",
    flexDirection: "column",
    padding: "15px",
  },
  mainDivider: {
    flexGrow: 1,
    minHeight: "20px",
  },
}));

//var updataData = true;

export default function Dashboard({user}) { //current user: {user_id, user_name}
  // const [user, setUser] = React.useState({ id:"Guest" });
  const [id, setId] = React.useState(0); // unit id
  // const [data, setData] = React.useState([]);
  const classes = useStyles();

  /* useEffect( () => {
    //if (updataData) {
      getSamples(id).then((retData) => {
        //updataData = false;
        setData(retData);
        console.log('Effect invoked');
      });
    //}
  }, [id]); */
  
  const handleIdChange = (id) => {
    //updataData =true;
    setId(id);
  }

  const testUnitList = [
        {id: 1, text: "Bio Unit #1"},
        {id: 2, text: "Bio Unit #2"},
        {id: 3, text: "Bio Unit #3"},
        {id: 4, text: "Bio Unit #4"},
        {id: 5, text: "Bio Unit #5"},
        {id: 6, text: "Bio Unit #6"},
        {id: 7, text: "Bio Unit #7"},
        {id: 8, text: "Bio Unit #8"},
        {id: 9, text: "Bio Unit #9"},
    ]
  
  const allowedList = user && user.user_name ==="reader" ? testUnitList : [];  

  /* const testSamples = [
    {"hive":1,"sample_time":"2020-06-01T00:00:00.000Z","temp_low":"19.353","temp_high":0,"temp_hot":"22.470","temp_out":13,"temp_target":"-10.000","humi_in":"71.77","humi_out":null,"heat_pwr":null,"fan":746,"mode":"monitor","heater_breakers":10},
    {"hive":1,"sample_time":"2020-06-01T01:00:00.000Z","temp_low":"19.008","temp_high":null,"temp_hot":"22.215","temp_out":13,"temp_target":"-10.000","humi_in":"72.41","humi_out":null,"heat_pwr":10,"fan":746,"mode":"monitor","heater_breakers":10},
    {"hive":1,"sample_time":"2020-06-01T02:00:00.000Z","temp_low":"18.409","temp_high":5,"temp_hot":"21.634","temp_out":12,"temp_target":"-10.000","humi_in":"70.73","humi_out":null,"heat_pwr":NaN,"fan":749,"mode":"monitor","heater_breakers":10},
    {"hive":1,"sample_time":"2020-06-01T03:00:00.000Z","temp_low":"17.577","temp_high":1,"temp_hot":"20.691","temp_out":11,"temp_target":"-10.000","humi_in":"70.60","humi_out":null,"heat_pwr":0,"fan":746,"mode":"monitor","heater_breakers":10},
    {"hive":1,"sample_time":"2020-06-01T04:00:00.000Z","temp_low":"17.743","temp_high":null,"temp_hot":"20.876","temp_out":13,"temp_target":"-10.000","humi_in":"72.77","humi_out":null,"heat_pwr":0,"fan":749,"mode":"monitor","heater_breakers":10},
    {"hive":1,"sample_time":"2020-06-01T05:00:00.000Z","temp_low":"18.435","temp_high":null,"temp_hot":"21.491","temp_out":14,"temp_target":"-10.000","humi_in":"72.25","humi_out":null,"heat_pwr":0,"fan":747,"mode":"monitor","heater_breakers":10},
    {"hive":1,"sample_time":"2020-06-01T06:00:00.000Z","temp_low":"18.767","temp_high":null,"temp_hot":"21.686","temp_out":15,"temp_target":"-10.000","humi_in":"68.90","humi_out":null,"heat_pwr":0,"fan":854,"mode":"monitor","heater_breakers":10},
    {"hive":1,"sample_time":"2020-06-01T07:00:00.000Z","temp_low":"19.797","temp_high":null,"temp_hot":"22.504","temp_out":18,"temp_target":"-10.000","humi_in":"66.04","humi_out":null,"heat_pwr":0,"fan":742,"mode":"monitor","heater_breakers":10},
    {"hive":1,"sample_time":"2020-06-01T08:00:00.000Z","temp_low":"21.270","temp_high":null,"temp_hot":"24.139","temp_out":20,"temp_target":"-10.000","humi_in":"62.21","humi_out":null,"heat_pwr":0,"fan":915,"mode":"monitor","heater_breakers":10},
  ]; */

  return (
    <Container component="main" maxWidth="lg" className={classes.rootContainer}>
      <CssBaseline />
      {/* <Navbar user={user} updateUser={handleUser}/> */}
      <Grid container className={classes.container} spacing={1}>
          <Control id={id} unitList={allowedList} handleIdChange={handleIdChange}/>
        <Grid item className={classes.main}>
          <Paper className={classes.mainPaper}>
            {/*<img alt="Beehive" src={MyImage}/>*/}
            <Typography variant="h6">
              Unit id {id} properties
            </Typography>
            <Divider/>
            <div className={classes.mainDivider}/>
            <ResultTimeChart user_id="1" hive_id={id}/>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}
