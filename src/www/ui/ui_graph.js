import { Graph } from "../core/graph.js";
import { UINode } from "./ui_node.js";
import { UIEdge } from "./ui_edge.js";
import { Line } from "./line.js";
import { Collapsible } from "./collapsible.js";
import { Draggable } from "./draggable.js";
import { UIDijkstrasAlgorithm } from "../algorithms/ui/ui_dijkstras_algorithm.js";
import { GraphSearcher } from "../algorithms/graph_searcher.js";
import { DijkstrasAlgorithm } from "../algorithms/dijkstras_algorithm.js";
var EAlgorithm;
(function (EAlgorithm) {
    EAlgorithm[EAlgorithm["Dijkstra"] = 0] = "Dijkstra";
})(EAlgorithm || (EAlgorithm = {}));
export class UIGraph extends Graph {
    static GetInstance() {
        if (!UIGraph.instance)
            UIGraph.instance = new UIGraph();
        return UIGraph.instance;
    }
    constructor() {
        super();
        this.canvasImage = null;
        this.selectedNodeID = -1;
        this.unconnectedEdge = null;
        this.pathfindingLock = false;
        this.hasUnsavedChanges = false;
        this.nodes = new Map();
        this.elements =
            {
                stylesheet: document.createElement("style"),
                toolbox: {
                    editor: {
                        labelNodeRadius: document.querySelector("[for=input_node_radius]"),
                        inputNodeRadius: document.querySelector("#input_node_radius"),
                        inputScale: document.querySelector("#input_scale"),
                        fileBackground: document.querySelector("#file_background"),
                        buttonSave: document.querySelector("#button_save"),
                        fileLoad: document.querySelector("#file_load")
                    },
                    pathfinding: {
                        selectAlgorithm: document.querySelector("#select_algorithm"),
                        selectStartNode: document.querySelector("#select_start_node"),
                        selectEndNode: document.querySelector("#select_end_node"),
                        buttonFindShortestPath: document.querySelector("#button_find_shortest_path"),
                        buttonFindShortestPathNoUI: document.querySelector("#button_find_shortest_path_no_ui"),
                        labelStepSpeed: document.querySelector("[for=input_step_speed]"),
                        inputStepSpeed: document.querySelector("#input_step_speed"),
                        labelPathfindingInfo: document.querySelector("#label_pathfinding_info")
                    }
                },
                canvas: document.querySelector("#canvas")
            };
        this.stylesheet =
            {
                nodeRadius: 50
            };
        this.UpdateStylesheet();
        document.head.appendChild(this.elements.stylesheet);
        this.pathfindingOptions =
            {
                algorithm: EAlgorithm.Dijkstra,
                startNode: null,
                endNode: null,
                stepSpeed: 0
            };
        this.elements.toolbox.editor.inputNodeRadius.addEventListener("input", () => this.InputNodeRadius_OnInput());
        this.elements.toolbox.editor.inputScale.addEventListener("change", () => this.InputScale_OnChange());
        this.elements.toolbox.editor.fileBackground.addEventListener("click", (e) => this.FileBackground_OnClick(e));
        this.elements.toolbox.editor.fileBackground.addEventListener("change", () => this.FileBackground_OnChange());
        this.elements.toolbox.editor.buttonSave.addEventListener("click", () => this.ButtonSave_OnClick());
        this.elements.toolbox.editor.fileLoad.addEventListener("change", () => this.FileLoad_OnChange());
        this.elements.toolbox.pathfinding.selectAlgorithm.addEventListener("change", () => this.SelectAlgorithm_OnChange());
        this.elements.toolbox.pathfinding.selectStartNode.addEventListener("change", () => this.SelectStartNode_OnChange());
        this.elements.toolbox.pathfinding.selectEndNode.addEventListener("change", () => this.SelectEndNode_OnChange());
        this.elements.toolbox.pathfinding.buttonFindShortestPath.addEventListener("click", () => this.ButtonFindPath_OnClick());
        this.elements.toolbox.pathfinding.buttonFindShortestPathNoUI.addEventListener("click", () => this.ButtonFindPathNoUI_OnClick());
        this.elements.toolbox.pathfinding.inputStepSpeed.addEventListener("input", () => this.InputStepSpeed_OnInput());
        for (const algorithm of Object.values(EAlgorithm)) {
            if (typeof algorithm !== "string")
                break;
            const option = document.createElement("option");
            option.value = algorithm;
            option.innerText = algorithm;
            this.elements.toolbox.pathfinding.selectAlgorithm.appendChild(option);
        }
        document.querySelector("#select_algorithm > option:first-child").selected = true;
        this.elements.canvas.addEventListener("click", (e) => this.Canvas_OnClick(e));
        window.addEventListener("beforeunload", (e) => this.Window_OnBeforeUnload(e));
        document.addEventListener("mousemove", (e) => this.Document_OnMouseMove(e));
        document.addEventListener("wheel", (e) => this.Document_OnWheel(e), { passive: false });
        document.addEventListener("keydown", (e) => this.Document_OnKeyDown(e));
        document.addEventListener("keyup", (e) => this.Document_OnKeyUp(e));
        this.ScaleToFit();
        Collapsible.Refresh();
        Draggable.Refresh();
    }
    AddNode(id = null) {
        if (id === null) {
            do
                id = Math.floor(Math.random() * Number.MAX_SAFE_INTEGER);
            while (this.nodes.has(id));
        }
        else if (this.nodes.has(id))
            throw new Error(`Node with ID ${id} already exists.`);
        const node = new UINode(id);
        this.nodes.set(id, node);
        node.element.div.addEventListener("click", (e) => this.Node_OnClick(e));
        const startOption = document.createElement("option");
        startOption.value = `${id}`;
        const endOption = startOption.cloneNode(true);
        node.element.label.addEventListener("change", () => startOption.innerText = endOption.innerText = node.element.label.value);
        startOption.innerText = endOption.innerText = node.element.label.value;
        if (this.pathfindingOptions.startNode === null) {
            this.pathfindingOptions.startNode = node;
            startOption.selected = true;
        }
        else if (this.pathfindingOptions.endNode === null) {
            this.pathfindingOptions.endNode = node;
            endOption.selected = true;
        }
        this.elements.toolbox.pathfinding.selectStartNode.appendChild(startOption);
        this.elements.toolbox.pathfinding.selectEndNode.appendChild(endOption);
        return node;
    }
    RemoveNode(node) {
        node.element.div.remove();
        super.RemoveNode(node);
        const startOption = this.elements.toolbox.pathfinding.selectStartNode.querySelector(`[value="${node.id}"]`);
        const endOption = this.elements.toolbox.pathfinding.selectEndNode.querySelector(`[value="${node.id}"]`);
        startOption.remove();
        endOption.remove();
        if (this.pathfindingOptions.startNode === node)
            this.pathfindingOptions.startNode = null;
        if (this.pathfindingOptions.endNode === node)
            this.pathfindingOptions.endNode = null;
    }
    AddEdge(node1, node2, weight, id) {
        if (node1 === undefined)
            throw new Error("Node 1 does not exist.");
        if (node2 === undefined)
            throw new Error("Node 2 does not exist.");
        if (id == undefined)
            id = Graph.GetUniqueID(Array.from(this.edgeList.keys()));
        else if (this.edgeList.has(id))
            throw new Error(`Edge with ID ${id} already exists.`);
        const edge = new UIEdge(id, weight);
        this.edgeList.set(id, [node1, node2, edge]);
        node1.AddEdge(node2, edge);
        node2.AddEdge(node1, edge);
        const line = new Line();
        edge.line = line;
        line.element.label.value = `${weight}`;
        this.elements.canvas.appendChild(line.element.div);
        line.thicknessPX = this.stylesheet.nodeRadius * UIGraph.LINE_THICKNESS_MULTIPLIER;
        const RedrawEdge = () => {
            line.baseX = node1.element.div.offsetLeft;
            line.baseY = node1.element.div.offsetTop;
            line.targetX = node2.element.div.offsetLeft;
            line.targetY = node2.element.div.offsetTop;
            line.Draw();
        };
        RedrawEdge();
        line.element.label.addEventListener("input", () => {
            let weight = Math.abs(parseInt(line.element.label.value.replace(/\D/g, "")));
            if (isNaN(weight) || weight < 0)
                weight = 0;
            line.element.label.value = `${weight}`;
            edge.weight = weight;
        });
        line.element.label.addEventListener("click", (e) => {
            if (!e.altKey)
                return;
            this.RemoveEdge(edge);
        });
        node1.element.div.addEventListener("dragging", () => RedrawEdge());
        node2.element.div.addEventListener("dragging", () => RedrawEdge());
        return edge;
    }
    Serialize() {
        return Object.assign(Object.assign({}, super.Serialize()), { canvasImage: this.canvasImage, nodeRadius: this.stylesheet.nodeRadius });
    }
    Deserialize(serializedGraph) {
        this.elements.canvas.style.backgroundImage = "";
        for (const node of this.nodes.values())
            this.RemoveNode(node);
        const uiSerializedGraph = serializedGraph;
        if (uiSerializedGraph.canvasImage) {
            this.elements.canvas.style.backgroundImage = `url(${uiSerializedGraph.canvasImage})`;
            this.canvasImage = uiSerializedGraph.canvasImage;
        }
        if (uiSerializedGraph.nodeRadius) {
            this.stylesheet.nodeRadius = uiSerializedGraph.nodeRadius;
            this.UpdateStylesheet();
        }
        for (let i = 0; i < uiSerializedGraph.nodes.length; i++) {
            const serializedNode = uiSerializedGraph.nodes[i];
            const node = this.AddNode(serializedNode.id);
            const uiSerializedNodes = uiSerializedGraph.nodes;
            if (uiSerializedNodes[i].px)
                node.element.div.style.left = `${uiSerializedNodes[i].px}px`;
            if (uiSerializedNodes[i].py)
                node.element.div.style.top = `${uiSerializedNodes[i].py}px`;
            if (uiSerializedNodes[i].label)
                node.element.label.value = uiSerializedNodes[i].label;
            const startOption = this.elements.toolbox.pathfinding.selectStartNode.querySelector(`[value="${node.id}"]`);
            const endOption = this.elements.toolbox.pathfinding.selectEndNode.querySelector(`[value="${node.id}"]`);
            startOption.innerText = endOption.innerText = node.element.label.value;
            this.elements.canvas.appendChild(node.element.div);
            Draggable.Register(node.element.div);
        }
        for (const serializedNode of serializedGraph.nodes) {
            const node = this.nodes.get(serializedNode.id);
            for (const neighbourNodeID of Object.keys(serializedNode.adjacencyList)) {
                const key = parseInt(neighbourNodeID);
                if (isNaN(key))
                    continue;
                const serializedEdges = serializedNode.adjacencyList[key];
                for (const serializedEdge of serializedEdges) {
                    const neighbourNode = this.nodes.get(key);
                    try {
                        const edge = this.AddEdge(node, neighbourNode, serializedEdge.weight, serializedEdge.id);
                        edge.line.element.label.value = `${edge.weight}`;
                        edge.label = serializedEdge.label !== undefined ? serializedEdge.label : `${serializedEdge.weight}`;
                    }
                    catch (ex) {
                        if (ex instanceof Error && ex.message == `Edge with ID ${serializedEdge.id} already exists.`)
                            continue;
                    }
                }
            }
        }
    }
    static PadLeft(str, length, char) {
        while (str.length < length)
            str = char + str;
        return str;
    }
    UpdateStylesheet() {
        this.elements.stylesheet.innerHTML = `*
        {
            --node-radius: ${this.stylesheet.nodeRadius}px;
        }`;
        this.elements.toolbox.editor.inputNodeRadius.value = `${this.stylesheet.nodeRadius}`;
        for (const node of this.nodes.values()) {
            for (const edges of node.adjacencyDict.values()) {
                for (const [_, edge] of edges) {
                    if (edge.line == null)
                        continue;
                    edge.line.thicknessPX = this.stylesheet.nodeRadius * UIGraph.LINE_THICKNESS_MULTIPLIER;
                    edge.line.Draw();
                }
            }
        }
    }
    InputNodeRadius_OnInput() {
        this.stylesheet.nodeRadius = parseInt(this.elements.toolbox.editor.inputNodeRadius.value);
        const uiString = UIGraph.PadLeft(`${this.stylesheet.nodeRadius}`, 2, "0");
        this.elements.toolbox.editor.labelNodeRadius.innerText = `Node radius (${uiString})`;
        this.UpdateStylesheet();
    }
    InputScale_OnChange() {
        this.elements.canvas.style.transform = `scale(${this.elements.toolbox.editor.inputScale.value})`;
    }
    FileBackground_OnClick(e) {
        if (!e.altKey)
            return;
        e.preventDefault();
        this.elements.canvas.style.backgroundImage = "";
    }
    FileBackground_OnChange() {
        if (this.elements.toolbox.editor.fileBackground.files == null || this.elements.toolbox.editor.fileBackground.files.length == 0)
            return;
        const reader = new FileReader();
        reader.onload = (e) => {
            var _a;
            this.canvasImage = (_a = e.target) === null || _a === void 0 ? void 0 : _a.result;
            this.elements.canvas.style.backgroundImage = `url(${this.canvasImage})`;
        };
        reader.readAsDataURL(this.elements.toolbox.editor.fileBackground.files[0]);
        this.elements.toolbox.editor.fileBackground.value = "";
    }
    ButtonSave_OnClick() {
        const data = JSON.stringify(this.Serialize());
        const blob = new Blob([data], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.download = `graph_${Math.floor(Date.now() / 1000)}.json`;
        link.href = url;
        if (new URLSearchParams(window.location.search).has("run_tests")) {
            console.log(data, JSON.parse(data));
            return;
        }
        link.click();
        link.remove();
        this.hasUnsavedChanges = false;
    }
    FileLoad_OnChange() {
        if (this.elements.toolbox.editor.fileLoad.files == null || this.elements.toolbox.editor.fileLoad.files.length == 0)
            return;
        const reader = new FileReader();
        reader.onload = (e) => {
            var _a;
            const data = JSON.parse((_a = e.target) === null || _a === void 0 ? void 0 : _a.result);
            this.Deserialize(data);
        };
        reader.readAsText(this.elements.toolbox.editor.fileLoad.files[0]);
        this.elements.toolbox.editor.fileLoad.value = "";
    }
    SelectAlgorithm_OnChange() {
        this.pathfindingOptions.algorithm = EAlgorithm[this.elements.toolbox.pathfinding.selectAlgorithm.value];
    }
    SelectStartNode_OnChange() {
        const id = parseInt(this.elements.toolbox.pathfinding.selectStartNode.value);
        const node = this.nodes.get(id);
        if (isNaN(id) || node == undefined) {
            this.elements.toolbox.pathfinding.selectStartNode.value = "";
            this.pathfindingOptions.startNode = null;
            return;
        }
        this.pathfindingOptions.startNode = node;
    }
    SelectEndNode_OnChange() {
        const id = parseInt(this.elements.toolbox.pathfinding.selectEndNode.value);
        const node = this.nodes.get(id);
        if (isNaN(id) || node == undefined) {
            this.elements.toolbox.pathfinding.selectEndNode.value = "";
            this.pathfindingOptions.endNode = null;
            return;
        }
        this.pathfindingOptions.endNode = node;
    }
    static Sleep(milliseconds) {
        if (milliseconds < 0)
            return Promise.resolve();
        return new Promise(resolve => setTimeout(resolve, milliseconds));
    }
    ResetColours() {
        for (const node of this.nodes.values()) {
            node.element.div.style.borderColor = "black";
            for (const edges of node.adjacencyDict.values()) {
                for (const [_, edge] of edges) {
                    if (edge.line == null)
                        continue;
                    edge.line.color = "black";
                    edge.line.Draw();
                }
            }
        }
    }
    async RunShortestPathFinder(Finder) {
        if (this.pathfindingLock)
            return Promise.resolve();
        this.pathfindingLock = true;
        this.elements.toolbox.pathfinding.buttonFindShortestPath.disabled = true;
        this.elements.toolbox.pathfinding.buttonFindShortestPathNoUI.disabled = true;
        this.ResetColours();
        if (this.pathfindingOptions.startNode == null) {
            alert("Invalid start node selected.");
            return Promise.resolve();
        }
        if (this.pathfindingOptions.endNode == null) {
            alert("Invalid end node selected.");
            return Promise.resolve();
        }
        if (!GraphSearcher.IsPathAvailable(this, this.pathfindingOptions.startNode, this.pathfindingOptions.endNode, true)) {
            alert("No path exists between the selected nodes.");
            return Promise.resolve();
        }
        const path = await Finder();
        let weight = 0;
        let uiString = "";
        for (let i = 0; i < path.length; i++) {
            const currentPart = path[i];
            let edgeLabel = "";
            if (currentPart.edge != null) {
                weight += currentPart.edge.weight;
                edgeLabel = currentPart.edge.label != null && currentPart.edge.label != "" ?
                    `(via ${currentPart.edge.label})` : `(${currentPart.edge.weight})`;
            }
            uiString += currentPart.node.element !== undefined ? currentPart.node.element.label.value : currentPart.node.id.toString();
            if (i < path.length - 1)
                uiString += ` ${edgeLabel}> `;
        }
        const startLabel = this.pathfindingOptions.startNode.element !== undefined ? this.pathfindingOptions.startNode.element.label.value : this.pathfindingOptions.startNode.id.toString();
        const endLabel = this.pathfindingOptions.endNode.element !== undefined ? this.pathfindingOptions.endNode.element.label.value : this.pathfindingOptions.endNode.id.toString();
        const resultString = `Showing the result for the shortest path between ${startLabel} and ${endLabel}:`
            + `\nPath weight: ${weight}`
            + `\nPath: ${uiString}`;
        const button = document.createElement("button");
        button.innerText = "Show result";
        button.onclick = () => alert(resultString);
        this.elements.toolbox.pathfinding.labelPathfindingInfo.innerHTML = "";
        this.elements.toolbox.pathfinding.labelPathfindingInfo.appendChild(button);
        this.pathfindingLock = false;
        this.elements.toolbox.pathfinding.buttonFindShortestPath.disabled = false;
        this.elements.toolbox.pathfinding.buttonFindShortestPathNoUI.disabled = false;
    }
    async FindShortestPathUI() {
        let path = [];
        switch (this.pathfindingOptions.algorithm) {
            case EAlgorithm.Dijkstra:
                let node_currentShortestPath = null;
                let node_previousNode = null;
                let edge_currentClosestEdge = null;
                let edge_currentClosestEdgeWeight = Number.MAX_SAFE_INTEGER;
                let edge_previousNode = null;
                let edge_previousEdge = null;
                const result = await UIDijkstrasAlgorithm.FindShortestPath(this, this.pathfindingOptions.startNode, this.pathfindingOptions.endNode, async (dNode) => {
                    this.elements.toolbox.pathfinding.labelPathfindingInfo.innerText = "Checking the shortest path to node"
                        + ` '${dNode.node.element !== undefined ? dNode.node.element.label.value : dNode.node.id}'...`;
                    if (edge_previousNode != null && edge_previousNode.element !== undefined)
                        edge_previousNode.element.div.style.borderColor = "black";
                    if (edge_previousEdge != null && edge_previousEdge.line != undefined) {
                        edge_previousEdge.line.color = "black";
                        edge_previousEdge.line.Draw();
                    }
                    if (edge_currentClosestEdge != null && edge_currentClosestEdge.line != undefined) {
                        edge_currentClosestEdge.line.color = "black";
                        edge_currentClosestEdge.line.Draw();
                    }
                    if (dNode.isBoxed || dNode.previousNode == null)
                        return;
                    if (node_previousNode !== node_currentShortestPath
                        && node_previousNode !== null) {
                        if (node_previousNode.node.element !== undefined)
                            node_previousNode.node.element.div.style.borderColor = "black";
                        if (node_previousNode.previousNode !== null) {
                            for (const [_, edge] of node_previousNode.previousNode.node.adjacencyDict.get(node_previousNode.node.id)) {
                                if (edge.line == null)
                                    continue;
                                edge.line.color = "black";
                                edge.line.Draw();
                            }
                        }
                    }
                    const previousUINode = dNode.previousNode.node;
                    const node = dNode.node;
                    const edges = previousUINode.adjacencyDict.get(node.id);
                    let colour = "yellow";
                    if (node_currentShortestPath == null || dNode.pathWeight < node_currentShortestPath.pathWeight) {
                        if (node_currentShortestPath !== null && node_currentShortestPath.previousNode !== null) {
                            const oldPreviousUINode = node_currentShortestPath.previousNode.node;
                            const oldNode = node_currentShortestPath.node;
                            const oldEdges = oldPreviousUINode.adjacencyDict.get(oldNode.id);
                            for (const [_, oldEdge] of oldEdges) {
                                if (oldEdge.line == undefined)
                                    continue;
                                oldEdge.line.color = "black";
                                oldEdge.line.Draw();
                            }
                            if (oldNode.element !== undefined)
                                oldNode.element.div.style.borderColor = "black";
                        }
                        node_currentShortestPath = dNode;
                        colour = "orange";
                    }
                    for (const [_, edge] of edges) {
                        if (edge.line == undefined)
                            continue;
                        edge.line.color = colour;
                        edge.line.Draw();
                    }
                    if (node.element !== undefined)
                        node.element.div.style.borderColor = colour;
                    node_previousNode = dNode;
                    await UIGraph.Sleep(this.pathfindingOptions.stepSpeed);
                }, async (dNode) => {
                    this.elements.toolbox.pathfinding.labelPathfindingInfo.innerText = "Boxed node"
                        + ` '${dNode.node.element !== undefined ? dNode.node.element.label.value : dNode.node.id}'...`;
                    if (node_previousNode != null) {
                        if (node_previousNode.node.element !== undefined)
                            node_previousNode.node.element.div.style.borderColor = "black";
                        if (node_previousNode.previousNode !== null) {
                            for (const [_, edge] of node_previousNode.previousNode.node.adjacencyDict.get(node_previousNode.node.id)) {
                                if (edge.line == null)
                                    continue;
                                edge.line.color = "black";
                                edge.line.Draw();
                            }
                        }
                    }
                    if (node_currentShortestPath != null) {
                        if (node_currentShortestPath.node.element !== undefined)
                            node_currentShortestPath.node.element.div.style.borderColor = "black";
                        if (node_currentShortestPath.previousNode !== null) {
                            for (const [_, edge] of node_currentShortestPath.previousNode.node.adjacencyDict.get(node_currentShortestPath.node.id)) {
                                if (edge.line == null)
                                    continue;
                                edge.line.color = "black";
                                edge.line.Draw();
                            }
                        }
                    }
                    const uiNode = dNode.node;
                    if (uiNode.element !== undefined)
                        uiNode.element.div.style.borderColor = "red";
                    if (dNode.previousNode != null) {
                        const uiEdge = dNode.previousEdge;
                        if (uiEdge.line !== undefined) {
                            uiEdge.line.color = "red";
                            uiEdge.line.Draw();
                        }
                    }
                    node_currentShortestPath = null;
                    node_previousNode = null;
                    edge_currentClosestEdge = null;
                    edge_currentClosestEdgeWeight = Number.MAX_SAFE_INTEGER;
                    edge_previousNode = null;
                    edge_previousEdge = null;
                    await UIGraph.Sleep(this.pathfindingOptions.stepSpeed);
                }, async (dNode, dEdgeNode) => {
                    this.elements.toolbox.pathfinding.labelPathfindingInfo.innerText = "Checking lightest edge on node"
                        + ` '${dNode.node.element !== undefined ? dNode.node.element.label.value : dNode.node.id}'...`;
                    if (dEdgeNode.isBoxed)
                        return;
                    if (edge_previousEdge != edge_currentClosestEdge && edge_previousEdge !== null && edge_previousEdge.line !== undefined) {
                        edge_previousEdge.line.color = "black";
                        edge_previousEdge.line.Draw();
                    }
                    const uiNode = dEdgeNode.node;
                    const edges = uiNode.adjacencyDict.get(dNode.node.id);
                    let colour = "yellow";
                    for (const [_, edge] of edges) {
                        if (edge.weight < edge_currentClosestEdgeWeight) {
                            if (edge_currentClosestEdge !== null && edge_currentClosestEdge.line !== undefined) {
                                edge_currentClosestEdge.line.color = "black";
                                edge_currentClosestEdge.line.Draw();
                            }
                            edge_currentClosestEdge = edge;
                            edge_currentClosestEdgeWeight = edge.weight;
                            colour = "orange";
                        }
                        if (edge.line !== undefined) {
                            edge.line.color = colour;
                            edge.line.Draw();
                        }
                        edge_previousNode = uiNode;
                        edge_previousEdge = edge;
                    }
                    await UIGraph.Sleep(this.pathfindingOptions.stepSpeed);
                }, async (dNode) => {
                    this.elements.toolbox.pathfinding.labelPathfindingInfo.innerText = "Shortest path found!";
                    const uiNode = dNode.node;
                    if (uiNode.element !== undefined)
                        uiNode.element.div.style.borderColor = "green";
                    await UIGraph.Sleep(this.pathfindingOptions.stepSpeed);
                });
                path = DijkstrasAlgorithm.DijkstraNodeToPathArray(result);
                break;
            default:
                alert("Invalid algorithm selected.");
                break;
        }
        this.ResetColours();
        const startLabel = this.pathfindingOptions.startNode.element !== undefined
            ? this.pathfindingOptions.startNode.element.label.value : this.pathfindingOptions.startNode.id;
        const endLabel = this.pathfindingOptions.endNode.element !== undefined
            ? this.pathfindingOptions.endNode.element.label.value : this.pathfindingOptions.endNode.id;
        this.elements.toolbox.pathfinding.labelPathfindingInfo.innerText = `Tracing shortest path from '${startLabel}' to '${endLabel}'...`;
        await UIGraph.Sleep(this.pathfindingOptions.stepSpeed);
        for (let i = 1; i < path.length; i++) {
            const currentPart = path[i];
            const previousPart = path[i - 1];
            if (i == 1 && previousPart.node.element !== undefined)
                previousPart.node.element.div.style.borderColor = "green";
            if (previousPart.edge.line !== undefined) {
                previousPart.edge.line.color = "green";
                previousPart.edge.line.Draw();
            }
            if (currentPart.node.element !== undefined)
                currentPart.node.element.div.style.borderColor = "green";
            await UIGraph.Sleep(this.pathfindingOptions.stepSpeed);
        }
        return path;
    }
    async FindShortestPathNoUI() {
        let path = [];
        switch (this.pathfindingOptions.algorithm) {
            case EAlgorithm.Dijkstra:
                const result = DijkstrasAlgorithm.FindShortestPath(this, this.pathfindingOptions.startNode, this.pathfindingOptions.endNode);
                path = DijkstrasAlgorithm.DijkstraNodeToPathArray(result);
                break;
            default:
                alert("Invalid algorithm selected.");
        }
        return path;
    }
    async ButtonFindPath_OnClick() {
        await this.RunShortestPathFinder(async () => this.FindShortestPathUI());
    }
    ButtonFindPathNoUI_OnClick() {
        this.RunShortestPathFinder(async () => this.FindShortestPathNoUI());
    }
    InputStepSpeed_OnInput() {
        const value = parseInt(this.elements.toolbox.pathfinding.inputStepSpeed.value);
        this.pathfindingOptions.stepSpeed = value;
        const uiString = UIGraph.PadLeft(`${value}`, 4, "0");
        this.elements.toolbox.pathfinding.labelStepSpeed.innerText = `Step speed (${uiString})`;
    }
    Canvas_OnClick(e) {
        if (e.target instanceof HTMLElement && e.target.parentElement === this.elements.canvas)
            this.elements.canvas.appendChild(e.target);
        this.hasUnsavedChanges = true;
        if (e.target === this.elements.canvas && e.shiftKey && !e.altKey && this.unconnectedEdge == null) {
            const node = this.AddNode();
            node.element.div.style.left = `${e.clientX / parseFloat(this.elements.toolbox.editor.inputScale.value)}px`;
            node.element.div.style.top = `${e.clientY / parseFloat(this.elements.toolbox.editor.inputScale.value)}px`;
            this.elements.canvas.appendChild(node.element.div);
            Draggable.Register(node.element.div);
        }
    }
    Node_OnClick(e) {
        var _a, _b, _c;
        if (e.target instanceof HTMLDivElement && e.target.classList.contains("node")) {
            if (!e.shiftKey && e.altKey) {
                if (!(e.target instanceof HTMLElement && e.target.classList.contains("node")))
                    return;
                this.RemoveNode(this.nodes.get(parseInt(e.target.id.substring(UINode.ID_PREFIX.length))));
            }
            else if (e.shiftKey && !e.altKey) {
                (_a = window.getSelection()) === null || _a === void 0 ? void 0 : _a.removeAllRanges();
                if (this.selectedNodeID === -1) {
                    if (!(e.target instanceof HTMLElement && e.target.classList.contains("node")))
                        return;
                    this.selectedNodeID = parseInt(e.target.id.substring(UINode.ID_PREFIX.length));
                    const node = this.nodes.get(this.selectedNodeID);
                    this.unconnectedEdge = new Line();
                    this.unconnectedEdge.thicknessPX = this.stylesheet.nodeRadius * UIGraph.LINE_THICKNESS_MULTIPLIER;
                    this.unconnectedEdge.baseX = node.element.div.offsetLeft;
                    this.unconnectedEdge.baseY = node.element.div.offsetTop;
                    this.unconnectedEdge.clickEvents = false;
                    this.elements.canvas.appendChild(this.unconnectedEdge.element.div);
                }
                else {
                    if (!(e.target instanceof HTMLElement && e.target.classList.contains("node")))
                        return;
                    this.AddEdge(this.nodes.get(this.selectedNodeID), this.nodes.get(parseInt(e.target.id.substring(UINode.ID_PREFIX.length))), 1);
                    this.selectedNodeID = -1;
                    (_b = this.unconnectedEdge) === null || _b === void 0 ? void 0 : _b.Dispose();
                    this.unconnectedEdge = null;
                }
            }
            else {
                this.selectedNodeID = -1;
                (_c = this.unconnectedEdge) === null || _c === void 0 ? void 0 : _c.Dispose();
                this.unconnectedEdge = null;
            }
        }
    }
    Window_OnBeforeUnload(e) {
        if (this.hasUnsavedChanges) {
            e.preventDefault();
            e.returnValue = "false";
        }
    }
    Document_OnMouseMove(e) {
        if (this.unconnectedEdge !== null) {
            this.unconnectedEdge.targetX = e.clientX;
            this.unconnectedEdge.targetY = e.clientY;
            this.unconnectedEdge.Draw();
        }
    }
    Document_OnWheel(e) {
        if (!e.ctrlKey)
            return;
        e.preventDefault();
        this.UpdateScale_Tick(e.deltaY < 0);
    }
    Document_OnKeyDown(e) {
        if (!e.ctrlKey || !(e.key === "+" ||
            e.key === "-" ||
            e.key === "=" ||
            e.key === "_" ||
            e.key === "0"))
            return;
        e.preventDefault();
        switch (e.key) {
            case "+":
            case "=":
                this.UpdateScale_Tick(true);
                break;
            case "-":
            case "_":
                this.UpdateScale_Tick(false);
                break;
            case "0":
                this.ScaleToFit();
                break;
        }
    }
    UpdateScale_Tick(increase) {
        const tick = 0.1;
        this.UpdateScale((parseFloat(this.elements.toolbox.editor.inputScale.value) + (increase ? tick : -tick)));
    }
    ScaleToFit() {
        const canvasWidth = 1024;
        const canvasHeight = 768;
        this.elements.canvas.style.width = `${canvasWidth}px`;
        this.elements.canvas.style.height = `${canvasHeight}px`;
        const clientWiderThanTall = document.body.clientWidth > document.body.clientHeight;
        const scale = !clientWiderThanTall ? document.body.clientWidth / canvasWidth : document.body.clientHeight / canvasHeight;
        this.UpdateScale(scale);
    }
    UpdateScale(scale) {
        const min = 0.1;
        let newScale = Math.round(scale * 100) / 100;
        newScale = Math.max(min, newScale);
        this.elements.toolbox.editor.inputScale.value = newScale.toString();
        this.elements.canvas.style.transform = `scale(${newScale})`;
    }
    Document_OnKeyUp(e) {
        if (this.unconnectedEdge !== null && !e.shiftKey) {
            this.unconnectedEdge.Dispose();
            this.unconnectedEdge = null;
            this.selectedNodeID = -1;
        }
    }
}
UIGraph.LINE_THICKNESS_MULTIPLIER = 0.04;
//# sourceMappingURL=ui_graph.js.map