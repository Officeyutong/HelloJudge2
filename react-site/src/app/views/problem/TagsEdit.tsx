import axios from "axios";
import _ from "lodash";
import React, { useEffect, useState } from "react";
import { Button, Dimmer, Header, Input, Label, Loader, Modal, Segment, SemanticCOLORS, Table } from "semantic-ui-react";
import { ButtonClickEvent, ProblemTagEntry } from "../../common/types";
import { useDocumentTitle } from "../../common/Utils";
import { showConfirm, showErrorModal } from "../../dialogs/Dialog";
import { showSuccessPopup } from "../../dialogs/Utils";
import { APIError } from "../../Exception";
import problemClient from "./client/ProblemClient";

interface ExtraTagEntry extends ProblemTagEntry {
    modified: boolean;
}
(window as (typeof window & { popup: any })).popup = showSuccessPopup;
const TagsEdit: React.FC<{}> = () => {
    useDocumentTitle("题目标签编辑");
    const [loaded, setLoaded] = useState(false);
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<ExtraTagEntry[]>([]);
    const [showAddModal, setShowAddModal] = useState(false);
    const [ID, setID] = useState("");
    useEffect(() => {
        if (!loaded) {
            (async () => {
                setLoading(true);
                try {
                    const resp = (await problemClient.getProblemtags()).map(x => ({ ...x, modified: false }));
                    setData(resp);
                    setLoaded(true); setLoading(false);
                } catch { } finally {
                }
            })();
        }
    }, [loaded]);
    const removeTag = (id: string) => {
        showConfirm(`您确定要删除 ${id}吗`, async () => {
            try {
                setLoading(true);
                await problemClient.removeProblemTag(id);
                setData(data.filter(x => x.id !== id));
                showSuccessPopup("删除成功");
            } catch { } finally {
                setLoading(false);
            }
        });
    };
    const update = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        const toSave = data.filter(x => x.modified);
        try {
            setLoading(true);
            target.classList.add("loading");
            await axios.all(toSave.map(x => problemClient.updateProblemTag(
                x.id, x.display, x.color
            )));
            showSuccessPopup("保存成功");
        } catch { } finally {
            setLoading(false);
            target.classList.remove("loading");
        }
    };
    const addTag = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget
        try {
            target.classList.add("loading");
            const resp = await problemClient.createProblemTag(ID);
            setData([...data, { ...resp, modified: false, id: ID }]);
            target.classList.remove("loading");
            setShowAddModal(false);
            window.scroll({
                top: document.body.clientHeight,
                behavior: "smooth"
            });
        } catch (e) {
            showErrorModal((e as APIError).message);
            target.classList.remove("loading");
        }
    };
    return <div>
        <Header as="h1">
            题目标签编辑
        </Header>
        <Segment stacked>
            {loading && <div style={{ height: "400px" }}>
                <Dimmer active>
                    <Loader></Loader>
                </Dimmer>
            </div>}
            <div>
                <Button color="green" onClick={() => {
                    setID("");
                    setShowAddModal(true);
                }}>
                    新建标签
                </Button>
                <Button color="green" onClick={update}>
                    保存
                </Button>
            </div>
            <Table celled textAlign="center">
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell>标签ID</Table.HeaderCell>
                        <Table.HeaderCell>显示名</Table.HeaderCell>
                        <Table.HeaderCell>颜色</Table.HeaderCell>
                        <Table.HeaderCell>预览</Table.HeaderCell>
                        <Table.HeaderCell>操作</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {data.map((x, i) => <Table.Row key={i}>
                        <Table.Cell>{x.id}</Table.Cell>
                        <Table.Cell>
                            <Input value={x.display} onChange={(e, d) => setData(_.set(_.clone(data), i, { ...x, display: d.value, modified: true }))}></Input>
                        </Table.Cell>
                        <Table.Cell>
                            <Input value={x.color} onChange={(e, d) => setData(_.set(_.clone(data), i, { ...x, color: d.value, modified: true }))}></Input>
                        </Table.Cell>
                        <Table.Cell>
                            <Label color={x.color as SemanticCOLORS}>
                                {x.display}
                            </Label>
                        </Table.Cell>
                        <Table.Cell>
                            <Button size="tiny" color="red" onClick={() => removeTag(x.id)}>
                                删除
                            </Button>
                        </Table.Cell>
                    </Table.Row>)}
                </Table.Body>
            </Table>
        </Segment>
        {showAddModal && <Modal open closeOnDimmerClick={false} size="tiny">
            <Modal.Header>请输入新标签的ID</Modal.Header>
            <Modal.Content>
                <Input fluid value={ID} onChange={(e, d) => setID(d.value)}></Input>
            </Modal.Content>
            <Modal.Actions>
                <Button color="green" onClick={addTag}>
                    确认
                </Button>
            </Modal.Actions>
        </Modal>}

    </div>;
}

export default TagsEdit;