import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { Header, Tab } from "semantic-ui-react";
import { useDocumentTitle } from "../../../common/Utils";
import InfoTab from "./InfoTab";
import UserEditTab from "./UserEditTab";

const PermissionPackEdit: React.FC<{}> = () => {
    const id = parseInt(useParams<{ id: string }>().id);
    const [title, setTitle] = useState("");
    useDocumentTitle(`${title} - 权限包`);
    return <div>
        <Header as="h1">
            {title}
        </Header>
        <Tab renderActiveOnly={false} panes={[
            { menuItem: "信息编辑", pane: <Tab.Pane key={0}><InfoTab id={id} updateTitle={setTitle} ></InfoTab></Tab.Pane> },
            { menuItem: "用户编辑", pane: <Tab.Pane key={1}><UserEditTab id={id}></UserEditTab></Tab.Pane> },
            
        ]}></Tab>
    </div>;
}

export default PermissionPackEdit;
