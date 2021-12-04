import React from "react";
import {Popover, Button} from '@material-ui/core'
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
    container: {
        maxWidth: "450px",
        padding: "15px",
        border: "2px solid #e34d7d", 
        borderRadius: "5px",
        backgroundColor: "#3f51b5",
        color: "#fff",
    },
    topics: {
        fontSize: "large",
        //color: "#e34d7d",
        marginBottom: "0"
    },
    paragraph: {
        marginTop: "0"
    }
}));

export function ShowHelp(props) { //open, anchor, handleClose
    const classes = useStyles();
    //const open = Boolean(props.anchor);

    const handleClose = () => {
        if (props.handleClose)
            props.handleClose();
    }

    return (
        <Popover
            id="popper"
            open={props.open}
            anchorEl={props.anchor}
            onClose={handleClose}
            anchorOrigin={{
                vertical: 'top',
                horizontal: 'center',
            }}
            transformOrigin={{
                vertical: 'top',
                horizontal: 'center',
            }}>
            <div className={classes.container}>
                <p className={classes.topics}>How it works</p>
                <p className={classes.paragraph}>QCard is an application designed for helping you learn German words. It ask you to translate random German word to English and compares the result with an internal dictionary. Than displays the result in a table and show a graphical statistics of your success. It is expected you to improve with time :)</p>
                <p className={classes.topics}>Sign up</p>
                <p className={classes.paragraph}>Signing up is very easy, no private information is required. User names are optional and are displayed on the status bar. The login is used to show your own success rate. In case you are not logged in, the results are registered to the deafult Guset account and the success rate is mixed with all other Guests.</p>
                <p className={classes.topics}>Random words</p>
                <p className={classes.paragraph}>The application offers a random word and it is 50% chance to display an "easy" or "hard" word.</p>
                <p className={classes.topics}>Periodic Q Cards</p>
                <p className={classes.paragraph}>You can also activate Q cards to show up in random time intervals. The application can notify you when a new card is avalable. This feature is usefull if you work on something else and you can get questions from time to time to help you learn German words effortless.</p>
                <Button onClick={handleClose} variant="contained" color="primary">
                    OK
                </Button>
            </div>
        </Popover>
    );
}