import { useEffect, useRef, useState } from "react";
import { Button, Container, Dimmer, Divider, Form, Grid, Header, Loader, Modal, Pagination, Progress, Segment } from "semantic-ui-react";
import { useDocumentTitle } from "../../common/Utils";
import { showErrorModal } from "../../dialogs/Dialog";
import imageStoreClient from "./client/ImageStoreClient";
import { ImageListEntry } from "./client/types";
import ImageCard from "./ImageCard";

const ImageList: React.FC<{}> = () => {
    const [loaded, setLoaed] = useState(false);
    const [loading, setLoading] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);
    const [showProgressModal, setShowProgressModal] = useState(false);
    const [progress, setProgress] = useState(0);
    const [pageCount, setPageCount] = useState(0);
    const [page, setPage] = useState(0);
    const [data, setData] = useState<ImageListEntry[]>([]);
    useDocumentTitle("图片上传服务")
    useEffect(() => {
        if (!loaded) loadPage(1);
    }, [loaded]);
    const loadPage = async (page: number) => {
        try {
            setLoading(true);
            const resp = await imageStoreClient.getImageList(page);
            setPageCount(resp.pageCount);
            setData(resp.images);
            setPage(page);
            setLoaed(true);
        } catch { } finally {
            setLoading(false);
        }
    };
    const doUpload = async () => {
        try {
            setProgress(0);
            const files = inputRef.current!.files;
            if (!files || files.length === 0) {
                showErrorModal("请选择文件!");
                return;
            }
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                const item = files[i];
                formData.append(item.name, item, item.name);
            }
            setShowProgressModal(true);
            await imageStoreClient.uploadImages(formData, evt => {
                setProgress(Math.floor(evt.loaded / evt.total * 100));
            });
            setShowProgressModal(false);
            await loadPage(1);

        } catch { } finally {

        }
    };

    return <>
        <Header as="h1">
            图片上传服务
        </Header>
        <Segment>
            {loading && <Dimmer active>
                <Loader></Loader>
            </Dimmer>}
            <Header as="h2">
                选择图片
            </Header>
            <Form>
                <Form.Field>
                    <input type="file" multiple ref={inputRef}></input>
                </Form.Field>
                <Form.Field>
                    <Button onClick={doUpload} color="green">
                        上传文件
                    </Button>
                </Form.Field>
            </Form>
            {loaded && <>
                <Divider></Divider>
                <Header as="h2">
                    已上传图片
                </Header>
                <Grid columns="3">
                    {data.map((item, i) => <Grid.Column key={i}>
                        <ImageCard
                            {...item}
                            withRemove={true}
                            removeCallback={() => loadPage(page)}
                        ></ImageCard>
                    </Grid.Column>)}
                </Grid>
                <Container textAlign="center">
                    <Pagination
                        totalPages={pageCount}
                        activePage={page}
                        onPageChange={(_, d) => loadPage(d.activePage as number)}
                    ></Pagination>
                </Container>
            </>}
        </Segment>
        {showProgressModal && <Modal size="tiny" closeOnDimmerClick={false} open>
            <Modal.Header>
                上传文件中
            </Modal.Header>
            <Modal.Content>
                <Progress percent={progress} progress="percent" active color="green"></Progress>
            </Modal.Content>
        </Modal>}
    </>;
};

export default ImageList;