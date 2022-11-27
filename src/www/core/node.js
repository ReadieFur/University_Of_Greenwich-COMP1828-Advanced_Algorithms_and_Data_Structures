export class Node {
    constructor(id) {
        this.adjacencyDict = new Map();
        this.id = id;
    }
    AddEdge(neighbouringNode, edge) {
        if (!this.adjacencyDict.has(neighbouringNode.id))
            this.adjacencyDict.set(neighbouringNode.id, new Map());
        this.adjacencyDict.get(neighbouringNode.id).set(edge.id, edge);
    }
    RemoveEdge(neighbouringNode, edge) {
        if (!this.adjacencyDict.has(neighbouringNode.id))
            return;
        this.adjacencyDict.get(neighbouringNode.id).delete(edge.id);
    }
    RemoveAllEdges(neighbouringNode) {
        if (!this.adjacencyDict.has(neighbouringNode.id))
            return;
        this.adjacencyDict.delete(neighbouringNode.id);
    }
    Serialize() {
        let adjacencyList = {};
        for (let [neighbourNodeID, edgeDict] of this.adjacencyDict) {
            adjacencyList[neighbourNodeID] = [];
            for (let edge of edgeDict.values())
                adjacencyList[neighbourNodeID].push(edge.Serialize());
        }
        return {
            id: this.id,
            adjacencyList
        };
    }
    static Deserialize(serializedNode) {
        const node = new Node(serializedNode.id);
        return node;
    }
}
//# sourceMappingURL=node.js.map