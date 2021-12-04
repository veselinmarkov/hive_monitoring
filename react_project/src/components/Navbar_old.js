import React from 'react';
import { AppBar, Toolbar, InputBase, Button, IconButton, Typography, Snackbar,
  Menu, MenuItem } from '@material-ui/core';
import { makeStyles, alpha } from '@material-ui/core/styles';
import { AccountCircle, HelpOutline } from '@material-ui/icons';
import { signUp, logout, login } from '../api/hivedb';
import SignupMenu from './SignupMenu';
import { ShowHelp } from './ShowHelp';
//import MuiAlert from '@material-ui/lab/Alert';

const useStyles = makeStyles((theme) => ({
    appBar: {
      borderRadius: "5px"
    },
    userText: {
      //marginRight: theme.spacing(2),
      flexGrow: 1,
    },
    signupText: {
      color: "inherit",
      background: "inherit"
    },
    toolbar: {
      minHeight: "48px",
      paddingLeft: "10px",
      paddingRight: "10px",  
    },
    search: {
      position: 'relative',
      borderRadius: theme.shape.borderRadius,
      backgroundColor: alpha(theme.palette.common.white, 0.15),
      '&:hover': {
        backgroundColor: alpha(theme.palette.common.white, 0.25),
      },
      marginLeft: 0,
      width: '100%',
      [theme.breakpoints.up('sm')]: {
        marginLeft: theme.spacing(1),
        width: 'auto',
      },
    },
    inputRoot: {
      color: 'inherit',
    },
    inputInput: {
      padding: theme.spacing(1, 1, 1, 1),
      // vertical padding + font size from searchIcon
      //paddingLeft: `calc(1em + ${theme.spacing(4)}px)`,
      transition: theme.transitions.create('width'),
      width: '100%',
      [theme.breakpoints.up('sm')]: {
        width: '12ch',
        '&:focus': {
          width: '20ch',
        },
      },
    },
  }));


export default function Navbar(props) {
    const [username, setUsername ] = React.useState("");
    const [password, setPassword ] = React.useState("");
    const [anchorEl, setAnchorEl] = React.useState(null);
    const [showSignupFlag, setShowSignupFlag] = React.useState(true);
    const [snakMessage, setSnakMessage] = React.useState(null);
    const classes = useStyles();
    let user;
    if (props.user.firstName || props.user.lastName)
      user = (props.user.firstName || "") + " " + (props.user.lastName || "");
    else
      user = props.user.id;
    let auth = user !== "Guest";

    const handleSignupClick = (event) => {
      setShowSignupFlag(true);
      setAnchorEl(event.currentTarget);
    };
    const handleHelpClick = (event) => {
      setShowSignupFlag(false);
      setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
      setAnchorEl(null);
    }

    const handleSignup = (firstName, lastName, username, password, clearUserData) => {
      setAnchorEl(null);
      if (! username || ! password)
        return;
      signUp(firstName, lastName, username, password).then( (res)=> {
        //console.log("Signup:" +JSON.stringify(res.data));
        if (props.updateUser) {
          props.updateUser(res.data);
          clearUserData();
          //  id: username,
          //  firstName: firstName,
          //  lastName: lastName
          //});
        }
      }).catch((err) => {
        //console.log(JSON.stringify(err));
        if (err.message) {
          if (String(err.message).indexOf("code 401") >0)
            setSnakMessage("User name already taken");
          else
            setSnakMessage(err.message);
        }
      });
    }

    const handleLogin = () => {
      login(username, password).then( (res)=> {
        //console.log("Login:" +JSON.stringify(res.data));
        if (props.updateUser)
          props.updateUser(res.data);
      }).catch((err) => {
        //console.log(JSON.stringify(err));
        if (err.message) {
          if (String(err.message).indexOf("code 401") > -1)
            setSnakMessage("User name or the password are not correct");
          else if (String(err.message).indexOf("code 400") > -1)
            setSnakMessage("Please specify user name and password");
          else
            setSnakMessage(err.message);
        }
      });
    }

    const handleLogout = () => {      
      setAnchorEl(null);
      logout().then( (res)=> {
        //console.log("Signup:" +JSON.stringify(res));
        if (props.updateUser)
          props.updateUser({ id:"Guest" });
      }).catch((err) => {
        //console.log(JSON.stringify(err));
        if (err.message) {
            setSnakMessage(err.message);
        }
      });
    }

    const handleUser = e => setUsername(e.target.value);
    const handlePass = e => setPassword(e.target.value);
    const handleSnakClose = () => setSnakMessage(null);

    return (
        <AppBar position="absolute" className={classes.appBar} position="static" color="primary">
          {auth ? 
            <Toolbar className={classes.toolbar}>
              <IconButton
                aria-label="account of current user"
                aria-controls="menu-appbar"
                aria-haspopup="true"
                color="inherit"
                onClick={handleSignupClick}
              >
                <AccountCircle />
              </IconButton>
              <Typography className={classes.userText} variant="h6" noWrap>
                {user}
              </Typography>
              <Menu
                id="menu-appbar"
                anchorEl={anchorEl}
                anchorOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                keepMounted
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                open={Boolean(anchorEl)}
                onClose={handleClose}>
                <MenuItem onClick={handleLogout}>Logout</MenuItem>
              </Menu>
              <IconButton
                color="inherit"
                onClick={handleHelpClick}>
                <HelpOutline/>
              </IconButton>
            </Toolbar>
           :   
            <Toolbar className={classes.toolbar}>
              <Typography className={classes.userText} variant="h6" noWrap>
                {user}
              </Typography>
              <div className={classes.search}>
                <InputBase
                placeholder="Username"
                classes={{
                  root: classes.inputRoot,
                  input: classes.inputInput,
                }} onChange={handleUser} value={username}/>
              </div>
              <div className={classes.search}>
                <InputBase
                placeholder="Password"
                type="password"
                classes={{
                  root: classes.inputRoot,
                  input: classes.inputInput,
                }} onChange={handlePass} value={password}/>
              </div>
              <Button onClick={handleLogin} variant="contained" color="primary">
                Login
              </Button>
              <Button className={classes.signupText} 
                onClick={handleSignupClick}
                variant="text"
                color="primary"
                aria-describedby="popper"
                //aria-controls="menu-appbar"
                //aria-haspopup="true"
                >
                <Typography variant="caption" noWrap>
                  Signup
                </Typography>
              </Button>
              <IconButton
                color="inherit"
                onClick={handleHelpClick}>
                <HelpOutline/>
              </IconButton>
              {/* <SignupMenu open={Boolean(anchorEl) && showSignupFlag} anchor={anchorEl} handleSignup={handleSignup} handleClose={handleClose}/> */}
            </Toolbar>
          }
        <ShowHelp open={Boolean(anchorEl) && ! showSignupFlag} anchor={anchorEl} handleClose={handleClose}/>
        <Snackbar open={Boolean(snakMessage)} autoHideDuration={6000} 
          onClose={handleSnakClose} message={snakMessage} 
          anchorOrigin={{ vertical: "top", horizontal: "center" }}>            
        </Snackbar>
      </AppBar>
      
    )
}