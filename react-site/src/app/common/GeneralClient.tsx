import { AxiosInstance } from "axios";
import { store } from "../states/Manager";

class GeneralClient {
    protected client: AxiosInstance | null = null;
    protected unwrapClient: AxiosInstance | null = null;
    protected unwrapExtraClient: AxiosInstance | null = null;

    constructor() {
        const state = store.getState();
        this.client = state.generalClient;
        this.unwrapClient = state.unwrapClient;
        this.unwrapExtraClient = state.unwrapExtraClient;
        store.subscribe(() => {
            this.client = store.getState().generalClient;
            this.unwrapClient = store.getState().unwrapClient;
            this.unwrapExtraClient = store.getState().unwrapExtraClient;
        });
    }
    public getNormalClient() {
        return this.client!;
    }

}

export default GeneralClient;