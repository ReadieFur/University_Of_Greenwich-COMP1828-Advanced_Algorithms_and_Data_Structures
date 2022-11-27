import { Graph } from "../core/graph.js";
import { Node } from "../core/node.js";

export class GraphSearcher
{
    /*
     * This search will visit all unvisited, connected nodes in the order they were added to the graph.
     * Meaning that it will visit nodes neighbors in a queue-like fashion.
     */
    private static BreadthFirstSearch(graph: Graph, node: Node, visited: Set<Node>): void
    {
        //We first start by adding the node to the queue.
        const queue = [node];

        while (queue.length > 0)
        {
            //Take the first node from the queue.
            const current = queue.shift()!;

            //If the node has been visited, continue, otherwise mark it as visited.
            if (visited.has(current)) continue;
            visited.add(current);

            //For each of the current node's neighbors, add them to the queue.
            for (const neighbor of current.adjacencyDict)
                queue.push(graph.nodes.get(neighbor[0])!);
        }
    }

    /*
     * This search will visit all unvisited, connected nodes one after the other, recursively.
     * Meaning that it will traverse one branch of the graph before moving on to the next.
     */
    //We can safley use the same visited Set when recursing becuase it is a data type and therefore is passed by reference, not a value, unlike a list.
    private static DepthFirstSearch(graph: Graph, node: Node, visited: Set<Node>): void
    {
        //If the node has been visited, return, otherwise mark it as visited.
        if (visited.has(node)) return;
        visited.add(node);

        //For each of the current node's neighbors, recursively call the DFS function.
        for (const neighbor of node.adjacencyDict)
            this.DepthFirstSearch(graph, graph.nodes.get(neighbor[0])!, visited);
    }

    /*
     * If useBFS is false, then DFS is used instead.
     */
    public static IsGraphConnected(graph: Graph, useBFS: boolean): boolean
    {
        //Both searches require a starting node which can be any arbitrary node in the graph, so we will just use the first one.
        const startingNode = graph.nodes.values().next().value as Node;
        const visited = new Set<Node>();

        if (useBFS) this.BreadthFirstSearch(graph, startingNode, visited);
        else this.DepthFirstSearch(graph, startingNode, visited);

        //We can tell if a graph is connected if the search returns a list of nodes whos size is equal to the number of nodes in the graph.
        return visited.size === graph.nodes.size;
    }

    public static IsPathAvailable(graph: Graph, start: Node, end: Node, useBFS: boolean): boolean
    {
        const visited = new Set<Node>();

        if (useBFS) this.BreadthFirstSearch(graph, start, visited);
        else this.DepthFirstSearch(graph, start, visited);

        //We can tell if a path is available if the search returns a list of nodes that contains the end node.
        return visited.has(end);
    }
}
