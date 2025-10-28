using NPOI.HSSF.UserModel;
using NPOI.SS.UserModel;
using NPOI.XSSF.UserModel;
using System.Globalization;
using System.Text;

namespace RB2Helper;

public static class ExcelHelper
{
    public static void CopySheet(
        List<ISheet> sheets,
        ISheet outputXssfSheet,
        XSSFWorkbook outputXssfWorkbook,
        DateTime dateFrom,
        DateTime dateTo)
    {
        var destRowIndex = outputXssfSheet.LastRowNum + 1;
        var rows = GetUniqueRows(sheets);
        foreach (var row in rows)
        {
            var dateCell = row.GetCell(6);
            var dateTime = GetStartTime(dateCell.StringCellValue);

            if (dateTime < dateFrom || dateTime > dateTo)
            {
                continue;
            }

            var playState = row.GetCell(10);
            if (string.Equals(playState.StringCellValue, "Cancelled", StringComparison.CurrentCultureIgnoreCase))
            {
                continue;
            }

            var xssfRow = outputXssfSheet.CreateRow(destRowIndex);
            for (var cellIdx = 0; cellIdx < row.LastCellNum; cellIdx++)
            {
                var hssfCell = row.GetCell(cellIdx);
                if (hssfCell == null)
                {
                    continue;
                }
                var xssfCell = xssfRow.CreateCell(cellIdx);
                CopyCellValue(hssfCell, xssfCell);
                CopyCellStyle(hssfCell, xssfCell, outputXssfWorkbook);
            }

            destRowIndex++;
        }
    }

    public static void CopyRow(
        ISheet inputHssfSheet,
        ISheet outputXssfSheet,
        XSSFWorkbook outputXssfWorkbook,
        int rowIdx,
        int destRowIndex)
    {
        var hssfRow = inputHssfSheet.GetRow(rowIdx);
        if (hssfRow == null)
        {
            return;
        }

        var xssfRow = outputXssfSheet.CreateRow(destRowIndex);
        for (var cellIdx = 0; cellIdx < hssfRow.LastCellNum; cellIdx++)
        {
            var hssfCell = hssfRow.GetCell(cellIdx);
            if (hssfCell != null)
            {
                var xssfCell = xssfRow.CreateCell(cellIdx);
                CopyCellValue(hssfCell, xssfCell);
                CopyCellStyle(hssfCell, xssfCell, outputXssfWorkbook);
            }
        }
    }

    public static void CopyCellValue(ICell sourceCell, ICell targetCell)
    {
        switch (sourceCell.CellType)
        {
            case CellType.Numeric:
                if (DateUtil.IsCellDateFormatted(sourceCell))
                {
                    var dateValue = sourceCell.DateCellValue;
                    if (dateValue.HasValue)
                    {
                        targetCell.SetCellValue(dateValue.Value);
                    }
                }
                else
                {
                    targetCell.SetCellValue(sourceCell.NumericCellValue);
                }
                break;
            case CellType.String:
                targetCell.SetCellValue(sourceCell.StringCellValue);
                break;
            case CellType.Boolean:
                targetCell.SetCellValue(sourceCell.BooleanCellValue);
                break;
            case CellType.Formula:
                targetCell.SetCellFormula(sourceCell.CellFormula);
                break;
            case CellType.Error:
                targetCell.SetCellErrorValue(sourceCell.ErrorCellValue);
                break;
            case CellType.Blank:
                // Leave blank
                break;
            default:
                targetCell.SetCellValue(sourceCell.ToString());
                break;
        }
    }

    public static void CopyCellStyle(ICell sourceCell, ICell targetCell, XSSFWorkbook targetWorkbook)
    {
        CopyCellStyleInternal(sourceCell, targetCell, targetWorkbook, isSourceXlsx: false);
    }

    public static void CopyCellStyleXlsx(ICell sourceCell, ICell targetCell, XSSFWorkbook targetWorkbook)
    {
        CopyCellStyleInternal(sourceCell, targetCell, targetWorkbook, isSourceXlsx: true);
    }

