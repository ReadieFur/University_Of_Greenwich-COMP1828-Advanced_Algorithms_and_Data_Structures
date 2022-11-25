#Because python's module resolution is $H1T I've moved all of the test instantiaters to this file so that the module resolutions don't conflict with how I've setup the main.py file.

from core.graph import Graph, SerializedGraph
from algorithms.algorithm_tests import AlgorithmTests

class JsonTests:
    @staticmethod
    def run() -> None:
        graph = Graph()
        n1 = graph.add_node()
        n2 = graph.add_node()
        graph.add_edge(n1, n2, 1)
        graph.serialize().save_to_file("./test_graph.json")

        loaded_graph = SerializedGraph.load_from_file("./test_graph.json")
        return #This line is here to place a breakpoint on so that I can see the result before the method returns.

if __name__ == "__main__":
    # JsonTests().run()
    AlgorithmTests.run()
    pass
