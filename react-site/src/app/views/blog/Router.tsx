import React, { lazy, Suspense } from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import GeneralDimmedLoader from "../utils/GeneralDimmedLoader";

// const ChallengeEdit = lazy(() => import("./ChallengeEdit"));
// const ChallengeList = lazy(() => import("./ChallengeList"));
const BlogEdit = lazy(() => import("./BlogEdit"));
const BlogList = lazy(() => import("./BlogList"));

const BlogRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>

        <Route exact path={`${match.path}/list/:uid`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <BlogList></BlogList>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/edit/:id?`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <BlogEdit></BlogEdit>
            </Suspense>
        </Route>
    </>
};

export default BlogRouter;
