import React, { lazy, Suspense } from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import GeneralDimmedLoader from "../utils/GeneralDimmedLoader";

const ImageList = lazy(() => import("./ImageList"));
const ImageStoreRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>

        <Route exact path={`${match.path}/list`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <ImageList></ImageList>
            </Suspense>
        </Route>
        {/* <Route exact path={`${match.path}/upload`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <ImageList></ImageList>
            </Suspense>
        </Route> */}
    </>
};

export default ImageStoreRouter;
