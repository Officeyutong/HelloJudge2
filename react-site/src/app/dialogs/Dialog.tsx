import React, { useState } from "react";
import ReactDOM from "react-dom";
import { Modal, Header, Message, Button, Confirm, Transition } from "semantic-ui-react";
type StateType = {
    showing: boolean;
    message: string;
    title: string;
    error: boolean;
    success: boolean;
    showTransition: boolean;
    withReturnToHome: boolean;

};
type PropType = {
    error: boolean;
    success: boolean;
    message: string;
    title: string;
    withReturnToHome: boolean;
};
class MyMessageBox extends React.Component<PropType, StateType> {


    readonly state: Readonly<StateType> = {
        showing: false,
        message: "",
        title: "标题",
        error: true,
        success: false,
        showTransition: false,
        withReturnToHome: false
    }
    public constructor(props: PropType) {
        super(props);
        this.state = {
            showing: false,
            showTransition: false,
            ...props

        };
    }
    componentDidMount() {
        this.setState({ ...this.state, showing: true })
    }
    render() {
        return (<Transition
            visible={this.state.showing}
            animation="fade"
            duration={200}
            unmountOnHide={true}
        >
            <Modal
                open={true}
                size="tiny"
                closeOnDimmerClick={false}
                closeOnDocumentClick={true}
            >
                <Header content={this.state.title} />
                <Modal.Content>
                    <Message error={this.state.error} success={!this.state.error}>
                        <Header>
                            <h3>{this.state.error ? "错误" : "完成"}</h3>
                        </Header>
                        <div dangerouslySetInnerHTML={{ __html: this.state.message }}>

                        </div>
                    </Message>
                </Modal.Content>
                <Modal.Actions>
                    {this.state.withReturnToHome && <Button as="a" color="blue" href="/">返回主页</Button>}
                    <Button color="blue" onClick={() => this.setState({ showing: false })}>关闭</Button>
                </Modal.Actions>
            </Modal>
        </Transition>);
    }
};

const show = (message?: string, title: string = "提示", error: boolean = false, success: boolean = false, withReturnToHome: boolean = false) => {
    let target = document.createElement("div");
    ReactDOM.render(<MyMessageBox message={String(message)} title={title} error={error} success={success} withReturnToHome={withReturnToHome} />, target);
};
const showErrorModal = (message?: string, title: string = "错误", withReturnToHome: boolean = false) => {
    show(message, title, true, false, withReturnToHome);
};
const showSuccessModal = (message?: string, title: string = "操作完成", withReturnToHome: boolean = false) => {
    show(message, title, false, true, withReturnToHome);
};
const ConfirmModal: React.FC<{ content?: string; title?: string; onConfirm: () => void; onCancel?: () => void; }> = (props) => {
    const [open, setOpen] = useState(true);
    return <Confirm
        content={props.content}
        header={props.title}
        onCancel={() => {
            setOpen(false);
            props.onCancel && props.onCancel();
        }}
        onConfirm={() => {
            setOpen(false);
            props.onConfirm();
        }}
        open={open}
    ></Confirm>
};

const showConfirm = (message: string, onConfirm: () => void, title?: string, onCancel?: (() => void)) => {
    let elem = document.createElement("div");
    ReactDOM.render(
        <ConfirmModal onConfirm={onConfirm} content={message!} title={title} onCancel={onCancel}>
        </ConfirmModal>,
        elem
    );
}

export { show, showConfirm, show as showDialog, showErrorModal, showSuccessModal };
