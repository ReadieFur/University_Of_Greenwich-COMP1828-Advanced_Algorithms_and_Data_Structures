import { Graph, ISerializedGraph } from "../core/graph.js";
import { Node } from "../core/node.js";
import { UINode, IUISerializedNode } from "./ui_node.js";
import { UIEdge, ISerializedUIEdge } from "./ui_edge.js";
import { Line } from "./line.js";
import { Collapsible } from "./collapsible.js";
import { Draggable } from "./draggable.js";
import { UIDijkstrasAlgorithm } from "../algorithms/ui/ui_dijkstras_algorithm.js";
import { GraphSearcher } from "../algorithms/graph_searcher.js";
import { DijkstrasAlgorithm, IDijkstraNode } from "../algorithms/dijkstras_algorithm.js";
import { IPathPart } from "../algorithms/algorithm_helpers.js";

interface IUISerializedGraph extends ISerializedGraph
{
    canvasImage: string | null;
    nodeRadius: number | null;
    // nodes: IUISerializedNode[];
}

interface IElements
{
    stylesheet: HTMLStyleElement;
    toolbox:
    {
        editor:
        {
            labelNodeRadius: HTMLLabelElement;
            inputNodeRadius: HTMLInputElement;
            inputScale: HTMLInputElement;
            fileBackground: HTMLInputElement;
            buttonSave: HTMLButtonElement;
            fileLoad: HTMLInputElement;
        },
        pathfinding:
        {
            selectAlgorithm: HTMLSelectElement;
            selectStartNode: HTMLSelectElement;
            selectEndNode: HTMLSelectElement;
            buttonFindShortestPath: HTMLButtonElement;
            buttonFindShortestPathNoUI: HTMLButtonElement;
            labelStepSpeed: HTMLLabelElement;
            inputStepSpeed: HTMLInputElement;
            labelPathfindingInfo: HTMLLabelElement;
        }
    }
    canvas: HTMLDivElement;
}

interface IDynamicStyles
{
    nodeRadius: number;
}

enum EAlgorithm
{
    Dijkstra
}

interface IPathfindingOptions
{
    algorithm: EAlgorithm;
    startNode: Node | null;
    endNode: Node | null;
    stepSpeed: number;
}

export class UIGraph extends Graph
{
    private static readonly LINE_THICKNESS_MULTIPLIER = 0.04;

    //#region Static
    private static instance?: UIGraph;

    public static GetInstance(): UIGraph
    {
        if (!UIGraph.instance) UIGraph.instance = new UIGraph();
        return UIGraph.instance;
    }
    //#endregion

    private readonly elements: IElements;
    private stylesheet: IDynamicStyles;
    private canvasImage: string | null = null;
    private selectedNodeID = -1;
    private unconnectedEdge: Line | null = null;
    private pathfindingOptions: IPathfindingOptions;
    private pathfindingLock = false;
    private hasUnsavedChanges = false;

    public override nodes: Map<number, UINode> = new Map<number, UINode>();