    public static void CopyCellStyleInternal(ICell sourceCell, ICell targetCell, XSSFWorkbook targetWorkbook, bool isSourceXlsx)
    {
        var sourceCellStyle = sourceCell.CellStyle;
        var targetCellStyle = targetWorkbook.CreateCellStyle();

        // Copy alignment
        targetCellStyle.Alignment = sourceCellStyle.Alignment;
        targetCellStyle.VerticalAlignment = sourceCellStyle.VerticalAlignment;
        targetCellStyle.Rotation = sourceCellStyle.Rotation;
        targetCellStyle.WrapText = sourceCellStyle.WrapText;
        targetCellStyle.Indention = sourceCellStyle.Indention;

        // Copy borders
        targetCellStyle.BorderLeft = sourceCellStyle.BorderLeft;
        targetCellStyle.BorderRight = sourceCellStyle.BorderRight;
        targetCellStyle.BorderTop = sourceCellStyle.BorderTop;
        targetCellStyle.BorderBottom = sourceCellStyle.BorderBottom;
        targetCellStyle.LeftBorderColor = sourceCellStyle.LeftBorderColor;
        targetCellStyle.RightBorderColor = sourceCellStyle.RightBorderColor;
        targetCellStyle.TopBorderColor = sourceCellStyle.TopBorderColor;
        targetCellStyle.BottomBorderColor = sourceCellStyle.BottomBorderColor;

        // Copy fill/background
        targetCellStyle.FillPattern = sourceCellStyle.FillPattern;
        targetCellStyle.FillForegroundColor = sourceCellStyle.FillForegroundColor;
        targetCellStyle.FillBackgroundColor = sourceCellStyle.FillBackgroundColor;

        // Copy font - handle both HSSF and XSSF workbooks
        var sourceWorkbook = sourceCell.Sheet.Workbook;
        var sourceFont = isSourceXlsx
            ? sourceWorkbook.GetFontAt(sourceCellStyle.FontIndex)
            : ((HSSFWorkbook)sourceWorkbook).GetFontAt(sourceCellStyle.FontIndex);

        var targetFont = targetWorkbook.CreateFont();
        targetFont.FontName = sourceFont.FontName;
        targetFont.FontHeightInPoints = sourceFont.FontHeightInPoints;
        targetFont.IsBold = sourceFont.IsBold;
        targetFont.IsItalic = sourceFont.IsItalic;
        targetFont.IsStrikeout = sourceFont.IsStrikeout;
        targetFont.Underline = sourceFont.Underline;
        targetFont.Color = sourceFont.Color;
        targetCellStyle.SetFont(targetFont);

        // Copy number format
        targetCellStyle.DataFormat = targetWorkbook.CreateDataFormat().GetFormat(sourceCellStyle.GetDataFormatString());

        // Copy protection
        targetCellStyle.IsLocked = sourceCellStyle.IsLocked;
        targetCellStyle.IsHidden = sourceCellStyle.IsHidden;

        // Apply the style to the target cell
        targetCell.CellStyle = targetCellStyle;
    }



    public static List<DateTime> GetAllDateTime(List<ISheet> sheets)
    {
        var dates = new List<DateTime>();

        foreach (var sheet in sheets)
        {
            for (var rowIdx = 1; rowIdx <= sheet.LastRowNum; rowIdx++)
            {
                var row = sheet.GetRow(rowIdx);
                if (row == null)
                {
                    continue;
                }
                var dateCell = row.GetCell(6);
                var dateTime = GetStartTime(dateCell.StringCellValue);
                if (dateTime != DateTime.MinValue && !dates.Contains(dateTime))
                {
                    dates.Add(dateTime);
                }
            }
        }

        return dates.Select(d => d.Date).Distinct().ToList();
    }


    public static DateTime GetStartTime(string dateString)
    {
        const string dateFormat = "dd.MM.yyyy - HH:mm";

        var success = DateTime.TryParseExact(
            dateString,
            dateFormat,
            CultureInfo.InvariantCulture,
            DateTimeStyles.None,
            out var dtObject
        );

        return success ? dtObject : DateTime.MinValue;
    }


    public static List<IRow> GetUniqueRows(List<ISheet> sheets)
    {
        var rows = new List<IRow>();
        foreach (var sheet in sheets)
        {
            for (var i = 1; i <= sheet.LastRowNum; i++)
            {
                var row = sheet.GetRow(i);
                if (row == null)
                {
                    continue;
                }

                rows.Add(row);
            }
        }

        return GetUniqueRows(rows);
    }

    public static List<IRow> GetUniqueRows(List<IRow> rows)
    {
        return rows.DistinctBy(GetRowContentHash)
            .OrderBy(p => GetStartTime(p.GetCell(6).StringCellValue))
            .ToList();
    }

    private static string GetRowContentHash(IRow row)
    {
        var contentBuilder = new StringBuilder();

        for (var cellIdx = 0; cellIdx < row.LastCellNum; cellIdx++)
        {
            var cell = row.GetCell(cellIdx);
            if (cell == null)
            {
                continue;
            }

            var cellValue = GetCellValueAsString(cell);
            contentBuilder.Append(cellValue);
            contentBuilder.Append('|');
        }

        return contentBuilder.ToString();
    }

    private static string GetCellValueAsString(ICell cell)
    {
        return cell.CellType switch
        {
            CellType.Numeric => DateUtil.IsCellDateFormatted(cell)
                ? cell.DateCellValue?.ToString("O") ?? ""
                : cell.NumericCellValue.ToString(CultureInfo.InvariantCulture),
            CellType.String => cell.StringCellValue,
            CellType.Boolean => cell.BooleanCellValue.ToString(),
            CellType.Formula => cell.CellFormula,
            CellType.Error => cell.ErrorCellValue.ToString(),
            CellType.Blank => "",
            _ => cell.ToString() ?? ""
        };
    }

}