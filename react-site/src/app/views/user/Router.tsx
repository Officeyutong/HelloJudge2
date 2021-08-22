import React from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import EmailRegister from "./EmailRegister";
import EmailRegisterAuth from "./EmailRegisterAuth";
import EmailResetPasswordView from "./EmailResetPassword";
import ForgetUsername from "./ForgetUsername";
import LoginView from "./LoginView";
import PhoneRegister from "./PhoneRegister";
import PhoneResetPassword from "./PhoneResetPassword";
import Profile from "./profile/Profile";
import ProfileEdit from "./profileedit/ProfileEdit";
const UserRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>
        <Route exact path={`${match.path}/login`} component={LoginView}></Route>
        <Route exact path={`${match.path}/register`} component={EmailRegister}></Route>
        <Route exact path={`${match.path}/phone/register`} component={PhoneRegister}></Route>
        <Route exact path={`${match.path}/phone/reset_password`} component={PhoneResetPassword}></Route>
        <Route exact path={`${match.path}/reset_password/:token`} component={EmailResetPasswordView}></Route>
        <Route exact path={`${match.path}/auth_email/:token`} component={EmailRegisterAuth}></Route>
        <Route exact path={`${match.path}/profile/:uid`} component={Profile}></Route>
        <Route exact path={`${match.path}/profile_edit/:uid`} component={ProfileEdit}></Route>
        <Route exact path={`${match.path}/user/forget_username`} component={ForgetUsername}></Route>
    </>
};

export default UserRouter;
