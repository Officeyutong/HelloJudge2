import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { Grid, Icon, Menu, Image, Container as SMContainer } from "semantic-ui-react";
import { axiosObj } from "../App";
import { useProfileImageMaker } from "../common/Utils";
import { StateType } from "../states/Manager";
const Container = React.memo((({ child }) => {
    return <>{child}</>
}) as React.FC<{ child: React.ReactNode }>);
const BaseView: React.FC<{}> = ({ children }) => {
    const [showDiscussionDetail, setShowDiscussionDetail] = useState(false);
    const userState = useSelector((s: StateType) => s.userState);
    const logout = () => {
        axiosObj.post("/api/logout").then(() => window.location.reload());
    };
    const phoneAuth = useSelector((s: StateType) => s.userState.userData.usePhoneAuth);
    const profileMaker = useProfileImageMaker();
    const [width, setWidth] = useState(document.documentElement.clientWidth);
    // const [showSideBar, setShowSideBar] = useState(false);
    const narrow = width <= 900;
    useEffect(() => {
        const listener = (e: UIEvent) => {
            setWidth(document.documentElement.clientWidth);
        };
        window.addEventListener("resize", listener);
        return () => window.removeEventListener("resize", listener);
    });
    const sideMenu = <Menu vertical icon="labeled">
        <Menu.Item as="a" href="/">
            <Icon name="home"></Icon>
            主页
        </Menu.Item>
        <Menu.Item as="a" href="/problems/1">
            <Icon name="tasks"></Icon>
            题库
        </Menu.Item>
        <Menu.Item as="a" href="/submissions/1">
            <Icon name="hdd"></Icon>
            提交
        </Menu.Item>
        <Menu.Item as="a" href="/team">
            <Icon name="address book"></Icon>
            团队
        </Menu.Item>
        <Menu.Item as="a" href="/challenge/list">
            <Icon name="chart bar"></Icon>
            天梯
        </Menu.Item>
        <Menu.Item as="a" href="/problemset/list/1">
            <Icon name="book"></Icon>
            习题集
        </Menu.Item>
        <Menu.Item as="a" href="/contests/1">
            <Icon name="chart line"></Icon>
            比赛
        </Menu.Item>
        <Menu.Item onClick={() => setShowDiscussionDetail(!showDiscussionDetail)} style={{ cursor: "pointer" }}>
            <Icon name="keyboard outline"></Icon>
            讨论 百科
        </Menu.Item>
        {showDiscussionDetail && <>
            <Menu.Item as="a" target="_blank" href="/discussions/discussion.problem.global/1">题目全局讨论</Menu.Item>
            <Menu.Item as="a" target="_blank" href="/wiki">百科</Menu.Item>
        </>}
        <Menu.Item as="a" target="_blank" href="/ranklist/1">
            <Icon name="signal"></Icon>
            排名
        </Menu.Item>
        {userState.login && <>
            <Menu.Item as="a" target="_blank" href="/ide">
                <Icon name="code"></Icon>
                在线IDE
            </Menu.Item>

        </>}
        <Menu.Item as="a" target="_blank" href="/help">
            <Icon name="help circle"></Icon>
            帮助
        </Menu.Item>
        {userState.login ? <>

        </> : <>
            <Menu.Item as="a" target="_blank" href="/login">
                请登录...
            </Menu.Item>
            <Menu.Item onClick={() => window.location.href = phoneAuth ? "/phone/register" : "/register"}>
                或者注册...
            </Menu.Item>

        </>}
        {userState.userData.backend_managable && <Menu.Item as="a" target="_blank" href="/admin">
            <Icon name="sitemap"></Icon>
            后台管理
        </Menu.Item>}
        {userState.login && <>
            <Menu.Item as="a" href={`/profile/${userState.userData.uid}`}>
                <Image avatar src={profileMaker(userState.userData.email)}></Image>
                <span>{userState.userData.username}</span>
            </Menu.Item>
            <Menu.Item onClick={logout} >
                <Icon name="x"></Icon>
                登出
            </Menu.Item>
        </>}
    </Menu>
    const mainBody = <>
        <SMContainer>
            <div style={{ width: "100%", marginBottom: "70px" }}>
                <Container child={children}></Container>
            </div>
        </SMContainer>
        <SMContainer textAlign="center">
            <div style={{ color: "darkgrey" }} >
                {userState.userData.appName} powered by <a href="https://github.com/Officeyutong/HelloJudge2">HelloJudge2</a>
            </div>
        </SMContainer>
    </>;
    return <Grid columns="2">
        <Grid.Row>
            <Grid.Column style={{ width: "max-content" }}>
                <div style={{ position: "fixed", overflowY: "scroll", height: "100%", left: 0, top: 0 }}>
                    {sideMenu}
                </div>
            </Grid.Column>
            <Grid.Column width="15" >
                <div style={narrow ? { marginLeft: "100px" } : undefined}>
                    {mainBody}
                </div>
            </Grid.Column>
        </Grid.Row>
    </Grid>
}

export default BaseView;