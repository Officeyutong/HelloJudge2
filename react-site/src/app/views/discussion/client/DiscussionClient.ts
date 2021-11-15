import { CancelToken } from "axios";
import QueryString from "qs";
import GeneralClient from "../../../common/GeneralClient";
import { DiscussionComment, DiscussionDetail, DiscussionListResponse } from "./types";

class DiscussionClient extends GeneralClient {
    async getDiscussions(path: string, page: number, countLimit: number): Promise<DiscussionListResponse> {
        return (await this.unwrapClient!.post("/api/get_discussion_list", {
            path: path, page: page, countLimit: countLimit
        })).data as DiscussionListResponse;
    }
    async getPathName(path: string): Promise<string> {
        const resp = await this.unwrapExtraClient!.post("/api/get_path_name", { path: path });
        return resp.data.name;
    }
    async removeDiscussion(discussionID: number) {
        await this.client!.post("/api/discussion/remove", { discussionID });
    }
    async updateDiscussion(id: number, content: string, title: string, top: boolean, will_private: boolean = false) {
        await this.client!.post("/api/discussion/update", { id, content, title, top, "private": will_private });
    }
    async postDiscussion(title: string, content: string, path: string, top: boolean, will_private: boolean = false): Promise<{ discussion_id: number }> {
        const resp = await this.unwrapExtraClient!.post("/api/post_discussion", { title, content, path, top, "private": will_private });
        return resp.data;
    }
    async postComment(content: string, discussionID: number): Promise<{ last_page: number }> {
        const resp = await this.unwrapExtraClient!.post("/api/post_comment", { content, discussionID });
        return resp.data;
    }
    async getDiscussionComments(discussion_id: number, page: number): Promise<{ data: DiscussionComment[]; page_count: number }> {
        const resp = await this.unwrapExtraClient!.post("/api/get_comments", QueryString.stringify({ discussion_id, page }));
        return resp.data;
    }
    async getDiscussion(id: number, cancelToken: CancelToken | undefined = undefined): Promise<DiscussionDetail> {
        const resp = await this.client!.post("/api/get_discussion", { id }, { cancelToken: cancelToken });
        return resp.data;
    }
};

const discussionClient = new DiscussionClient();

export default discussionClient;
