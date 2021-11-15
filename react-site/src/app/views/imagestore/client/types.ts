
interface ImageListEntry {
    filename: string;
    filesize: number;
    upload_time: number;
    file_id: string;
    thumbnail_id: string;
};
interface ImageListResponse {
    pageCount: number;
    images: ImageListEntry[];
};
export type {
    ImageListEntry,
    ImageListResponse
}