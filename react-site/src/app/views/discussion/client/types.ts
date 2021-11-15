interface DiscussionEntry {
    uid: number;
    username: string;
    email: string;
    time: number;
    title: string;
    comment_count: number;
    last_comment_time: number | null;
    id: number;
    private: boolean;
};

interface DiscussionListResponse {
    page_count: number;
    current_page: number;
    managable: boolean;
    data: DiscussionEntry[];
};

interface DiscussionDetail {
    id: number;
    path: string;
    title: string;
    content: string;
    uid: number;
    top: boolean;
    time: number;
    private: boolean;
    email: string;
    username: string;

};

interface DiscussionComment {
    id: number;
    username: string;
    uid: number;
    content: string;
    time: number;
    email: string;
};

export type {
    DiscussionEntry,
    DiscussionListResponse,
    DiscussionComment,
    DiscussionDetail
}