interface UserFeedEntry {
    uid: number;
    username: string;
    email: string;
    time: string;
    content: string;
};
interface UserFeedResponse {
    pageCount: number;
    data: UserFeedEntry[];
};
interface FeedStreamEntry {
    id: number;
    uid: number;
    email: string;
    time: string;
    content: string;
    top: boolean;
    username: string;
};

export type {
    UserFeedEntry,
    FeedStreamEntry,
    UserFeedResponse
}