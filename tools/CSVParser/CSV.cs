using System.Collections.Generic;
using System.IO;
using CSVParser.Shared;

#nullable enable
namespace CSVParser
{
    internal class CSV
    {
        public static IEnumerable<CSVEntry> LoadCSV(string path = "./london_underground_data.csv")
        {
            foreach (string fileLine in File.ReadAllLines(path))
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

                yield return new()
                {
                    Line = line,
                    Station = station,
                    NextStation = nextStation,
                    Weight = weight
                };
            }
        }
    }
}
