import React from "react";

import { Route, BrowserRouter as Router, withRouter, RouteComponentProps, Switch } from "react-router-dom";

import BaseView from "./views/BaseView";
import AdminView from "./views/admin/AdminView";
import HomePage from "./views/homepage/HomePage";
import UserRouter from "./views/user/Router";
import ProblemRouter from "./views/problem/Router";
import ProblemSolutionRouter from "./views/problemsolution/Router";
import PermissionPackRouter from "./views/permissionpack/Router";
import ContestRouter from "./views/contest/Router";
import ProblemsetRouter from "./views/problemset/Router";
import VirtualContestRouter from "./views/virtualcontest/Router";
import { useSelector } from "react-redux";
import { StateType } from "./states/Manager";

// type RequireDataLoadingRouteProps = { loaded: boolean };
// const RequireDataLoadingRoute = connect(
//     (state: StateType): RequireDataLoadingRouteProps => ({ loaded: state.dataState.loaded })
// )(
//     (
//         (props) => {
//             const { loaded } = props;
//             if (!loaded) {
//                 return <Route render={() => <>
//                     <Segment stacked>
//                         <Dimmer active>
//                             <Loader>加载数据中...</Loader>
//                         </Dimmer>
//                         <div style={{ height: "300px" }}></div>
//                     </Segment></>}></Route>
//             } else {
//                 return <Route {...props}></Route>
//             }
//         }
//     ) as React.FC<RouteProps & RequireDataLoadingRouteProps>
// );

const SubRoutes = withRouter(({ match }: RouteComponentProps) => {
    return <>
        <Route exact path={`${match.path}/admin`} component={AdminView}></Route>
        <Route exact path={`${match.path}/`} component={HomePage}></Route>
        <Route path={`${match.path}/problemsolution`}>
            <ProblemSolutionRouter></ProblemSolutionRouter>
        </Route>
        <Route path={`${match.path}/problemset`}>
            <ProblemsetRouter></ProblemsetRouter>
        </Route>
        <Route path={`${match.path}/virtualcontest`}>
            <VirtualContestRouter></VirtualContestRouter>
        </Route>

        <ProblemRouter></ProblemRouter>
        <UserRouter></UserRouter>
        <ContestRouter></ContestRouter>
        <Route path={`${match.path}/permissionpack`} component={PermissionPackRouter}></Route>
    </>;
});
const MyRouter: React.FC<{}> = () => {
    const clientLoaded = useSelector((s: StateType) => s.generalClient !== null && s.unwrapClient !== null && s.unwrapExtraClient !== null);
    console.log(clientLoaded);
    console.log(useSelector((s: StateType) => s));
    return <Router>
        <BaseView>
            {clientLoaded && <Switch>
                <Route path="/rs">
                    <SubRoutes></SubRoutes>
                </Route>
                <SubRoutes></SubRoutes>
            </Switch>}
        </BaseView>
    </Router>;
}
export default MyRouter;