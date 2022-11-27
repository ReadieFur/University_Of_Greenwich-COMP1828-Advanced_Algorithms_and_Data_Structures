import { AlgorithmTests } from "./algorithms/algorithm_tests.js";
import { UITests } from "./ui/ui_tests.js";
import { UIGraph } from "./ui/ui_graph.js";

class Index
{
    private static initailized = false;

    public static Main(): void
    {
        if (Index.initailized) return;
        Index.initailized = true;

        UIGraph.GetInstance();

        if (new URLSearchParams(window.location.search).has("run_tests"))
        {
            AlgorithmTests.Run();
            UITests.Run();
        }
    }
}
Index.Main();
