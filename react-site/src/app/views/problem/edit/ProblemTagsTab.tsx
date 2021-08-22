import React, { useEffect, useState } from "react";
import { Button, Dimmer, Divider, Header, Loader, Modal } from "semantic-ui-react";
import { ButtonClickEvent, ProblemTagEntry } from "../../../common/types";
import { showSuccessPopup } from "../../../dialogs/Utils";
import ProblemTagLabel from "../../utils/ProblemTagLabel";
import problemClient from "../client/ProblemClient";

const ProblemTags: React.FC<{ id: number; defaultTags: ProblemTagEntry[] }> = ({ id, defaultTags }) => {
    const [allTags, setAllTags] = useState<ProblemTagEntry[]>([]);
    const [loading, setLoading] = useState(false);
    const [loaded, setLoaded] = useState(false);
    const [usedTags, setUsedTags] = useState<ProblemTagEntry[]>(defaultTags);
    const [showModal, setShowModal] = useState(false);
    const [currTags, setCurrTags] = useState<ProblemTagEntry[]>([]);
    const currUsingTags = new Set(currTags.map(x => x.id));
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    setLoading(true);
                    const resp = await problemClient.getProblemtags();
                    setAllTags(resp);
                    setLoaded(true);
                } catch { } finally {
                    setLoading(false);
                }
            })();
        }
    }, [loaded]);
    const saveTags = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            await problemClient.updateTagsForProblem(id, currTags.map(x => x.id));
            setUsedTags([...currTags]);
            setShowModal(false);
            showSuccessPopup("保存成功");
        } catch {

        }
        finally {
            target.classList.remove("loading");
        }
    };
    return <div>
        {loading && <div style={{ height: "400px" }}>
            <Dimmer active>
                <Loader>加载中...</Loader>
            </Dimmer>
        </div>}
        {loaded && <>
            <Header as="h3">
                已选中标签
            </Header>
            <div>
                {usedTags.map((x, i) => <ProblemTagLabel
                    data={x}
                    key={i}
                ></ProblemTagLabel>)}
            </div>
            <Divider></Divider>
            <Button color="green" onClick={() => {
                setCurrTags([...usedTags]);
                setShowModal(true);
            }}>
                编辑
            </Button>
        </>}
        {showModal && <Modal open size="small" closeOnDimmerClick={false}>
            <Modal.Header>
                标签编辑
            </Modal.Header>
            <Modal.Content>
                <Header as="h3">
                    可用标签
                </Header>
                <div>
                    {allTags.filter(x => !currUsingTags.has(x.id)).map((x, i) => <ProblemTagLabel
                        data={x}
                        onClick={() => setCurrTags([...currTags.filter(y => y.id !== x.id), x])}
                        key={i}
                    ></ProblemTagLabel>)}
                </div>
                <Divider></Divider>
                <Header as="h3">
                    已选中标签
                </Header>
                <div>
                    {currTags.map((x, i) => <ProblemTagLabel
                        key={i}
                        data={x}
                        onClick={() => setCurrTags(currTags.filter(y => y.id !== x.id))}
                    ></ProblemTagLabel>)}
                </div>
            </Modal.Content>
            <Modal.Actions>
                <Button onClick={saveTags} color="green">
                    保存更改
                </Button>
                <Button onClick={() => setShowModal(false)} color="red">
                    取消
                </Button>
            </Modal.Actions>
        </Modal>
        }
    </div >;
};

export default React.memo(ProblemTags);