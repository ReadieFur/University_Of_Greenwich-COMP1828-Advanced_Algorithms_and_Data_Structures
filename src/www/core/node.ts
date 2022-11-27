import { Edge, ISerializedEdge } from "./edge.js";

//#region Serialized interfaces
export interface ISerializedNode
{
    id: number;
    adjacencyList:
    {
        [neighbourNodeID: number]: ISerializedEdge[];
    };
}
//#endregion

export class Node
{
    public readonly id: number;
    public adjacencyDict: Map<number /*Node ID*/, Map<number /*Edge ID*/, Edge>> = new Map<number, Map<number, Edge>>();

    constructor(id: number)
    {
        this.id = id;
    }

    public AddEdge(neighbouringNode: Node, edge: Edge): void
    {
        if (!this.adjacencyDict.has(neighbouringNode.id))
            this.adjacencyDict.set(neighbouringNode.id, new Map<number, Edge>());

        this.adjacencyDict.get(neighbouringNode.id)!.set(edge.id, edge);
    }

    public RemoveEdge(neighbouringNode: Node, edge: Edge): void
    {
        if (!this.adjacencyDict.has(neighbouringNode.id))
            return;

        this.adjacencyDict.get(neighbouringNode.id)!.delete(edge.id);
    }

    public RemoveAllEdges(neighbouringNode: Node): void
    {
        if (!this.adjacencyDict.has(neighbouringNode.id))
            return;

        this.adjacencyDict.delete(neighbouringNode.id);
    }

    public Serialize(): ISerializedNode
    {
        let adjacencyList: { [neighbourNodeID: number]: ISerializedEdge[] } = {};

        for (let [neighbourNodeID, edgeDict] of this.adjacencyDict)
        {
            adjacencyList[neighbourNodeID] = [];

            for (let edge of edgeDict.values())
                adjacencyList[neighbourNodeID].push(edge.Serialize());
        }

        return {
            id: this.id,
            adjacencyList
        };
    }

    public static Deserialize(serializedNode: ISerializedNode): Node
    {
        const node = new Node(serializedNode.id);
        //Skip adding edges as their target nodes may not have been deserialized yet.
        return node;
    }
}
