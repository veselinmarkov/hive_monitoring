import React from 'react'
import { createTheme, ThemeProvider } from '@material-ui/core/styles';
import {
    BrowserRouter as Router,
    Route
  } from 'react-router-dom';
import Navbar from './components/Navbar'; 
import FrontPage from './components/FrontPage';
import Dashboard from './Dashboard';

const theme = createTheme({
  palette: {
      primary: {
          main: '#14908a', //20, 144, 138 green
      },
      secondary: {
          main: '#97295e', //151,41,94 lila
      },
      info: {
          main: '#f2a327', //242, 163, 39 yellow
      }
  }                          
})

export default function App() {
  const [user, setUser] = React.useState(null);
  
  const handleUserChange = (user) => setUser(user)

  return (
    <ThemeProvider theme={theme}>
      <Navbar user={user} handleUserChange={handleUserChange}/>
      <Router>
        <Route exact path="/">
          <FrontPage/>
        </Route>
        <Route path="/dash">
          <Dashboard user={user}/>
        </Route>
      </Router>
    </ThemeProvider>
  );
}