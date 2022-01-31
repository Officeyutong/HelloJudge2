import React, { useCallback, useEffect, useState } from "react";
import { Dimmer, Grid, Header, Loader, Segment, Pagination, Divider } from "semantic-ui-react";
import { showConfirm, showErrorModal } from "../../../dialogs/Dialog";
import contestClient from "../client/ContestClient";
import { ClarificationDetailResponse } from "../client/types";
import ClarificationArea from "./ClarificationArea";
import ClarificationSendArea from "./ClarificationSendArea";

interface ClarificationListProps {
    contestID: number;
    virtualID: number;
    closed: boolean;
    managable: boolean;
    status: number;
};

const ClarificationList: React.FC<ClarificationListProps> = ({
    closed,
    contestID,
    virtualID,
    managable,
    status
}) => {
    const [loading, setLoading] = useState(false);
    const [loaded, setLoaded] = useState(false);
    const [page, setPage] = useState(0);
    const [pageCount, setPageCount] = useState(0);
    const [data, setData] = useState<ClarificationDetailResponse[]>([]);

    const loadPage = useCallback(async (page: number) => {
        try {
            setLoading(true);
            const resp = await contestClient.getClarificationList(contestID, page);
            setPageCount(resp.pageCount);
            setData(resp.data);
            setPage(page);
            setLoaded(true);
        } catch (e: any) {
            showErrorModal(e.message);
        } finally {
            setLoading(false);
        }

    }, [contestID]);
    useEffect(() => {
        if (!loaded) {
            loadPage(1);
        }
    }, [loadPage, loaded]);
    const removeClar = (id: number) => {
        showConfirm("您确定要删除此条回复吗?", async () => {
            try {
                setLoading(true);
                await contestClient.removeClarification(id);
                setLoading(false);
                await loadPage(page);
            } catch { } finally {
                setLoading(false);

            }
        });
    };
    return <>
        {data.length !== 0 && <><Header as="h3">
            提问
        </Header>
            <Segment>
                {loading && <Dimmer active><Loader></Loader></Dimmer>}
                {loading && data.length === 0 && <div style={{ height: "400px" }}></div>}
                {data.map((x, i) => <div key={i}>
                    <ClarificationArea
                        {...x}
                        managable={managable}
                        showEditReply={true}
                        removeCallback={() => removeClar(x.id)}
                    ></ClarificationArea>
                </div>)}
                <Grid columns="3" centered>
                    <Grid.Column>
                        <Pagination
                            totalPages={pageCount}
                            activePage={page}
                            onPageChange={(e, d) => loadPage(d.activePage as number)}
                        ></Pagination>
                    </Grid.Column>
                </Grid>
            </Segment>
            <Divider></Divider></>}
        {virtualID === -1 && status === 0 && <ClarificationSendArea
            contest={contestID}
            refresh={() => loadPage(1)}
        ></ClarificationSendArea>}
    </>;
};

export default React.memo(ClarificationList);