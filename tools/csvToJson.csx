// #define DO_OCR

#if DO_OCR
#r "nuget: System.Drawing.Common, 5.0.3"
#endif
#r "nuget: Newtonsoft.Json, 12.0.3"
#r "nuget: Tesseract, 4.1.1"
#r "nuget: F23.StringSimilarity, 5.0.0"

#load "./shared.cs"

#nullable enable

using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Text.Json;
using Newtonsoft.Json;
using Tesseract;
using F23.StringSimilarity;

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

List<OCREntry> ocrEntries = new();
#if DO_OCR
TesseractEngine engine = new TesseractEngine(Path.Combine(Environment.CurrentDirectory,
    true ? "tessdata_best-4.1.0" : "tessdata_fast-4.1.0"), "eng", EngineMode.LstmOnly);
Pix image = Pix.LoadFromFile(Path.Combine(Environment.CurrentDirectory, "./standard-tube-map-1.png"));
Image systemImage = Image.FromFile(Path.Combine(Environment.CurrentDirectory, "./standard-tube-map-1.png"));
image.XRes = 2735;
image.YRes = 1909;
using (var page = engine.Process(image, PageSegMode.AutoOsd))
{
    ResultIterator result = page.GetIterator();
    result.Begin();
    PageIteratorLevel pageIteratorLevel = PageIteratorLevel.Word;
    while (result.Next(pageIteratorLevel))
    {
        bool gotRect = result.TryGetBoundingBox(pageIteratorLevel, out Rect rect);
        /*using (var graphics = Graphics.FromImage(systemImage))
        {
            graphics.DrawRectangle(Pens.Red, rect.X1, rect.Y1, rect.Width, rect.Height);
        }*/

        if (!gotRect)
            continue;

        string word = result.GetText(pageIteratorLevel).Trim();

        float confidence = result.GetConfidence(pageIteratorLevel);

        //Console.WriteLine(word);
        //Console.WriteLine(rect);
        //Console.WriteLine(confidence);

        ocrEntries.Add(new()
        {
            Text = word,
            //BoundingBox = new Rectangle(rect.X1, rect.Y1, rect.Width, rect.Height),
            PX = rect.X1,
            PY = rect.Y1,
            Confidence = confidence
        });
    }
}
//Save the ocrEntries to a JSON file.
File.WriteAllText(Path.Combine(Environment.CurrentDirectory, "ocrEntries.json"), JsonConvert.SerializeObject(ocrEntries));
#else
ocrEntries = JsonConvert.DeserializeObject<List<OCREntry>>(File.ReadAllText(Path.Combine(Environment.CurrentDirectory, "ocrEntries.json")));
#endif

//For each CSVEntry, find the closest OCREntry text.
//This matching method isn't the best but it cleans up the data enough that it makes manually cleaning up the data feasible.
List<Entry> entries = new();
foreach (CSVEntry csvEntry in csvEntries)
{
    OCREntry closestEntry = ocrEntries[0];
    float closestDistance = float.MaxValue;
    foreach (OCREntry ocrEntry in ocrEntries)
    {
        float distance = (float)new Levenshtein().Distance(csvEntry.Station.Split(' ')[0], ocrEntry.Text);
        //If the distance is within the margin of the confidence, then we can use this entry.
        if (100 - distance >= ocrEntry.Confidence && distance < closestDistance)
        {
            closestDistance = distance;
            closestEntry = ocrEntry;
        }
    }

    //(int px, int py) = TranslateImagePosToMapPos(closestEntry.BoundingBox.X, closestEntry.BoundingBox.Y);
    // (int px, int py) = TranslateImagePosToMapPos(closestEntry.PX, closestEntry.PY);
    const int mapWidth = 1024;
    const int mapHeight = 768;
    const int imageWidth = 2735;
    const int imageHeight = 1909;
    const int imageSpacingBottom = 53;
    const int imageSpacingRight = 0;
    const int targetWidth = mapWidth - imageSpacingRight;
    const int targetHeight = mapHeight - imageSpacingBottom;

    // int px = (int)Math.Round((double)closestEntry.BoundingBox.X / imageWidth * targetWidth);
    // int py = (int)Math.Round((double)closestEntry.BoundingBox.Y / imageHeight * targetHeight);
    int px = (int)Math.Round((double)closestEntry.PX / imageWidth * targetWidth);
    int py = (int)Math.Round((double)closestEntry.PY / imageHeight * targetHeight);

    entries.Add(new()
    {
        Line = csvEntry.Line,
        Station = csvEntry.Station,
        NextStation = csvEntry.NextStation,
        Weight = csvEntry.Weight,
        PX = px,
        PY = py
    });
}

UIGraph graph = new UIGraph();
graph.canvasImage = File.ReadAllText("./standard-tube-map-1.png.base64");
graph.nodeRadius = 15;

Random random = new(1);
List<long> ids = new();

foreach (Entry entry in entries)
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

foreach (CSVEntry entry in csvEntries)
{
    UINode node = graph.nodes.Find(n => n.label == entry.Station)!;
    UINode? nextNode = graph.nodes.Find(n => n.label == entry.NextStation);
    if (nextNode == null)
        continue;

    Edge edge = new(nextNode.id)
    {
        weight = uint.Parse(entry.Weight)
    };

    node.adjacencyList.Add(edge);
}

string json = JsonConvert.SerializeObject(graph, Formatting.Indented);
Console.WriteLine(json);
File.WriteAllText("./london_underground_data-auto.json", json);

struct OCREntry
{
    public string Text { get; set; }
    //public Rectangle BoundingBox { get; set; }
    public int PX { get; set; }
    public int PY { get; set; }
    public float Confidence { get; set; }
}

struct Entry //: CSVEntry
{
    public string Line { get; set; }
    public string Station { get; set; }
    public string? NextStation { get; set; }
    public string Weight { get; set; }
    public float PX { get; set; }
    public float PY { get; set; }
}
