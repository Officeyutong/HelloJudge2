import React, { lazy, Suspense } from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import { Dimmer, Loader } from "semantic-ui-react";
import GeneralDimmedLoader from "../utils/GeneralDimmedLoader";
import ContestProblem from "./ContestProblem";
import ClarificationEdit from "./show/ClarificationEdit";

const ContestList = lazy(() => import("./ContestList"));
const ContestShow = lazy(() => import("./show/ContestShow"));
const ContestEdit = lazy(() => import("./edit/ContestEdit"));
const ContestRanklist = lazy(() => import("./ContestRanklist"));
const ContestRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>
        <Route exact path={`${match.path}/contest/ranklist/:contestID`} component={() => <Suspense
            fallback={<GeneralDimmedLoader />}
        >
            <ContestRanklist></ContestRanklist>
        </Suspense>}></Route>
        <Route exact path={`${match.path}/contest/:contestID/problem/:problemID`} component={ContestProblem}></Route>
        <Route exact path={`${match.path}/contests/:page`} component={() => <Suspense fallback={<Dimmer active> <Loader></Loader></Dimmer>}>
            <ContestList></ContestList>
        </Suspense>}></Route>
        <Route exact path={`${match.path}/contest/:id`} component={() => <Suspense fallback={<GeneralDimmedLoader />}>
            <ContestShow></ContestShow>
        </Suspense>}></Route>
        <Route exact path={`${match.path}/contest/clarification/edit/:id`} component={ClarificationEdit}></Route>
        <Route exact path={`${match.path}/contest/edit/:id`} component={() => <Suspense fallback={<GeneralDimmedLoader />}>
            <ContestEdit></ContestEdit>
        </Suspense>}></Route>
    </>
};

export default ContestRouter;
