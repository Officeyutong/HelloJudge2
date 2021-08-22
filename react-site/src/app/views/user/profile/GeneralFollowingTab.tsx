import React, { Fragment, useCallback, useEffect, useState } from "react";
import { Button, Dimmer, Divider, Feed, Grid, Image, Loader, Pagination } from "semantic-ui-react";
import { useAlreadyLogin, useProfileImageMaker } from "../../../common/Utils";
import { FolloweeItem, FollowerItem } from "../client/types";
import userClient from "../client/UserClient";

const GeneralFollowingTab: React.FC<{
    provider: (page: number) => Promise<{ pageCount: number; data: FolloweeItem[] | FollowerItem[] }>
}> = ({ provider }) => {
    const [loaded, setLoaded] = useState(false);
    const [data, setData] = useState<FolloweeItem[] | FollowerItem[]>([]);
    const [page, setPage] = useState(1);
    const [pageCount, setPageCount] = useState(0);
    const [loading, setLoading] = useState(false);
    const makeImageURL = useProfileImageMaker();
    const alreadyLogin = useAlreadyLogin();
    const loadPage = useCallback(async (page: number) => {
        try {
            setLoading(true);
            let resp = await provider(page);
            setData(resp.data);
            setPageCount(resp.pageCount);
            setPage(page);
        } catch { } finally {
            setLoading(false);
        }
    }, [provider]);
    useEffect(() => {
        if (!loaded) {
            loadPage(1).then(() => setLoaded(true));
        }
    }, [loaded, loadPage]);
    return <div>
        {loading && <Dimmer active>
            <Loader></Loader>
        </Dimmer>}
        <Feed size="large">
            {data.map((x, i) => <Fragment key={i}><Feed.Event key={i}>
                <Feed.Label><Image src={makeImageURL(x.email)}></Image></Feed.Label>
                <Feed.Content>
                    <Feed.Summary>
                        <a href={`/profile/${x.uid}`}>{x.username}</a><div className="date">生效于 {x.time}</div>
                    </Feed.Summary>

                </Feed.Content>
                {alreadyLogin && <Feed.Meta>
                    <Button size="tiny" color={x.followedByMe ? "blue" : undefined} onClick={async (evt) => {
                        let r = evt.currentTarget;
                        try {
                            r.classList.add("loading");
                            await userClient.toggleFollowState(x.uid);
                            await loadPage(page);
                        } catch { } finally {
                            r.classList.remove("loading");
                        }
                    }}>{x.followedByMe ? "已关注" : "关注"}</Button>
                </Feed.Meta>}

            </Feed.Event>
                <Divider key={-i - 1}></Divider>
            </Fragment>)}
        </Feed>
        <Grid columns="2" centered>
            <Grid.Column>
                <Pagination
                    totalPages={pageCount}
                    activePage={page}
                    onPageChange={(_, d) => loadPage(d.activePage as number)}
                ></Pagination>
            </Grid.Column>
        </Grid>
    </div>;
}

export default GeneralFollowingTab;