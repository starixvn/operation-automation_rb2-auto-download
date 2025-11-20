// See https://aka.ms/new-console-template for more information

using RB2Helper;


// Get arguments from command line
foreach (var arg in args)
{
    Console.WriteLine($"Arg: {arg}");
}

if (args.Length <= 0)
{
    args = ["test"];
}

if (args[0] == "test")
{
    await Uploader.UploadFile(@"C:\BG\RB2-12-07-2026tennis.xlsx");
}

else
{
    ExcelMerger.Prepare();
    ExcelMerger.Action(args[0]);
    Zipper.ZipOriginalFile();
    await Uploader.UploadAllFilesToInfoSite();
}


Console.WriteLine("Hello, World!");
