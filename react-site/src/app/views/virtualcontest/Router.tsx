import React, { lazy, Suspense } from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import GeneralDimmedLoader from "../utils/GeneralDimmedLoader";
const VirtualContestCreate = lazy(() => import("./VirtualContestCreate"));
const VirtualContestList = lazy(() => import("./VirtualContestList"));

const VirtualContestRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>
        <Route exact path={`${match.path}/create/:id`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <VirtualContestCreate></VirtualContestCreate>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/list`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <VirtualContestList></VirtualContestList>
            </Suspense>
        </Route>
    </>
};

export default VirtualContestRouter;
