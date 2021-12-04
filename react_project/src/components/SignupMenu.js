import React from 'react'
import {Popover, Button, Input, Divider, Box, Typography} from '@material-ui/core'
import { makeStyles } from '@material-ui/core/styles';
import {login, signUp} from '../api/hivedb' 

const useStyles = makeStyles((theme) => ({ 
    container: {
      display: "flex",
      gap: "10px",
      flexDirection: "column",
      padding: "35px",
    //   border: "2px solid #e34d7d", 
      border: "2px solid",
      borderColor: theme.palette.primary.main,
      borderRadius: "5px",
      width: "300px",
    //   backgroundColor: theme.palette.primary.main,
    //   color: "primary",
    },
    inputText: {
        backgroundColor: theme.palette.background.default
    }
}));

export default function SignupMenu({anchor, handleFeedBack, handleClose}) {
    const [firstName, setFirstName ] = React.useState("");
    const [lastName, setLastName ] = React.useState("");
    const [email, setEmail ] = React.useState("");
    const [username1, setUsername1 ] = React.useState("");
    const [username2, setUsername2 ] = React.useState("");
    const [password1, setPassword1 ] = React.useState("");
    const [password2, setPassword2 ] = React.useState("");
    const [password2Rep, setPassword2Rep ] = React.useState("");
    const [showError1, setShowError1 ] = React.useState("");
    const [showError2, setShowError2 ] = React.useState("");
    const classes = useStyles();

    /* if (! props.handleFeedBack || ! props.handleClose)
        throw Error('Property handleFeedBack and handleClose are required!')
 */
    const handleSignUp = async () => {
        if (! username2 || ! password2) {
            setShowError2('Please, provide Username and Password for Signing up');
            return;
        } else if (password2 !== password2Rep) {
            setShowError2('"Repeat Password" do not match the original Password')
            return;
        }
        let response = await signUp(firstName, lastName, email, username2, password2);
        if (response.error) {
            if (response.status === "400")
                setShowError2('The user name already exists; ' +response.error);
            else
                setShowError2(response.error);
            return;
        }
        response = await login(username2, password2);
        handleFeedBack("User created", response.error);
        if (response.error) {
            setShowError2(response.error);
            return;
        }
        setShowError2('');
        setFirstName('');
        setLastName('');
        setEmail('');
        setUsername2('');
        setPassword2('');
        setPassword2Rep('');
    }

    const handleLogin = async () => {
        if (! username1 || ! password1) {
            setShowError1('Please, provide Username and Password to login');
            return
        }
        const response = await login(username1, password1);
        handleFeedBack("Login successfull", response.error)
        if (response.error)
            if (response.status ==="401")
                setShowError1('Invalid credentials. Incorrect User or password; ' +response.error);
            else
                setShowError1(response.error);
        else {
            setShowError1('')
            setUsername1('');
            setPassword1('');
        }
    }

    const handleLocalClose = () => {
        setShowError1('');
        setShowError2('');
        handleClose();
    }

    const handleFirstName = e => setFirstName(e.target.value);
    const handleLastName = e => setLastName(e.target.value);
    const handleEmail = e => setEmail(e.target.value);
    const handleUser1 = e => setUsername1(e.target.value);
    const handlePassword1 = e => setPassword1(e.target.value);
    const handleUser2 = e => setUsername2(e.target.value);
    const handlePassword2 = e => setPassword2(e.target.value);
    const handlePassword2Rep = e => setPassword2Rep(e.target.value);
    return (
        <Popover
            id="popper"
            open={Boolean(anchor)}
            anchorEl={anchor}
            onClose={handleLocalClose}
            anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'center',
            }}
            transformOrigin={{
                vertical: 'top',
                horizontal: 'center',
            }} >
                <Box component="form" className={classes.container}>
                    <Input className={classes.inputText} placeholder="User"
                        onChange={handleUser1} value={username1}/>
                    <Input type={"password"} className={classes.inputText} 
                        placeholder="password" onChange={handlePassword1} value={password1}/>
                    <Typography color="error">{showError1}</Typography>
                    <Button onClick={handleLogin} variant="contained" color="primary">
                        Login
                    </Button>

                    <Divider variant="middle" style={{marginTop: "30px", marginBottom: "30px"}}/>
                    <Typography style={{alignSelf: "flex-end"}}>or Sign up</Typography>
                    <Input className={classes.inputText} placeholder="First Name"
                        onChange={handleFirstName} value={firstName}/>
                    <Input className={classes.inputText} placeholder="Last Name"
                        onChange={handleLastName} value={lastName}/>
                    <Input className={classes.inputText} placeholder="E-Mail"
                        onChange={handleEmail} value={email}/>
                    <Input className={classes.inputText} placeholder="User"
                        onChange={handleUser2} value={username2}/>
                    <Input type={"password"} className={classes.inputText} 
                        placeholder="password" onChange={handlePassword2} value={password2}/>
                    <Input type={"password"} className={classes.inputText} 
                        placeholder="repeat password" onChange={handlePassword2Rep} value={password2Rep}/>
                    <Typography color="error">{showError2}</Typography>
                    <Button onClick={handleSignUp} variant="contained" color="primary">
                        Sign Up
                    </Button>
                </Box>
            </Popover>
    )
}