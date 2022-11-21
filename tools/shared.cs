#r "nuget: Newtonsoft.Json, 12.0.3"

#nullable enable

using System;
using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;

public static class Shared
{
    public static List<CSVEntry> GetCSVEntries()
    {
        List<CSVEntry> csvEntries = new();
        foreach (string fileLine in File.ReadAllLines("./london_underground_data.csv"))
        {
            string[] parts = fileLine.Split(',');
            if (parts.Length != 4)
                continue;

            string? line = parts[0];
            string? station = parts[1];
            string? nextStation = parts[2];
            string? weight = parts[3];

            if (string.IsNullOrEmpty(weight))
                continue;

            csvEntries.Add(new()
            {
                Line = line,
                Station = station,
                NextStation = nextStation,
                Weight = weight
            });
        }
        return csvEntries;
    }
}

public struct CSVEntry
{
    public string Line { get; set; }
    public string Station { get; set; }
    public string? NextStation { get; set; }
    public string Weight { get; set; }
}

//https://github.com/ReadieFur/GraphBuilder
public class Graph
{
    public List<Node> nodes = new List<Node>();
}

public class UIGraph : Graph
{
    public string? canvasImage = null;
    public int? nodeRadius = null;
    new public List<UINode> nodes = new List<UINode>();
}

public class Node
{
    public long id;
    public List<Edge> adjacencyList = new List<Edge>();

    public Node(long id)
    {
        this.id = id;
    }
}

public class UINode : Node
{
    public uint px = 0;
    public uint py = 0;
    public string label = "";
    new public List<UIEdge> adjacencyList = new List<UIEdge>();

    public UINode(long id) : base(id) {}
}

public class Edge
{
    public long neighbouringNodeID;
    public uint weight = 1;

    public Edge(long id)
    {
        this.neighbouringNodeID = id;
    }
}

class UIEdge : Edge
{
    public string label { get; set; }

    public UIEdge(long neighbouringNodeID) : base(neighbouringNodeID) {}
}
