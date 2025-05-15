import fitz  # PyMuPDF
import xml.etree.ElementTree as ET
import json
import os

def pdf_to_svg(pdf_path, svg_path):
    """
    讀取 PDF 檔案的第一頁並將其轉換為 SVG 格式，然後儲存到指定的路徑。

    參數:
    pdf_path (str): 輸入的 PDF 檔案路徑。
    svg_path (str): 輸出的 SVG 檔案路徑。

    返回:
    str: SVG 圖像的內容字串。
    """
    try:
        doc = fitz.open(pdf_path)
        if doc.page_count > 0:
            page = doc.load_page(0)  # 讀取第一頁
            # 將頁面轉換為 SVG 格式，禁用文字轉換為路徑以保留文字
            svg_content = page.get_svg_image(text_as_path=False)
            with open(svg_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            print(f"成功將 '{pdf_path}' 的第一頁儲存為 '{svg_path}'")
            return svg_content
        else:
            print(f"錯誤：PDF 檔案 '{pdf_path}' 沒有頁面可供轉換。")
            return None
    except Exception as e:
        print(f"處理 PDF 檔案 '{pdf_path}' 時發生錯誤：{e}")
        return None
    finally:
        if 'doc' in locals() and doc:
            doc.close()




def generate_svg_metadata(svg_content):
    """
    從 SVG 內容字串中提取元數據。

    參數:
    svg_content (str): SVG 圖像的內容字串。

    返回:
    dict: 包含 SVG 元數據的字典 (width, height, viewBox, elements_count)。
          如果解析失敗則返回 None。
    """
    if not svg_content:
        return None
    try:
        # 移除可能存在的 XML 宣告，避免 ET.fromstring 出錯
        if svg_content.startswith("<?xml"):
            svg_content = svg_content.split("?>", 1)[-1].strip()
        
        root = ET.fromstring(svg_content)
        metadata = {
            'width': root.attrib.get('width'),
            'height': root.attrib.get('height'),
            'viewBox': root.attrib.get('viewBox'),
            'elements_count': len(list(root))  # 計算 SVG 根元素下的直接子元素數量
        }
        return metadata
    except ET.ParseError as e:
        print(f"解析 SVG 內容時發生錯誤：{e}")
        # 嘗試從更外層的結構中提取 viewBox, width, height
        # 這是一個備用方案，如果 PyMuPDF 輸出的 SVG 結構略有不同
        try:
            # 假設 SVG 內容可能包含在 <svg> 標籤內
            import re
            width_match = re.search(r'width="([^"]+)"', svg_content)
            height_match = re.search(r'height="([^"]+)"', svg_content)
            viewbox_match = re.search(r'viewBox="([^"]+)"', svg_content)
            
            if width_match and height_match and viewbox_match:
                metadata_fallback = {
                    'width': width_match.group(1),
                    'height': height_match.group(1),
                    'viewBox': viewbox_match.group(1),
                    'elements_count': 'N/A (parsing error)' # 元素數量無法在此情況下準確計算
                }
                print("警告：使用備用方法提取元數據，elements_count 可能不準確。")
                return metadata_fallback
            else:
                return None
        except Exception as fallback_e:
            print(f"備用解析 SVG 內容時也發生錯誤：{fallback_e}")
            return None
    except Exception as e:
        print(f"生成 SVG 元數據時發生未知錯誤：{e}")
        return None
    

def run(pdf_file_path, svg_output_path):
    #"../../../Docs/ID_Phase/2D_spec.pdf"
    # pdf_file_path = '../../../Docs/ID_Phase/2D_spec.pdf'  # 您的 PDF 檔案名稱
    # svg_output_path = '2D_spec.svg' # 輸出的 SVG 檔案名稱

    # 檢查 PDF 檔案是否存在
    if not os.path.exists(pdf_file_path):
        print(f"錯誤：找不到 PDF 檔案 '{pdf_file_path}'。請確保檔案存在於正確的路徑。")
        # 根據搜索結果 [1]，檔案可能無法直接讀取，但假設執行環境可以找到它。
        # 此處添加一個提示，如果檔案真的不存在，使用者會看到。
        # 不過，既然其他程式碼都假設檔案存在，我們繼續。
        # 如果您從一個上傳的檔案執行，請確保它已放置在程式可以存取的位置。

    # 1. 讀取 PDF 並將圖像儲存為 SVG 格式
    svg_image_content = pdf_to_svg(pdf_file_path, svg_output_path)

    if svg_image_content:
        # 2. 為 SVG 圖像生成元數據
        metadata_dict = generate_svg_metadata(svg_image_content)

        if metadata_dict:
            # 3. 將元數據轉換為 JSON 格式並輸出
            json_metadata = json.dumps(metadata_dict, indent=4)
            print("\nSVG 圖像的 JSON 元數據:")
            print(json_metadata)

            # (可選) 將 JSON 元數據儲存到檔案
            json_output_path = 'metadata.json'
            try:
                with open(json_output_path, 'w', encoding='utf-8') as f_json:
                    json.dump(metadata_dict, f_json, indent=4)
                print(f"\n元數據也已儲存至 '{json_output_path}'")
            except Exception as e:
                print(f"儲存 JSON 元數據到檔案時發生錯誤：{e}")
        else:
            print("無法生成 SVG 元數據。")
    else:
        print(f"由於無法將 PDF 轉換為 SVG，因此無法生成元數據。")