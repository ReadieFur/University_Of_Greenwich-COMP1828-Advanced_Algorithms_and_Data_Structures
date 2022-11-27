import { Graph } from "../core/graph.js";
import { DijkstrasAlgorithm } from "./dijkstras_algorithm.js";
import { GraphSearcher } from "./graph_searcher.js";
import { IPathPart } from "./algorithm_helpers.js";

class GraphSearcherTests
{
    public static Run(): void
    {
        console.log(GraphSearcherTests.name);

        this.Test1();
        this.Test2();
    }

    private static Test1(): void
    {
        console.log(this.Test1.name);

        const graph = new Graph();

        const node1 = graph.AddNode();
        const node2 = graph.AddNode();
        const node3 = graph.AddNode();
        const node4 = graph.AddNode();

        graph.AddEdge(node1, node2, 1);
        graph.AddEdge(node1, node3, 1);
        graph.AddEdge(node2, node4, 1);

        console.log("BFS", GraphSearcher.IsGraphConnected(graph, true)); //true
        console.log("DFS", GraphSearcher.IsGraphConnected(graph, false)); //true
    }

    private static Test2(): void
    {
        console.log(this.Test2.name);

        const graph = new Graph();

        const node1 = graph.AddNode();
        const node2 = graph.AddNode();
        const node3 = graph.AddNode();
        const node4 = graph.AddNode();

        graph.AddEdge(node1, node2, 1);
        graph.AddEdge(node1, node3, 1);
        // graph.AddEdge(node2, node4, 1);

        console.log("BFS", GraphSearcher.IsGraphConnected(graph, true)); //false
        console.log("DFS", GraphSearcher.IsGraphConnected(graph, false)); //false
    }
}

class DijkstrasAlgorithmTests
{
    public static Run(): void
    {
        console.log(DijkstrasAlgorithmTests.name);

        this.Test1();
        this.Test2();
    }

    private static MapPart(labels: Map<number, string>, part: IPathPart): string
    {
        const label = labels.get(part.node.id)!;
        if (part.edge == null)
            return label;
        return `${label} (${part.edge.weight})>`;
    }

    private static Test1(): void
    {
        console.log(this.Test1.name);

        const graph = new Graph();

        const A = graph.AddNode();
        const B = graph.AddNode();
        const C = graph.AddNode();
        const D = graph.AddNode();

        graph.AddEdge(A, B, 1);
        graph.AddEdge(A, C, 4);
        graph.AddEdge(B, D, 2);
        graph.AddEdge(B, D, 1);
        graph.AddEdge(C, D, 1);

        const labels: Map<number, string> = new Map<number, string>();
        labels.set(A.id, "A");
        labels.set(B.id, "B");
        labels.set(C.id, "C");
        labels.set(D.id, "D");

        /**
         *     B-----|
         *    / \    |
         *  (1) (2) (1)
         *  /     \  |
         * A       D-|
         *  \     /
         *  (4) (1)
         *    \ /
         *     C
         */

        //Expected shortest path from A to D is A (1)> B (1)> D.
        const expectedResult = "A (1)> B (1)> D";
        const shortestPath = DijkstrasAlgorithm.DijkstraNodeToPathArray(DijkstrasAlgorithm.FindShortestPath(graph, A, D))
            .map(p => this.MapPart(labels, p)).join(" ");
        console.log(shortestPath, "|", expectedResult, "|", shortestPath.toString() === expectedResult.toString());

        //Expected shortest path from B to C is B (1)> D (1)> C.
        const expectedResult2 = "B (1)> D (1)> C";
        const shortestPath2 = DijkstrasAlgorithm.DijkstraNodeToPathArray(DijkstrasAlgorithm.FindShortestPath(graph, B, C))
            .map(p => this.MapPart(labels, p)).join(" ");
        console.log(shortestPath2, "|" , expectedResult2, "|", shortestPath2.toString() === expectedResult2.toString());
    }

    private static Test2(): void
    {
        console.log(this.Test2.name);

        const graph = new Graph();
        const A = graph.AddNode();
        const B = graph.AddNode();
        const C = graph.AddNode();
        const D = graph.AddNode();
        const E = graph.AddNode();
        const F = graph.AddNode();
        const G = graph.AddNode();

        //From the example: COMP1828 "Graph 1.pptx" slide 33
        graph.AddEdge(A, B, 4);
        graph.AddEdge(A, C, 3);
        graph.AddEdge(B, D, 1);
        graph.AddEdge(B, F, 4);
        graph.AddEdge(C, D, 3);
        graph.AddEdge(C, E, 5);
        graph.AddEdge(D, E, 2);
        graph.AddEdge(D, F, 2);
        graph.AddEdge(D, G, 7);
        graph.AddEdge(E, G, 2);
        graph.AddEdge(F, G, 4);

        const labels: Map<number, string> = new Map<number, string>();
        labels.set(A.id, "A");
        labels.set(B.id, "B");
        labels.set(C.id, "C");
        labels.set(D.id, "D");
        labels.set(E.id, "E");
        labels.set(F.id, "F");
        labels.set(G.id, "G");

        /**
         *     B -----(4)----- F
         *    / \            / |
         *  (4)  -(1)-   -(2)  |
         *  /         \ /      |
         * A ---(7)--- D ---  (4)
         *  \          |    \  |
         *  (3)       (2)   (7)|
         *    \        |      \|
         *     C -(5)- E -(2)- G
         */

        //Expected shortest path from A to G is A (4)> B (1)> D (2)> E (2)> G.
        const expectedResult = "A (4)> B (1)> D (2)> E (2)> G";
        const shortestPath = DijkstrasAlgorithm.DijkstraNodeToPathArray(DijkstrasAlgorithm.FindShortestPath(graph, A, G))
            .map(p => this.MapPart(labels, p)).join(" ");
        console.log(shortestPath, "|", expectedResult, "|", shortestPath.toString() === expectedResult.toString());
    }
}

export class AlgorithmTests
{
    public static Run(): void
    {
        GraphSearcherTests.Run();
        DijkstrasAlgorithmTests.Run();
    }
}
// AlgorithmTests.Run();
