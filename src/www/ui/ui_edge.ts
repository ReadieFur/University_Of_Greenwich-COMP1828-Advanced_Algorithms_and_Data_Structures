import { Edge, ISerializedEdge } from "../core/edge.js";
import { Line } from "./line.js";

export interface ISerializedUIEdge extends ISerializedEdge
{
    label: string;
}

export class UIEdge extends Edge
{
    public line?: Line;
    public label = "";

    public override Serialize(): ISerializedUIEdge
    {
        return {
            ...super.Serialize(),
            label: this.label
        }
    }

    public static override Deserialize(serializedEdge: ISerializedUIEdge): UIEdge
    {
        const uiEdge = new UIEdge(serializedEdge.id, serializedEdge.weight);
        uiEdge.label = serializedEdge.label;
        return uiEdge;
    }
}
