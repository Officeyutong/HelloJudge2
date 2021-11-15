import React, { lazy, Suspense } from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import GeneralDimmedLoader from "../utils/GeneralDimmedLoader";

const Help = lazy(() => import("./Help"));
const MiscRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>
        <Route exact path={`${match.path}/help`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <Help></Help>
            </Suspense>
        </Route>
    </>
};

export default MiscRouter;
