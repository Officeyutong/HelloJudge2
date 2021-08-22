import React from "react";
import { Feed, Label } from "semantic-ui-react";
import { converter } from "../../common/Markdown";
import { useProfileImageMaker } from "../../common/Utils";
import { FeedStreamEntry } from "./client/types";

const FeedArea: React.FC<{ data: FeedStreamEntry[] }> = ({ data }) => {
    const makeImageURL = useProfileImageMaker();
    return <Feed>
        {data.map((x, i) => <Feed.Event key={i}>
            <Feed.Label>
                <img src={makeImageURL(x.email)} alt=""></img>
            </Feed.Label>
            <Feed.Content>
                <Feed.Summary>
                    <a href={`/profile/${x.uid}`} target="_blank" rel="noreferrer">{x.username}</a>发送了动态{x.top && <Label size="tiny" color="red">置顶</Label>}<Feed.Date>{x.time} - ID: {x.id}</Feed.Date>
                </Feed.Summary>
                <Feed.Extra>
                    <div dangerouslySetInnerHTML={{ __html: converter.makeHtml(x.content) }}></div>
                </Feed.Extra>
            </Feed.Content>
        </Feed.Event>)}
    </Feed>
};

export default FeedArea;