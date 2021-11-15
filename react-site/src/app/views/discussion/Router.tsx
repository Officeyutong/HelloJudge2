import React, { lazy, Suspense } from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import GeneralDimmedLoader from "../utils/GeneralDimmedLoader";

const DiscussionList = lazy(() => import("./DiscussionList"));
const DiscussionShow = lazy(() => import("./DiscussionShow"));


const DiscussionRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>
        <Route exact path={`${match.path}/discussions/:path/:page`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <DiscussionList></DiscussionList>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/show_discussion/:id`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <DiscussionShow></DiscussionShow>
            </Suspense>
        </Route>
    </>
};

export default DiscussionRouter;
