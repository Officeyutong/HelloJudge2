import React, { lazy, Suspense } from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import GeneralDimmedLoader from "../utils/GeneralDimmedLoader";

const ProblemCard = lazy(() => import("./ProblemCard"));

const CardRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>
        <Route exact path={`${match.path}/problem/:id`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <ProblemCard></ProblemCard>
            </Suspense>
        </Route>

    </>
};

export default CardRouter;
