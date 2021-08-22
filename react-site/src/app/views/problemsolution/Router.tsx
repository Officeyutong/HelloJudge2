import React from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import SolutionCreateView from "./SolutionEditView";

const ProblemSolutionRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>
        <Route exact path={`${match.path}/user_create/:problemID`} component={() => <SolutionCreateView admin={false}></SolutionCreateView>}></Route>
        <Route exact path={`${match.path}/admin_create`} component={() => <SolutionCreateView admin></SolutionCreateView>}></Route>
        <Route exact path={`${match.path}/user_edit/:solutionID`} component={() => <SolutionCreateView edit></SolutionCreateView>}></Route>
        <Route exact path={`${match.path}/admin_edit/:solutionID`} component={() => <SolutionCreateView edit></SolutionCreateView>}></Route>


    </>
};

export default ProblemSolutionRouter;
