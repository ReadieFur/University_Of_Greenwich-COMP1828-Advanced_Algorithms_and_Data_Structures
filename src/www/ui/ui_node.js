import { Node } from "../core/node.js";
export class UINode extends Node {
    constructor(id) {
        super(id);
        this.adjacencyDict = new Map();
        this.element =
            {
                div: document.createElement("div"),
                label: document.createElement("input")
            };
        this.element.div.id = `${UINode.ID_PREFIX}${id}`;
        this.element.div.classList.add("node", "draggable", "d_ignore_children");
        this.element.label.value = `${id}`;
        this.element.label.type = "text";
        this.element.div.appendChild(this.element.label);
    }
    RemoveEdge(neighbouringNode, edge) {
        if (!this.adjacencyDict.has(neighbouringNode.id))
            return;
        const uiEdge = edge;
        if (uiEdge.line !== undefined)
            uiEdge.line.Dispose();
        this.adjacencyDict.get(neighbouringNode.id).delete(edge.id);
    }
    RemoveAllEdges(neighbouringNode) {
        if (!this.adjacencyDict.has(neighbouringNode.id))
            return;
        for (const [_, edge] of this.adjacencyDict.get(neighbouringNode.id)) {
            if (edge.line !== undefined)
                edge.line.Dispose();
        }
        this.adjacencyDict.delete(neighbouringNode.id);
    }
    Serialize() {
        return Object.assign(Object.assign({}, super.Serialize()), { px: this.element.div.offsetLeft, py: this.element.div.offsetTop, label: this.element.label.value });
    }
}
UINode.ID_PREFIX = "node_";
//# sourceMappingURL=ui_node.js.map