    private constructor()
    {
        super();

        this.elements =
        {
            stylesheet: document.createElement("style"),
            toolbox:
            {
                editor:
                {
                    labelNodeRadius: document.querySelector("[for=input_node_radius]") as HTMLLabelElement,
                    inputNodeRadius: document.querySelector("#input_node_radius") as HTMLInputElement,
                    inputScale: document.querySelector("#input_scale") as HTMLInputElement,
                    fileBackground: document.querySelector("#file_background") as HTMLInputElement,
                    buttonSave: document.querySelector("#button_save") as HTMLButtonElement,
                    fileLoad: document.querySelector("#file_load") as HTMLInputElement
                },
                pathfinding:
                {
                    selectAlgorithm: document.querySelector("#select_algorithm") as HTMLSelectElement,
                    selectStartNode: document.querySelector("#select_start_node") as HTMLSelectElement,
                    selectEndNode: document.querySelector("#select_end_node") as HTMLSelectElement,
                    buttonFindShortestPath: document.querySelector("#button_find_shortest_path") as HTMLButtonElement,
                    buttonFindShortestPathNoUI: document.querySelector("#button_find_shortest_path_no_ui") as HTMLButtonElement,
                    labelStepSpeed: document.querySelector("[for=input_step_speed]") as HTMLLabelElement,
                    inputStepSpeed: document.querySelector("#input_step_speed") as HTMLInputElement,
                    labelPathfindingInfo: document.querySelector("#label_pathfinding_info") as HTMLLabelElement
                }
            },
            canvas: document.querySelector("#canvas") as HTMLDivElement
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

        for (const algorithm of Object.values(EAlgorithm))
        {
            if (typeof algorithm !== "string")
                break;

            const option = document.createElement("option");
            option.value = algorithm;
            option.innerText = algorithm;
            this.elements.toolbox.pathfinding.selectAlgorithm.appendChild(option);
        }
        (<HTMLOptionElement>document.querySelector("#select_algorithm > option:first-child")).selected = true;

        this.elements.canvas.addEventListener("click", (e) => this.Canvas_OnClick(e));

        window.addEventListener("beforeunload", (e) => this.Window_OnBeforeUnload(e));

        document.addEventListener("mousemove", (e) => this.Document_OnMouseMove(e));
        //https://chromestatus.com/feature/6662647093133312
        document.addEventListener("wheel", (e) => this.Document_OnWheel(e), { passive: false });
        document.addEventListener("keydown", (e) => this.Document_OnKeyDown(e));
        document.addEventListener("keyup", (e) => this.Document_OnKeyUp(e));

        this.ScaleToFit();

        Collapsible.Refresh();
        Draggable.Refresh();
    }

    //#region Overrides
    public override AddNode(id: number | null = null): Node
    {
        if (id === null)
        {
            do id = Math.floor(Math.random() * Number.MAX_SAFE_INTEGER);
            while (this.nodes.has(id));
        }
        else if (this.nodes.has(id))
            throw new Error(`Node with ID ${id} already exists.`);

        const node = new UINode(id);
        this.nodes.set(id, node);
        node.element.div.addEventListener("click", (e) => this.Node_OnClick(e));

        const startOption = document.createElement("option");
        startOption.value = `${id}`;
        const endOption = startOption.cloneNode(true) as HTMLOptionElement;

        node.element.label.addEventListener("change", () => startOption.innerText = endOption.innerText = node.element.label.value);
        startOption.innerText = endOption.innerText = node.element.label.value;

        if (this.pathfindingOptions.startNode === null)
        {
            this.pathfindingOptions.startNode = node;
            startOption.selected = true;
        }
        else if (this.pathfindingOptions.endNode === null)
        {
            this.pathfindingOptions.endNode = node;
            endOption.selected = true;
        }

        this.elements.toolbox.pathfinding.selectStartNode.appendChild(startOption);
        this.elements.toolbox.pathfinding.selectEndNode.appendChild(endOption);

        return node;
    }

    public override RemoveNode(node: UINode): void
    {
        node.element.div.remove();
        super.RemoveNode(node);

        const startOption = this.elements.toolbox.pathfinding.selectStartNode.querySelector(`[value="${node.id}"]`) as HTMLOptionElement;
        const endOption = this.elements.toolbox.pathfinding.selectEndNode.querySelector(`[value="${node.id}"]`) as HTMLOptionElement;
        startOption.remove();
        endOption.remove();

        if (this.pathfindingOptions.startNode === node)
            this.pathfindingOptions.startNode = null;
        if (this.pathfindingOptions.endNode === node)
            this.pathfindingOptions.endNode = null;
    }

    public override AddEdge(node1: UINode, node2: UINode, weight: number, id?: number): UIEdge
    {
        //#region Base
        if (node1 === undefined) throw new Error("Node 1 does not exist.");
        if (node2 === undefined) throw new Error("Node 2 does not exist.");

        if (id == undefined)
            id = Graph.GetUniqueID(Array.from(this.edgeList.keys()));
        else if (this.edgeList.has(id))
            throw new Error(`Edge with ID ${id} already exists.`);

        const edge = new UIEdge(id, weight);
        this.edgeList.set(id, [node1, node2, edge]);

        node1.AddEdge(node2, edge);
        node2.AddEdge(node1, edge);
        //#endregion

        const line = new Line();
        edge.line = line;

        line.element.label.value = `${weight}`;
        this.elements.canvas.appendChild(line.element.div);
        line.thicknessPX = this.stylesheet.nodeRadius * UIGraph.LINE_THICKNESS_MULTIPLIER;
        const RedrawEdge = () =>
        {
            line.baseX = node1.element.div.offsetLeft;
            line.baseY = node1.element.div.offsetTop;
            line.targetX = node2.element.div.offsetLeft;
            line.targetY = node2.element.div.offsetTop;
            line.Draw();
        };
        RedrawEdge();

        line.element.label.addEventListener("input", () =>
        {
            let weight = Math.abs(parseInt(line.element.label.value.replace(/\D/g, "")));
            if (isNaN(weight) || weight < 0) weight = 0;

            //Only allow numeric input.
            line.element.label.value = `${weight}`;

            //Update the weight of the edges.
            edge.weight = weight;
        });

        line.element.label.addEventListener("click", (e) =>
        {
            if (!e.altKey) return;
            this.RemoveEdge(edge);
        });

        node1.element.div.addEventListener("dragging", () => RedrawEdge());
        node2.element.div.addEventListener("dragging", () => RedrawEdge());

        return edge;
    }

    public override Serialize(): IUISerializedGraph
    {
        return {
            ...super.Serialize(),
            canvasImage: this.canvasImage,
            nodeRadius: this.stylesheet.nodeRadius
        }
    }
    //#endregion

    public override Deserialize(serializedGraph: ISerializedGraph): void
    {
        //#region Reset the graph.
        this.elements.canvas.style.backgroundImage = "";

        for (const node of this.nodes.values())
            this.RemoveNode(node);
        //#endregion

        //#region Load the new data.
        const uiSerializedGraph = serializedGraph as IUISerializedGraph;
        if (uiSerializedGraph.canvasImage)
        {
            this.elements.canvas.style.backgroundImage = `url(${uiSerializedGraph.canvasImage})`;
            this.canvasImage = uiSerializedGraph.canvasImage;
        }
        if (uiSerializedGraph.nodeRadius)
        {
            this.stylesheet.nodeRadius = uiSerializedGraph.nodeRadius;
            this.UpdateStylesheet();
        }

        for (let i = 0; i < uiSerializedGraph.nodes.length; i++)
        {
            const serializedNode = uiSerializedGraph.nodes[i];
            const node = this.AddNode(serializedNode.id) as UINode;

            const uiSerializedNodes = uiSerializedGraph.nodes as IUISerializedNode[];
            if (uiSerializedNodes[i].px) node.element.div.style.left = `${uiSerializedNodes[i].px}px`;
            if (uiSerializedNodes[i].py) node.element.div.style.top = `${uiSerializedNodes[i].py}px`;
            if (uiSerializedNodes[i].label) node.element.label.value = uiSerializedNodes[i].label;

            const startOption = this.elements.toolbox.pathfinding.selectStartNode.querySelector(`[value="${node.id}"]`) as HTMLOptionElement;
            const endOption = this.elements.toolbox.pathfinding.selectEndNode.querySelector(`[value="${node.id}"]`) as HTMLOptionElement;
            startOption.innerText = endOption.innerText = node.element.label.value;

            this.elements.canvas.appendChild(node.element.div);
            Draggable.Register(node.element.div);
        }

        for (const serializedNode of serializedGraph.nodes)
        {
            const node = this.nodes.get(serializedNode.id)!;
            for (const neighbourNodeID of Object.keys(serializedNode.adjacencyList))
            {
                const key = parseInt(neighbourNodeID);
                if (isNaN(key)) continue;
                const serializedEdges = serializedNode.adjacencyList[key];

                for (const serializedEdge of serializedEdges)
                {
                    const neighbourNode = this.nodes.get(key)!;
                    try
                    {
                        const edge = this.AddEdge(node, neighbourNode, serializedEdge.weight, serializedEdge.id);
                        edge.line!.element.label.value = `${edge.weight}`;
                        edge.label = (<ISerializedUIEdge>serializedEdge).label !== undefined ? (<ISerializedUIEdge>serializedEdge).label : `${serializedEdge.weight}`;
                    }
                    catch (ex)
                    {
                        if (ex instanceof Error && ex.message == `Edge with ID ${serializedEdge.id} already exists.`) continue;
                    }
                }
            }
        }
        //#endregion
    }

    private static PadLeft(str: string, length: number, char: string): string
    {
        while (str.length < length) str = char + str;
        return str;
    }

    private UpdateStylesheet(): void
    {
        this.elements.stylesheet.innerHTML = `*
        {
            --node-radius: ${this.stylesheet.nodeRadius}px;
        }`;

        this.elements.toolbox.editor.inputNodeRadius.value = `${this.stylesheet.nodeRadius}`;

        for (const node of this.nodes.values())
        {
            for (const edges of node.adjacencyDict.values())
            {
                for (const [_, edge] of edges)
                {
                    if (edge.line == null) continue;
                    edge.line.thicknessPX = this.stylesheet.nodeRadius * UIGraph.LINE_THICKNESS_MULTIPLIER;
                    edge.line.Draw();
                }
            }
        }
    }

    private InputNodeRadius_OnInput(): void
    {
        this.stylesheet.nodeRadius = parseInt(this.elements.toolbox.editor.inputNodeRadius.value);
        const uiString = UIGraph.PadLeft(`${this.stylesheet.nodeRadius}`, 2, "0");
        this.elements.toolbox.editor.labelNodeRadius.innerText = `Node radius (${uiString})`;
        this.UpdateStylesheet();
    }

    private InputScale_OnChange(): void
    {
        this.elements.canvas.style.transform = `scale(${this.elements.toolbox.editor.inputScale.value})`;
    }

    private FileBackground_OnClick(e: MouseEvent): void
    {
        //If the alt key was held when pressing the button, remove the background image.
        if (!e.altKey)
            return;
        e.preventDefault();
        this.elements.canvas.style.backgroundImage = "";
    }

    private FileBackground_OnChange(): void
    {
        if (this.elements.toolbox.editor.fileBackground.files == null || this.elements.toolbox.editor.fileBackground.files.length == 0)
            return;

        //Get the image as a base64 string.
        const reader = new FileReader();
        reader.onload = (e) =>
        {
            this.canvasImage = e.target?.result as string;
            this.elements.canvas.style.backgroundImage = `url(${this.canvasImage})`;
        };
        reader.readAsDataURL(this.elements.toolbox.editor.fileBackground.files[0]);

        //Clear the file input.
        this.elements.toolbox.editor.fileBackground.value = "";
    }

    private ButtonSave_OnClick(): void
    {
        //Save the graph to the local disk as "graph_<UNIX_TIMESTAMP>.json".
        const data = JSON.stringify(this.Serialize());
        const blob = new Blob([data], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.download = `graph_${Math.floor(Date.now() / 1000)}.json`;
        link.href = url;

        if (new URLSearchParams(window.location.search).has("run_tests"))
        {
            //If we're running tests, log the data instead saving downloading it.
            console.log(data, JSON.parse(data));
            return;
        }

        link.click();
        link.remove();

        this.hasUnsavedChanges = false;
    }

    private FileLoad_OnChange(): void
    {
        if (this.elements.toolbox.editor.fileLoad.files == null || this.elements.toolbox.editor.fileLoad.files.length == 0)
            return;

        //Load the graph from the local disk.
        const reader = new FileReader();
        reader.onload = (e) =>
        {
            const data = JSON.parse(e.target?.result as string) as IUISerializedGraph;
            this.Deserialize(data);
        }
        reader.readAsText(this.elements.toolbox.editor.fileLoad.files[0]);

        //Clear the file input.
        this.elements.toolbox.editor.fileLoad.value = "";
    }

    private SelectAlgorithm_OnChange(): void
    {
        this.pathfindingOptions.algorithm = EAlgorithm[this.elements.toolbox.pathfinding.selectAlgorithm.value as keyof typeof EAlgorithm];
    }

    private SelectStartNode_OnChange(): void
    {
        const id = parseInt(this.elements.toolbox.pathfinding.selectStartNode.value);
        const node = this.nodes.get(id);
        if (isNaN(id) || node == undefined)
        {
            this.elements.toolbox.pathfinding.selectStartNode.value = "";
            this.pathfindingOptions.startNode = null;
            return;
        }

        this.pathfindingOptions.startNode = node;
    }

    private SelectEndNode_OnChange(): void
    {
        const id = parseInt(this.elements.toolbox.pathfinding.selectEndNode.value);
        const node = this.nodes.get(id);
        if (isNaN(id) || node == undefined)
        {
            this.elements.toolbox.pathfinding.selectEndNode.value = "";
            this.pathfindingOptions.endNode = null;
            return;
        }
        this.pathfindingOptions.endNode = node;
    }

    private static Sleep(milliseconds: number): Promise<void>
    {
        if (milliseconds < 0)
            return Promise.resolve();
        return new Promise(resolve => setTimeout(resolve, milliseconds));
    }

    private ResetColours(): void
    {
        for (const node of this.nodes.values())
        {
            node.element.div.style.borderColor = "black";

            for (const edges of node.adjacencyDict.values())
            {
                for (const [_, edge] of edges)
                {
                    if (edge.line == null) continue;
                    edge.line.color = "black";
                    edge.line.Draw();
                }
            }
        }
    }

    private async RunShortestPathFinder(Finder: () => Promise<IPathPart[]>): Promise<void>
    {
        if (this.pathfindingLock)
            return Promise.resolve();
        this.pathfindingLock = true;
        this.elements.toolbox.pathfinding.buttonFindShortestPath.disabled = true;
        this.elements.toolbox.pathfinding.buttonFindShortestPathNoUI.disabled = true;

        this.ResetColours();

        if (this.pathfindingOptions.startNode == null)
        {
            alert("Invalid start node selected.");
            return Promise.resolve();
        }
        if (this.pathfindingOptions.endNode == null)
        {
            alert("Invalid end node selected.");
            return Promise.resolve();
        }

        if (!GraphSearcher.IsPathAvailable(this, this.pathfindingOptions.startNode, this.pathfindingOptions.endNode, true))
        {
            alert("No path exists between the selected nodes.");
            return Promise.resolve();
        }

        const path = await Finder();
        let weight = 0;
        let uiString = "";
        for (let i = 0; i < path.length; i++)
        {
            const currentPart = path[i];

            let edgeLabel = "";
            if (currentPart.edge != null)
            {
                weight += currentPart.edge.weight;
                edgeLabel = (<UIEdge>currentPart.edge).label != null && (<UIEdge>currentPart.edge).label != "" ?
                    `(via ${(<UIEdge>currentPart.edge).label})` : `(${currentPart.edge.weight})`;
            }

            uiString += (<UINode>currentPart.node).element !== undefined ? (<UINode>currentPart.node).element.label.value : currentPart.node.id.toString();

            if (i < path.length - 1)
                uiString += ` ${edgeLabel}> `;
        }

        const startLabel = (<UINode>this.pathfindingOptions.startNode).element !== undefined ? (<UINode>this.pathfindingOptions.startNode).element.label.value : this.pathfindingOptions.startNode.id.toString();
        const endLabel = (<UINode>this.pathfindingOptions.endNode).element !== undefined ? (<UINode>this.pathfindingOptions.endNode).element.label.value : this.pathfindingOptions.endNode.id.toString();
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

    private async FindShortestPathUI(): Promise<IPathPart[]>
    {
        //TODO: Animate UI colour changes.
        let path: IPathPart[] = [];
        switch (this.pathfindingOptions.algorithm)
        {
            case EAlgorithm.Dijkstra:
                //#region node variables
                let node_currentShortestPath: IDijkstraNode | null = null;
                let node_previousNode: IDijkstraNode | null = null;
                //#endregion
                //#region edge variables
                let edge_currentClosestEdge: UIEdge | null = null;
                let edge_currentClosestEdgeWeight: number = Number.MAX_SAFE_INTEGER;
                let edge_previousNode: UINode | null = null;
                let edge_previousEdge: UIEdge | null = null;
                //#endregion
                const result = await UIDijkstrasAlgorithm.FindShortestPath(this, this.pathfindingOptions.startNode!, this.pathfindingOptions.endNode!,
                    async (dNode) =>
                    {
                        //onCheckingShortestPath.

                        this.elements.toolbox.pathfinding.labelPathfindingInfo.innerText = "Checking the shortest path to node"
                            + ` '${(<UINode>dNode.node).element !== undefined ? (<UINode>dNode.node).element.label.value : dNode.node.id}'...`;

                        //#region Edge cleanup.
                        if (edge_previousNode != null && edge_previousNode.element !== undefined)
                            edge_previousNode.element.div.style.borderColor = "black";

                        if (edge_previousEdge != null && edge_previousEdge.line != undefined)
                        {
                            edge_previousEdge.line.color = "black";
                            edge_previousEdge.line.Draw();
                        }

                        if (edge_currentClosestEdge != null && edge_currentClosestEdge.line != undefined)
                        {
                            edge_currentClosestEdge.line.color = "black";
                            edge_currentClosestEdge.line.Draw();
                        }
                        //#endregion

                        //Skip updating the UI and sleeping if we are checking against a boxed node, or if this is the start node.
                        if (dNode.isBoxed || dNode.previousNode == null)
                            return;

                        if (node_previousNode !== node_currentShortestPath
                            && node_previousNode !== null)
                        {
                            if ((<UINode>node_previousNode.node).element !== undefined)
                                (<UINode>node_previousNode.node).element.div.style.borderColor = "black";

                            if (node_previousNode.previousNode !== null)
                            {
                                for (const [_, edge] of node_previousNode.previousNode.node.adjacencyDict.get(node_previousNode.node.id)!)
                                {
                                    if ((<UIEdge>edge).line == null) continue;
                                    (<UIEdge>edge).line!.color = "black";
                                    (<UIEdge>edge).line!.Draw();
                                }
                            }
                        }

                        const previousUINode = dNode.previousNode.node as UINode;
                        const node = dNode.node as UINode;
                        const edges = previousUINode.adjacencyDict.get(node.id)!;

                        let colour = "yellow";
                        if (node_currentShortestPath == null || dNode.pathWeight < node_currentShortestPath.pathWeight)
                        {
                            if (node_currentShortestPath !== null && node_currentShortestPath.previousNode !== null)
                            {
                                const oldPreviousUINode = node_currentShortestPath.previousNode.node as UINode;
                                const oldNode = node_currentShortestPath.node as UINode;
                                const oldEdges = oldPreviousUINode.adjacencyDict.get(oldNode.id)!;

                                for (const [_, oldEdge] of oldEdges)
                                {
                                    if (oldEdge.line == undefined) continue;
                                    oldEdge.line.color = "black";
                                    oldEdge.line.Draw();
                                }

                                if (oldNode.element !== undefined)
                                    oldNode.element.div.style.borderColor = "black";
                            }

                            node_currentShortestPath = dNode;

                            colour = "orange";
                        }

                        for (const [_, edge] of edges)
                        {
                            if (edge.line == undefined) continue;
                            edge.line.color = colour;
                            edge.line.Draw();
                        }

                        if (node.element !== undefined)
                            node.element.div.style.borderColor = colour;

                        node_previousNode = dNode;

                        await UIGraph.Sleep(this.pathfindingOptions.stepSpeed);
                    },
                    async (dNode) =>
                    {
                        //onNodeBoxed.

                        this.elements.toolbox.pathfinding.labelPathfindingInfo.innerText = "Boxed node"
                            + ` '${(<UINode>dNode.node).element !== undefined ? (<UINode>dNode.node).element.label.value : dNode.node.id}'...`;

                        //#region Node cleanup.
                        if (node_previousNode != null)
                        {
                            if ((<UINode>node_previousNode.node).element !== undefined)
                                (<UINode>node_previousNode.node).element.div.style.borderColor = "black";

                            if (node_previousNode.previousNode !== null)
                            {
                                for (const [_, edge] of node_previousNode.previousNode.node.adjacencyDict.get(node_previousNode.node.id)!)
                                {
                                    if ((<UIEdge>edge).line == null) continue;
                                    (<UIEdge>edge).line!.color = "black";
                                    (<UIEdge>edge).line!.Draw();
                                }
                            }
                        }

                        if (node_currentShortestPath != null)
                        {
                            if ((<UINode>node_currentShortestPath.node).element !== undefined)
                                (<UINode>node_currentShortestPath.node).element.div.style.borderColor = "black";

                            if (node_currentShortestPath.previousNode !== null)
                            {
                                for (const [_, edge] of node_currentShortestPath.previousNode.node.adjacencyDict.get(node_currentShortestPath.node.id)!)
                                {
                                    if ((<UIEdge>edge).line == null) continue;
                                    (<UIEdge>edge).line!.color = "black";
                                    (<UIEdge>edge).line!.Draw();
                                }
                            }
                        }
                        //#endregion

                        const uiNode = dNode.node as UINode;
                        if (uiNode.element !== undefined)
                            uiNode.element.div.style.borderColor = "red";

                        if (dNode.previousNode != null)
                        {
                            const uiEdge = dNode.previousEdge as UIEdge;
                            if (uiEdge.line !== undefined)
                            {
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
                    },
                    async (dNode, dEdgeNode) =>
                    {
                        //onCheckingEdge.

                        this.elements.toolbox.pathfinding.labelPathfindingInfo.innerText = "Checking lightest edge on node"
                            + ` '${(<UINode>dNode.node).element !== undefined ? (<UINode>dNode.node).element.label.value : dNode.node.id}'...`;

                        if (dEdgeNode.isBoxed)
                            return;

                        if (edge_previousEdge != edge_currentClosestEdge && edge_previousEdge !== null && edge_previousEdge.line !== undefined)
                        {
                            edge_previousEdge.line.color = "black";
                            edge_previousEdge.line.Draw();
                        }

                        const uiNode = dEdgeNode.node as UINode;
                        const edges = uiNode.adjacencyDict.get(dNode.node.id)!;

                        let colour = "yellow";
                        for (const [_, edge] of edges)
                        {
                            if (edge.weight < edge_currentClosestEdgeWeight)
                            {
                                if (edge_currentClosestEdge !== null && edge_currentClosestEdge.line !== undefined)
                                {
                                    edge_currentClosestEdge.line.color = "black";
                                    edge_currentClosestEdge.line.Draw();
                                }

                                edge_currentClosestEdge = edge;
                                edge_currentClosestEdgeWeight = edge.weight;

                                colour = "orange";
                            }

                            if (edge.line !== undefined)
                            {
                                edge.line.color = colour;
                                edge.line.Draw();
                            }

                            edge_previousNode = uiNode;
                            edge_previousEdge = edge;
                        }

                        await UIGraph.Sleep(this.pathfindingOptions.stepSpeed);
                    },
                    async (dNode) =>
                    {
                        //onShortestPathFound.

                        this.elements.toolbox.pathfinding.labelPathfindingInfo.innerText = "Shortest path found!";

                        const uiNode = dNode.node as UINode;
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

        //#region Trace sortest path.
        this.ResetColours();
        const startLabel = (<UINode>this.pathfindingOptions.startNode).element !== undefined
            ? (<UINode>this.pathfindingOptions.startNode).element.label.value : this.pathfindingOptions.startNode!.id;
        const endLabel = (<UINode>this.pathfindingOptions.endNode).element !== undefined
            ? (<UINode>this.pathfindingOptions.endNode).element.label.value : this.pathfindingOptions.endNode!.id;
        this.elements.toolbox.pathfinding.labelPathfindingInfo.innerText = `Tracing shortest path from '${startLabel}' to '${endLabel}'...`;
        await UIGraph.Sleep(this.pathfindingOptions.stepSpeed);
        for (let i = 1; i < path.length; i++)
        {
            const currentPart = path[i];
            const previousPart = path[i - 1];

            if (i == 1 && (<UINode>previousPart.node).element !== undefined)
                (<UINode>previousPart.node).element.div.style.borderColor = "green";

            if ((<UIEdge>previousPart.edge).line !== undefined)
            {
                (<UIEdge>previousPart.edge).line!.color = "green";
                (<UIEdge>previousPart.edge).line!.Draw();
            }

            if ((<UINode>currentPart.node).element !== undefined)
                (<UINode>currentPart.node).element.div.style.borderColor = "green";

            await UIGraph.Sleep(this.pathfindingOptions.stepSpeed);
        }
        //#endregion

        return path;
    }

    private async FindShortestPathNoUI(): Promise<IPathPart[]>
    {
        let path: IPathPart[] = [];
        switch (this.pathfindingOptions.algorithm)
        {
            case EAlgorithm.Dijkstra:
                const result = DijkstrasAlgorithm.FindShortestPath(this, this.pathfindingOptions.startNode!, this.pathfindingOptions.endNode!);
                path = DijkstrasAlgorithm.DijkstraNodeToPathArray(result);
                break;
            default:
                alert("Invalid algorithm selected.");
        }
        return path;
    }

    private async ButtonFindPath_OnClick(): Promise<void>
    {
        await this.RunShortestPathFinder(async () => this.FindShortestPathUI());
    }

    private ButtonFindPathNoUI_OnClick(): void
    {
        this.RunShortestPathFinder(async () => this.FindShortestPathNoUI());
    }

    private InputStepSpeed_OnInput(): void
    {
        const value = parseInt(this.elements.toolbox.pathfinding.inputStepSpeed.value);
        this.pathfindingOptions.stepSpeed = value;
        const uiString = UIGraph.PadLeft(`${value}`, 4, "0");
        this.elements.toolbox.pathfinding.labelStepSpeed.innerText = `Step speed (${uiString})`;
    }

    private Canvas_OnClick(e: MouseEvent): void
    {
        //Move the clicked element, if it is a direct child of the canvas, to the top.
        if (e.target instanceof HTMLElement && e.target.parentElement === this.elements.canvas)
            this.elements.canvas.appendChild(e.target);

        this.hasUnsavedChanges = true;

        /* Options:
         * Shift click directly onto the canvas create a node.
         * Click and drag on a node to move it.
         * Shift click a node to draw an edge.
         * Alt click a node or edge to delete it.
         * [Future] Shift click the canvas to move the view.
         */
        if (e.target === this.elements.canvas && e.shiftKey && !e.altKey && this.unconnectedEdge == null)
        {
            //Create node.
            const node = this.AddNode() as UINode;
            //Move these to public methods in UINode?
            node.element.div.style.left = `${e.clientX / parseFloat(this.elements.toolbox.editor.inputScale.value)}px`;
            node.element.div.style.top = `${e.clientY / parseFloat(this.elements.toolbox.editor.inputScale.value)}px`;
            this.elements.canvas.appendChild(node.element.div);
            Draggable.Register(node.element.div);
        }
    }

    private Node_OnClick(e: MouseEvent): void
    {
        if (e.target instanceof HTMLDivElement && e.target.classList.contains("node"))
        {
            //Move these to their node constructors to avoid less DOM querying.
            if (!e.shiftKey && e.altKey)
            {
                //Delete node.
                if (!(e.target instanceof HTMLElement && e.target.classList.contains("node")))
                    return;
                this.RemoveNode(this.nodes.get(parseInt(e.target.id.substring(UINode.ID_PREFIX.length))) as UINode);
            }
            else if (e.shiftKey && !e.altKey)
            {
                //Create edge.
                //To prevent element selection while holding the shift key, deselect all elements.
                //https://stackoverflow.com/questions/6562727/is-there-a-function-to-deselect-all-text-using-javascript
                window.getSelection()?.removeAllRanges();

                if (this.selectedNodeID === -1)
                {
                    //Store the clicked node if possible and wait for another node to be clicked.
                    if (!(e.target instanceof HTMLElement && e.target.classList.contains("node"))) return;
                    this.selectedNodeID = parseInt(e.target.id.substring(UINode.ID_PREFIX.length));

                    //Create a line to visualise the unconnected edge.
                    const node = this.nodes.get(this.selectedNodeID) as UINode;
                    this.unconnectedEdge = new Line();
                    this.unconnectedEdge.thicknessPX = this.stylesheet.nodeRadius * UIGraph.LINE_THICKNESS_MULTIPLIER;
                    this.unconnectedEdge.baseX = node.element.div.offsetLeft;
                    this.unconnectedEdge.baseY = node.element.div.offsetTop;
                    this.unconnectedEdge.clickEvents = false;
                    this.elements.canvas.appendChild(this.unconnectedEdge.element.div);
                }
                else
                {
                    if (!(e.target instanceof HTMLElement && e.target.classList.contains("node"))) return;

                    //Create the edge between the two nodes with an initial weight of 1.
                    this.AddEdge(this.nodes.get(this.selectedNodeID) as UINode,
                        this.nodes.get(parseInt(e.target.id.substring(UINode.ID_PREFIX.length))) as UINode, 1);

                    //Clear the selected node.
                    this.selectedNodeID = -1;
                    this.unconnectedEdge?.Dispose();
                    this.unconnectedEdge = null;
                }
            }
            else
            {
                this.selectedNodeID = -1;
                this.unconnectedEdge?.Dispose();
                this.unconnectedEdge = null;
            }
        }
    }

    private Window_OnBeforeUnload(e: BeforeUnloadEvent): void
    {
        if (this.hasUnsavedChanges)
        {
            e.preventDefault();
            e.returnValue = "false";
        }
    }

    private Document_OnMouseMove(e: MouseEvent): void
    {
        //If there is an unconnected edge present, update it's position.
        if (this.unconnectedEdge !== null)
        {
            this.unconnectedEdge.targetX = e.clientX;
            this.unconnectedEdge.targetY = e.clientY;
            this.unconnectedEdge.Draw();
        }
    }

    //#region https://stackoverflow.com/questions/24826430/javascript-prevent-page-zooming
    private Document_OnWheel(e: WheelEvent): void
    {
        if (!e.ctrlKey) return;
        e.preventDefault();
        this.UpdateScale_Tick(e.deltaY < 0);
    }

    private Document_OnKeyDown(e: KeyboardEvent): void
    {
        if (!e.ctrlKey || !(
            e.key === "+" ||
            e.key === "-" ||
            e.key === "=" ||
            e.key === "_" ||
            e.key === "0"))
            return;
        e.preventDefault();

        switch (e.key)
        {
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

    private UpdateScale_Tick(increase: boolean)
    {
        const tick = 0.1;
        this.UpdateScale((parseFloat(this.elements.toolbox.editor.inputScale.value) + (increase ? tick : -tick)))
    }

    private ScaleToFit(): void
    {
        //#region Scale the canvas to fit the window.
        //https://github.com/ReadieFur/BSDP-Overlay/blob/aa875128ce495deec23aff16af377a66772fc728/src/view/view.ts#L147-L179
        const canvasWidth = 1024; //4
        const canvasHeight = 768; //3
        this.elements.canvas.style.width = `${canvasWidth}px`;
        this.elements.canvas.style.height = `${canvasHeight}px`;
        const clientWiderThanTall = document.body.clientWidth > document.body.clientHeight;
        const scale = !clientWiderThanTall ? document.body.clientWidth / canvasWidth : document.body.clientHeight / canvasHeight;
        this.UpdateScale(scale);
        // this.elements.canvas.style[!clientWiderThanTall ? "width" : "height"] =
        //     `${(!clientWiderThanTall ? document.body.clientWidth : document.body.clientHeight) / scale}px`;
        //#endregion
    }

    private UpdateScale(scale: number)
    {
        const min = 0.1;
        let newScale = Math.round(scale * 100) / 100;
        newScale = Math.max(min, newScale);
        this.elements.toolbox.editor.inputScale.value = newScale.toString();
        this.elements.canvas.style.transform = `scale(${newScale})`;
    }
    //#endregion

    private Document_OnKeyUp(e: KeyboardEvent): void
    {
        //If there is an unconnected edge present and the shift key is released, delete the unconnected edge and clear the selected node.
        if (this.unconnectedEdge !== null && !e.shiftKey)
        {
            this.unconnectedEdge.Dispose();
            this.unconnectedEdge = null;
            this.selectedNodeID = -1;
        }
    }
}
