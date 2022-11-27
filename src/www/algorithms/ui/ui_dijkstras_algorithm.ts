import { Graph } from "../../core/graph.js";
import { Node } from "../../core/node.js";
import { Edge } from "../../core/edge.js";
import { IDijkstraNode } from "../dijkstras_algorithm.js";

type AsyncCallback<T> = (dijkstraNode: T) => Promise<void>;
type AsyncCallback2<T> = (dijkstraNode: T, dijkstraEdgeNode: T, edge: Edge) => Promise<void>;

export class UIDijkstrasAlgorithm
{
    public static readonly DEFAULT_CALLBACK: AsyncCallback<IDijkstraNode> = async () => {};

    public static async FindShortestPath(graph: Graph, startNode: Node, endNode: Node,
        onCheckingShortestPath: AsyncCallback<IDijkstraNode> = this.DEFAULT_CALLBACK,
        // onShortestPathChanged: AsyncCallback<IDijkstraNode> = this.DEFAULT_CALLBACK,
        onNodeBoxed: AsyncCallback<IDijkstraNode> = this.DEFAULT_CALLBACK,
        onCheckingEdge: AsyncCallback2<IDijkstraNode> = this.DEFAULT_CALLBACK, //Passes the edge node as the second parameter.
        // onClosestEdgeChanged: AsyncCallback2<IDijkstraNode> = this.DEFAULT_CALLBACK, //Passes the edge node as the second parameter.
        onShortestPathFound: AsyncCallback<IDijkstraNode> = this.DEFAULT_CALLBACK
    ): Promise<IDijkstraNode>
    {
        const dijkstraNodes = new Map<number, IDijkstraNode>();
        for (const i of graph.nodes.keys())
            dijkstraNodes.set(i,
            {
                node: graph.nodes.get(i)!,
                previousNode: null,
                previousEdge: null,
                pathWeight: Number.MAX_SAFE_INTEGER,
                isBoxed: false
            });

        dijkstraNodes.get(startNode.id)!.pathWeight = 0;

        //I use a for loop here instead of a while true loop to prevent the possibility of an infinite loop, though this should never happen...
        for (let i = 0; i < graph.nodes.size; i++)
        {
            //#region Find the known shortest path to the current node.
            let lightestNodeID = 0;
            let lightestPath = Number.MAX_SAFE_INTEGER;
            for (const j of dijkstraNodes.keys())
            {
                const dijkstraNodeJ = dijkstraNodes.get(j)!;

                await onCheckingShortestPath(dijkstraNodeJ);

                if (dijkstraNodeJ.isBoxed || dijkstraNodeJ.pathWeight >= lightestPath)
                    continue;

                lightestNodeID = j;
                lightestPath = dijkstraNodeJ.pathWeight;

                // await onShortestPathChanged(dijkstraNodeJ);
            }
            //#endregion

            /*
             * I create variables here with references to the Dijkstra node here.
             * This is done to save on time on what would be spent accessing the dictionary multiple times below.
             * As classes are passed by reference in C#, it is fine to assign to a new variable here as we store the reference to the object.
             * This however does come at the cost of slightly increased memory usage, though I do wonder if this creation on the heap is slower.
             * This can be seen being done in the loops above and below this too.
             */
            const dijkstraNode = dijkstraNodes.get(lightestNodeID)!;

            //TODO: Explain the below better.
            //As we have now explored all of this nodes neighbours (occurred in the previous iteration, except for the first), we can now box it.
            dijkstraNode.isBoxed = true;

            await onNodeBoxed(dijkstraNode);

            //As the node we are working with past this point is boxed, if it is the node we are looking for, we can return here.
            if (lightestNodeID == endNode.id)
            {
                await onShortestPathFound(dijkstraNode);
                return dijkstraNode;
            }

            //#region Update the path weight of this nodes unboxed neighbours.
            for (const [neighbouringNodeID, edges] of dijkstraNode.node.adjacencyDict)
            {
                const dijkstraEdgeNode = dijkstraNodes.get(neighbouringNodeID)!;

                //If I haven't boxed this node and the new distance is less than the current distance + the edge weight...
                if (dijkstraEdgeNode.isBoxed)
                    continue;

                for (const edge of edges.values())
                {
                    await onCheckingEdge(dijkstraNode, dijkstraEdgeNode, edge);

                    if (dijkstraNode.pathWeight + edge.weight >= dijkstraEdgeNode.pathWeight)
                        continue;

                    //Update the edge node's distance from the start node using the current shortest path + this edges weight.
                    dijkstraEdgeNode.pathWeight = dijkstraNode.pathWeight + edge.weight;
                    dijkstraEdgeNode.previousNode = dijkstraNode;
                    dijkstraEdgeNode.previousEdge = edge;

                    // await onClosestEdgeChanged(dijkstraNode, dijkstraEdgeNode);
                }
            }
            //#endregion
        }

        //If we do end somehow end up here, something has gone wrong.
        throw new Error(`Failed to find a path from node '${startNode.id}' to node '${endNode.id}' on the specified graph.`);
    }
}
