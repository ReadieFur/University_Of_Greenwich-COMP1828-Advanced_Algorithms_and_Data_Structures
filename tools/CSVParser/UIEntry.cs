#nullable enable
using CSVParser.Shared;
using System.Collections.Generic;

namespace CSVParser
{
    public class UIEntry : CSVEntry
    {
        public float PX { get; set; }
        public float PY { get; set; }

        public static List<CSVEntry> ToCSVEntryList(List<UIEntry> uiEntries)
        {
            List<CSVEntry> csvEntries = new();
            foreach (UIEntry uiEntry in uiEntries)
                csvEntries.Add(uiEntry);
            return csvEntries;
        }
    }
}
