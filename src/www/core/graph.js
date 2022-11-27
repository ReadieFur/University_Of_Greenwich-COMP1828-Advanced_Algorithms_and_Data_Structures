import { Node } from "./node.js";
import { Edge } from "./edge.js";
export class Graph {
    constructor() {
        this.nodes = new Map();
        this.edgeList = new Map();
    }
    static GetUniqueID(usedIDs) {
        let id;
        do
            id = Math.floor(Math.random() * Number.MAX_SAFE_INTEGER);
        while (usedIDs.includes(id));
        return id;
    }
    AddNode() {
        const id = Graph.GetUniqueID(Array.from(this.nodes.keys()));
        const node = new Node(id);
        this.nodes.set(id, node);
        return node;
    }
    RemoveNode(node) {
        if (node === undefined)
            throw new Error("Node does not exist.");
        for (const neighbor of node.adjacencyDict)
            this.nodes.get(neighbor[0]).RemoveAllEdges(node);
        this.nodes.delete(node.id);
    }
    AddEdge(node1, node2, weight, id) {
        if (node1 === undefined)
            throw new Error("Node 1 does not exist.");
        if (node2 === undefined)
            throw new Error("Node 2 does not exist.");
        if (id == undefined)
            id = Graph.GetUniqueID(Array.from(this.edgeList.keys()));
        else if (this.edgeList.has(id))
            throw new Error(`Edge with ID ${id} already exists.`);
        const edge = new Edge(id, weight);
        this.edgeList.set(id, [node1, node2, edge]);
        node1.AddEdge(node2, edge);
        node2.AddEdge(node1, edge);
        return edge;
    }
    RemoveEdge(edge) {
        if (edge === undefined)
            throw new Error("Edge does not exist.");
        const [node1, node2, _] = this.edgeList.get(edge.id);
        node1.RemoveEdge(node2, edge);
        node2.RemoveEdge(node1, edge);
        this.edgeList.delete(edge.id);
    }
    Serialize() {
        return {
            nodes: Array.from(this.nodes.values(), node => node.Serialize())
        };
    }
    Deserialize(serializedGraph) {
        const graph = new Graph();
        for (const serializedNode of serializedGraph.nodes) {
            const node = Node.Deserialize(serializedNode);
            graph.nodes.set(node.id, node);
        }
        for (const serializedNode of serializedGraph.nodes) {
            const node = this.nodes.get(serializedNode.id);
            for (const neighbourNodeID of Object.keys(serializedNode.adjacencyList)) {
                const key = parseInt(neighbourNodeID);
                if (isNaN(key))
                    continue;
                const serializedEdges = serializedNode.adjacencyList[key];
                for (const serializedEdge of serializedEdges) {
                    const neighbourNode = this.nodes.get(key);
                    try {
                        this.AddEdge(node, neighbourNode, serializedEdge.weight, serializedEdge.id);
                    }
                    catch (ex) {
                        if (ex instanceof Error && ex.message == `Edge with ID ${serializedEdge.id} already exists.`)
                            continue;
                    }
                }
            }
        }
    }
}
//# sourceMappingURL=graph.js.map