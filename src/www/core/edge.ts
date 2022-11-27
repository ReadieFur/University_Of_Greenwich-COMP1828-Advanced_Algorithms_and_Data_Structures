//#region Serialized interfaces
export interface ISerializedEdge
{
    id: number;
    weight: number;
}
//#endregion

export class Edge
{
    public readonly id: number;
    public weight: number;

    public constructor(id: number, weight: number)
    {
        this.id = id;
        this.weight = weight;
    }

    public Serialize(): ISerializedEdge
    {
        return {
            id: this.id,
            weight: this.weight
        };
    }

    public static Deserialize(serializedEdge: ISerializedEdge): Edge
    {
        return new Edge(serializedEdge.id, serializedEdge.weight);
    }
}
