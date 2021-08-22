import { Button, Icon, Input, Modal } from "semantic-ui-react";
import { ButtonClickEvent } from "../../common/types";
import { onChangeType } from "../../common/Utils";


interface InviteCodeInputModalProps {
    onClose: (evt: ButtonClickEvent) => void;
    value: string;
    onChange: onChangeType;
    title: string;
};

const InviteCodeInputModal: React.FC<InviteCodeInputModalProps> = ({
    onChange, onClose, value,title
}) => <Modal open size="tiny">
        <Modal.Header>
            {title}
        </Modal.Header>
        <Modal.Content>
            <Input fluid value={value} onChange={onChange}></Input>
        </Modal.Content>
        <Modal.Actions>
            <Button color="green" icon labelPosition="right" onClick={onClose}>
                <Icon name="checkmark"></Icon>
                确认
            </Button>
        </Modal.Actions>
    </Modal>;

export default InviteCodeInputModal;