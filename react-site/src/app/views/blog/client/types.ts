import { GeneralUserEntry } from "../../../common/types";

interface BlogListEntry {
    title: string;
    time: number;
    commentCount: number;
    lastCommentAt: number | null;
    summary: string;
    id: number;
    private: boolean;
};
interface BlogUserData extends GeneralUserEntry {
    publicBlogCount: number;
}
interface BlogListResponse {
    pageCount: number;
    data: BlogListEntry[];
    userData: BlogUserData;
    managable: boolean;
};

export type {
    BlogListEntry,
    BlogListResponse,
    BlogUserData,
}