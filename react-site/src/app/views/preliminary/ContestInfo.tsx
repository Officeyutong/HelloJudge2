import _ from "lodash";
import React, { useMemo } from "react";
import { Link } from "react-router-dom";
import { Button, Form, Icon, Segment } from "semantic-ui-react";
import { PUBLIC_URL } from "../../App";
import { Markdown } from "../../common/Markdown";
import { toLocalTime } from "../../common/Utils";
import UserLink from "../utils/UserLink";
import { PreliminaryContestDetail } from "./client/types";

type ContestInfoProps = Pick<PreliminaryContestDetail, "description" | "duration" | "uploader" | "upload_time" | "problems"> & { id: number };


const ContestInfo: React.FC<ContestInfoProps> = ({
    description,
    duration,
    uploader,
    upload_time,
    id,
    problems
}) => {
    const selectionCount = useMemo(() => _(problems).sumBy(t => t.problemType === "selection" ? 1 : 0), [problems]);
    const blankCount = useMemo(() => _(problems).sumBy(t => t.problemType === "fill_blank" ? 1 : 0), [problems]);
    const fullScore = useMemo(() => _(problems).map(t => t.score).sum(), [problems]);

    return <Segment stacked>
        <Form>
            {description && <Form.Field>
                <label>比赛简介</label>
                <Markdown markdown={description}></Markdown>
            </Form.Field>}
            <Form.Field>
                <label>比赛时长</label>
                <div>{Math.ceil(duration / 60)} 分钟</div>
            </Form.Field>
            <Form.Field>
                <label>比赛提供者</label>
                <UserLink data={uploader}></UserLink>
            </Form.Field>
            <Form.Field>
                <label>上传时间</label>
                <div>{toLocalTime(upload_time)}</div>
            </Form.Field>
            <Form.Field>
                <label>信息</label>
                <div>共 {selectionCount} 道选择题, {blankCount} 道填空题, 满分 {fullScore}</div>
            </Form.Field>
            <Button icon labelPosition="right" color="green" as={Link} to={`${PUBLIC_URL}/preliminary/contest/${id}/0`}>
                进入比赛
                <Icon name="arrow right"></Icon>
            </Button>
        </Form>
    </Segment>
};

export default ContestInfo;