import { Draggable } from "./draggable.js";
export class UITests {
    static HaveTestsRun() {
        return UITests.haveTestsRun;
    }
    static Run() {
        if (this.haveTestsRun)
            throw new Error("Tests have already been run.");
        this.haveTestsRun = true;
        this.AddNodes(5);
        this.AddEdges(true, 9999);
        this.SaveGraph();
    }
    static AddNodes(numberOfNodesToCreate) {
        const canvas = document.querySelector("#canvas");
        const canvasScale = Draggable.GetElementTransforms(canvas).get("scale");
        for (let i = 0; i < numberOfNodesToCreate; i++) {
            const x = Math.floor(Math.random() * (canvas.clientWidth * 0.90) * canvasScale);
            const y = Math.floor(Math.random() * (canvas.clientHeight * 0.90) * canvasScale);
            canvas.dispatchEvent(new MouseEvent("click", { clientX: x, clientY: y, shiftKey: true }));
        }
    }
    static AddEdges(forceConnectedGraph, numberOfEdgesToCreate = null) {
        if (numberOfEdgesToCreate === null || numberOfEdgesToCreate < 1)
            return;
        const nodes = document.querySelectorAll(".node");
        let maxNumberOfPossibleEdges = 0;
        for (let i = 0; i < nodes.length; i++)
            maxNumberOfPossibleEdges += i;
        if (numberOfEdgesToCreate > maxNumberOfPossibleEdges)
            numberOfEdgesToCreate = maxNumberOfPossibleEdges;
        const connectedNodes = [];
        for (let i = 0; i < numberOfEdgesToCreate; i++) {
            let node1;
            let node2;
            do {
                node1 = nodes[Math.floor(Math.random() * nodes.length)];
                node2 = nodes[Math.floor(Math.random() * nodes.length)];
            } while (node1 === node2 || connectedNodes.some(x => (x[0] === node1 && x[1] === node2) || (x[0] === node2 && x[1] === node1)));
            connectedNodes.push([node1, node2]);
            const node1Rect = node1.getBoundingClientRect();
            node1.dispatchEvent(new MouseEvent("click", {
                clientX: node1Rect.left + (node1Rect.width * 0.5),
                clientY: node1Rect.top + (node1Rect.height * 0.5),
                shiftKey: true
            }));
            const node2Rect = node2.getBoundingClientRect();
            node2.dispatchEvent(new MouseEvent("click", {
                clientX: node2Rect.left + (node2Rect.width * 0.5),
                clientY: node2Rect.top + (node2Rect.height * 0.5),
                shiftKey: true
            }));
        }
        if (forceConnectedGraph) {
            for (const node of nodes) {
                if (connectedNodes.some(n => n[0] === node || n[1] === node))
                    continue;
                const nodeRect = node.getBoundingClientRect();
                node.dispatchEvent(new MouseEvent("click", {
                    clientX: nodeRect.left + (nodeRect.width * 0.5),
                    clientY: nodeRect.top + (nodeRect.height * 0.5),
                    shiftKey: true
                }));
                const connectedNode = connectedNodes[Math.floor(Math.random() * connectedNodes.length)][0];
                const connectedNodeRect = connectedNode.getBoundingClientRect();
                connectedNode.dispatchEvent(new MouseEvent("click", {
                    clientX: connectedNodeRect.left + (connectedNodeRect.width * 0.5),
                    clientY: connectedNodeRect.top + (connectedNodeRect.height * 0.5),
                    shiftKey: true
                }));
            }
        }
        for (const edge of document.querySelectorAll(".line > input")) {
            const value = Math.max(1, Math.floor(Math.random() * 10));
            edge.value = `${value}`;
            edge.dispatchEvent(new Event("input"));
        }
    }
    static SaveGraph() {
        const saveButton = document.querySelector("#button_save");
        saveButton.click();
    }
    static LoadGraph() {
        const data = `{"nodes":[{"id":1637586818818333,"adjacencyList":[{"nodeID":8977538827660239,"weight":17},{"nodeID":3310532549615201,"weight":84}],"px":745,"py":687,"label":"1637586818818333"},{"id":3310532549615201,"adjacencyList":[{"nodeID":8977538827660239,"weight":54},{"nodeID":1637586818818333,"weight":84}],"px":792,"py":328,"label":"3310532549615201"},{"id":8977538827660239,"adjacencyList":[{"nodeID":3310532549615201,"weight":54},{"nodeID":1637586818818333,"weight":17},{"nodeID":3185470184531985,"weight":95},{"nodeID":6555993046046635,"weight":70}],"px":528,"py":507,"label":"8977538827660239"},{"id":6555993046046635,"adjacencyList":[{"nodeID":8977538827660239,"weight":70}],"px":313,"py":703,"label":"6555993046046635"},{"id":3185470184531985,"adjacencyList":[{"nodeID":8977538827660239,"weight":95}],"px":307,"py":371,"label":"3185470184531985"}],"canvasImage":null}`;
        const nodes = document.querySelectorAll(".node");
        for (const node of nodes) {
            const nodeRect = node.getBoundingClientRect();
            node.dispatchEvent(new MouseEvent("click", {
                clientX: nodeRect.left + (nodeRect.width * 0.5),
                clientY: nodeRect.top + (nodeRect.height * 0.5),
                altKey: true
            }));
        }
    }
}
UITests.haveTestsRun = false;
//# sourceMappingURL=ui_tests.js.map