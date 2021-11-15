import { Button, Form, Grid, Image, Modal, Segment } from "semantic-ui-react";
import { toLocalTime } from "../../common/Utils";
import imageStoreClient from "./client/ImageStoreClient";
import * as clipboard from "clipboardy";
import { ButtonClickEvent } from "../../common/types";
import { useState } from "react";
interface ImageCardProps {
    filename: string;
    filesize: number;
    upload_time: number;
    file_id: string;
    thumbnail_id: string;
    withRemove: boolean;
    removeCallback: () => void;
};

const ImageCard: React.FC<ImageCardProps> = (props) => {
    const [showModal, setShowModal] = useState(false);
    const removeThis = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            await imageStoreClient.removeImage(props.file_id);
            props.removeCallback();
        } catch { } finally {
            target.classList.remove("loading");
        }
    };
    return <>
        <Segment>
            <Grid columns="2">
                <Grid.Column width="4">
                    <Image onClick={() => { setShowModal(true); }} style={{ height: "auto", cursor: "pointer" }} src={imageStoreClient.makeImageURL(props.thumbnail_id)}></Image>
                </Grid.Column>
                <Grid.Column width="12">
                    <Form>
                        <Form.Field>
                            <label>文件名</label>
                            <span>{props.filename}</span>
                        </Form.Field>
                        <Form.Field>
                            <label>上传时间</label>
                            <span>{toLocalTime(props.upload_time)}</span>
                        </Form.Field>
                        <Form.Field>
                            <span>
                                <Button size="tiny" color="blue" onClick={() => clipboard.write(`${window.origin}${imageStoreClient.makeImageURL(props.file_id)}`)}>
                                    URL
                                </Button>
                                <Button size="tiny" color="blue" onClick={() => clipboard.write(`![${props.filename}](${window.origin}${imageStoreClient.makeImageURL(props.file_id)})`)}>
                                    Markdown
                                </Button>
                                {props.withRemove && <Button onClick={removeThis} color="red" size="tiny">
                                    删除
                                </Button>}
                            </span>
                        </Form.Field>
                    </Form>
                </Grid.Column>
            </Grid>
        </Segment>
        {showModal && <Modal basic open={showModal} onClose={() => setShowModal(false)} closeOnDimmerClick={true}>
            <Modal.Content>
                <Image src={imageStoreClient.makeImageURL(props.file_id)}></Image>
            </Modal.Content>
        </Modal>}

    </>;
};

export default ImageCard;