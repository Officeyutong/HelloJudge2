import React, { lazy, Suspense } from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import GeneralDimmedLoader from "../utils/GeneralDimmedLoader";

const ProblemtodoList = lazy(() => import("./ProblemtodoList"));
const ProblemtodoRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>
        <Route exact path={`${match.path}/list`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <ProblemtodoList></ProblemtodoList>
            </Suspense>
        </Route>
    </>
};

export default ProblemtodoRouter;
