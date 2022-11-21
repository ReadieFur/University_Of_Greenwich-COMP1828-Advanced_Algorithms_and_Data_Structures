using CSVParser.Shared.Core;

namespace CSVParser.Shared.UI
{
    public class UIEdge : Edge
    {
        public string label { get; set; }

        public UIEdge(long neighbouringNodeID) : base(neighbouringNodeID) {}
    }
}
