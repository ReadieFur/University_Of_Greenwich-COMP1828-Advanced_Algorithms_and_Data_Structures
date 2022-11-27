import { Graph } from "../core/graph.js";
import { Node } from "../core/node.js";
import { Edge } from "../core/edge.js";
import { IPathPart } from "./algorithm_helpers.js";

export interface IDijkstraNode
{
    node: Node;
    previousNode: IDijkstraNode | null;
    previousEdge: Edge | null;
    pathWeight: number;
    isBoxed: boolean;
}

/*
* I am using the following psuedocode to assist in my creation of this algorithm:
* From: COMP1828 "Graph 2.pptx" slide 30:
# Input: A weighted connected graph G = (V, E) with nonnegative weights and its vertex s
# Output: The length dv of a shortest path from s to v and it's penultimate vertex pv for every vertex v in V
Algorithm (G, s)
    Initialize(Q) # initialize priority queue to empty
    for every vertex v in V
        dv <- INFINITY
        pv <- NULL
        Insert(Q, v, dv) # initialize vertex priority in the priority queue
    ds <- 0
    Decrease(Q, s, ds) # update priority of s with ds
    Vt <- 0/
    for i <- 0 to |V| - 1 do
        u* <- DeleteMin(Q) # delete the minimum priority element
        Vt <- Vt U {u*}
        for every vertex u in V - Vt that is adjacent to u* do
            if du + w(u*, u) < du
                du <- du + w(u*, u)
                pu <- u*
                Decrease(Q, u, du)
*/
export class DijkstrasAlgorithm
{
    public static FindShortestPath(graph: Graph, startNode: Node, endNode: Node): IDijkstraNode
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

                if (dijkstraNodeJ.isBoxed || dijkstraNodeJ.pathWeight >= lightestPath)
                    continue;

                lightestNodeID = j;
                lightestPath = dijkstraNodeJ.pathWeight;
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

            //As the node we are working with past this point is boxed, if it is the node we are looking for, we can return here.
            if (lightestNodeID == endNode.id)
                return dijkstraNode;

            //#region Update the path weight of this nodes unboxed neighbours.
            for (const [neighbouringNodeID, edges] of dijkstraNode.node.adjacencyDict)
            {
                const dijkstraEdgeNode = dijkstraNodes.get(neighbouringNodeID)!;

                //If I haven't boxed this node and the new distance is less than the current distance + the edge weight...
                if (dijkstraEdgeNode.isBoxed)
                    continue;

                for (const edge of edges.values())
                {
                    if (dijkstraNode.pathWeight + edge.weight >= dijkstraEdgeNode.pathWeight)
                        continue;

                    //Update the edge node's distance from the start node using the current shortest path + this edges weight.
                    dijkstraEdgeNode.pathWeight = dijkstraNode.pathWeight + edge.weight;
                    dijkstraEdgeNode.previousNode = dijkstraNode;
                    dijkstraEdgeNode.previousEdge = edge;
                }
            }
            //#endregion
        }

        //If we do end somehow end up here, something has gone wrong.
        throw new Error(`Failed to find a path from node '${startNode.id}' to node '${endNode.id}' on the specified graph.`);
    }

    public static DijkstraNodeToPathArray(dijkstraNode: IDijkstraNode): IPathPart[]
    {
        const pathArray: IPathPart[] = [];

        let currentNode = dijkstraNode;
        let previousEdge: Edge | null = null;
        while (currentNode != null)
        {
            pathArray.push(
            {
                node: currentNode.node,
                edge: previousEdge
            });

            previousEdge = currentNode.previousEdge;

            if (currentNode.previousNode == null)
                break;

            currentNode = currentNode.previousNode;
        }

        return pathArray.reverse();
    }
}
