import GeneralClient from "../../../common/GeneralClient";
import { FeedStreamEntry, UserFeedResponse } from "./types";

class FeedClient extends GeneralClient {
    async getUserFeeds(uid: number, page: number): Promise<UserFeedResponse> {
        return (await this.unwrapClient!.post("/api/feed/get_feeds", { uid: uid, page: page })).data;
    }
    async toggleTopStatus(feedID: number) {
        await this.client!.post("/api/feed/toggle_top_state", { feedID: feedID });
    }
    async getFeedStream(): Promise<FeedStreamEntry[]> {
        return (await (this.client!.post("/api/feed/get_feed_stream"))).data;
    }
};

const feedClient = new FeedClient();

export default feedClient;