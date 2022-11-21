namespace CSVParser
{
    public struct OCREntry
    {
        public string Text { get; set; }
        //public Rectangle BoundingBox { get; set; }
        public int PX { get; set; }
        public int PY { get; set; }
        public float Confidence { get; set; }
    }
}
