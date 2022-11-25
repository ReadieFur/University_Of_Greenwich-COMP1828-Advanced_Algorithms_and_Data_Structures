from typing import Any, List, Callable, Tuple
import os
from time import time
from tubemap.core.tubemap_graph import TubemapGraph, SerializedTubemapGraph
from tubemap.core.tubemap_node import TubemapNode
from tubemap.core.tubemap_edge import TubemapEdge
from algorithms.algorithm import AAlgorithm
from algorithms.dijkstras_algorithm import DijkstrasAlgorithm
from algorithms.bellman_fords_algorithm_dp import BellmanFordsAlgorithmDP
from tubemap.algorithms.tubemap_graph_searcher import TubemapGraphSearcher
from tubemap.algorithms.tubemap_dijkstras_algorithm import TubemapDijkstrasAlgorithm
from tubemap.algorithms.tubemap_bellman_fords_algorithm_dp import TubemapBellmanFordsAlgorithmDP

class Program:
    INFO = {
        "name": "Tubemapper",
        "version": "0.6.3",
        "author": "Tristan Read (ReadieFur)"
    }

    __ALGORITHMS = [
        "Dijkstra",
        "Bellman Ford DP"
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
                    Program.print("For any argument that requires a space in it, surround it with double quotes (e.g.", (' "', 'yellow'), ("argument", 'cyan'), ('"', 'yellow'), ").")
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
            Program.print("Lists all nodes in the graph with the lines to their neighbors.")
            Program.print("Usage:")
            Program.print((f"list", 'yellow'))
            Program.print(("line", 'yellow'), (" <station>...", 'cyan'), "\n\tLists the neighboring stations and their lines of the specified station(s).")
            return

        nodes: List[TubemapNode] = []
        if len(args) == 0:
            nodes = Program.__graph.nodes.values()
        else:
            for arg in args:
                node = Program.__get_node_from_label_or_id(arg)
                if node is None:
                    Program.print((f"Invalid station", 'red'), (f" '{arg}'", 'green'), (f".", 'red'))
                    continue
                nodes.append(node)

        if len(nodes) == 0:
            Program.print((f"No stations found.", 'red'))
            return

        buffer: List[(str, str)] = []
        for node in nodes:
            station_str = Program.build_coloured_string((Program.__get_tag(node), 'green'))

            line_buffer = []
            for neighboring_node_id, edges in node.adjacency_dict.items():
                neighboring_node = Program.__graph.nodes[neighboring_node_id]
                neighbor_string = Program.build_coloured_string((Program.__get_tag(neighboring_node), 'green'))

                neighbor_string += f" (via"
                for edge in edges.values():
                    neighbor_string += Program.build_coloured_string((f" {Program.__get_tag(edge)}", 'cyan'), ",")
                neighbor_string = f"{neighbor_string[:-1]})"

                line_buffer.append(neighbor_string)

            line_buffer.sort()
            buffer.append((station_str, ', '.join(line_buffer)))

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
            Program.print(("line info", 'yellow'), (" [station1] [station2]", 'magenta'), "\n\tShows a histogram of the times it takes to travel between the two stations using all possible lines.")
            Program.print(("line info", 'yellow'), (" [station1] [station2] [line]", 'magenta'), "\n\tShows if a line is closed or not between the specified stations.")
            Program.print(("line open", 'yellow'), (" [station1] [station2] [line]", 'magenta'), "\n\tOpens a line.")
            Program.print(("line close", 'yellow'), (" [station1] [station2] [line]", 'magenta'), "\n\tCloses a line.")
            return

        if len(args) < 3:
            Program.print((f"Invalid syntax.", 'red'))
            return

        node1 = Program.__get_node_from_label_or_id(args[1])
        node2 = Program.__get_node_from_label_or_id(args[2])

        if node1 is None:
            Program.print((f"Invalid first station.", 'red'))
            return
        elif node2 is None:
            Program.print((f"Invalid second station.", 'red'))
            return
        elif node2.id not in node1.adjacency_dict:
            Program.print((f"The two stations are not connected.", 'red'))
            return

        if args[0] == "info" and len(args) == 3:
            Program.print("Histogram of times between ", (f"{Program.__get_tag(node1)}", 'green'), " and ", (f"{Program.__get_tag(node2)}", 'green'), ":")
            histogram_data = [(Program.__get_tag(edge), edge.weight) for edge in node1.adjacency_dict[node2.id].values()]
            #Sort the entries by their tag and then by their weight in descending order.
            histogram_data = sorted(sorted(histogram_data, key=lambda x: x[0]), key=lambda x: x[1], reverse=True)
            Program.__display_histogram(histogram_data, "Line", "Time (minutes)")
        elif len(args) == 4:
            edge = Program.__get_edge_from_label_or_id(node1, node2, args[3])
            if edge is None:
                Program.print((f"The two stations do not have a connection on the specified line.", 'red'))
                return

            node1_tag = Program.__get_tag(node1)
            node2_tag = Program.__get_tag(node2)
            edge_tag = Program.__get_tag(edge)

            prefix = Program.build_coloured_string("The Line between", (f" '{node1_tag}'", 'green'), " and", (f" '{node2_tag}'", 'green'), " via", (f" '{edge_tag}'", 'cyan'), " is")
            if args[0] == "info":
                info_str = f"{prefix} "
                if edge.closed:
                    info_str += Program.build_coloured_string(("closed", 'red'))
                else:
                    info_str += Program.build_coloured_string(("open", 'green'), " and will take ", (f"{edge.weight}", 'cyan'), " minutes to travel between")
                Program.print(info_str, ".")
            elif args[0] == "open":
                edge.closed = False
                Program.print(f"{prefix} now ", ("open", 'green'), ".")
            elif args[0] == "close":
                edge.closed = True
                if not TubemapGraphSearcher.is_path_available(Program.__graph, node1, node2):
                    edge.closed = False
                    Program.print(("The Line between", 'red'), (f" '{node1_tag}'", 'green'), (" and", 'red'), (f" '{node2_tag}'", 'green'), (" via", 'red'), (f" '{edge_tag}'", 'cyan'), (" cannot be closed as it would cause one of the stations to be unreachable.", 'red'))
                else:
                    Program.print(f"{prefix} now ", ("closed", 'red'), ".")
            else:
                Program.print((f"Invalid syntax.", 'red'))
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
            Program.print(("algorithm list", 'yellow'), "\n\tLists the available algorithms.")
            Program.print(("algorithm", 'yellow'), (" [algorithm]", 'magenta'), "\n\tSets the algorithm.")
            return

        algorithms_lower = [algorithm.lower() for algorithm in Program.__ALGORITHMS]

        if len(args) < 1:
            Program.print("The current algorithm is", (f" '{Program.__ALGORITHMS[Program.__algorithm]}'", 'green'), ".")
        elif args[0] == "list":
            Program.print("Available algorithms:")
            for algorithm in Program.__ALGORITHMS:
                Program.print("-", (f" {algorithm}", 'cyan'))
        elif args[0].lower() in algorithms_lower:
            Program.__algorithm = algorithms_lower.index(args[0].lower())
            Program.print("The algorithm is now", (f" '{Program.__ALGORITHMS[Program.__algorithm]}'", 'green'), ".")
        else:
            Program.print((f"Invalid algorithm.", 'red'))

    @staticmethod
    def __command_go(args: List[str], show_help = False) -> None:
        """Finds the shortest route between the set start and end nodes using the specified algorithm."""
        if show_help:
            Program.print("Finds the shortest route between the set start and end nodes using the specified algorithm.")
            Program.print("Usage: ", ("go", 'yellow'))
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

        if not TubemapGraphSearcher.is_path_available(Program.__graph, Program.__start_node, Program.__end_node):
            Program.print((f"No route is available between the start and end stations.", 'red'))
            return

        base_algorithm: AAlgorithm = None
        tubemap_algorithm: AAlgorithm = None
        if Program.__algorithm == 0:
            base_algorithm = DijkstrasAlgorithm
            tubemap_algorithm = TubemapDijkstrasAlgorithm
        elif Program.__algorithm == 1:
            base_algorithm = BellmanFordsAlgorithmDP
            tubemap_algorithm = TubemapBellmanFordsAlgorithmDP

        calculation_start_time = time()
        optimal_path_part_array = base_algorithm.find_shortest_path(Program.__graph, Program.__start_node, Program.__end_node)
        tubemap_path_part_array = tubemap_algorithm.find_shortest_path(Program.__graph, Program.__start_node, Program.__end_node)
        calculation_duration = time() - calculation_start_time
        if "debug" in args:
            Program.print((f"Calculation took {calculation_duration * 1000:.2f}ms.", 'black'))

        optimal_path_weight = 0
        tubemap_path_weight = 0
        path_string = ""
        current_line = ""
        stops_between_lines = 0

        #region Build the path string
        #region First node
        path_string = Program.build_coloured_string("Start at ", (f"'{Program.__get_tag(tubemap_path_part_array[0].node)}'", 'green'), ".\n")
        current_line = Program.__get_tag(tubemap_path_part_array[0].edge)
        stops_between_lines += 1
        #endregion

        #region Middle nodes
        for i in range(1, len(tubemap_path_part_array) - 1):
            current_part = tubemap_path_part_array[i]

            if current_part.edge is not None:
                tubemap_path_weight += current_part.edge.weight

                edge_tag = Program.__get_tag(current_part.edge)
                if current_line != edge_tag:
                    path_string += Program.build_coloured_string(f"Ride", (f" {stops_between_lines}", 'cyan'), f" {'stop' if stops_between_lines == 1 else 'stops'} to", (f" '{Program.__get_tag(current_part.node)}'", 'green'), " via the", (f" '{current_line}'", 'cyan'), " line.\n")
                    current_line = edge_tag
                    stops_between_lines = 0

                stops_between_lines += 1

        for i in range(1, len(optimal_path_part_array) - 1):
            current_part = optimal_path_part_array[i]
            if current_part.edge is not None:
                optimal_path_weight += current_part.edge.weight
        #endregion

        #region Last node
        path_string += Program.build_coloured_string(f"Ride ", (f"{stops_between_lines}", 'cyan'), f" {'stop' if stops_between_lines == 1 else 'stops'} to ", (f"'{Program.__get_tag(tubemap_path_part_array[len(tubemap_path_part_array) - 1].node)}'", 'green'), " via the", (f" '{current_line}'", 'cyan'), " line, where you will arrive at your destination.")
        #endregion

        #Print the summary.
        Program.print("The route from ", (f"'{Program.__get_tag(Program.__start_node)}'", 'green'), " to ", (f"'{Program.__get_tag(Program.__end_node)}'", 'green'), " has a duration of ", (f"{tubemap_path_weight} minutes", 'cyan'), f".")

        #If there were line closures, print a message saying that the optimal route may not be available.
        if tubemap_path_weight != optimal_path_weight:
            Program.print((f"Due to some line closures, the journey will take", 'red'), (f" {tubemap_path_weight - optimal_path_weight} minutes", 'cyan'), (f" longer than the most optimal route", 'red'), (f" ({optimal_path_weight} minutes)", 'green'), (f".", 'red'))

        #Print the route.
        Program.print(path_string)

        #Display a histogram showing the time taken between stations.
        Program.print("Histogram of times between each previous station:")
        histogram_data: List[Tuple[str, int]] = []
        for i in range(len(tubemap_path_part_array)):
            current_station = Program.__get_tag(tubemap_path_part_array[i].node)
            previous_edge = 0 if tubemap_path_part_array[i - 1].edge is None else tubemap_path_part_array[i - 1].edge.weight
            histogram_data.append((current_station, previous_edge))
        Program.__display_histogram(histogram_data, "Station", "Time between previous station (minutes)")

    @staticmethod
    def __command_clear(args: List[str], show_help = False) -> None:
        """Clears the console."""
        if show_help:
            Program.print("Clears the console.")
            Program.print("Usage: ", ("clear", 'yellow'))
            return

        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def __command_exit(args: List[str], show_help = False) -> None:
        """Exits the program."""
        if show_help:
            Program.print("Exits the program.")
            Program.print("Usage: ", ("exit", 'yellow'))
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

    @staticmethod
    def __display_histogram(entries: List[Tuple[str, int]], header1: str, header2: str) -> None:
            MAX_WIDTH = 80
            MAX_TAG_LENGTH = 20
            MIN_PADDING = 2

            """Histogram layout:
            Top row is the time labels from smallest_weight to largest_weight.
            The graph is offset to the right by the length of longest_tag + " | ".
            The rest of the rows have their edge right aligned to the | and their weight bar following it.
            The second is the edge with the longest weight.
            The last is the edge with the shortest weight.
            ---
                Line   |                Time
                       | smallest_weight ... largest_weight
                   tag | ==================================
                   ... | ================...
            len(edges) | ======...
            """

            longest_label = max(len(header1) + 1, min(MAX_TAG_LENGTH, len(max(entries, key=lambda x: len(x[0]))[0])))
            largest_value = max(entries, key=lambda x: x[1])[1]
            smallest_value = min(0, min(entries, key=lambda x: x[1])[1])
            remaining_width = MAX_WIDTH - (longest_label + 3)

            #region Build the histogram.
            #region Header
            #Offset the graph by the length of longest_tag and then add " | ".
            #For this specific use case, we won't expect the weights to be any largest than 100.
            #Use an increment pattern where the first digit is always 1, 2, 5, in increments of 10 each iteration.
            #This isn't perfect and will break on small MAX_WIDTHs, but it's good enough for this use case.
            fine_step = (largest_value + abs(smallest_value)) / remaining_width
            #Now find the closest step from the pattern above that is larger than the fine step.
            step = 0
            i = 0 #The iteration of 1, 2 or 5 we are on.
            j = 0 #The multiplier modifier.
            space_between_steps = 0
            steps = 0
            largest_digit_count = max(len(str(largest_value)), len(str(smallest_value)))
            #If the space_between_steps is less than MIN_PADDING then we need to increase the step size.
            while step < fine_step or space_between_steps < MIN_PADDING:
                multiplier = 10 ** j
                if i == 0:
                    step = 1
                elif i == 1:
                    step = 2
                elif i == 2:
                    step = 5
                    j += 1
                step *= multiplier
                i = (i + 1) % 3
                #Now we have the step size, calculate how many steps we need to fit in the MAX_WIDTH between smallest_weight and largest_weight.
                #(This is required to be calculated within this loop because we need this value for knowing if the step space is valid).
                steps = int((largest_value + abs(smallest_value)) / step)
                #If the step size multiplied by the number of steps is less than largest_weight then we need to add another step.
                if step * steps < largest_value:
                    steps += 1
                #We need to take into account how many digits the largest step is when calculating the space between steps.
                space_between_steps = int(remaining_width / steps) - largest_digit_count
            #Now we can build the header...
            #We must manually add the first.
            subheader = f"{smallest_value}"
            for i in range(steps):
                next_step = str(smallest_value + (i + 1) * step)
                #We need to make sure that the header parts keep the same offset regardless of the number of digits in the step.
                #This is done by adding spaces after the label to keep the offset.
                subheader += f"{next_step:>{space_between_steps + (len(next_step) - largest_digit_count)}}"

            #We need to know where the graph ends so we know where to set the max bar width to and to properly center align the sub-header.
            #We can "cheat" (as opposed to calculating it mathematically) in getting this value by taking the header and trimming the right side.
            graph_width = len(subheader.rstrip())

            #Add the headers.
            #Sub-headers should be center aligned with their corresponding column.
            header1 = header1.rjust((longest_label // 2) + (len(header1) // 2) + 1).ljust(longest_label)
            header2 = header2.rjust((graph_width // 2) + (len(header2) // 2))
            Program.print((header1, 'magenta'), " | ", (header2, 'magenta'))

            Program.print(" " * longest_label + " | ", (subheader, 'magenta'))
            #endregion

            #Body
            for entry in entries:
                tag = entry[0]
                if len(tag) > longest_label:
                    tag = tag[:longest_label - 3].rstrip().rstrip(".") + "..."
                tag = Program.build_coloured_string((tag.rjust(longest_label), 'green'))

                #For the bar size, we need to convert the range of smallest_weight to largest_weight into a range of 0 to graph_width.
                bar = Program.build_coloured_string(("=" * (((entry[1] - smallest_value) * graph_width) // (largest_value - smallest_value)), 'cyan'))

                Program.print(f"{tag} | {bar}")
            #endregion
            #endregion

if __name__ == "__main__":
    Program.Main()
