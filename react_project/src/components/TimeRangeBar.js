import {Toolbar, Typography, Button } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({ 
    container: {
      display: "flex",
      //gap: "10px",
      //flexDirection: "column",
      //padding: "35px",
    //   border: "2px solid #e34d7d", 
      border: "2px solid",
      borderColor: theme.palette.primary.main,
      borderRadius: "5px",
      //width: "300px",
    //   backgroundColor: theme.palette.primary.main,
    //   color: "primary",
    },
    //inputText: {
    //    backgroundColor: theme.palette.background.default
    //},
    button1: {
      //maxWidth: "156px",
      //maxHeight: "64px",
      // backgroundColor: "#3f51b5",
      background: theme.palette.primary.main,
      color: "#fff",
      fontSize: theme.typography.body1,
    },
}));

export function TimeRangeBar({handleRangeChange}) { //{function to invoke with new timeRange}
    const classes = useStyles();

    return (
        <Toolbar className={classes.container}>
            <Button className={classes.button} onClick={(event) => handleRangeChange( event, 1)}>
                Last Day
            </Button>
            <Button className={classes.button} color="inherit" onClick={(event) => handleRangeChange( event, 3)}>
                Last 3 days
            </Button>
            <Button className={classes.button} color="inherit" onClick={(event) => handleRangeChange( event, 7)}>
                Last week
            </Button>
            <Button className={classes.button} color="inherit" onClick={(event) => handleRangeChange( event, 30)}>
                Last month
            </Button>
            <Button className={classes.button} color="inherit" onClick={(event) => handleRangeChange( event, 365)}>
                Last year
            </Button>
            <div style={{flexGrow: 1}}/>
            <Typography variant="body2"  style={{ minWidth:"100px"}}>Turn mouse scroller to zoom, drag the mouse to pan</Typography>
        </Toolbar>
    )
}
