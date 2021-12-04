// import { FormatLineSpacingRounded } from "@material-ui/icons"
import {Container, Box, Typography, 
    List, ListItem, ListItemIcon, ListItemText} from '@material-ui/core';
import MyFlower from '../pictures/flowers_wide.jpg';
import MyFlower_long from '../pictures/flowers_long.jpg';
import MyBee from '../pictures/bee.jpg';
import MyLogo from '../pictures/bee_logo_f4.svg' ;
import CheckCircleRoundedIcon from '@material-ui/icons/CheckCircleRounded';
import { makeStyles } from '@material-ui/core/styles'; 
import { Copyright } from '@material-ui/icons';

const useStyles = makeStyles((theme) => ({
    rootContainer: {
      padding: "0px 20px", 
      margin: "70px 5px 0px", 
    //   border: "2px solid #e34d7d", 
      borderRadius: "7px",
      //height: "100vh"
        //backgroundImage: "linear-gradient(rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.5)),url('/static/media/beehive.471e8a0b.png')",
        backgroundImage: `linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9)),url(${MyFlower})`,
        backgroundRepeat: "no-repeat",
        backgroundPosition: "center center",
        backgroundSize: "cover",
        backgroundAttachment: "scroll",
    },
    container: {
      alignItems: "stretch",
      margin: "50px 5px",
      flexWrap: "nowrap",
    //   height:"1500px",
    },
    footerContainer: {
        margin: "0px 25px", 
        marginBottom: "0px", 
        position: "relative", 
        height:"100px"
    },
    copyright: {
        display: "flex",
        flexDirection: "row", 
        alignItems: "center",
        color: theme.palette.secondary.main,
        position: "absolute", 
        right: "30px", 
        bottom: "10px"
    }
  }))

export default function FrontPage() {
    const classes = useStyles();

    const introLines = [
        { "id": 1, "text": "Continuous beehive climate supervision and control through Internet" },
        { "id": 2, "text": "Keeping optimal temperature and humidity for the bee colony during the winter period" },
        { "id": 3, "text": "Protection of the bee colony and its brood during the cold spring turnovers" },
        { "id": 4, "text": "Beehive sound transmission to the beekeeper and its recording" },
        { "id": 5, "text": "Possibility to initiate cleansing flights during windless or warm winter days" },
        { "id": 6, "text": "Enhance beehive ventilation during the hot summer days" },
    ]

    return (
        <Container component="main" maxWidth="lg" className={classes.rootContainer}>
          {/* <div className={classes.container}> */}
            <Box sx={{display: "flex", alignItems:"center"}}>                
                <img alt="Logo" src={MyLogo} width="230"/> 
                <Box> 
                    <Typography variant="h1" color="primary">
                        BeeComfort
                    </Typography>
                    <Typography variant="h4" color="secondary">
                        Comfort ambient for your Honey bees
                    </Typography>
                </Box>
            </Box>
            <Box sx={{margin: "25px", marginBottom: "0px", position: "relative", height:"300px"}}>
                <img alt="Flower" src={MyFlower_long} width="1100" style={{position: "absolute", bottom: "40px", right: "45px"}}/>
                <img alt="Bee" src={MyBee} width="200" style={{position: "absolute", bottom: "0px", right: "0px"}}/>
            </Box>
            <List style={{marginLeft: "100px"}}>
                {introLines.map( item => (
                    <ListItem key={item.id}>
                        <ListItemIcon><CheckCircleRoundedIcon color="primary"/></ListItemIcon>
                        <ListItemText>
                            <Typography variant="h6">{item.text}</Typography>    
                        </ListItemText>
                    </ListItem>
                ))}
            </List>
            <Box className= {classes.footerContainer}>
                <Box className ={classes.copyright}>
                    <Copyright style={{marginLeft: 5}}/>
                    <Typography variant="h6">
                            2021 BeeComfort
                    </Typography>
                </Box>
            </Box>
        {/* </div> */}
        </Container>
    );
}