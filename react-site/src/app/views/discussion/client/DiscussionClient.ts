import GeneralClient from "../../../common/GeneralClient";
import { DiscussionListResponse } from "./types";

class DiscussionClient extends GeneralClient {
    async getDiscussions(path: string, page: number, countLimit: number): Promise<DiscussionListResponse> {
        return (await this.unwrapClient!.post("/api/get_discussion_list", {
            path: path, page: page, countLimit: countLimit
        })).data as DiscussionListResponse;
    }
};

const discussionClient = new DiscussionClient();

export default discussionClient;
