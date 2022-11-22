#define NO_CLI

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
using System.Diagnostics;
using CSVParser.Patchers;

#nullable enable
namespace CSVParser
{
    internal class Program
    {
        public static void Main(string[] args)
        {
#if !NO_CLI
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
#else
            //ParseData();
            PatchData();
#endif
        }

        private static void Bayswater(UIGraph graph)
        {
            var a = graph.nodes.Where(n => n.label == "Bayswater"
                || n.adjacencyList.Any(a => graph.nodes.Find(en => en.id == a.neighbouringNodeID)?.label == "Bayswater")).ToList();
        }

        private static void ParseData()
        {
#if !NO_CLI
            Console.WriteLine("Do OCR? (y/N)");
            bool doOCR = Console.ReadLine()?.ToLower() == "y";
#else
            bool doOCR = false;
#endif

            List<CSVEntry> csvEntries = CSV.LoadCSV().ToList();
            
            List<UIEntry> entries;
            if (doOCR)
                entries = OCR.MatchValues(csvEntries, OCR.DoOCR()).ToList();
            else
                //OCR must have been run at least once if this this statment is reached.
                entries = OCR.MatchValues(csvEntries, JsonConvert.DeserializeObject<List<OCREntry>>(File.ReadAllText("ocrEntries.json"))!).ToList();

            var a = entries.Where(e => e.Station == "Bayswater" || e.NextStation == "Bayswater").ToList();

            UIGraph graph = new();
            graph.canvasImage = File.ReadAllText("./standard-tube-map-1.png.base64");
            graph.nodeRadius = 15;

            Random random = new(1);
            List<long> ids = new();

            foreach (UIEntry entry in entries)
            {
                long id;
                do id = Convert.ToInt64(Math.Floor((double)random.Next(0, int.MaxValue)));
                while (ids.Contains(id));
                ids.Add(id);

                //Look for the station name in the OCR result and get the bounding box.

                UINode node = new(id)
                {
                    px = Convert.ToUInt32(entry.PX),
                    py = Convert.ToUInt32(entry.PY),
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

            //Remove the nodes that have no edges.
            graph.nodes.RemoveAll(n => n.adjacencyList.Count == 0);

            string json = JsonConvert.SerializeObject(graph, Formatting.Indented);
            Console.WriteLine(json);
            File.WriteAllText("./london_underground_data-auto.json", json);
        }

        private static void PatchData()
        {
            UIPatcher.Patch();
        }
    }
}
