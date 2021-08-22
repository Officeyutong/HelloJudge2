import React, { useEffect, useState } from "react";
import { Header, Table } from "semantic-ui-react";
import discussionClient from "../discussion/client/DiscussionClient";
import { DiscussionEntry } from "../discussion/client/types";

const ProblemDiscussionBlock: React.FC<{ id: number }> = ({ id }) => {
    const [discussion, setDiscussion] = useState<DiscussionEntry[]>([]);
    const [loaded, setLoaded] = useState(false);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    const discuss = await discussionClient.getDiscussions(`discussion.problem.${id}`, 1, 10);
                    setDiscussion(discuss.data);
                    setLoaded(true);
                } catch { } finally {

                }
            })();
        }
    }, [loaded, id]);

    return <>
        <Header as="h4">讨论</Header>
        {discussion.length !== 0 ? <Table basic="very" collapsing celled>
            <Table.Body>
                {discussion.map((x, i) => <Table.Row key={i}>
                    <Table.Cell>
                        <a href={`/show_discussion/${x.id}`} target="_blank" rel="noreferrer">{x.title}</a>
                    </Table.Cell>
                </Table.Row>)}
            </Table.Body>
        </Table> : <div>无</div>}
        <a href={`/discussions/discussion.problem.${id}/1`} target="_blank" rel="noreferrer">查看更多</a>
    </>
};

export default React.memo(ProblemDiscussionBlock);