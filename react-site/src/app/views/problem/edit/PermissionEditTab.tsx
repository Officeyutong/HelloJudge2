import React from "react";
import { Checkbox, Form, Input } from "semantic-ui-react";
import { ProblemUpdateInfo } from "../client/types";
import { v4 as uuidv4 } from "uuid";
type ProblemPermission = Pick<ProblemUpdateInfo, "public" | "invite_code" | "submissionVisible">;

interface PermissionEditProps extends ProblemPermission {
    onUpdate: (data: ProblemPermission) => void;
};

const PermissionEdit: React.FC<PermissionEditProps> = (props) => {

    const data: ProblemPermission = {
        public: props.public,
        invite_code: props.invite_code,
        submissionVisible: props.submissionVisible
    };
    const update = (idata: ProblemPermission) => {
        props.onUpdate({
            invite_code: idata.invite_code,
            public: idata.public,
            submissionVisible: idata.submissionVisible
        });
    };
    return <div>
        <Form>
            <Form.Field>
                <Checkbox
                    checked={props.public}
                    toggle
                    onChange={() => update({ ...data, public: !data.public })}
                    label="公开(如果此题非公开，则用户需要具有相应权限才可使用)"
                ></Checkbox>
            </Form.Field>
            {!data.public && <>
                <Form.Field>
                    <label>邀请码</label>
                    <Input actionPosition="left" action={{
                        content: "随机生成",
                        onClick: () => update({ ...data, invite_code: uuidv4() })
                    }} value={data.invite_code} onChange={(e, d) => update({ ...data, invite_code: d.value })}></Input>
                </Form.Field>
                <Form.Field>
                    <Checkbox
                        checked={data.submissionVisible}
                        toggle
                        onChange={() => update({ ...data, submissionVisible: !data.submissionVisible })}
                        label="允许用户查看其他人的提交(如果勾选，则有权限使用该题目的用户可以查看其他人在该题目的提交)"
                    ></Checkbox>
                </Form.Field>

            </>}
        </Form>
    </div>;
};
export default PermissionEdit;