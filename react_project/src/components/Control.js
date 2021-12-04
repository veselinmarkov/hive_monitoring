import React from 'react';
import {Card, CardHeader, CardActionArea} from '@material-ui/core';
import { HomeOutlined} from '@material-ui/icons';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
    sidebar: {
      width: "40%",
      maxWidth: "330px",
      display: "flex",
      flexDirection: "row",
      flexWrap: "wrap",
      padding: 10,
      height: "100%",
      '& > *': {
        margin: theme.spacing(0.5),
      }
    },
    inCardButton: {
      padding: "unset"
    },
    card: {
      maxWidth: "156px",
      maxHeight: "64px",
      // backgroundColor: "#3f51b5",
      background: theme.palette.primary.main,
      color: "#fff",
    },
    cardMarker: {
      color: "#fff",
      // backgroundColor: "#e34d7d"
      backgroundColor: theme.palette.secondary.main,
    },
    empty: {}
  }));

export default function Control({id, unitList, handleIdChange}) {
    /* 
    id - current unit id;
    unitList: [
      {id: 1, text: "Bio Unit #1"},
      {id: 2, text: "Bio Unit #2"},
      {id: 3, text: "Bio Unit #3"},
    ] ;
    handleIdChange - handler to execute when unit id has changed;
    */
    const classes = useStyles();
    
    const handleClick = (e) => {
        //console.log(e.currentTarget.id);
        if (handleIdChange)
            handleIdChange( Number(e.currentTarget.id));
    }

    return (
        <div className={classes.sidebar}>
            {unitList.map(element => {
                return (<Card className={classes.card} 
                    onClick={handleClick} key={element.id} id={element.id}>
                    <CardActionArea>
                    <CardHeader 
                      avatar={<HomeOutlined />} 
                      title={element.text}
                      className={ (element.id === id) ? classes.cardMarker : classes.empty}
                      /*
                      action={
                        <IconButton aria-label="settings" className={classes.inCardButton}>
                          <HighlightOffOutlined/>
                        </IconButton>
                      }
                      */
                      />
                    </CardActionArea>
                  </Card>)
            })}
            {/*
            <Card className={classes.card, classes.cardMarker} onClick={handleClick}>
            <CardActionArea>
            <CardHeader 
              avatar={<HomeOutlined />} 
              title="Bio Unit #1"
              action={
                <IconButton aria-label="settings" className={classes.inCardButton}>
                  <HighlightOffOutlined/>
                </IconButton>
              }/>
            </CardActionArea>
          </Card>
          <Card className={classes.card}>
            <CardHeader 
              avatar={<HomeOutlined />} 
              title="Bio Unit #2"
              action={
                <IconButton aria-label="settings" className={classes.inCardButton}>
                  <HighlightOffOutlined/>
                </IconButton>
              }/>
          </Card>
          <Card className={classes.card}>
            <CardHeader 
              avatar={<HomeOutlined />} 
              title="Bio Unit #3"
              action={
                <IconButton aria-label="settings" className={classes.inCardButton}>
                  <HighlightOffOutlined/>
                </IconButton>
              }/>
          </Card>
            */}
        </div>
    )
}