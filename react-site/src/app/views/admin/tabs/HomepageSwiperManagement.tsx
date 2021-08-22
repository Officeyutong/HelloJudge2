import React, { useCallback, useEffect, useState } from "react";
import { Input, Table, Image, Button, Icon, Dimmer, Loader, Modal } from "semantic-ui-react";
import { showSuccessPopup } from "../../../dialogs/Utils";
import HomepageSwiper from "../../utils/HomepageSwiper";
import { adminClient } from "../client/AdminClient";
import { HomepageSwiperList } from "../client/types";

const HomepageSwiperManagement: React.FC<{}> = () => {
    //TODO: 没写完
    const [loaded, setLoaded] = useState(false);
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<HomepageSwiperList | null>(null);
    const [preview, setPreview] = useState(false);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    setLoading(true);
                    setData(await adminClient.getHomepageSwiperList());
                    setLoaded(true);
                } catch (e) { }
                finally { setLoading(false); }
            })();
        }
    }, [loaded]);
    const save = useCallback(async () => {
        try {
            setLoading(true);
            await adminClient.updateHomepageSwiper(data!);
            showSuccessPopup("保存完成!");
        } catch (e) { } finally { setLoading(false); }
    }, [data]);
    return <div>
        {loading && <div>
            <Dimmer active>
                <Loader>加载中...</Loader>
            </Dimmer>
            <div style={{ height: "400px" }}></div>
        </div>}
        {loaded && <div>
            <Table>
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell>图片URL</Table.HeaderCell>
                        <Table.HeaderCell>链接URL</Table.HeaderCell>
                        <Table.HeaderCell>图片预览</Table.HeaderCell>
                        <Table.HeaderCell>操作</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {data!.map((x, i) => <Table.Row key={i}>
                        <Table.Cell>
                            <Input fluid value={x.image_url} onChange={(_, d) => {
                                const arr = [...data!];
                                arr[i].image_url = d.value;
                                setData(arr);
                            }}></Input>
                        </Table.Cell>
                        <Table.Cell>
                            <Input fluid value={x.link_url} onChange={(_, d) => {
                                const arr = [...data!];
                                arr[i].link_url = d.value;
                                setData(arr);
                            }}></Input>
                        </Table.Cell>
                        <Table.Cell>
                            <Image size="tiny" src={x.image_url}></Image>
                        </Table.Cell>
                        <Table.Cell>
                            <Button.Group>
                                <Button color="green" size="tiny" icon disabled={i === 0} onClick={() => {
                                    const arr = [...data!];
                                    [arr[i - 1], arr[i]] = [arr[i], arr[i - 1]];
                                    setData(arr);
                                }}>
                                    <Icon name="angle up"></Icon>
                                </Button>
                                <Button color="green" size="tiny" icon disabled={i === data!.length - 1} onClick={() => {
                                    const arr = [...data!];
                                    [arr[i + 1], arr[i]] = [arr[i], arr[i + 1]];
                                    setData(arr);
                                }}>
                                    <Icon name="angle down"></Icon>
                                </Button>
                                <Button color="green" size="tiny" icon onClick={() => setData(data!.filter((x, j) => j !== i))}>
                                    <Icon name="times"></Icon>
                                </Button>
                            </Button.Group>
                        </Table.Cell>
                    </Table.Row>)}
                </Table.Body>
            </Table>
            <Button color="blue" onClick={() => setData([...data!, { image_url: "", link_url: "" }])}>添加</Button>
            <Button color="green" onClick={() => setPreview(true)}>预览</Button>
            <Button color="green" onClick={save}>保存</Button>
        </div>}

        <Modal open={preview}>
            <Modal.Content>
                <HomepageSwiper data={data!}></HomepageSwiper>
            </Modal.Content>
            <Modal.Actions>
                <Button color="green" onClick={() => setPreview(false)}>
                    关闭
                </Button>
            </Modal.Actions>
        </Modal>
    </div>;
}

export default HomepageSwiperManagement;