import GeneralClient from "../../../common/GeneralClient";
import { BlogListResponse } from "./types";

class BlogClient extends GeneralClient {
    async getBlogList(uid: number, page: number): Promise<BlogListResponse> {
        return (await this.unwrapExtraClient!.post("/api/blog/list", { uid, page })).data;
    }
};

const blogClient = new BlogClient();

export default blogClient;