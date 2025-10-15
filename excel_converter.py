"""
Excel Converter Module
Chuyển đổi file Excel từ định dạng XLS sang XLSX

Các chức năng chính:
1. convert_xls_to_xlsx() - Chuyển đổi một file XLS thành XLSX
2. convert_multiple_xls_files() - Chuyển đổi nhiều file XLS trong thư mục
3. convert_and_replace_xls() - Chuyển đổi và tự động xóa file gốc
4. convert_and_replace_multiple_xls() - Chuyển đổi nhiều file và tự động xóa file gốc

Ví dụ sử dụng:
    # Chuyển đổi một file (giữ lại file gốc)
    result = convert_xls_to_xlsx('data.xls', 'data.xlsx')
    
    # Chuyển đổi một file và xóa file gốc
    result = convert_xls_to_xlsx('data.xls', 'data.xlsx', delete_original=True)
    
    # Hoặc sử dụng hàm tiện ích
    result = convert_and_replace_xls('data.xls', 'data.xlsx')
    
    # Chuyển đổi tất cả file XLS trong thư mục và xóa file gốc
    results = convert_and_replace_multiple_xls('/path/to/xls/files')

Sử dụng từ command line:
    python excel_converter.py input.xls output.xlsx --delete-original
"""

import os
import pandas as pd
from pathlib import Path
import logging

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def convert_xls_to_xlsx(input_file_path, output_file_path=None, delete_original=False):
    """
    Chuyển đổi file XLS thành XLSX
    
    Args:
        input_file_path (str): Đường dẫn đến file XLS cần chuyển đổi
        output_file_path (str, optional): Đường dẫn file XLSX đầu ra.
                                        Nếu None, sẽ tự động tạo tên file mới.
        delete_original (bool): Có xóa file gốc sau khi chuyển đổi thành công hay không.
                              Mặc định là False.
    
    Returns:
        str: Đường dẫn đến file XLSX đã được tạo, hoặc None nếu có lỗi
        
    Raises:
        FileNotFoundError: Khi file input không tồn tại
        ValueError: Khi file input không đúng định dạng XLS
        Exception: Các lỗi khác trong quá trình chuyển đổi
    """
    try:
        # Kiểm tra file input có tồn tại không
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"File không tồn tại: {input_file_path}")
        
        # Kiểm tra extension của file input
        input_path = Path(input_file_path)
        if input_path.suffix.lower() != '.xls':
            raise ValueError(f"File input phải có định dạng .xls, nhận được: {input_path.suffix}")
        
        # Tạo đường dẫn output nếu không được cung cấp
        if output_file_path is None:
            output_file_path = str(input_path.with_suffix('.xlsx'))
        
        logger.info(f"Bắt đầu chuyển đổi: {input_file_path} -> {output_file_path}")
        
        # Đọc file XLS
        try:
            # Sử dụng engine 'xlrd' để đọc file .xls
            df = pd.read_excel(input_file_path, engine='xlrd')
            logger.info(f"Đã đọc thành công file XLS với {len(df)} dòng dữ liệu")
        except Exception as e:
            logger.error(f"Lỗi khi đọc file XLS: {str(e)}")
            raise Exception(f"Không thể đọc file XLS: {str(e)}")
        
        # Ghi ra file XLSX
        try:
            df.to_excel(output_file_path, index=False, engine='openpyxl')
            logger.info(f"Đã ghi thành công file XLSX: {output_file_path}")
        except Exception as e:
            logger.error(f"Lỗi khi ghi file XLSX: {str(e)}")
            raise Exception(f"Không thể ghi file XLSX: {str(e)}")
        
        # Kiểm tra file output đã được tạo thành công
        if os.path.exists(output_file_path):
            file_size = os.path.getsize(output_file_path)
            logger.info(f"Chuyển đổi thành công! File XLSX: {output_file_path} (Kích thước: {file_size} bytes)")
            
            # Xóa file gốc nếu được yêu cầu
            if delete_original:
                try:
                    os.remove(input_file_path)
                    logger.info(f"Đã xóa file gốc: {input_file_path}")
                except Exception as e:
                    logger.warning(f"Không thể xóa file gốc {input_file_path}: {str(e)}")
                    # Không raise exception vì việc chuyển đổi đã thành công
            
            return output_file_path
        else:
            raise Exception("File XLSX không được tạo thành công")
            
    except FileNotFoundError as e:
        logger.error(f"Lỗi file không tồn tại: {str(e)}")
        return None
    except ValueError as e:
        logger.error(f"Lỗi giá trị không hợp lệ: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Lỗi chuyển đổi: {str(e)}")
        return None
