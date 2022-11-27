import { Node } from "../core/node.js";
import { Edge } from "../core/edge.js";

export interface IPathPart
{
    node: Node;
    edge: Edge | null;
}
