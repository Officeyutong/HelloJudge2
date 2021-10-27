import { DateTime } from "luxon";
import QueryString from "qs";
import React, { useEffect, useMemo, useRef, useState } from "react";
import { Button, Dimmer, Divider, Form, Loader, Message, Modal, Progress, Table } from "semantic-ui-react";
import { showErrorModal, showSuccessModal } from "../../../dialogs/Dialog";
import { showSuccessPopup } from "../../../dialogs/Utils";
import UserLink from "../../utils/UserLink";
import teamClient from "../client/TeamClient";
import { TeamFileEntry } from "../client/types";

interface TeamFileProps {
    teamID: number;
    isAdmin: boolean;

};

const TeamFile: React.FC<TeamFileProps> = ({ teamID, isAdmin }) => {
    const [loading, setLoading] = useState(false);
    const [loaded, setLoaded] = useState(false);
    const [data, setData] = useState<TeamFileEntry[]>([]);
    const [showProgressModal, setShowProgressModal] = useState(false);
    const [percent, setPercent] = useState(0);
    const sortedData = useMemo(() => {
        const newData = [...data];
        newData.sort((x, y) => x.filename < y.filename ? -1 : 1);
        return newData;
    }, [data]);
    const inputRef = useRef<HTMLInputElement>(null);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    setLoading(true);
                    setData(await teamClient.getTeamFiles(teamID));
                    setLoaded(true);
                } catch { } finally {
                    setLoading(false);
                }
            })();
        }
    }, [loaded, teamID]);
    const removeFile = async (fileID: string) => {
        try {
            setLoading(true);
            await teamClient.removeTeamFile(teamID, fileID);
            setData(await teamClient.getTeamFiles(teamID));
            showSuccessPopup("删除成功!");
        } catch { } finally {
            setLoading(false);
        }
    };
    const doUpload = async () => {
        const elem = inputRef.current;
        if (elem === null) return;
        const files = elem.files;

        if (files === null || files.length === 0) {
            showErrorModal("请选择文件！");
            return;
        }
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            const current = files[i];
            formData.append(
                current.name, current, current.name
            );
        }
        try {
            setShowProgressModal(true);
            setPercent(0);
            await teamClient.uploadTeamFile(
                teamID,
                formData,
                evt => {
                    setPercent(Math.floor(100 * evt.loaded / evt.total));
                }
            )
            setData(await teamClient.getTeamFiles(teamID));
            showSuccessModal("上传完成!");
        } catch { } finally {
            setShowProgressModal(false);
        }
    };
    return <>
        {loading && <Dimmer active>
            <Loader></Loader>
        </Dimmer>}
        {isAdmin && <>
            <Message info>
                <Message.Header>
                    提示
                </Message.Header>
                <Message.Content>
                    <p>团队管理员可以在此上传文件，团队内的所有成员可以在此下载文件</p>
                </Message.Content>
            </Message>
            <Form>
                <Form.Group>
                    <Form.Field>
                        <input multiple type="file" ref={inputRef}></input>
                    </Form.Field>
                    <Form.Field>
                        <Button color="green" onClick={doUpload}>
                            上传
                        </Button>
                    </Form.Field>
                </Form.Group>
            </Form>
            <Divider></Divider>

        </>}
        {sortedData.length === 0 ? <div>还没有团队文件...</div> : <Table>
            <Table.Header>
                <Table.Row>
                    <Table.HeaderCell>文件名</Table.HeaderCell>
                    <Table.HeaderCell>文件大小</Table.HeaderCell>
                    <Table.HeaderCell>上传用户</Table.HeaderCell>
                    <Table.HeaderCell>上传时间</Table.HeaderCell>
                    <Table.HeaderCell>操作</Table.HeaderCell>
                </Table.Row>
            </Table.Header>
            <Table.Body>
                {sortedData.map((x, i) => <Table.Row key={i}>
                    <Table.Cell>{x.filename}</Table.Cell>
                    <Table.Cell>{Math.ceil(x.filesize / 1024)} KB</Table.Cell>
                    <Table.Cell><UserLink data={x.uploader}></UserLink></Table.Cell>
                    <Table.Cell>{DateTime.fromSeconds(x.upload_time).toJSDate().toLocaleString()}</Table.Cell>
                    <Table.Cell>
                        <Button as="a" href={
                            `/api/team/download_file?${QueryString.stringify({ teamID: teamID, fileID: x.file_id })}`
                        } size="tiny" color="green">下载</Button>
                        {isAdmin && <Button size="tiny" color="red" onClick={() => removeFile(x.file_id)}>删除</Button>}
                    </Table.Cell>
                </Table.Row>)}
            </Table.Body>
        </Table>}
        {showProgressModal && <Modal size="tiny" closeOnDimmerClick={false} open>
            <Modal.Header>
                上传文件中
            </Modal.Header>
            <Modal.Content>
                <Progress percent={percent} progress="percent" active color="green"></Progress>
            </Modal.Content>
        </Modal>}
    </>;
};

export default TeamFile;