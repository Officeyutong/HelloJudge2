import React from "react";
import { Button, Icon } from "semantic-ui-react";

const MiscManagement: React.FC<{}> = () => {

    return <div>
        <Button color="green" labelPosition="right" icon onClick={() => { window.open("/permissionpack/list") }}>
            <Icon name="paper plane outline"></Icon>
            前往权限包管理
        </Button>
        <Button color="green" labelPosition="right" icon onClick={() => { window.open("/wiki/config") }}>
            <Icon name="paper plane outline"></Icon>
            前往Wiki管理
        </Button>

    </div>;
}

export default MiscManagement;