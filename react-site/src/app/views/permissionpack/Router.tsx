import React from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import PermissionPackEdit from "./edit/PermissionPackEdit";
import UserPacks from "./UserPacks";

const PermissionPackRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>
        <Route exact path={`${match.path}/user_packs`} component={UserPacks}></Route>
        <Route exact path={`${match.path}/edit/:id`} component={PermissionPackEdit}></Route>
    </>
};

export default PermissionPackRouter;
