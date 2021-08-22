import React, { useEffect, useRef, useState } from 'react';
import ReCAPTCHA from "react-google-recaptcha";
import { Button, Dimmer, Grid, Loader, Message, Segment } from 'semantic-ui-react';
import utilClient from './client/UtilClient';
(window as typeof window & { recaptchaOptions: any }).recaptchaOptions = {
    useRecaptchaNet: true,
};
enum States {
    ERROR = -1,
    UNLOADED = 1, //初始化
    LOADING = 2, //preparation中
    LOADED = 3, //sitekey获取完成
    RECAPTCHA_LOADING = 4, //加载recaptcha中
    RECAPTCHA_LOADED = 5, //recaptcha加载完成
    AUTHED = 6, //已经经过了reCaptcha认证
    CODE_SENDING = 7, //正在发送验证码
    CODE_SENDED = 8, //验证码已发送
    CODE_ERROR = 9,//验证码发送错误
};
const SendSMSCodeDialog: React.FC<{ phone: string; mustNotUse: boolean; onClose: () => void }> = ({ phone, mustNotUse, onClose }) => {
    const [siteKey, setSiteKey] = useState("");
    const [state, setState] = useState<States>(States.UNLOADED);
    const [token, setToken] = useState<string | null>(null);
    const [message, setMessage] = useState<string>("");
    const [sended, setSended] = useState(false);
    const recaptchaRef = useRef<ReCAPTCHA | any>();
    useEffect(() => {
        (async () => {
            switch (state) {
                case States.UNLOADED:
                    setState(States.LOADING);
                    utilClient.recaptchaPreparation().then(resp => {
                        setSiteKey(resp.site_key);
                        setState(States.LOADED);
                    }).catch(() => {
                        setState(States.ERROR);
                    });
                    break;
                case States.LOADED:
                    setState(States.RECAPTCHA_LOADING);
                    break;
            };
        })();
    }, [state]);
    const sendCode = async () => {
        setSended(true);
        setState(States.CODE_SENDING);
        let resp = await utilClient.sendSMSCode(phone, token, mustNotUse);
        setMessage(resp.message);
        if (resp.code === -1) setState(States.CODE_ERROR);
        else setState(States.CODE_SENDED);
        recaptchaRef.current!.reset();
    };
    return <div>
        <Segment>
            {(state === States.LOADING || state === States.RECAPTCHA_LOADING) && <Dimmer active>
                <Loader></Loader></Dimmer>}
            {state >= States.RECAPTCHA_LOADING && <div>
                <Grid columns="3" centered>
                    <Grid.Column>
                        <Grid columns="1">
                            <Grid.Column>
                                <ReCAPTCHA
                                    ref={recaptchaRef}
                                    sitekey={siteKey}
                                    asyncScriptOnLoad={() => setState(States.RECAPTCHA_LOADED)}
                                    onChange={token => {
                                        setToken(token);
                                        setState(States.AUTHED);

                                    }}
                                ></ReCAPTCHA>
                            </Grid.Column>

                            <Grid.Column>
                                <Button color="green" onClick={onClose}>
                                    关闭
                                </Button>
                                {(state >= States.AUTHED) && <Button color="green" loading={state === States.CODE_SENDING} onClick={sendCode}>
                                    {!sended ? "发送验证码" : "重发验证码"}
                                </Button>}
                            </Grid.Column>
                        </Grid>
                    </Grid.Column>
                </Grid>
                {state >= States.CODE_SENDED && <Message success={state === States.CODE_SENDED} error={state === States.CODE_ERROR}>
                    {message}
                </Message>}
            </div>}
        </Segment>
    </div>;
}

export default SendSMSCodeDialog;