import { useState } from "react";
import { Button } from "semantic-ui-react";
import { TeamDetail } from "../client/types";
import BatchAddMembersDialog from "./BatchAddMembersDialog";

interface TeamManageProps {
    team: number;
    reloadCallback: () => void;
    teamMembers: TeamDetail["members"];
};

const TeamManage: React.FC<TeamManageProps> = (props) => {
    const [showBatchAddModal, setShowBatchAddModal] = useState(false);
    return <>
        <Button color="green" onClick={() => setShowBatchAddModal(true)}>批量添加成员</Button>
        {showBatchAddModal && <BatchAddMembersDialog
            finishCallback={props.reloadCallback}
            onClose={() => setShowBatchAddModal(false)}
            open={showBatchAddModal}
            team={props.team}
            teamMembers={props.teamMembers}
        ></BatchAddMembersDialog>}
    </>;
};

export default TeamManage;