import React from "react";
import { Button, Icon } from "semantic-ui-react";

const PermissionPackTab: React.FC<{}> = () => {
    return <Button color="green" labelPosition="right" icon onClick={() => { window.open("/permissionpack/list") }}>
        <Icon name="paper plane outline"></Icon>
        前往权限包管理
    </Button>;
}
export default PermissionPackTab;
