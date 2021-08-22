import React, { lazy, Suspense } from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import GeneralDimmedLoader from "../utils/GeneralDimmedLoader";
import TagsEdit from "./TagsEdit";
const ShowProblem = lazy(() => import("./ShowProblem"));
const ProblemEdit = lazy(() => import("./edit/ProblemEdit"));
const ProblemList = lazy(() => import("./list/ProblemList"));
const ProblemRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>
        <Route exact path={`${match.path}/show_problem/:problemID`} component={
            () => <Suspense fallback={<GeneralDimmedLoader />}>
                <ShowProblem></ShowProblem>
            </Suspense>
        }></Route>
        <Route exact path={`${match.path}/tags/edit`} component={TagsEdit}></Route>
        <Route exact path={`${match.path}/problem_edit/:problemID`} component={
            () => <Suspense fallback={<GeneralDimmedLoader />}>
                <ProblemEdit></ProblemEdit>
            </Suspense>
        }></Route>
        <Route exact path={`${match.path}/problems/:page`} component={
            () => <Suspense fallback={<GeneralDimmedLoader />}>
                <ProblemList></ProblemList>
            </Suspense>
        }></Route>
    </>
};

export default ProblemRouter;
