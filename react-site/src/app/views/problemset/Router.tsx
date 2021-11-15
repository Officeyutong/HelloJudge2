import React, { lazy, Suspense } from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import GeneralDimmedLoader from "../utils/GeneralDimmedLoader";
const ProblemsetEdit = lazy(() => import("./ProblemsetEdit"));
const ProblemsetList = lazy(() => import("./ProblemsetList"));
const ProblemsetShow = lazy(() => import("./ProblemsetShow"));
const ProblemsetRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>
        <Route exact path={`${match.path}/list/:page`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <ProblemsetList></ProblemsetList>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/show/:id`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <ProblemsetShow></ProblemsetShow>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/edit/:id`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <ProblemsetEdit></ProblemsetEdit>
            </Suspense>
        </Route>
    </>
};

export default ProblemsetRouter;
