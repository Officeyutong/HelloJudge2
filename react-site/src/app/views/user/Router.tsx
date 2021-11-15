
import { lazy, Suspense } from "react";
import { useRouteMatch } from "react-router";
import { Route } from "react-router-dom";
import GeneralDimmedLoader from "../utils/GeneralDimmedLoader";
const EmailRegister = lazy(() => import("./EmailRegister"))
const EmailRegisterAuth = lazy(() => import("./EmailRegisterAuth"))
const EmailResetPasswordView = lazy(() => import("./EmailResetPassword"))
const ForgetUsername = lazy(() => import("./ForgetUsername"))
const GlobalRanklist = lazy(() => import("./GlobalRanklist"))
const LoginView = lazy(() => import("./LoginView"))
const PhoneRegister = lazy(() => import("./PhoneRegister"))
const PhoneResetPassword = lazy(() => import("./PhoneResetPassword"))
const Profile = lazy(() => import("./profile/Profile"))
const ProfileEdit = lazy(() => import("./profileedit/ProfileEdit"))
const PhoneAuth = lazy(() => import("./PhoneAuth"));
const UserRouter: React.FC<{}> = () => {
    const match = useRouteMatch();
    return <>
        <Route exact path={`${match.path}/login`} >
            <Suspense fallback={<GeneralDimmedLoader />}>
                <LoginView></LoginView>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/register`} >
            <Suspense fallback={<GeneralDimmedLoader />}>
                <EmailRegister></EmailRegister>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/phone/register`} >
            <Suspense fallback={<GeneralDimmedLoader />}>
                <PhoneRegister></PhoneRegister>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/phone/reset_password`} >
            <Suspense fallback={<GeneralDimmedLoader />}>
                <PhoneResetPassword></PhoneResetPassword>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/reset_password/:token`} >
            <Suspense fallback={<GeneralDimmedLoader />}>
                <EmailResetPasswordView></EmailResetPasswordView>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/auth_email/:token`} >
            <Suspense fallback={<GeneralDimmedLoader />}>
                <EmailRegisterAuth></EmailRegisterAuth>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/profile/:uid`} >
            <Suspense fallback={<GeneralDimmedLoader />}>
                <Profile></Profile>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/profile_edit/:uid`} >
            <Suspense fallback={<GeneralDimmedLoader />}>
                <ProfileEdit></ProfileEdit>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/user/forget_username`} >
            <Suspense fallback={<GeneralDimmedLoader />}>
                <ForgetUsername></ForgetUsername>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/ranklist/:page`} >
            <Suspense fallback={<GeneralDimmedLoader />}>
                <GlobalRanklist></GlobalRanklist>
            </Suspense>
        </Route>
        <Route exact path={`${match.path}/phoneauth`} >
            <Suspense fallback={<GeneralDimmedLoader />}>
                <PhoneAuth></PhoneAuth>
            </Suspense>
        </Route>
    </>
};

export default UserRouter;
