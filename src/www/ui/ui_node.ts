import { Node, ISerializedNode } from "../core/node.js";
import { UIEdge } from "./ui_edge.js";
import { Edge } from "../core/edge.js";

export interface IUISerializedNode extends ISerializedNode
{
    px: number;
    py: number;
    label: string;
}

/*Element structure:
<div class="node">
    <label class="center">ID</label>
</div>
*/
interface IElement
{
    div: HTMLDivElement;
    label: HTMLInputElement;
}

export class UINode extends Node
{
    public static readonly ID_PREFIX = "node_";

    public readonly element: IElement;

    public override adjacencyDict: Map<number, Map<number, UIEdge>> = new Map<number, Map<number, UIEdge>>();

    constructor(id: number)
    {
        super(id);

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

    public override RemoveEdge(neighbouringNode: Node, edge: Edge): void
    {
        if (!this.adjacencyDict.has(neighbouringNode.id))
            return;

        const uiEdge = edge as UIEdge;
        if (uiEdge.line !== undefined)
            uiEdge.line.Dispose();

        this.adjacencyDict.get(neighbouringNode.id)!.delete(edge.id);
    }

    public override RemoveAllEdges(neighbouringNode: Node): void
    {
        if (!this.adjacencyDict.has(neighbouringNode.id))
            return;

        for (const [_, edge] of this.adjacencyDict.get(neighbouringNode.id)!)
        {
            if (edge.line !== undefined)
                edge.line.Dispose();
        }

        this.adjacencyDict.delete(neighbouringNode.id);
    }

    public override Serialize(): IUISerializedNode
    {
        return {
            ...super.Serialize(),
            px: this.element.div.offsetLeft,
            py: this.element.div.offsetTop,
            label: this.element.label.value
        };
    }
}
