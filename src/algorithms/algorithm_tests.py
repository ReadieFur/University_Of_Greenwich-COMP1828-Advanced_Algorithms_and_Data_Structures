from typing import Dict
from time import time
from main import Program
from .algorithm import PathPart
from .graph_searcher import GraphSearcher
from .algorithm import AAlgorithm
from .dijkstras_algorithm import DijkstrasAlgorithm
from .bellman_fords_algorithm_dp import BellmanFordsAlgorithmDP
from core.graph import Graph
from core.node import Node

class _TestHelpers:
    @staticmethod
    def _map_part(labels: Dict[int, str], part: PathPart) -> str:
        label = labels[part.node.id]
        if part.edge is None:
            return label
        return f"{label} ({part.edge.weight})>"

    @staticmethod
    def evaluate_algorithm(graph: Graph, start_node: Node, end_node: Node, algorithm: AAlgorithm, labels: Dict[int, str], expected_result: str) -> None:
        start_time = time()
        result = algorithm.find_shortest_path(graph, start_node, end_node)
        duration = time() - start_time
        shortest_path = str.join(" ", [_TestHelpers._map_part(labels, node) for node in result])
        test_passed = expected_result == shortest_path
        Program.print((f"Expected result: {str(expected_result)}", 'yellow'), end=", ")
        Program.print((f"Actual result: {str(shortest_path)}", 'magenta'), end=", ")
        Program.print(("Test passed: ", 'cyan'), (str(test_passed), 'green' if test_passed else 'red'), end=", ")
        Program.print((f"Duration: {duration * 1000}ms", 'black'))

    @staticmethod
    def algorithm_test1(algorithm: AAlgorithm) -> None:
        print(_TestHelpers.algorithm_test1.__name__)

        graph = Graph()

        a = graph.add_node()
        b = graph.add_node()
        c = graph.add_node()
        d = graph.add_node()

        graph.add_edge(a, b, 1)
        graph.add_edge(a, c, 4)
        graph.add_edge(b, d, 2)
        graph.add_edge(b, d, 1)
        graph.add_edge(c, d, 1)

        LABELS = {
            a.id: "A",
            b.id: "B",
            c.id: "C",
            d.id: "D"
        }

        visual_graph = """
        *     B-----|
        *    / \    |
        *  (1) (2) (1)
        *  /     \  |
        * A       D-|
        *  \     /
        *  (4) (1)
        *    \ /
        *     C
        """
        Program.print((str.join("\n", [line.lstrip() for line in visual_graph.splitlines()]), 'green'))

        #Expected shortest path from A to D is A (1)> B (1)> D.
        _TestHelpers.evaluate_algorithm(graph, a, d, algorithm, LABELS, "A (1)> B (1)> D")

        #Expected shortest path from B to C is B (1)> D (1)> C.
        _TestHelpers.evaluate_algorithm(graph, b, c, algorithm, LABELS, "B (1)> D (1)> C")

    @staticmethod
    def algorithm_test2(algorithm: AAlgorithm) -> None:
        print(_TestHelpers.algorithm_test2.__name__)

        graph = Graph()

        a = graph.add_node()
        b = graph.add_node()
        c = graph.add_node()
        d = graph.add_node()
        e = graph.add_node()
        f = graph.add_node()
        g = graph.add_node()

        #From the example: COMP1828 "Graph 1.pptx" slide 33
        graph.add_edge(a, b, 4)
        graph.add_edge(a, c, 3)
        graph.add_edge(b, d, 1)
        graph.add_edge(b, f, 4)
        graph.add_edge(c, d, 3)
        graph.add_edge(c, e, 5)
        graph.add_edge(d, e, 2)
        graph.add_edge(d, f, 2)
        graph.add_edge(d, g, 7)
        graph.add_edge(e, g, 2)
        graph.add_edge(f, g, 4)

        LABELS = {
            a.id: "A",
            b.id: "B",
            c.id: "C",
            d.id: "D",
            e.id: "E",
            f.id: "F",
            g.id: "G"
        }

        visual_graph = """
        *     B -----(4)----- F
        *    / \            / |
        *  (4)  -(1)-   -(2)  |
        *  /         \ /      |
        * A ---(7)--- D ---  (4)
        *  \          |    \  |
        *  (3)       (2)   (7)|
        *    \        |      \|
        *     C -(5)- E -(2)- G
        """
        Program.print((str.join("\n", [line.lstrip() for line in visual_graph.splitlines()]), 'green'))

        #Expected shortest path from A to G is A (4)> B (1)> D (2)> E (2)> G.
        _TestHelpers.evaluate_algorithm(graph, a, g, algorithm, LABELS, "A (4)> B (1)> D (2)> E (2)> G")

