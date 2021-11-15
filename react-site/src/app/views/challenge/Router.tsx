import React, { lazy, Suspense } from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import GeneralDimmedLoader from "../utils/GeneralDimmedLoader";

const ChallengeEdit = lazy(() => import("./ChallengeEdit"));
const ChallengeList = lazy(() => import("./ChallengeList"));

const ChallengeRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>

        <Route exact path={`${match.path}/list`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <ChallengeList></ChallengeList>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/edit/:id`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <ChallengeEdit></ChallengeEdit>
            </Suspense>
        </Route>
    </>
};

export default ChallengeRouter;
