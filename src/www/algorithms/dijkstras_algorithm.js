export class DijkstrasAlgorithm {
    static FindShortestPath(graph, startNode, endNode) {
        const dijkstraNodes = new Map();
        for (const i of graph.nodes.keys())
            dijkstraNodes.set(i, {
                node: graph.nodes.get(i),
                previousNode: null,
                previousEdge: null,
                pathWeight: Number.MAX_SAFE_INTEGER,
                isBoxed: false
            });
        dijkstraNodes.get(startNode.id).pathWeight = 0;
        for (let i = 0; i < graph.nodes.size; i++) {
            let lightestNodeID = 0;
            let lightestPath = Number.MAX_SAFE_INTEGER;
            for (const j of dijkstraNodes.keys()) {
                const dijkstraNodeJ = dijkstraNodes.get(j);
                if (dijkstraNodeJ.isBoxed || dijkstraNodeJ.pathWeight >= lightestPath)
                    continue;
                lightestNodeID = j;
                lightestPath = dijkstraNodeJ.pathWeight;
            }
            const dijkstraNode = dijkstraNodes.get(lightestNodeID);
            dijkstraNode.isBoxed = true;
            if (lightestNodeID == endNode.id)
                return dijkstraNode;
            for (const [neighbouringNodeID, edges] of dijkstraNode.node.adjacencyDict) {
                const dijkstraEdgeNode = dijkstraNodes.get(neighbouringNodeID);
                if (dijkstraEdgeNode.isBoxed)
                    continue;
                for (const edge of edges.values()) {
                    if (dijkstraNode.pathWeight + edge.weight >= dijkstraEdgeNode.pathWeight)
                        continue;
                    dijkstraEdgeNode.pathWeight = dijkstraNode.pathWeight + edge.weight;
                    dijkstraEdgeNode.previousNode = dijkstraNode;
                    dijkstraEdgeNode.previousEdge = edge;
                }
            }
        }
        throw new Error(`Failed to find a path from node '${startNode.id}' to node '${endNode.id}' on the specified graph.`);
    }
    static DijkstraNodeToPathArray(dijkstraNode) {
        const pathArray = [];
        let currentNode = dijkstraNode;
        let previousEdge = null;
        while (currentNode != null) {
            pathArray.push({
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
//# sourceMappingURL=dijkstras_algorithm.js.map