// See https://aka.ms/new-console-template for more information

using RB2Helper;

// Get arguments from command line
foreach (var arg in args)
{
    Console.WriteLine($"Arg: {arg}");
}

Console.WriteLine($"Sports: {args[0]}");

ExcelConverter.Prepare();

ExcelConverter.Action(args[0]);

Console.WriteLine("Hello, World!");
