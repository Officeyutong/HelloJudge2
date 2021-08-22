interface DiscussionEntry {
    uid: number;
    username: string;
    email: string;
    time: string;
    title: string;
    comment_count: number;
    last_comment_time: string;
    id: number;
    private: boolean;
};

interface DiscussionListResponse {
    page_count: number;
    current_page: number;
    managable: boolean;
    data: DiscussionEntry[];
};
export type {
    DiscussionEntry,
    DiscussionListResponse
}