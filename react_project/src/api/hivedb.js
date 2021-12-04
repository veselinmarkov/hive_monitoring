import axios from "axios";
/* import {samples} from "/home/vesko/hivebox/src/api/samples";
import { TimeRange } from "pondjs"; */

/* export function getSamples(id) {
    const promise = new Promise((resolve, reject) => {
        resolve(samples.filter((element) => element.hive === id));
    })
    return promise;
} */

const axiosInstance = axios.create({
    // baseURL: 'http://127.0.0.1:8000/api/',
    timeout: 5000,
    headers: {
        'Authorization': sessionStorage.getItem('access_token') ? "JWT " + sessionStorage.getItem('access_token') : "",
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }
});

export async function getSamples(hive_id, timerange) {
    if (! axiosInstance.defaults.headers['Authorization'] ) {
    //authorization header not present or no user specified, probably not logged in
        throw new Error({status: "401", statusText: "Not logged in"});
    }
    // const errorResponse = null;
    let tryAgain = 3;
    while (tryAgain >0) {
        try {
            return await axiosInstance.get('/api/samples/', { params: { sample1: timerange.begin(), 
            sample2: timerange.end(), hive: hive_id}});
        } catch (error) {
            // console.log(JSON.stringify(error));
            if (error.response.status !== 401)
                throw Error(error);
        }
        // try {
        // try to resfresh the token
            console.log("Try to refresh the token");
            if (! sessionStorage.getItem('refresh_token'))
                throw new Error({status: "401", statusText: "Not logged in"});
            const response = await axiosInstance.post('/api/token/refresh/', {refresh: sessionStorage.getItem('refresh_token')});
            axiosInstance.defaults.headers['Authorization'] = 'JWT ' + response.data.access;
            sessionStorage.setItem('access_token', response.data.access);
            sessionStorage.setItem('refresh_token', response.data.refresh);
        /* } catch (error) {
            if (error.response.status !== 401)
                return error.response;

        } */
        tryAgain -= 1;
    }
    // return Promise((_, reject) => reject({status: "500", statusText: "Connection give up after 3 attempts"}))
    throw new Error({status: "500", statusText: "Connection give up after 3 attempts"});
}

/* export function getInfo() {
    return axios.get('info/');
}

export function saveRecord(record) {
    return axios.post('card/', record);
} */

export async function refresh() {
    if (! sessionStorage.getItem('refresh_token'))
        throw new Error({status: "401", statusText: "Not logged in"});
    const response = await axiosInstance.post('/api/token/refresh/', {refresh: sessionStorage.getItem('refresh_token')});
    axiosInstance.defaults.headers['Authorization'] = 'JWT ' + response.data.access;
    sessionStorage.setItem('access_token', response.data.access);
    sessionStorage.setItem('refresh_token', response.data.refresh);
    return response;
}

export async function signUp(firstname, lastname, email, user, pass) {
    const record =  {
        firstName: firstname,
        lastName: lastname,
        email: email,
        username: user,
        password: pass
    };
    //console.log("Invoked wordsdb.signUp, record:" +JSON.stringify(record));
    try {
        const response = await axiosInstance.post('/api/user/create/', record);
        //console.log("Invoked wordsdb.login, response:" +JSON.stringify(response));
        return {status: "200", message: response.statusText}
    } catch (error) {
        console.log("Catch signUp, error:" +JSON.stringify(error));
        return {status: "400", error: JSON.stringify(error.message)}
    }
}

export async function login(user, pass) {
    const record =  {
        username: user,
        password:pass
    };
    // console.log("Invoked wordsdb.login, record:" +JSON.stringify(record));
    try {
        const response = await axiosInstance.post('/api/token/obtain/', record);
        //console.log("Invoked wordsdb.login, response:" +JSON.stringify(response));
        axiosInstance.defaults.headers['Authorization'] = 'JWT ' + response.data.access;
        sessionStorage.setItem('access_token', response.data.access);
        sessionStorage.setItem('refresh_token', response.data.refresh);
        return {status: "200", message: response.statusText}
    } catch (error) {
        console.log("Catch Login, error:" +JSON.stringify(error));
        return {status: "401", error: JSON.stringify(error.message)}
    }
}

export function logout() {
    axiosInstance.defaults.headers['Authorization'] = null;
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    // return axios.get('logout/');
} 

/* export function getAllforUser(user) {
    const res = axios.get('cards/'+ String(user), {params: {order: "asc"}});
    return res.then(res => {
        //console.log(JSON.stringify(res));
        return res.data.map( doc => {
            let timeIndex = doc._id.indexOf('&') +1;
            let time = doc._id.substr(timeIndex);
            return {...doc, _id: time}
        })
    })
}

export function getLast5forUser(user) {
    const res = axios.get('cards/'+ String(user), {params:{limit: 5, order: "desc"}});
    return res.then(res => {
        //console.log(JSON.stringify(res));
        return res.data.map( doc => {
            let timeIndex = doc._id.indexOf('&') +1;
            let time = doc._id.substr(timeIndex);
            return {...doc, _id: new Date(time).toLocaleString()}
        })
    })
} */
