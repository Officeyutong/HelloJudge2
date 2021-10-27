import _ from "lodash";
import React from "react";
import { useSelector } from "react-redux";
import { Icon, Label } from "semantic-ui-react";
import { SemanticICONS } from "semantic-ui-react/dist/commonjs/generic";
import { SubmissionStatus } from "../../common/types";
import { StateType } from "../../states/Manager";

const JudgeStatusLabel: React.FC<{ status: SubmissionStatus; showText?: boolean }> = ({ status, showText }) => {
    const willShowText = showText === undefined ? true : showText;
    const judgeStatus = useSelector((s: StateType) => s.userState.userData.judgeStatus);
    const extractedData: typeof judgeStatus[0] = _.has(judgeStatus, status) ? judgeStatus[status]! : {
        icon: "" as SemanticICONS, color: "black", text: status
    };
    const loading = extractedData.icon.includes("loading");

    return <Label color={extractedData.color} circular={!willShowText}>
        <Icon loading={loading} name={(extractedData.icon || "").replaceAll(/((icon)|(loading))/g, "").trim() as SemanticICONS}></Icon>
        {willShowText ? extractedData.text : null}
    </Label>;
};

export default JudgeStatusLabel;