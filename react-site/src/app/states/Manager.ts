import { AxiosInstance } from 'axios';
import { createStore, Action } from 'redux';
import { SemanticCOLORS, SemanticICONS } from 'semantic-ui-react/dist/commonjs/generic';



export interface UserStateType {
    login: boolean;
    userData: {
        uid: number;
        group: string;
        group_name: string;
        backend_managable: boolean;
        username: string;
        email: string;
        salt: string;
        judgeStatus: { [key: string]: { icon: SemanticICONS; text: string; color: SemanticCOLORS } };
        appName: string;
        usePolling: boolean;
        registerURL: string;
        gravatarURL: string;
        usePhoneAuth: boolean;
        canUseImageStore: boolean;
        displayRepoInFooter: boolean;
    }
}

export interface StateType {
    userState: UserStateType;
    generalClient: AxiosInstance | null;
    unwrapClient: AxiosInstance | null;
    unwrapExtraClient: AxiosInstance | null;
    userConfig: {
        aceTheme: string;
    };
    displayBaseView: boolean;
};

const defaultState: StateType = {
    userState: {
        login: false,
        userData: {
            uid: -1,
            group: "",//用户组ID
            group_name: "",//用户组名
            backend_managable: false,//是否可以进行后台管理
            username: "",//用户名
            email: "",//电子邮件
            salt: "",//密码盐
            judgeStatus: {},
            appName: "",//应用名
            usePolling: true,//使用轮询
            registerURL: "",//注册页面URL
            gravatarURL: "",//gravatar前缀,
            usePhoneAuth: false,
            canUseImageStore: false,
            displayRepoInFooter: false
        }
    },
    generalClient: null,
    unwrapClient: null,
    unwrapExtraClient: null,
    userConfig: {
        aceTheme: "github"
    },
    displayBaseView: true
};

export interface SimpleAction extends Action<string> {
    readonly type: string;
    modify(arg0: StateType): StateType;
}
export function makeUserStateUpdateAction(login: boolean, userData: UserStateType["userData"]) {
    return {
        type: 'USERSTATE_UPDATE',
        modify: (state: StateType) => {
            let result = {
                ...state,
                userState: {
                    login: login,
                    userData: userData
                }
            };
            return result;
        },
    } as SimpleAction;
}
export function makeDataStateUpdateAction(loaded: boolean) {
    return {
        type: 'DATASTATE_UPDATE',
        modify: (state: StateType) => {
            let result = {
                ...state,
                dataState: {
                    loaded: loaded
                }
            };
            return result;
        },
    } as SimpleAction;
}

export function makeClientUpdateAction(generalClient: AxiosInstance | null, unwrapClient: AxiosInstance | null, unwrapExtraClient: AxiosInstance | null) {
    return {
        type: "CLIENT_UPDATE",
        modify: (state: StateType) => ({
            ...state,
            generalClient: generalClient,
            unwrapClient: unwrapClient,
            unwrapExtraClient: unwrapExtraClient
        })
    } as SimpleAction;
}
export function makeDisplayBaseViewUpdateAction(display: boolean) {
    return {
        type: "BASEVIEW_DISPLAY_UPDATE",
        modify: (state: StateType) => ({
            ...state,
            displayBaseView: display
        })
    } as SimpleAction;
}
const myReducer = (state = defaultState, action: SimpleAction) => {
    if (!action.type.startsWith('@@redux')) {
        return action.modify(state);
    } else {
        return state;
    }
};

const store = createStore(myReducer);

export { store };
