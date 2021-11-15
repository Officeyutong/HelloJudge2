import React, { useEffect, useState } from "react";
import discussionClient from "./client/DiscussionClient";
import { DiscussionComment } from "./client/types";
import { Comment, Dimmer, Loader, Container, Divider, Pagination } from "semantic-ui-react";
import { toLocalTime, useProfileImageMaker } from "../../common/Utils";
import UserLink from "../utils/UserLink";
import { Markdown } from "../../common/Markdown";
interface DiscussionCommentsProps {
    discussionID: number;
    replyCallback: (username: string) => void;
    defaultPage: number;
};

const DiscussionComments: React.FC<DiscussionCommentsProps> = (props) => {
    const [loaded, setLoaded] = useState(false);
    const [loading, setLoading] = useState(false);
    const [page, setPage] = useState(-1);
    const [pageCount, setPageCount] = useState(0);
    const [data, setData] = useState<DiscussionComment[]>([]);
    const makeImage = useProfileImageMaker();
    const loadPage = async (page: number) => {
        try {
            setLoading(true);
            const resp = await discussionClient.getDiscussionComments(props.discussionID, page);
            setPageCount(resp.page_count);
            setData(resp.data);
            setLoaded(true);
            setPage(page);
            setLoading(false);
        } catch { } finally { }
    }
    useEffect(() => {
        if (!loaded) loadPage(props.defaultPage);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [loaded]);
    return <>
        {loading && <>
            <Dimmer active>
                <Loader></Loader>
            </Dimmer>
        </>}
        {loaded && data.length === 0 && <>
            <Container>
                暂无评论
            </Container>
        </>}
        {loaded && data.length !== 0 && <>
            <Comment.Group>
                {data.map((item, i) => <Comment key={i}>
                    <Comment.Avatar src={makeImage(item.email)}>
                    </Comment.Avatar>
                    <Comment.Content>
                        <Comment.Author as={UserLink} data={{ uid: item.uid, username: item.username }}>
                        </Comment.Author>
                        <Comment.Metadata>
                            <div>{toLocalTime(item.time)}</div>
                        </Comment.Metadata>
                        <Comment.Text>
                            <Markdown markdown={item.content}></Markdown>
                        </Comment.Text>
                        <Comment.Actions>
                            {
                                // eslint-disable-next-line jsx-a11y/anchor-is-valid
                                <a onClick={() => props.replyCallback(item.username)}>回复</a>
                            }
                        </Comment.Actions>
                    </Comment.Content>
                    <Divider></Divider>
                </Comment>)}
            </Comment.Group>
            <Container textAlign="center">
                <Pagination
                    totalPages={pageCount}
                    activePage={page}
                    onPageChange={(_, d) => loadPage(d.activePage as number)}
                ></Pagination>
            </Container>
        </>}
    </>;
};

export default DiscussionComments;