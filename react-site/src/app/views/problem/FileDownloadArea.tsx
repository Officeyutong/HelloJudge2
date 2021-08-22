import _ from "lodash";
import React, { useMemo, useState } from "react";
import { Container, Header, Label } from "semantic-ui-react";
import { ProblemInfo } from "./client/types";
import ProblemFilesModal from "./ProblemFilesModal";

interface FileDownloadAreaProps {
    data: Pick<ProblemInfo, "downloads" | "files">;
    urlMaker: (filename: string) => string;
};

const FileDownloadArea: React.FC<FileDownloadAreaProps> = ({ data, urlMaker }) => {
    const [showFiles, setShowFiles] = useState(false);
    const downloads = useMemo(() => new Set(data.downloads), [data.downloads]);
    return <>
        <div style={{ marginTop: "20px" }}>
            <Header as="h4">
                文件下载
            </Header>
            {_(data.files).map(x => x.name).filter(y => downloads.has(y)).take(5).map((x, i) => <Label key={i} as="a" href={urlMaker(x)} style={{ marginBottom: "5px" }}>
                <span>{x}</span>
            </Label>).value()}
            <Container textAlign="right">
                {
                    // eslint-disable-next-line jsx-a11y/anchor-is-valid
                    <a style={{ cursor: "pointer" }} onClick={() => setShowFiles(true)}>查看全部...</a>
                }
            </Container>
        </div>

        {showFiles && <ProblemFilesModal
            onClose={() => setShowFiles(false)}
            open={showFiles}
            data={data!}
            urlMaker={urlMaker}
        ></ProblemFilesModal>}
    </>
};

export default React.memo(FileDownloadArea);