import { useEffect } from "react";
import { usePreferredMemoryUnit } from "../../common/Utils";

interface MemoryCostLabelProps {
    memoryCost: number;
};
type MemoryUnit = "byte" | "kilobyte" | "millionbyte" | "gigabyte";

const MemoryUnitMapping: { [K in MemoryUnit]: { label: string; ratio: number; } } = {
    byte: { label: "B", ratio: 1 },
    gigabyte: { label: "GB", ratio: 1024 * 1024 * 1024 },
    kilobyte: { label: "KB", ratio: 1024 },
    millionbyte: { label: "MB", ratio: 1024 * 1024 }
};

const MemoryCostLabel: React.FC<MemoryCostLabelProps> = ({ memoryCost }) => {
    const [unit, setUnit] = usePreferredMemoryUnit<MemoryUnit>("kilobyte");
    useEffect(() => {
        if (unit !== "byte" && unit !== "kilobyte" && unit !== "gigabyte" && unit !== "millionbyte") {
            setUnit("kilobyte");
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [unit]);
    const { label, ratio } = MemoryUnitMapping[unit];
    return <div>{Math.ceil(memoryCost / ratio)} {label}</div>;
};

export type {
    MemoryUnit
}
export default MemoryCostLabel;