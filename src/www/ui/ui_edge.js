import { Edge } from "../core/edge.js";
export class UIEdge extends Edge {
    constructor() {
        super(...arguments);
        this.label = "";
    }
    Serialize() {
        return Object.assign(Object.assign({}, super.Serialize()), { label: this.label });
    }
    static Deserialize(serializedEdge) {
        const uiEdge = new UIEdge(serializedEdge.id, serializedEdge.weight);
        uiEdge.label = serializedEdge.label;
        return uiEdge;
    }
}
//# sourceMappingURL=ui_edge.js.map