import React, { useEffect, useState } from "react";
import { show, showErrorModal } from "./dialogs/Dialog";
import Router from "./Router";
// import { store } from './states/Manager';
import { Provider } from 'react-redux';
import { makeClientUpdateAction, makeUserStateUpdateAction, store } from "./states/Manager";
import 'semantic-ui-css/semantic.min.css'
import { Container } from "semantic-ui-react";
import { APIError } from "./Exception";
import "katex/dist/katex.min.css";
import "./App.css";
import axios from "axios";
import "./LinkButton.css";
const PUBLIC_URL = process.env.PUBLIC_URL;
const MIXED_FRONTEND = PUBLIC_URL === "rs";
const BACKEND_BASE_URL = process.env.REACT_APP_BASE_URL;
const DEBUG_MODE = process.env.NODE_ENV === "development";
const axiosObj = axios.create({
    baseURL: BACKEND_BASE_URL,
    withCredentials: true
});
const axiosErrorHandler = (err: any) => {
    let resp = err.response;
    console.log(resp);
    if (resp) {
        const data = resp.data as {
            data?: any;
            message?: string;
            code: number;
        };
        if (DEBUG_MODE) {
            show(JSON.stringify(data), resp.status + " " + resp.statusText, true);
        }
        else { show(data.message, resp.status + " " + resp.statusText, true); }
    }
    else
        show(err, "发生错误", true);
    throw err;
};
const unwrapAxiosClient = axios.create({
    baseURL: BACKEND_BASE_URL,
    withCredentials: true
});
const unwrapExtraAxiosClient = axios.create({
    baseURL: BACKEND_BASE_URL,
    withCredentials: true
});

axiosObj.interceptors.response.use(resp => {
    let data = resp.data as {
        code: number;
        // error: null | any;
        data?: any;
        message?: string;
    };
    if (data.code !== 0) {
        console.log(data);
        showErrorModal(JSON.stringify(data.message));
        throw new APIError(JSON.stringify(data.message));
    }
    resp.data = data.data;
    return resp;
}, axiosErrorHandler);
unwrapExtraAxiosClient.interceptors.response.use(resp => {
    let data = resp.data as {
        code: number;
        // error: null | any;
        data?: any;
        message?: string;
    };
    if (data.code !== 0) {
        console.log(data);
        showErrorModal(JSON.stringify(data.message));
        throw new APIError(JSON.stringify(data.message));
    }
    return resp;
}, axiosErrorHandler);
unwrapAxiosClient.interceptors.response.use(r => r, axiosErrorHandler);
store.dispatch(makeClientUpdateAction(axiosObj, unwrapAxiosClient, unwrapExtraAxiosClient));
axios.post("/api/query_login_state").then(resp => {
    const result = resp.data;
    store.dispatch(makeUserStateUpdateAction(result.result, result));
});
const App: React.FC<{}> = () => {
    const [displayBaseView, setDisplayBaseView] = useState(store.getState().displayBaseView);
    useEffect(() => {
        const unsubscribe = store.subscribe(() => setDisplayBaseView(store.getState().displayBaseView));
        return unsubscribe;
    }, []);
    const inner = <>
        <Provider store={store} >
            <Router></Router>
        </Provider>
    </>
    return displayBaseView ? <Container style={{ marginTop: "70px", marginBottom: "70px" }}>
        {inner}
    </Container> : inner;

};

export default App;
export { axiosObj, BACKEND_BASE_URL, DEBUG_MODE, MIXED_FRONTEND, PUBLIC_URL }