import QueryString from "qs";
import GeneralClient from "../../../common/GeneralClient";
import { ImageListResponse } from "./types";

class ImageStoreClient extends GeneralClient {
    async uploadImages(files: FormData, prorgressHandler: (evt: ProgressEvent) => void): Promise<{ [key: string]: string }> {
        return (await this.client!.post("/api/imagestore/upload", files, {
            onUploadProgress: prorgressHandler
        })).data;
    }
    makeImageURL(image_id: string): string {
        return `/api/imagestore/get?${QueryString.stringify({ file_id: image_id })}`;
    }
    async removeImage(file_id: string) {
        await this.client!.post("/api/imagestore/remove", { file_id });
    }
    async getImageList(page: number = 1): Promise<ImageListResponse> {
        return (await this.client!.post("/api/imagestore/list", { page })).data;
    }

};
const imageStoreClient = new ImageStoreClient();

export default imageStoreClient;