import React from "react";
import { Button, Modal, Table } from "semantic-ui-react";
import { ProblemInfo } from "./client/types";
interface ProblemFilesModalProps {
    open: boolean;
    onClose: () => void;
    data: Pick<ProblemInfo, "files" | "downloads">,
    urlMaker: (filename: string) => string;
}

const ProblemFilesModal: React.FC<ProblemFilesModalProps> = ({
    onClose,
    open,
    data,
    urlMaker
}) => {
    const downloadSet = new Set<string>();
    data.downloads.map(x => downloadSet.add(x));
    const downloadData = data.files.filter(x => downloadSet.has(x.name));
    // const [downloading, setDownloading] = useState(false);
    // const [finished, setFinished] = useState(0);
    // const [totalCount, setTotalCount] = useState(0);
    downloadData.sort((x, y) => {
        const key1 = x.name, key2 = y.name;
        if (key1 < key2) return -1;
        else if (key1 === key2) return 0;
        else return 1;
    });
    // const download = async () => {
    //     try {
    //         setFinished(0);
    //         setTotalCount(downloadData.length);
    //         const resp = await axios.all(downloadData.map(async (entry) => {
    //             const url = urlMaker(entry.name);
    //             const r = await axios.get(url,{
    //                 responseType:"blob"
    //             });
    //             setFinished(r => r + 1);
    //             const blob = new Blob([r.data]);
    //             return { filename: entry.name, data: blob };
    //         }));
    //         const zip = new JSZip();
    //         resp.forEach(item => zip.file(item.filename, item.data));
    //         const zipFile = await zip.generateAsync({ type: "blob" });
    //         FileSaver.saveAs(zipFile, "download.zip");
    //     } catch { } finally {
    //         setDownloading(false);
    //     }
    // }
    return <Modal
        open={open}
        onClose={onClose}
        size="tiny"
        closeOnDimmerClick={false}
    >
        <Modal.Header>
            题目文件下载
        </Modal.Header>
        <Modal.Content>
            <div style={{ overflowY: "scroll", maxHeight: "700px" }}>
                <Table celled>
                    <Table.Header>
                        <Table.Row>
                            <Table.HeaderCell>文件名</Table.HeaderCell>
                            <Table.HeaderCell>大小</Table.HeaderCell>
                            <Table.HeaderCell>操作</Table.HeaderCell>
                        </Table.Row>
                    </Table.Header>
                    <Table.Body>
                        {downloadData.map((x, i) => <Table.Row
                            key={i}
                        >
                            <Table.Cell>{x.name}</Table.Cell>
                            <Table.Cell>{Math.ceil(x.size / 1024)}KB</Table.Cell>
                            <Table.Cell>
                                <Button size="tiny" as="a" color="green" href={urlMaker(x.name)} target="_blank" rel="noreferrer">下载</Button>
                            </Table.Cell>
                        </Table.Row>)}
                    </Table.Body>
                </Table>
            </div>
            {/* {downloading && <>
                <Progress progress percent={Math.round(finished / totalCount * 100)} success></Progress>
            </>} */}
        </Modal.Content>
        <Modal.Actions>
            {/* <Button disabled={downloading} color="green" onClick={download}>
                打包下载
            </Button> */}
            <Button color="red" onClick={onClose}>
                关闭
            </Button>
        </Modal.Actions>
    </Modal>
};

export default React.memo(ProblemFilesModal);