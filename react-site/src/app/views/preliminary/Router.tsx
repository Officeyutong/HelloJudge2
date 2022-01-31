import React, { lazy, Suspense } from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import GeneralDimmedLoader from "../utils/GeneralDimmedLoader";


const PreliminaryContestList = lazy(() => import("./PreliminaryContestList"));
const PreliminaryContest = lazy(() => import("./PreliminaryContest"));
const PreliminaryRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>
        <Route exact path={`${match.path}/list/:page?`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <PreliminaryContestList></PreliminaryContestList>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/contest/:contest/:problem?`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <PreliminaryContest></PreliminaryContest>
            </Suspense>
        </Route>
    </>
};

export default PreliminaryRouter;
