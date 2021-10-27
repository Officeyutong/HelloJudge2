import React, { lazy, Suspense } from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import GeneralDimmedLoader from "../utils/GeneralDimmedLoader";

const SubmissionList = lazy(() => import("./list/SubmissionList"));
const SubmitAnswer = lazy(() => import("./SubmitAnswer"));
const ShowSubmission = lazy(() => import("./show/ShowSubmission"));
const SubmissionRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>
        <Route exact path={`${match.path}/submissions/:page`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <SubmissionList></SubmissionList>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/submit_answer/:problem`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <SubmitAnswer></SubmitAnswer>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/show_submission/:submission`}>
            <Suspense fallback={<GeneralDimmedLoader />}>
                <ShowSubmission></ShowSubmission>
            </Suspense>
        </Route>
    </>
};

export default SubmissionRouter;
