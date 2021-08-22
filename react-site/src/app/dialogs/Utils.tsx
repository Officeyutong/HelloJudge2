import React from "react";
import ReactDOM from "react-dom";
import { Icon, Message, Transition } from "semantic-ui-react";
export function showAutoDisappearPopup(component: React.ReactElement, timeout: number = 3000) {
    // for(const item of document.){
    //     item.remove();
    // }
    document.querySelectorAll(".my-popup-message").forEach(x => x.remove());
    let elem = document.createElement("div");
    ReactDOM.render(<Transition
        visible={true}
        animation="fade"
        duration={200}
        unmountOnHide
    >
        <div>
            {component}
        </div>
    </Transition>, elem);
    elem.classList.add("my-popup-message");
    elem.style.position = "absolute";
    elem.style.top = `${document.documentElement.scrollTop + 100}px`;
    elem.style.zIndex = "99999";
    document.body.appendChild(elem);
    elem.style.left = (document.body.clientWidth / 2 - elem.clientWidth / 2).toString() + "px";
    setTimeout(() => {
        elem.remove();
    }, timeout);
}
export function showSuccessPopup(message: string, timeout: number = 3000) {
    showAutoDisappearPopup(<Message color="green" compact floating style={{ width: "100%" }}>
        <p style={{ textAlign: "center" }}><Icon name="checkmark" color="green"></Icon>{message}</p>
    </Message>, timeout)
};
export function showErrorPopup(message: string, timeout: number = 3000) {
    showAutoDisappearPopup(<Message compact floating style={{ width: "100%" }}>
        <p style={{ textAlign: "center" }}><Icon name="times" color="red"></Icon>{message}</p>
    </Message>, timeout)
};