class _GraphSearcherTests:
    @staticmethod
    def run() -> None:
        print(_GraphSearcherTests.__name__)
        _GraphSearcherTests._test1()
        _GraphSearcherTests._test2()

    @staticmethod
    def _test1() -> None:
        print(_GraphSearcherTests._test1.__name__)

        graph = Graph()

        A = graph.add_node()
        B = graph.add_node()
        C = graph.add_node()
        D = graph.add_node()

        graph.add_edge(A, B, 1)
        graph.add_edge(A, C, 1)
        graph.add_edge(B, D, 1)

        visual_graph = """
        *     A
        *    / \\
        *  (1) (1)
        *  /     \\
        * B       C
        *  \\
        *  (1)
        *    \\
        *     D
        """
        Program.print((str.join("\n", [line.lstrip() for line in visual_graph.splitlines()]), 'green'))

        expected_result = True
        bfs_result = GraphSearcher.is_graph_connected(graph, True)
        bsf_passed = expected_result == bfs_result
        Program.print((f"Expected result: {str(expected_result)}", 'yellow'), end=", ")
        Program.print((f"Actual result: {str(bfs_result)}", 'magenta'), end=", ")
        Program.print(("Test passed: ", 'cyan'), (str(bsf_passed), 'green' if bsf_passed else 'red'))

        dfs_result = GraphSearcher.is_graph_connected(graph, False)
        dsf_passed = expected_result == dfs_result
        Program.print((f"Expected result: {str(expected_result)}", 'yellow'), end=", ")
        Program.print((f"Actual result: {str(dfs_result)}", 'magenta'), end=", ")
        Program.print(("Test passed: ", 'cyan'), (str(dsf_passed), 'green' if dsf_passed else 'red'))

    @staticmethod
    def _test2() -> None:
        print(_GraphSearcherTests._test2.__name__)

        graph = Graph()

        A = graph.add_node()
        B = graph.add_node()
        C = graph.add_node()
        D = graph.add_node()

        graph.add_edge(A, B, 1)
        graph.add_edge(A, C, 1)
        # graph.add_edge(B, D, 1)

        visual_graph = """
        *     A
        *    / \\
        *  (1) (1)
        *  /     \\
        * B       C
        *     D
        """
        Program.print((str.join("\n", [line.lstrip() for line in visual_graph.splitlines()]), 'green'))

        expected_result = False
        bfs_result = GraphSearcher.is_graph_connected(graph, True)
        bsf_passed = expected_result == bfs_result
        Program.print((f"Expected result: {str(expected_result)}", 'yellow'), end=", ")
        Program.print((f"Actual result: {str(bfs_result)}", 'magenta'), end=", ")
        Program.print(("Test passed: ", 'cyan'), (str(bsf_passed), 'green' if bsf_passed else 'red'))

        dfs_result = GraphSearcher.is_graph_connected(graph, False)
        dsf_passed = expected_result == dfs_result
        Program.print((f"Expected result: {str(expected_result)}", 'yellow'), end=", ")
        Program.print((f"Actual result: {str(dfs_result)}", 'magenta'), end=", ")
        Program.print(("Test passed: ", 'cyan'), (str(dsf_passed), 'green' if dsf_passed else 'red'))

class _DijkstrasAlgorithmTests:
    @staticmethod
    def run() -> None:
        print(_DijkstrasAlgorithmTests.__name__)
        _TestHelpers.algorithm_test1(DijkstrasAlgorithm)
        _TestHelpers.algorithm_test2(DijkstrasAlgorithm)

class _BellmanFordsAlgorithmTests:
    @staticmethod
    def run() -> None:
        print(_BellmanFordsAlgorithmTests.__name__)
        _TestHelpers.algorithm_test1(BellmanFordsAlgorithmDP)
        _TestHelpers.algorithm_test2(BellmanFordsAlgorithmDP)

class AlgorithmTests:
    @staticmethod
    def run() -> None:
        _GraphSearcherTests.run()
        _DijkstrasAlgorithmTests.run()
        _BellmanFordsAlgorithmTests.run()
