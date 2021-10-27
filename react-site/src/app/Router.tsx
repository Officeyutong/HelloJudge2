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
import SubmissionRouter from "./views/submission/Router";
import TeamRouter from "./views/team/Router";
import ProblemtodoRouter from "./views/problemtodo/Router";

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
        <Route path={`${match.path}/problemtodo`}>
            <ProblemtodoRouter></ProblemtodoRouter>
        </Route>
        <Route path={`${match.path}/virtualcontest`}>
            <VirtualContestRouter></VirtualContestRouter>
        </Route>

        <ProblemRouter></ProblemRouter>
        <UserRouter></UserRouter>
        <ContestRouter></ContestRouter>
        <SubmissionRouter></SubmissionRouter>
        <TeamRouter></TeamRouter>
        <Route path={`${match.path}/permissionpack`} component={PermissionPackRouter}></Route>
    </>;
});
const MyRouter: React.FC<{}> = () => {
    const clientLoaded = useSelector((s: StateType) => s.generalClient !== null && s.unwrapClient !== null && s.unwrapExtraClient !== null);
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