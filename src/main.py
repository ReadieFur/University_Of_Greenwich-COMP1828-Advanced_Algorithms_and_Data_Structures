from typing import List, Callable
import os
from tubemap.core.tubemap_graph import TubemapGraph, SerializedTubemapGraph
from tubemap.core.tubemap_node import TubemapNode
# from algorithms.graph_searcher import GraphSearcher
# from algorithms.dijkstras_algorithm import DijkstrasAlgorithm
from tubemap.algorithms.tubemap_graph_searcher import TubemapGraphSearcher
from tubemap.algorithms.tubemap_dijkstras_algorithm import TubemapDijkstrasAlgorithm

class Program:
    INFO = {
        "name": "Tubemapper",
        "version": "0.1",
        "author": "Tristan Read (ReadieFur)"
    }

    __ALGORITHMS = [
        "dijkstra"
    ]

    __graph: TubemapGraph = None
    __start_node: TubemapNode = None
    __end_node: TubemapNode = None
    __algorithm: int = 0

    @staticmethod
    def Main() -> None:
        Program.__load_graph()
        Program.__cli()

    def __load_graph() -> None:
        """Loads the graph from the file."""
        if not os.path.exists("./tubemap.json"):
            raise FileNotFoundError(f"The tubemap.json graph file was not found in the working directory ({os.getcwd()}).")
        Program.__graph = SerializedTubemapGraph.load_from_file("./tubemap.json")

    def __cli() -> None:
        """The command line interface for the program (also the main loop)."""
        print(f"{Program.INFO['name']} v{Program.INFO['version']} by {Program.INFO['author']}")

        print("Type 'help' for a list of commands.")
        print("Type 'exit' to exit the program.")

        COMMANDS = {
            # "help",
            "list": Program.__command_list,
            "line": Program.__command_line,
            "start": Program.__command_start,
            "end": Program.__command_end,
            "algorithm": Program.__command_algorithm,
            "go": Program.__command_go,
            "exit": Program.__command_exit
        }

        while True:
            command = input("> ").lower()

            command_prefix = command.split(" ")[0]
            #The following splits the remaining args on spaces like the above but joins strings back together between quotes.
            #It does not support nested quotes and I don't have a need to for this project.
            command_args_split = command.split(" ")[1:]
            command_args = []
            i = 0
            current_arg = ""
            while True:
                if i >= len(command_args_split):
                    break
                if command_args_split[i].startswith('"'):
                    current_arg = command_args_split[i][1:]
                    while not command_args_split[i].endswith('"'):
                        i += 1
                        current_arg += f" {command_args_split[i]}"
                    current_arg = current_arg[:-1]
                    command_args.append(current_arg)
                else:
                    command_args.append(command_args_split[i])
                i += 1

            if command_prefix == "help":
                if len(command_args) == 0:
                    print("Command syntax: [required] <optional>")
                    print(f"For help with sub-commands, type: help [command]")
                    print("Commands:")
                    for command in COMMANDS:
                        print(f"{command}")
                else:
                    if command_args[0] not in COMMANDS:
                        print("Invalid command.")
                    else:
                        COMMANDS[command_args[0]](command_args, True)
            elif command_prefix in COMMANDS:
                COMMANDS[command_prefix](command_args)
            else:
                print("Invalid command.")

    def __command_list(args: List[str], show_help: bool = False) -> None:
        """Lists the nodes in the graph."""
        if show_help:
            print("Lists all nodes in the graph with the lines to their neighbours.")
            print("Usage: list")
            return

        buffer: List[(str, str)] = []

        for node in Program.__graph.nodes.values():
            info = [Program.__get_node_tag(node), ""]

            line_buffer = []
            for edge in node.adjacency_list:
                line_buffer.append(Program.__get_node_tag(edge))
            line_buffer.sort()
            info[1] = f"{', '.join(line_buffer)}"

            buffer.append((info[0], info[1]))

        buffer.sort(key=lambda x: x[0])

        longest_station_name = len(max(buffer, key=lambda x: len(x[0]))[0])
        #https://stackoverflow.com/questions/34734572/tabs-in-print-are-not-consistent-python
        string_formatter = f"{{0:<{longest_station_name}}} -> {{1}}"

        for info in buffer:
            print(string_formatter.format(info[0], info[1]))

    def __command_line(args: List[str], show_help: bool = False) -> None:
        """Shows or updates the properties of a line."""
        if show_help:
            print("Shows or updates the properties of a line.")
            print("Usage:")
            print("line info [station1] [station2]\n\tShows if a line is closed or not between the specified stations.")
            print("line open [station1] [station2]\n\tOpens a line.")
            print("line close [station1] [station2]\n\tCloses a line.")

        if len(args) < 3:
            print("Invalid syntax.")
            return

        node1 = Program.__get_node_from_label_or_id(args[1])
        node2 = Program.__get_node_from_label_or_id(args[2])

        if node1 is None:
            print("Invalid first station.")
            return
        if node2 is None:
            print("Invalid second station.")
            return

        edge = node1.adjacency_list.get(node2)
        if edge is None:
            print("Stations do not have a line between them.")
            return

        if args[0] == "info":
            print(f"Line between '{Program.__get_node_tag(node1)}' and '{Program.__get_node_tag(node2)}' is {'closed' if edge.closed else 'open'}.")
        elif args[0] == "open":
            edge.closed = False
            print(f"Line between '{Program.__get_node_tag(node1)}' and '{Program.__get_node_tag(node2)}' is now open.")
        elif args[0] == "close":
            edge.closed = True
            print(f"Line between '{Program.__get_node_tag(node1)}' and '{Program.__get_node_tag(node2)}' is now closed.")
        else:
            print("Invalid syntax.")

    @staticmethod
    def __command_start(args: List[str], show_help = False) -> None:
        """Sets the start node."""
        if show_help:
            print("Sets the station to start at.")
            print("Usage:")
            print("start\n\tShows the current start station.")
            print("start [station]\n\tSets the start station.")
            return

        if len(args) < 1:
            if Program.__start_node is None:
                print("The start station has not been set.")
            else:
                print(f"The start station is '{Program.__get_node_tag(Program.__start_node)}'.")
            return

        node = Program.__get_node_from_label_or_id(args[0])
        if node is None:
            print("Invalid station.")
            return

        Program.__start_node = node
        print(f"Start station set to '{Program.__get_node_tag(node)}'.")

    @staticmethod
    def __command_end(args: List[str], show_help = False) -> None:
        """Sets the end node."""
        if show_help:
            print("Sets the station to end at.")
            print("Usage:")
            print("end\n\tShows the current end station.")
            print("end [station]\n\tSets the end station.")
            return

        if len(args) < 1:
            if Program.__end_node is None:
                print("The end station has not been set.")
            else:
                print(f"The end station is '{Program.__get_node_tag(Program.__end_node)}'.")
            return

        node = Program.__get_node_from_label_or_id(args[0])
        if node is None:
            print("Invalid station.")
            return

        Program.__end_node = node
        print(f"End station set to '{Program.__get_node_tag(node)}'.")

    @staticmethod
    def __command_algorithm(args: List[str], show_help = False) -> None:
        """Sets the algorithm to use."""
        if show_help:
            print("Sets the algorithm to use.")
            print("Usage:")
            print("algorithm\n\tShows the current algorithm.")
            print("algorithm [algorithm]\n\tSets the algorithm.")
            print("Algorithms:")
            for algorithm in Program.__ALGORITHMS:
                print(f"\t{algorithm}")
            return

        if len(args) < 1:
            print(f"The current algorithm is '{Program.__ALGORITHMS[Program.__algorithm]}'.")
            return

        if args[0].lower() not in Program.__ALGORITHMS:
            print("Invalid algorithm.")
            return

        Program.__algorithm = args.index(args[0].lower())
        print(f"Algorithm set to '{Program.__ALGORITHMS[Program.__algorithm]}'.")

    @staticmethod
    def __command_go(args: List[str], show_help = False) -> None:
        """Finds the shortest path between the set start and end nodes using the specified algorithm."""
        if show_help:
            print("Finds the shortest path between the set start and end nodes using the specified algorithm.")
            print("Usage: calculate")

        if Program.__start_node is None:
            print("The start station has not been set.")
            return
        elif Program.__end_node is None:
            print("The end station has not been set.")
            return

        # if not GraphSearcher.is_path_available(Program.__start_node, Program.__end_node, True):
        if not TubemapGraphSearcher.is_path_available(Program.__start_node, Program.__end_node):
            print("No path is available between the start and end stations.")
            return

        weight = 0
        node_array = []

        if Program.__algorithm == 0:
            # dijkstra_node = DijkstrasAlgorithm.find_shortest_path(Program.__graph, Program.__start_node, Program.__end_node)
            dijkstra_node = TubemapDijkstrasAlgorithm.find_shortest_path(Program.__graph, Program.__start_node, Program.__end_node)
            weight = dijkstra_node.path_weight
            node_array = TubemapDijkstrasAlgorithm.dijkstra_node_to_node_array(dijkstra_node)

        buffer = []
        for node in node_array:
            buffer.append(Program.__get_node_tag(node))
        path_string = " -> ".join(buffer)

        print(f"The shortest path from '{Program.__get_node_tag(Program.__start_node)}' to '{Program.__get_node_tag(Program.__end_node)}', with a duration of {weight} minutes, is: {path_string}")

    @staticmethod
    def __command_exit(args: List[str], show_help = False) -> None:
        """Exits the program."""
        if show_help:
            print("Exits the program.")
            print("Usage: exit")
        else:
            exit()

    @staticmethod
    def __get_node(predicate: Callable[[TubemapNode], bool]) -> TubemapNode:
        """Finds the first node in a graph matching against a predicate."""
        for node in Program.__graph.nodes.values():
            if predicate(node):
                return node
        return None

    @staticmethod
    def __get_node_from_label_or_id(tag: str) -> TubemapNode:
        """Finds the first node in a graph matching against a label or ID."""
        return Program.__get_node(lambda node: node.label.strip().lower() == tag.lower() or node.id == tag)

    @staticmethod
    def __get_node_tag(node: TubemapNode) -> str:
        """Gets the tag of a node."""
        return (node.label if node.label != "" else node.id).strip()

if __name__ == "__main__":
    Program.Main()
