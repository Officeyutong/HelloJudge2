import React, { useEffect, useState } from "react";
import { Dimmer, Header, Loader, Tab } from "semantic-ui-react";
import { useDocumentTitle } from "../../common/Utils";
import PermissionPackList from "../permissionpack/PermissionPackList";
import { adminClient } from "./client/AdminClient";
import { AdminBasicInfo } from "./client/types";
import ConfigPreviewTab from "./tabs/ConfigPreviewTab";
import FeedManagement from "./tabs/FeedManagement";
import GeneralView from "./tabs/GeneralTab";
import HomepageSwiperManagement from "./tabs/HomepageSwiperManagement";
import MiscManagement from "./tabs/MiscManagement";
import PermissionGroupTab from "./tabs/PermissionGroupTab";
// import PermissionPackTab from "./tabs/PermissionPackTab";
import RatingManagement from "./tabs/RatingManagement";
import UserManagement from "./tabs/UserManagement";

const AdminView: React.FC<{}> = () => {
    useDocumentTitle("后台管理");
    const [loaded, setLoaded] = useState(false);
    const [basicData, setBasicData] = useState<AdminBasicInfo | null>(null);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                setBasicData(await adminClient.getAdminBasicInfo());
                setLoaded(true);
            })();
        }
    }, [loaded]);
    return loaded ? <>
        <div>
            <Header as="h1">后台管理</Header>
            <Tab renderActiveOnly={false} panes={[
                { menuItem: "概览", pane: <Tab.Pane key={0}><GeneralView data={basicData!}></GeneralView></Tab.Pane> },
                { menuItem: "Rating管理", pane: <Tab.Pane key={1}><RatingManagement></RatingManagement></Tab.Pane> },
                { menuItem: "设置预览", pane: <Tab.Pane key={2}><ConfigPreviewTab data={basicData!.settings}></ConfigPreviewTab></Tab.Pane> },
                { menuItem: "权限组设定", pane: <Tab.Pane key={3}><PermissionGroupTab></PermissionGroupTab></Tab.Pane> },
                { menuItem: "全局推送", pane: <Tab.Pane key={4}><FeedManagement></FeedManagement></Tab.Pane> },
                { menuItem: "主页轮播管理", pane: <Tab.Pane key={5}><HomepageSwiperManagement></HomepageSwiperManagement></Tab.Pane> },
                { menuItem: "权限包管理", pane: <Tab.Pane key={-1}><PermissionPackList></PermissionPackList></Tab.Pane> },
                { menuItem: "用户管理", pane: <Tab.Pane key={6}><UserManagement></UserManagement></Tab.Pane> },
                { menuItem: "杂项", pane: <Tab.Pane key={7}><MiscManagement></MiscManagement></Tab.Pane> },
            ]}></Tab>
        </div>
    </> : <>
        <div style={{ height: "400px" }}>
            <Dimmer active>
                <Loader>加载数据中...</Loader>
            </Dimmer>
        </div>
    </>;
}

export default AdminView;