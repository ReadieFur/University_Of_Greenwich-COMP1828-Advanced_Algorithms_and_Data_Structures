from typing import List, Callable
import os
from tubemap.core.tubemap_graph import TubemapGraph, SerializedTubemapGraph
from tubemap.core.tubemap_node import TubemapNode
from tubemap.core.tubemap_edge import TubemapEdge
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
        print(f"{Program.get_colour_string('magenta')}{Program.INFO['name']} {Program.get_colour_string('cyan')}v{Program.INFO['version']}{Program.get_colour_string()} by {Program.get_colour_string('green')}{Program.INFO['author']}{Program.get_colour_string()}")

        print(f"Type {Program.get_colour_string('yellow')}'help'{Program.get_colour_string()} for a list of commands.")
        print(f"Type {Program.get_colour_string('yellow')}'exit'{Program.get_colour_string()} to exit the program.")

        COMMANDS = {
            # "help",
            "list": Program.__command_list,
            "line": Program.__command_line,
            "start": Program.__command_start,
            "end": Program.__command_end,
            "algorithm": Program.__command_algorithm,
            "go": Program.__command_go,
            "clear": Program.__command_clear,
            "exit": Program.__command_exit
        }

        while True:
            command = input(f"{Program.get_colour_string('yellow')}>{Program.get_colour_string()} ").lower()

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
                    print(f"Command syntax: {Program.get_colour_string('magenta')}[required]{Program.get_colour_string()} {Program.get_colour_string('cyan')}<optional>{Program.get_colour_string()}")
                    print(f"For help with sub-commands, type: {Program.get_colour_string('yellow')}help{Program.get_colour_string()} {Program.get_colour_string('magenta')}[command]{Program.get_colour_string()}")
                    print("Commands:")
                    for command in COMMANDS:
                        print(f"- {Program.get_colour_string('yellow')}{command}{Program.get_colour_string()}")
                else:
                    if command_args[0] not in COMMANDS:
                        print(f"{Program.get_colour_string('red')}Invalid command.{Program.get_colour_string()}")
                    else:
                        COMMANDS[command_args[0]](command_args, True)
            elif command_prefix in COMMANDS:
                COMMANDS[command_prefix](command_args)
            else:
                print(f"{Program.get_colour_string('red')}Invalid command.{Program.get_colour_string()}")

    def __command_list(args: List[str], show_help: bool = False) -> None:
        """Lists the nodes in the graph."""
        if show_help:
            print("Lists all nodes in the graph with the lines to their neighbours.")
            print(f"Usage: {Program.get_colour_string('yellow')}list{Program.get_colour_string()}")
            return

        buffer: List[(str, str)] = []

        for node in Program.__graph.nodes.values():
            info = [f"{Program.get_colour_string('green')}{Program.__get_tag(node)}{Program.get_colour_string()}", ""]

            line_buffer = []
            for neibouring_node_id, edges in node.adjacency_dict.items():
                neibouring_node = Program.__graph.nodes[neibouring_node_id]
                neighbour_string = f"{Program.get_colour_string('green')}{Program.__get_tag(neibouring_node)}"

                neighbour_string += f" {Program.get_colour_string()}(via"
                for edge in edges.values():
                    neighbour_string += f" {Program.get_colour_string('cyan')}{Program.__get_tag(edge)}{Program.get_colour_string()},"
                neighbour_string = f"{neighbour_string[:-1]}){Program.get_colour_string()}"

                line_buffer.append(neighbour_string)

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
            print(f"{Program.get_colour_string('yellow')}line info {Program.get_colour_string('magenta')}[station1] [station2] [line]{Program.get_colour_string()}\n\tShows if a line is closed or not between the specified stations.")
            print(f"{Program.get_colour_string('yellow')}line open {Program.get_colour_string('magenta')}[station1] [station2] [line]{Program.get_colour_string()}\n\tOpens a line.")
            print(f"{Program.get_colour_string('yellow')}line close {Program.get_colour_string('magenta')}[station1] [station2] [line]{Program.get_colour_string()}\n\tCloses a line.")

        if len(args) < 3:
            print("Invalid syntax.")
            return

        node1 = Program.__get_node_from_label_or_id(args[1])
        node2 = Program.__get_node_from_label_or_id(args[2])

        if node1 is None:
            print(f"{Program.get_colour_string('red')}Invalid first station.{Program.get_colour_string()}")
            return
        if node2 is None:
            print(f"{Program.get_colour_string('red')}Invalid second station.{Program.get_colour_string()}")
            return

        if node2.id not in node1.adjacency_dict:
            print(f"{Program.get_colour_string('red')}The two stations are not connected.{Program.get_colour_string()}")
            return

        edge = Program.__get_edge_from_label_or_id(node1, node2, args[3])
        if edge is None:
            print(f"{Program.get_colour_string('red')}The two stations do not have a connection on the specified line.{Program.get_colour_string()}")
            return

        node1_tag = Program.__get_tag(node1)
        node2_tag = Program.__get_tag(node2)
        edge_tag = Program.__get_tag(edge)

        prefix = f"The Line between {Program.get_colour_string('green')}'{node1_tag}'{Program.get_colour_string()} and {Program.get_colour_string('green')}'{node2_tag}'{Program.get_colour_string()} via {Program.get_colour_string('green')}'{edge_tag}'{Program.get_colour_string()} is"
        if args[0] == "info":
            print(f"{prefix} {Program.get_colour_string('cyan')}{'closed' if edge.closed else 'open'}.")
        elif args[0] == "open":
            edge.closed = False
            print(f"{prefix} now {Program.get_colour_string('cyan')}open.")
        elif args[0] == "close":
            edge.closed = True
            print(f"{prefix} now {Program.get_colour_string('cyan')}closed.")
        else:
            print(f"{Program.get_colour_string('red')}Invalid syntax.")
        print(Program.get_colour_string(), end="")

    @staticmethod
    def __command_start(args: List[str], show_help = False) -> None:
        """Sets the start node."""
        if show_help:
            print("Sets the station to start at.")
            print("Usage:")
            print(f"{Program.get_colour_string('yellow')}start{Program.get_colour_string()}\n\tShows the current start station.")
            print(f"{Program.get_colour_string('yellow')}start {Program.get_colour_string('magenta')}[station]{Program.get_colour_string()}\n\tSets the start station.")
            return

        if len(args) < 1:
            if Program.__start_node is None:
                print(f"{Program.get_colour_string('red')}The start station has not been set.")
            else:
                print(f"The start station is {Program.get_colour_string('green')}'{Program.__get_tag(Program.__start_node)}'.")
            print(Program.get_colour_string(), end="")
            return

        node = Program.__get_node_from_label_or_id(args[0])
        if node is None:
            print(f"{Program.get_colour_string('red')}Invalid station.{Program.get_colour_string()}")
            return

        Program.__start_node = node
        print(f"Start station set to {Program.get_colour_string('green')}'{Program.__get_tag(node)}'{Program.get_colour_string()}.")

    @staticmethod
    def __command_end(args: List[str], show_help = False) -> None:
        """Sets the end node."""
        if show_help:
            print("Sets the station to end at.")
            print("Usage:")
            print(f"{Program.get_colour_string('yellow')}end{Program.get_colour_string()}\n\tShows the current end station.")
            print(f"{Program.get_colour_string('yellow')}end{Program.get_colour_string()} {Program.get_colour_string('magenta')}[station]{Program.get_colour_string()}\n\tSets the end station.")
            return

        if len(args) < 1:
            if Program.__end_node is None:
                print(f"{Program.get_colour_string('red')}The end station has not been set.")
            else:
                print(f"The end station is {Program.get_colour_string('green')}'{Program.__get_tag(Program.__end_node)}'.")
            print(Program.get_colour_string(), end="")
            return

        node = Program.__get_node_from_label_or_id(args[0])
        if node is None:
            print(f"{Program.get_colour_string('red')}Invalid station.{Program.get_colour_string()}")
            return

        Program.__end_node = node
        print(f"End station set to {Program.get_colour_string('green')}'{Program.__get_tag(node)}'{Program.get_colour_string()}.")

    @staticmethod
    def __command_algorithm(args: List[str], show_help = False) -> None:
        """Sets the algorithm to use."""
        if show_help:
            print("Sets the algorithm to use.")
            print("Usage:")
            print(f"{Program.get_colour_string('yellow')}algorithm{Program.get_colour_string()}\n\tShows the current algorithm.")
            print(f"{Program.get_colour_string('yellow')}algorithm {Program.get_colour_string('magenta')}[algorithm]{Program.get_colour_string()}\n\tSets the algorithm.")
            print("Algorithms:")
            for algorithm in Program.__ALGORITHMS:
                print(f"- {Program.get_colour_string('cyan')}{algorithm}{Program.get_colour_string()}")
            return

        if len(args) < 1:
            print(f"The current algorithm is {Program.get_colour_string('green')}'{Program.__ALGORITHMS[Program.__algorithm]}'{Program.get_colour_string()}.")
            return

        if args[0].lower() not in Program.__ALGORITHMS:
            print(f"{Program.get_colour_string('red')}Invalid algorithm.{Program.get_colour_string()}")
            return

        Program.__algorithm = args.index(args[0].lower())
        print(f"Algorithm set to {Program.get_colour_string('green')}'{Program.__ALGORITHMS[Program.__algorithm]}'{Program.get_colour_string()}.")

    @staticmethod
    def __command_go(args: List[str], show_help = False) -> None:
        """Finds the shortest route between the set start and end nodes using the specified algorithm."""
        if show_help:
            print("Finds the shortest route between the set start and end nodes using the specified algorithm.")
            print(f"Usage: {Program.get_colour_string('yellow')}go{Program.get_colour_string()}")
            return

        if Program.__start_node is None:
            print(f"{Program.get_colour_string('red')}The start station has not been set.{Program.get_colour_string()}")
            return
        elif Program.__end_node is None:
            print(f"{Program.get_colour_string('red')}The end station has not been set.{Program.get_colour_string()}")
            return
        elif Program.__start_node == Program.__end_node:
            print(f"{Program.get_colour_string('red')}The start and end stations are the same.{Program.get_colour_string()}")
            return

        # if not GraphSearcher.is_path_available(Program.__start_node, Program.__end_node, True):
        if not TubemapGraphSearcher.is_path_available(Program.__graph, Program.__start_node, Program.__end_node):
            print(f"{Program.get_colour_string('red')}No route is available between the start and end stations.{Program.get_colour_string()}")
            return

        path_part_array = []
        if Program.__algorithm == 0:
            path_part_array = TubemapDijkstrasAlgorithm.find_shortest_path(Program.__graph, Program.__start_node, Program.__end_node)

        weight = 0
        path_string = ""
        current_line = ""
        stops_between_lines = 0

        #region Build the path string
        #region First node
        path_string += f"Start at {Program.get_colour_string('cyan')}'{Program.__get_tag(path_part_array[0].node)}'{Program.get_colour_string()} on the {Program.get_colour_string('cyan')}'{Program.__get_tag(path_part_array[0].edge)}'{Program.get_colour_string()} line.\n"
        current_line = Program.__get_tag(path_part_array[0].edge)
        stops_between_lines += 1
        #endregion

        #region Middle nodes
        for i in range(1, len(path_part_array) - 1):
            current_part = path_part_array[i]

            if current_part.edge is not None:
                weight += current_part.edge.weight

                edge_tag = Program.__get_tag(current_part.edge)
                if current_line != edge_tag:
                    path_string += f"Ride {Program.get_colour_string('cyan')}{stops_between_lines}{Program.get_colour_string()} {'stop' if stops_between_lines == 1 else 'stops'} to {Program.get_colour_string('cyan')}'{Program.__get_tag(current_part.node)}'{Program.get_colour_string()}.\n"
                    path_string += f"Change to the {Program.get_colour_string('cyan')}{Program.get_colour_string('cyan')}'{edge_tag}'{Program.get_colour_string()}{Program.get_colour_string()} line.\n"
                    current_line = edge_tag
                    stops_between_lines = 0

                stops_between_lines += 1
        #endregion

        #region Last node
        path_string += f"Ride {Program.get_colour_string('cyan')}{stops_between_lines}{Program.get_colour_string()} stops to {Program.get_colour_string('cyan')}'{Program.__get_tag(path_part_array[len(path_part_array) - 1].node)}'{Program.get_colour_string()} where you will arrive at your destination."
        #endregion

        print(f"The shortest route from {Program.get_colour_string('green')}'{Program.__get_tag(Program.__start_node)}'{Program.get_colour_string()} to {Program.get_colour_string('green')}'{Program.__get_tag(Program.__end_node)}{Program.get_colour_string()}' has a duration of {Program.get_colour_string('green')}{weight}{Program.get_colour_string()} minutes.\n{path_string}")

    @staticmethod
    def __command_clear(args: List[str], show_help = False) -> None:
        """Clears the console."""
        if show_help:
            print("Clears the console.")
            print(f"Usage: {Program.get_colour_string('yellow')}clear{Program.get_colour_string()}")
            return

        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def __command_exit(args: List[str], show_help = False) -> None:
        """Exits the program."""
        if show_help:
            print("Exits the program.")
            print(f"Usage: {Program.get_colour_string('yellow')}exit{Program.get_colour_string()}")
        else:
            exit()

    @staticmethod
    def __get_node(predicate: Callable[[TubemapNode], bool]) -> TubemapNode | None:
        """Finds the first node in a graph matching against a predicate."""
        for node in Program.__graph.nodes.values():
            if predicate(node):
                return node
        return None

    @staticmethod
    def __get_node_from_label_or_id(tag: str) -> TubemapNode | None:
        """Finds the first node in a graph matching against a label or ID."""
        return Program.__get_node(lambda node: node.label.strip().lower() == tag.lower() or node.id == tag)

    @staticmethod
    def __get_edge_from_label_or_id(node1: TubemapNode, node2: TubemapNode, tag: str) -> TubemapEdge | None:
        """Finds the first edge between two nodes matching against a label or ID."""
        for edge in node1.adjacency_dict[node2.id].values():
            if edge.label.strip().lower() == tag.lower() or edge.id == tag:
                return edge
        return None

    @staticmethod
    def __get_tag(item: TubemapNode | TubemapEdge) -> str:
        """Gets the tag of a node."""
        return (item.label if item.label != "" else str(item.id)).strip()

    @staticmethod
    def get_colour_string(foreground: str | None = None, background: str | None = None, effect: str | None = None) -> str:
        """Gets a colour string for use in the console."""
        #https://ozzmaker.com/add-colour-to-text-in-python/
        PREFIX = "\033["
        COLOURS = {
            "default": 0,
            "black": 30,
            "red": 31,
            "green": 32,
            "yellow": 33,
            "blue": 34,
            "magenta": 35,
            "cyan": 36,
            "white": 37
        }
        TEXT_EFFECTS = {
            "default": 0,
            "bold": 1,
            "underline": 2,
            "italic": 3,
            "inverse": 4,
            "strikethrough": 9
        }

        foreground_id = COLOURS[foreground] if foreground is not None else COLOURS["default"]
        background_id = COLOURS[background] + 10 if background is not None else COLOURS["default"] + 10
        effect_id = TEXT_EFFECTS[effect] if effect is not None else TEXT_EFFECTS["default"]

        return f"{PREFIX}{effect_id};{foreground_id};{background_id}m"

if __name__ == "__main__":
    Program.Main()
