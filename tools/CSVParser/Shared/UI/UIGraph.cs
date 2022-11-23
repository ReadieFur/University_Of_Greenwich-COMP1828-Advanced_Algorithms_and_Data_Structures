using System.Collections.Generic;
using CSVParser.Shared.Core;

#nullable enable
namespace CSVParser.Shared.UI
{
    public class UIGraph : SerializedGraph
    {
        public string? canvasImage = null;
        public int? nodeRadius = null;
        new public List<UINode> nodes = new List<UINode>();
    }
}
