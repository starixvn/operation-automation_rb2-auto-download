// See https://aka.ms/new-console-template for more information

using RB2Helper;

// Get arguments from command line
foreach (var arg in args)
{
    Console.WriteLine($"Arg: {arg}");
}

if (args.Length == 0)
{
    args = ["tennis"];
}

Console.WriteLine($"Sports: {args[0]}");

ExcelMerger.Prepare();

ExcelMerger.Action(args[0]);

Zipper.ZipOriginalFile();

Console.WriteLine("Hello, World!");
