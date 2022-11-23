from typing import Any, List, Callable, Tuple
import os
from tubemap.core.tubemap_graph import TubemapGraph, SerializedTubemapGraph
from tubemap.core.tubemap_node import TubemapNode
from tubemap.core.tubemap_edge import TubemapEdge
from tubemap.algorithms.tubemap_graph_searcher import TubemapGraphSearcher
from tubemap.algorithms.tubemap_dijkstras_algorithm import TubemapDijkstrasAlgorithm

class Program:
    INFO = {
        "name": "Tubemapper",
        "version": "0.3",
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
        Program.print((Program.INFO['name'], 'magenta'), (f" v{Program.INFO['version']}", 'cyan'), " by", (f" {Program.INFO['author']}", 'green'))

        Program.print("Type ", (f"'help'", 'yellow'), " for a list of commands.")
        Program.print("Type ", (f"'exit'", 'yellow'), " to exit the program.")

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
            # command = input(f"{Program.get_colour_string('yellow')}>{Program.get_colour_string()} ").lower()
            command = input(Program.build_coloured_string(("> ", 'yellow'))).lower()

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
                    Program.print("Command syntax: ", (f"[required]", 'magenta'), " ", (f"<optional>", 'cyan'))
                    Program.print("For help with sub-commands, type: ", (f"help", 'yellow'), " ", (f"[command]", 'magenta'))
                    Program.print("Commands:")
                    for command in COMMANDS:
                        Program.print(f"- ", (f"{command}", 'yellow'))
                else:
                    if command_args[0] not in COMMANDS:
                        Program.print((f"Invalid command.", 'red'))
                    else:
                        COMMANDS[command_args[0]](command_args, True)
            elif command_prefix in COMMANDS:
                COMMANDS[command_prefix](command_args)
            else:
                Program.print((f"Invalid command.", 'red'))

    def __command_list(args: List[str], show_help: bool = False) -> None:
        """Lists the nodes in the graph."""
        if show_help:
            Program.print("Lists all nodes in the graph with the lines to their neighbours.")
            Program.print("Usage: ", (f"list", 'yellow'))
            return

        buffer: List[(str, str)] = []

        for node in Program.__graph.nodes.values():
            info = [Program.build_coloured_string((Program.__get_tag(node), 'green')), ""]

            line_buffer = []
            for neibouring_node_id, edges in node.adjacency_dict.items():
                neibouring_node = Program.__graph.nodes[neibouring_node_id]
                neighbour_string = Program.build_coloured_string((Program.__get_tag(neibouring_node), 'green'))

                neighbour_string += f" (via"
                for edge in edges.values():
                    neighbour_string += Program.build_coloured_string((f" {Program.__get_tag(edge)}", 'cyan'), ",")
                neighbour_string = f"{neighbour_string[:-1]})"

                line_buffer.append(neighbour_string)

            line_buffer.sort()
            info[1] = f"{', '.join(line_buffer)}"

            buffer.append((info[0], info[1]))

        buffer.sort(key=lambda x: x[0])

        longest_station_name = len(max(buffer, key=lambda x: len(x[0]))[0])
        #https://stackoverflow.com/questions/34734572/tabs-in-print-are-not-consistent-python
        string_formatter = f"{{0:<{longest_station_name}}} -> {{1}}"

        for info in buffer:
            Program.print(string_formatter.format(info[0], info[1]))

    def __command_line(args: List[str], show_help: bool = False) -> None:
        """Shows or updates the properties of a line."""
        if show_help:
            Program.print("Shows or updates the properties of a line.")
            Program.print("Usage:")
            Program.print(("line info", 'yellow'), (" [station1] [station2] [line]", 'magenta'), "\n\tShows if a line is closed or not between the specified stations.")
            Program.print(("line open", 'yellow'), (" [station1] [station2] [line]", 'magenta'), "\n\tOpens a line.")
            Program.print(("line close", 'yellow'), (" [station1] [station2] [line]", 'magenta'), "\n\tCloses a line.")

        if len(args) < 3:
            Program.print((f"Invalid syntax.", 'red'))
            return

        node1 = Program.__get_node_from_label_or_id(args[1])
        node2 = Program.__get_node_from_label_or_id(args[2])

        if node1 is None:
            Program.print((f"Invalid first station.", 'red'))
            return
        if node2 is None:
            Program.print((f"Invalid second station.", 'red'))
            return

        if node2.id not in node1.adjacency_dict:
            Program.print((f"The two stations are not connected.", 'red'))
            return

        edge = Program.__get_edge_from_label_or_id(node1, node2, args[3])
        if edge is None:
            Program.print((f"The two stations do not have a connection on the specified line.", 'red'))
            return

        node1_tag = Program.__get_tag(node1)
        node2_tag = Program.__get_tag(node2)
        edge_tag = Program.__get_tag(edge)

        prefix = Program.build_coloured_string("The Line between ", (f"'{node1_tag}'", 'green'), " and ", (f"'{node2_tag}'", 'green'), " via ", (f"'{edge_tag}'", 'green'), " is")
        if args[0] == "info":
            Program.print(f"{prefix} ", ("closed" if edge.closed else "open", 'cyan'), ".")
        elif args[0] == "open":
            edge.closed = False
            Program.print(f"{prefix} now ", ("open", 'cyan'), ".")
        elif args[0] == "close":
            edge.closed = True
            Program.print(f"{prefix} now ", ("closed", 'cyan'), ".")
        else:
            Program.print((f"Invalid syntax.", 'red'))

    @staticmethod
    def __command_start(args: List[str], show_help = False) -> None:
        """Sets the start node."""
        if show_help:
            Program.print("Sets the station to start at.")
            Program.print("Usage:")
            Program.print(("start", 'yellow'), "\n\tShows the current start station.")
            Program.print(("start", 'yellow'), (" [station]", 'magenta'), "\n\tSets the start station.")
            return

        if len(args) < 1:
            if Program.__start_node is None:
                Program.print((f"The start station has not been set.", 'red'))
            else:
                Program.print("The start station is ", (f"'{Program.__get_tag(Program.__start_node)}'", 'green'), ".")
            return

        node = Program.__get_node_from_label_or_id(args[0])
        if node is None:
            Program.print((f"Invalid station.", 'red'))
            return

        Program.__start_node = node
        Program.print("The start station is now ", (f"'{Program.__get_tag(Program.__start_node)}'", 'green'), ".")

    @staticmethod
    def __command_end(args: List[str], show_help = False) -> None:
        """Sets the end node."""
        if show_help:
            Program.print("Sets the station to end at.")
            Program.print("Usage:")
            Program.print(("end", 'yellow'), "\n\tShows the current end station.")
            Program.print(("end", 'yellow'), (" [station]", 'magenta'), "\n\tSets the end station.")
            return

        if len(args) < 1:
            if Program.__end_node is None:
                Program.print((f"The end station has not been set.", 'red'))
            else:
                Program.print("The end station is ", (f"'{Program.__get_tag(Program.__end_node)}'", 'green'), ".")
            return

        node = Program.__get_node_from_label_or_id(args[0])
        if node is None:
            Program.print((f"Invalid station.", 'red'))
            return

        Program.__end_node = node
        Program.print("The end station is now ", (f"'{Program.__get_tag(Program.__end_node)}'", 'green'), ".")

    @staticmethod
    def __command_algorithm(args: List[str], show_help = False) -> None:
        """Sets the algorithm to use."""
        if show_help:
            Program.print("Sets the algorithm to use.")
            Program.print("Usage:")
            Program.print(("algorithm", 'yellow'), "\n\tShows the current algorithm.")
            Program.print(("algorithm", 'yellow'), (" [algorithm]", 'magenta'), "\n\tSets the algorithm.")
            Program.print("Algorithms:")
            for algorithm in Program.__ALGORITHMS:
                Program.print((f"- {algorithm}", 'cyan'))
            return

        if len(args) < 1:
            Program.print("The current algorithm is ", (f"'{Program.__ALGORITHMS[Program.__algorithm]}'", 'green'), ".")
            return

        if args[0].lower() not in Program.__ALGORITHMS:
            Program.print((f"Invalid algorithm.", 'red'))
            return

        Program.__algorithm = args.index(args[0].lower())
        Program.print("The algorithm is now ", (f"'{Program.__ALGORITHMS[Program.__algorithm]}'", 'green'), ".")

    @staticmethod
    def __command_go(args: List[str], show_help = False) -> None:
        """Finds the shortest route between the set start and end nodes using the specified algorithm."""
        if show_help:
            Program.print("Finds the shortest route between the set start and end nodes using the specified algorithm.")
            Program.print("Usage:", ("go", 'yellow'))
            return

        if Program.__start_node is None:
            Program.print((f"The start station has not been set.", 'red'))
            return
        elif Program.__end_node is None:
            Program.print((f"The end station has not been set.", 'red'))
            return
        elif Program.__start_node == Program.__end_node:
            Program.print((f"The start and end stations are the same.", 'red'))
            return

        # if not GraphSearcher.is_path_available(Program.__start_node, Program.__end_node, True):
        if not TubemapGraphSearcher.is_path_available(Program.__graph, Program.__start_node, Program.__end_node):
            Program.print((f"No route is available between the start and end stations.", 'red'))
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
        path_string = Program.build_coloured_string("Start at ", (f"'{Program.__get_tag(path_part_array[0].node)}'", 'cyan'), " on the ", (f"'{Program.__get_tag(path_part_array[0].edge)}'", 'cyan'), " line.\n")
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
                    path_string += Program.build_coloured_string(f"Ride ", (f"{stops_between_lines}", 'cyan'), f" {'stop' if stops_between_lines == 1 else 'stops'} to ", (f"'{Program.__get_tag(current_part.node)}'", 'cyan'), ".\n")
                    path_string += Program.build_coloured_string("Change to the ", (f"'{edge_tag}'", 'cyan'), " line.\n")
                    current_line = edge_tag
                    stops_between_lines = 0

                stops_between_lines += 1
        #endregion

        #region Last node
        path_string += Program.build_coloured_string(f"Ride ", (f"{stops_between_lines}", 'cyan'), f" {'stop' if stops_between_lines == 1 else 'stops'} to ", (f"'{Program.__get_tag(path_part_array[len(path_part_array) - 1].node)}'", 'cyan'), " where you will arrive at your destination.")
        #endregion

        Program.print("The shortest route from ", (f"'{Program.__get_tag(Program.__start_node)}'", 'green'), " to ", (f"'{Program.__get_tag(Program.__end_node)}'", 'green'), " has a duration of ", (weight, 'green'), f" minutes.\n{path_string}")

    @staticmethod
    def __command_clear(args: List[str], show_help = False) -> None:
        """Clears the console."""
        if show_help:
            Program.print("Clears the console.")
            Program.print("Usage:", ("clear", 'yellow'))
            return

        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def __command_exit(args: List[str], show_help = False) -> None:
        """Exits the program."""
        if show_help:
            Program.print("Exits the program.")
            Program.print("Usage:", ("exit", 'yellow'))
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

    @staticmethod
    def build_coloured_string(*items: Tuple[Any, str] | str) -> str:
        """Builds a string with colour."""
        string = ""
        for item in items:
            if isinstance(item, tuple):
                string += f"{Program.get_colour_string(item[1])}{item[0]}{Program.get_colour_string()}"
            else:
                string += item
        return string

    @staticmethod
    def print(*items: Tuple[Any, str] | str, end: str = "\n") -> None:
        """Prints a string with colour."""
        print(Program.build_coloured_string(*items), end = end)

if __name__ == "__main__":
    Program.Main()
