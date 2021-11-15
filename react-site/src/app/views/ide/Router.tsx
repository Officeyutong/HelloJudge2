import React, { lazy, Suspense } from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import GeneralDimmedLoader from "../utils/GeneralDimmedLoader";

const OnlineIDE = lazy(() => import("./OnlineIDE"));
const OnlineIDERouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>

        <Route exact path={`${match.path}/ide`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <OnlineIDE></OnlineIDE>
            </Suspense>
        </Route>
    </>
};

export default OnlineIDERouter;
