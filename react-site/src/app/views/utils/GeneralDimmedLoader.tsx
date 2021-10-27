import { Dimmer, Loader } from "semantic-ui-react";

const GeneralDimmedLoader: React.FC<{}> = () => <div style={{ height: "400px" }}>
    <Dimmer active><Loader></Loader></Dimmer>
</div>;


export default GeneralDimmedLoader;