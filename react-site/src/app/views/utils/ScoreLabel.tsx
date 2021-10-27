
interface ScoreLabelProps {
    score: number;
    fullScore: number;
};

const ScoreLabel: React.FC<ScoreLabelProps> = ({ score, fullScore }) => {
    const ratio = score / fullScore * 100;
    let color: string;
    if (ratio <= 50) color = "red";
    else if (ratio <= 70) color = "orange";
    else if (ratio < 100) color = "darkorange";
    else color = "green";
    return <span style={{ color: color, fontWeight: "bold" }}>{score}/{fullScore}</span>
};


export default ScoreLabel;