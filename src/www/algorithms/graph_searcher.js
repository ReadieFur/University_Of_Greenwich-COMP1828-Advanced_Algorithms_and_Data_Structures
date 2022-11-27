export class GraphSearcher {
    static BreadthFirstSearch(graph, node, visited) {
        const queue = [node];
        while (queue.length > 0) {
            const current = queue.shift();
            if (visited.has(current))
                continue;
            visited.add(current);
            for (const neighbor of current.adjacencyDict)
                queue.push(graph.nodes.get(neighbor[0]));
        }
    }
    static DepthFirstSearch(graph, node, visited) {
        if (visited.has(node))
            return;
        visited.add(node);
        for (const neighbor of node.adjacencyDict)
            this.DepthFirstSearch(graph, graph.nodes.get(neighbor[0]), visited);
    }
    static IsGraphConnected(graph, useBFS) {
        const startingNode = graph.nodes.values().next().value;
        const visited = new Set();
        if (useBFS)
            this.BreadthFirstSearch(graph, startingNode, visited);
        else
            this.DepthFirstSearch(graph, startingNode, visited);
        return visited.size === graph.nodes.size;
    }
    static IsPathAvailable(graph, start, end, useBFS) {
        const visited = new Set();
        if (useBFS)
            this.BreadthFirstSearch(graph, start, visited);
        else
            this.DepthFirstSearch(graph, start, visited);
        return visited.has(end);
    }
}
//# sourceMappingURL=graph_searcher.js.map