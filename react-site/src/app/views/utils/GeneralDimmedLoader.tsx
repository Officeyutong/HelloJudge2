import { Dimmer, Loader } from "semantic-ui-react";

const GeneralDimmedLoader: React.FC<{}> = () => <div style={{ height: "400px" }}>
    <Dimmer active>
        <Loader>
            加载页面中...
        </Loader>
    </Dimmer>
</div>;


export default GeneralDimmedLoader;