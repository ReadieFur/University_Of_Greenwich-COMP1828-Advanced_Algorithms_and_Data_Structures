export class Edge {
    constructor(id, weight) {
        this.id = id;
        this.weight = weight;
    }
    Serialize() {
        return {
            id: this.id,
            weight: this.weight
        };
    }
    static Deserialize(serializedEdge) {
        return new Edge(serializedEdge.id, serializedEdge.weight);
    }
}
//# sourceMappingURL=edge.js.map