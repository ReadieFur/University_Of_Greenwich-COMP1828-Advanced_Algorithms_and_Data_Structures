using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using CSVParser.Shared;
using CSVParser.Shared.Core;
using CSVParser.Shared.UI;

#nullable enable
namespace CSVParser
{
    internal class Program
    {
        public static void Main(string[] args)
        {
            while (true)
            {
                Console.WriteLine("1. Parse data");
                Console.WriteLine("2. Patch data");
                Console.WriteLine("3. Exit");
                string userInput = Console.ReadLine();
                switch (userInput.ToLower())
                {
                    case "1":
                        ParseData();
                        break;
                    case "2":
                        PatchData();
                        break;
                    case "3":
                        return;
                    default:
                        Console.WriteLine("Invalid input");
                        break;
                }
            }
        }

        private static void ParseData()
        {
            Console.WriteLine("Do OCR? (y/N)");
            bool doOCR = Console.ReadLine()?.ToLower() == "y";

            List<CSVEntry> entries = CSV.LoadCSV().ToList();

            if (doOCR) entries = OCR.MatchValues(entries, OCR.DoOCR());
            else
            {
                try
                {
                    entries = OCR.MatchValues(entries,
                        JsonConvert.DeserializeObject<List<OCREntry>>(File.ReadAllText("ocrEntries.json"))!);
                }
                catch
                {
                    Console.WriteLine("Couldn't find an existing parsed OCR file, node positions will not be set.");
                }
            }

            UIGraph graph = new();
            graph.canvasImage = File.ReadAllText("./standard-tube-map-1.png.base64");
            graph.nodeRadius = 15;

            Random random = new(1);
            List<long> ids = new();

            foreach (CSVEntry entry in entries)
            {
                UIEntry? uiEntry = entry as UIEntry;

                long id;
                do id = Convert.ToInt64(Math.Floor((double)random.Next(0, int.MaxValue)));
                while (ids.Contains(id));
                ids.Add(id);

                //Look for the station name in the OCR result and get the bounding box.

                UINode node = new(id)
                {
                    px = Convert.ToUInt32(uiEntry?.PX),
                    py = Convert.ToUInt32(uiEntry?.PY),
                    label = entry.Station
                };
                graph.nodes.Add(node);
            }

            foreach (CSVEntry entry in entries)
            {
                string line = entry.Line;
                UINode node = graph.nodes.Find(n => n.label == entry.Station)!;
                UINode? nextNode = graph.nodes.Find(n => n.label == entry.NextStation);
                if (nextNode == null)
                    continue;

                UIEdge edge = new(nextNode.id)
                {
                    weight = uint.Parse(entry.Weight),
                    label = line
                };

                node.adjacencyList.Add(edge);
            }

            //Join duplicate nodes.
            IEnumerable<UINode> duplicateNodes = graph.nodes.GroupBy(n => n.label).Where(g => g.Count() > 1).SelectMany(g => g.Skip(1));
            foreach (UINode duplicateNode in duplicateNodes)
            {
                UINode node = graph.nodes.Find(n => n.label == duplicateNode.label)!;
                foreach (UIEdge edge in duplicateNode.adjacencyList)
                {
                    UINode neighbouringNode = graph.nodes.Find(n => n.id == edge.neighbouringNodeID);
                    long neighbouringNodeID = edge.neighbouringNodeID;
                    if (duplicateNodes.Contains(neighbouringNode))
                        neighbouringNodeID = graph.nodes.Find(n => n.label == neighbouringNode.label)!.id;

                    UIEdge newEdge = new(neighbouringNodeID)
                    {
                        weight = edge.weight,
                        label = edge.label
                    };

                    if (!node.adjacencyList.Any(e =>
                        e.neighbouringNodeID == neighbouringNodeID
                        && e.weight == newEdge.weight
                        && e.label == newEdge.label))
                        node.adjacencyList.Add(newEdge);
                }
            }
            foreach (UINode duplicateNode in duplicateNodes)
                graph.nodes.Remove(duplicateNode);

            string json = JsonConvert.SerializeObject(graph, Formatting.Indented);
            Console.WriteLine(json);
            File.WriteAllText("./london_underground_data-auto.json", json);

        }

        private static void PatchData()
        {
        }
    }
}
