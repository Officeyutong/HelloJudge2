import { DateTime } from "luxon";
import React, { useEffect, useRef, useState } from "react";
import { Button, Checkbox, Dimmer, Divider, Form, Grid, Header, Input, Loader, Message, Modal, Progress, Table } from "semantic-ui-react";
import { ButtonClickEvent } from "../../../common/types";
import { showErrorModal, showSuccessModal } from "../../../dialogs/Dialog";
import problemClient from "../client/ProblemClient";
import { ProblemEditReceiveInfo } from "../client/types";

type ProblemFilesEntry = Pick<ProblemEditReceiveInfo, "files" | "downloads" | "provides">;

interface ProblemFilesEditProps extends ProblemFilesEntry {
    id: number;
    onUpdate: (data: ProblemFilesEntry) => void;
};
function transformTime(timestamp: number): string {
    return DateTime.fromSeconds(timestamp).toJSDate().toLocaleString();
}
const ProblemFilesEditTab: React.FC<ProblemFilesEditProps> = (props) => {
    const {
        downloads,
        files,
        provides,
        id
    } = props;
    const data: ProblemFilesEntry = {
        downloads, files, provides
    };
    const update = (idata: ProblemFilesEntry) => {
        props.onUpdate({
            downloads: idata.downloads,
            files: idata.files,
            provides: idata.provides
        });
    };
    const [downloadsSet, setDownloadsSet] = useState<Set<string>>(new Set());
    const [providesSet, setProvidesSet] = useState<Set<string>>(new Set());
    const [loading, setLoading] = useState(false);
    const [decompressZip, setDecompressZip] = useState(true);
    const uploadInputRef = useRef<Input>(null);
    const [showProgressModal, setShowProgressModal] = useState(false);
    const [progress, setProgress] = useState(0);
    useEffect(() => {
        setDownloadsSet(new Set(downloads));
    }, [downloads]);
    useEffect(() => {
        setProvidesSet(new Set(provides));
    }, [provides]);
    const removeFile = async (evt: ButtonClickEvent, name: string) => {
        try {
            setLoading(true);
            const resp = await problemClient.removeProblemFile(id, name);
            update({ ...data, files: resp.file_list });
        } catch { } finally {
            setLoading(false);
        }
    };
    const regenerateFileList = async () => {
        try {
            setLoading(true);
            const resp = await problemClient.regenerateFileList(id);
            update({ ...data, files: resp });
        } catch { } finally {
            setLoading(false);
        }
    };
    const doFileUplpad = async () => {
        try {
            setProgress(0);
            const refVal = uploadInputRef.current!;
            const inputRef = refVal as (typeof refVal & {
                inputRef: {
                    current: HTMLInputElement
                }
            });
            const files = inputRef.inputRef.current.files;
            if (!files || files.length === 0) {
                showErrorModal("请选择文件!");
                return;
            }
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                const item = files[i];
                formData.append(
                    item.name, item, item.name
                );
            }
            formData.append("decompress_zip", (decompressZip ? 1 : 0).toString());
            setShowProgressModal(true);
            const resp = await problemClient.uploadProblemFile(id, formData, (evt: ProgressEvent) => {
                setProgress(Math.floor(evt.loaded / evt.total * 100));
            });
            update({ ...data, files: resp.file_list });
            showSuccessModal("上传成功!");
            inputRef.inputRef.current.files = null;
        } catch { } finally {
            setShowProgressModal(false);
        }
    };
    return <div>
        {loading && <Dimmer active>
            <Loader></Loader>
        </Dimmer>}
        <Grid columns="2">
            <Grid.Column width="12">
                <Table>
                    <Table.Header>
                        <Table.Row>
                            <Table.HeaderCell>ID</Table.HeaderCell>
                            <Table.HeaderCell>文件名</Table.HeaderCell>
                            <Table.HeaderCell>上传时间</Table.HeaderCell>
                            <Table.HeaderCell>大小</Table.HeaderCell>
                            <Table.HeaderCell>操作</Table.HeaderCell>
                            <Table.HeaderCell>公开</Table.HeaderCell>
                            <Table.HeaderCell>编译时提供</Table.HeaderCell>
                        </Table.Row>
                    </Table.Header>
                    <Table.Body>
                        {files.map((x, i) => <Table.Row key={i}>
                            <Table.Cell>{i + 1}</Table.Cell>
                            <Table.Cell>{x.name}</Table.Cell>
                            <Table.Cell>{x.last_modified_time ? transformTime(x.last_modified_time) : null}</Table.Cell>
                            <Table.Cell>{Math.ceil(x.size / 1024)}KB</Table.Cell>
                            <Table.Cell>
                                <Button.Group>
                                    <Button size="tiny" color="green" as="a" href={`/api/download_file/${id}/${x.name}`}>下载</Button>
                                    <Button size="tiny" color="red" onClick={e => removeFile(e, x.name)}>删除</Button>
                                </Button.Group>
                            </Table.Cell>
                            <Table.Cell>
                                <Checkbox toggle checked={downloadsSet.has(x.name)} onChange={() => {
                                    if (downloadsSet.has(x.name)) {
                                        update({ ...data, downloads: data.downloads.filter(y => y !== x.name) });
                                    } else {
                                        update({ ...data, downloads: [...data.downloads, x.name] });
                                    }
                                }}></Checkbox>
                            </Table.Cell>
                            <Table.Cell>
                                <Checkbox toggle checked={providesSet.has(x.name)} onChange={() => {
                                    if (providesSet.has(x.name)) {
                                        update({ ...data, provides: data.provides.filter(y => y !== x.name) });
                                    } else {
                                        update({ ...data, provides: [...data.provides, x.name] });
                                    }
                                }}></Checkbox>
                            </Table.Cell>
                        </Table.Row>)}
                    </Table.Body>
                </Table>
            </Grid.Column>
            <Grid.Column width="4">
                <Grid columns="1">
                    <Grid.Column>
                        <Button color="green" onClick={() => update({ ...data, downloads: data.files.map(x => x.name) })}>
                            全部公开
                        </Button>
                        <Button color="red" onClick={() => update({ ...data, downloads: [] })}>
                            全部不公开
                        </Button>
                    </Grid.Column>
                    <Grid.Column>
                        <Button color="green" onClick={regenerateFileList}>
                            重新生成文件列表
                        </Button>
                        <Divider></Divider>
                    </Grid.Column>
                    <Grid.Column>
                        <Header as="h3">
                            上传文件
                        </Header>
                        <Form>
                            <Form.Field>
                                <Checkbox label="自动解压zip文件" toggle checked={decompressZip} onChange={(_, d) => setDecompressZip(!decompressZip)}></Checkbox>
                            </Form.Field>
                            <Form.Field>
                                <Input type="file" fluid ref={uploadInputRef} multiple></Input>
                            </Form.Field>
                            <Button color="green" onClick={doFileUplpad}>
                                上传
                            </Button>
                        </Form>
                        <Message info>
                            <Message.Header>
                                提示
                            </Message.Header>
                            <Message.Content>
                                部分文件的文件名可能会被处理以保证服务器数据安全。
                            </Message.Content>
                        </Message>
                    </Grid.Column>
                </Grid>
            </Grid.Column>
        </Grid>
        {showProgressModal && <Modal size="tiny" closeOnDimmerClick={false} open>
            <Modal.Header>
                上传文件中
            </Modal.Header>
            <Modal.Content>
                <Progress percent={progress} progress="percent" active color="green"></Progress>
            </Modal.Content>
        </Modal>}
    </div>;
};

export default ProblemFilesEditTab;