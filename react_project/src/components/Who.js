import React from 'react'
import { Container, Box, Typography, Divider } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles'; 

import BackFlower from '../pictures/flowers_wide_lowRes.jpg';
import ManPicture from '../pictures/Man_picture.PNG';
import WomanPicture from '../pictures/Woman_picture.PNG';
import VeskoPicture from '../pictures/Vesko_picture.jpg';

const employees = [
    { "id": 1,
        "name": "Mityu Mitev",
        "role": "Concept, architecture and hardware definition of the product",
        "experience": " Analog design engineer",
        "picture": ManPicture,
        "email": "mityu_mitev@yahoo.com",
    },
    { "id": 2,
        "name": "Ilia Krastev",
        "role": "Embedded developer",
        "experience": "Long experienced Software developer in various projects",
        "picture": ManPicture,
        "email": "ikrustev@gmail.com",
    },
    { "id": 3,
        "name": "Veselin Markov",
        "role": "Full stack developer",
        "experience": "Telekommunication engineer, Mobile networks, Data Analyst",
        "picture": VeskoPicture,
        "email": "veselin.markov@gmail.com",
    },
    { "id": 4,
        "name": "Maria Minekova",
        "role": "Beekeeping expert",
        "experience": "",
        "picture": WomanPicture,
        "email": "",
    },
    { "id": 5,
        "name": "Chicho Pepi",
        "role": "Beekeeping expert",
        "experience": "",
        "picture": ManPicture,
        "email": "",
    },
]

const useStyles = makeStyles((theme) => ({
    rootContainer: {
      padding: "0px 20px", 
      margin: "70px 5px 0px", 
    //   border: "2px solid #e34d7d", 
      borderRadius: "7px",
      //height: "100vh"
        //backgroundImage: "linear-gradient(rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.5)),url('/static/media/beehive.471e8a0b.png')",
        backgroundImage: `linear-gradient(rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.95)),url(${BackFlower})`,
        backgroundRepeat: "repeat",
        // backgroundPosition: "center center",
        // backgroundSize: "cover",
        backgroundAttachment: "scroll",
    },
    container: {
        marginLeft: "100px", 
        display:"flex", 
        flexFlow:"column",
    },
    person: {
        display: "flex", 
        alignItems:"center", 
        margin:"30px",
    }
}))

export default function Who() {
    const classes = useStyles();

    return (
        <Container component="main" maxWidth="lg" className={classes.rootContainer}>
            <Box className={classes.container}>
            {employees.map(emp => (
                <Box className={classes.person} key={emp.id}>                
                    {Boolean(emp.id % 2) && <img alt={emp.name} src={emp.picture} width="130"/> }
                    <Box sx={{margin: "20px", minWidth: "300px",}}> 
                    <   Typography gutterBottom variant="h5" component="div">
                            {emp.name}
                        </Typography>
                        <Typography variant="h6" color="textSecondary">
                            {emp.role}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                            <Typography component="span" variant="body1" color="textPrimary">Experience: </Typography> 
                            {emp.experience}
                        </Typography>
                        {/* <Typography variant="body2" color="textSecondary">
                            <Typography component="span" variant="body1" color="textPrimary">e-mail: </Typography> 
                            {emp.email}
                        </Typography> */}
                    </Box>                
                    {Boolean((emp.id +1) % 2) && <img alt={emp.name} src={emp.picture} width="130"/> }
                </Box>
            /* <Card sx={{ maxWidth: 245 }} key={emp.id}>
                <CardMedia
                    component="img"
                    height="140"
                    image={emp.picture}
                />
                <CardContent>
                    <Typography gutterBottom variant="h5" component="div">
                    {emp.name}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                    {emp.role}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                    Experience: {emp.experience}
                    </Typography>
                </CardContent>
            </Card> */
            ))}
            </Box>
        </Container>
    )
}