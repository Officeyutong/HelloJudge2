import React from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import ProblemsetEdit from "./ProblemsetEdit";
import ProblemsetList from "./ProblemsetList";
import ProblemsetShow from "./ProblemsetShow";

const ProblemsetRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>
        <Route exact path={`${match.path}/list/:page`} component={ProblemsetList} ></Route>
        <Route exact path={`${match.path}/show/:id`} component={ProblemsetShow} ></Route>
        <Route exact path={`${match.path}/edit/:id`} component={ProblemsetEdit} ></Route>
    </>
};

export default ProblemsetRouter;
