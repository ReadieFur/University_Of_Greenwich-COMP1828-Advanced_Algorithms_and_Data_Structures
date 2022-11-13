from typing import List
import os
from tubemap.tubemap_graph import TubemapGraph, SerializedTubemapGraph
from tubemap.tubemap_node import TubemapNode

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
        if not os.path.exists("./src/tubemap.json"):
            raise FileNotFoundError("The tubemap.json graph file was not found in './src/'.")
        Program.__graph = SerializedTubemapGraph.load_from_file("./src/tubemap.json")

    def __cli() -> None:
        """The command line interface for the program (also the main loop)."""
        print(f"{Program.INFO['name']} v{Program.INFO['version']} by {Program.INFO['author']}")

        print("Type 'help' for a list of commands.")
        print("Type 'exit' to exit the program.")

        COMMANDS = {
            # "help",
            "list": Program.__command_list,
            "line": Program.__command_line,
            "from": Program.__command_from,
            "to": Program.__command_to,
            "algorithm": Program.__command_algorithm,
            "calculate": Program.__command_calculate,
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
                    print("Command syntax: <required> [optional]")
                    print(f"For help with sub-commands, type: help [command]")
                    print("Commands:")
                    for command in COMMANDS:
                        print(f"- {command}")
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
            print("Lists the nodes in the graph.")
            print("Usage: list")
            return

        for node in Program.__graph.nodes.values():
            print(f"- {node.id}")

    def __command_line(args: List[str], show_help: bool = False) -> None:
        """Shows or updates the properties of a line."""
        if show_help:
            print("Shows or updates the properties of a line.")
            print("Usage:")
            print("line info [station1] [station2]\n\tShows if a line is closed or not between the specified stations.")
            print("line open [station1] [station2]\n\tOpens a line.")
            print("line close [station1] [station2]\n\tCloses a line.")
            return

    @staticmethod
    def __command_from(args: List[str], show_help = False) -> None:
        """Sets the start node."""
        if show_help:
            print("Sets the start node.")
            print("Usage: from <node>")
            return

    @staticmethod
    def __command_to(args: List[str], show_help = False) -> None:
        """Sets the end node."""
        if show_help:
            print("Sets the end node.")
            print("Usage: to <node>")
            return

    @staticmethod
    def __command_algorithm(args: List[str], show_help = False) -> None:
        """Sets the algorithm to use."""
        if show_help:
            print("Sets the algorithm to use.")
            print("Usage: algorithm <algorithm>")
            print("Algorithms:")
            for algorithm in Program.__ALGORITHMS:
                print(f"- {algorithm}")
            return

    @staticmethod
    def __command_calculate(args: List[str], show_help = False) -> None:
        """Calculates the shortest path between the start and end nodes."""
        if show_help:
            print("Calculates the shortest path between the start and end nodes.")
            print("Usage: calculate")
            return

    @staticmethod
    def __command_exit(args: List[str], show_help = False) -> None:
        """Exits the program."""
        if show_help:
            print("Exits the program.")
            print("Usage: exit")
        else:
            exit()

if __name__ == "__main__":
    Program.Main()
