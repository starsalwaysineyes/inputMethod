"""
简单输入法实现
数据格式示例：
{ "index" : 1, "char" : "一", "strokes" : 1, "pinyin" : [ "yī" ], "radicals" : "一", "frequency" : 0, "structure" : "D0" }
"""

import json
from typing import List, Dict
from collections import defaultdict


class PinyinInputMethod:
    """简单的拼音输入法"""
    
    def __init__(self, jsonl_file: str = "char_common_base.jsonl"):
        """
        初始化输入法，读取字库文件并构建拼音索引
        
        Args:
            jsonl_file: 字库文件路径
        """
        self.pinyin_dict = defaultdict(list)  # 拼音 -> [字符列表]
        self.pinyin_dict_no_tone = defaultdict(list)  # 无声调拼音 -> [字符列表]   
        self.char_data = {}  # 字符 -> 完整数据
        self._load_data(jsonl_file)
    
    def _remove_tone(self, pinyin: str) -> str:
        """
        去除拼音声调和标准化特殊字符
        
        Args:
            pinyin: 带声调的拼音
            
        Returns:
            不带声调的标准拼音
        """
        tone_map = {
            'ā': 'a', 'á': 'a', 'ǎ': 'a', 'à': 'a',
            'ē': 'e', 'é': 'e', 'ě': 'e', 'è': 'e',
            'ī': 'i', 'í': 'i', 'ǐ': 'i', 'ì': 'i',
            'ō': 'o', 'ó': 'o', 'ǒ': 'o', 'ò': 'o',
            'ū': 'u', 'ú': 'u', 'ǔ': 'u', 'ù': 'u',
            'ǖ': 'v', 'ǘ': 'v', 'ǚ': 'v', 'ǜ': 'v', 'ü': 'v',
            'ɡ': 'g',  # IPA 符号 ɡ (U+0261) 转为普通 g
            'ń': 'n', 'ň': 'n', 'ǹ': 'n',  # 其他可能的声调字符
        }
        result = ''
        for char in pinyin:
            result += tone_map.get(char, char)
        return result
    
    def _load_data(self, jsonl_file: str):
        """
        从 JSONL 文件加载数据并构建索引
        
        Args:
            jsonl_file: 字库文件路径
        """
        print(f"正在加载字库文件: {jsonl_file}")
        count = 0
        
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 去除末尾的逗号（如果有）
                    if line.endswith(','):
                        line = line[:-1]
                    
                    # 解析 JSON
                    data = json.loads(line)
                    char = data['char']
                    pinyins = data['pinyin']
                    frequency = data.get('frequency', 999)
                    
                    # 保存完整数据
                    self.char_data[char] = data
                    
                    # 为每个拼音建立索引
                    for py in pinyins:
                        # 带声调的索引
                        self.pinyin_dict[py].append({
                            'char': char,
                            'frequency': frequency
                        })
                        
                        # 不带声调的索引
                        py_no_tone = self._remove_tone(py)
                        self.pinyin_dict_no_tone[py_no_tone].append({
                            'char': char,
                            'frequency': frequency,
                            'pinyin': py
                        })
                    
                    count += 1
            
            # 按频率排序候选字（frequency 越小越常用）
            for py in self.pinyin_dict:
                self.pinyin_dict[py].sort(key=lambda x: x['frequency'])
            
            for py in self.pinyin_dict_no_tone:
                self.pinyin_dict_no_tone[py].sort(key=lambda x: x['frequency'])
            
            print(f"加载完成！共加载 {count} 个汉字")
            print(f"拼音索引数量（带声调）: {len(self.pinyin_dict)}")
            print(f"拼音索引数量（不带声调）: {len(self.pinyin_dict_no_tone)}")
            
        except FileNotFoundError:
            print(f"错误：找不到文件 {jsonl_file}")
        except json.JSONDecodeError as e:
            print(f"错误：JSON 解析失败 - {e}")
    
    def get_candidates(self, pinyin: str, with_tone: bool = False) -> List[str]:
        """
        根据拼音获取候选字
        
        Args:
            pinyin: 拼音（可带或不带声调）
            with_tone: 是否使用声调匹配（默认 False，不区分声调）
            
        Returns:
            候选字列表，按使用频率排序
        """
        if with_tone:
            candidates = self.pinyin_dict.get(pinyin, [])
        else:
            # 先尝试去除声调
            py_no_tone = self._remove_tone(pinyin)
            candidates = self.pinyin_dict_no_tone.get(py_no_tone, [])
        
        return [item['char'] for item in candidates]
    
    def get_candidates_with_info(self, pinyin: str, with_tone: bool = False) -> List[Dict]:
        """
        根据拼音获取候选字及详细信息
        
        Args:
            pinyin: 拼音（可带或不带声调）
            with_tone: 是否使用声调匹配（默认 False，不区分声调）
            
        Returns:
            候选字详细信息列表
        """
        if with_tone:
            return self.pinyin_dict.get(pinyin, [])
        else:
            py_no_tone = self._remove_tone(pinyin)
            return self.pinyin_dict_no_tone.get(py_no_tone, [])


def main():
    """示例用法"""
    # 创建输入法实例
    ime = PinyinInputMethod()
    
    # 测试查询
    test_pinyins = ['yi', 'er', 'shi', 'zhong', 'guo']
    
    print("\n" + "="*50)
    print("测试拼音输入法")
    print("="*50)
    
    for py in test_pinyins:
        candidates = ime.get_candidates(py)
        if candidates:
            print(f"\n拼音: {py}")
            print(f"候选字 (前10个): {' '.join(candidates[:10])}")
        else:
            print(f"\n拼音: {py}")
            print("没有找到候选字")
    
    # 交互式测试
    print("\n" + "="*50)
    print("交互式测试（输入 'q' 退出）")
    print("="*50)
    
    while True:
        user_input = input("\n请输入拼音: ").strip()
        if user_input.lower() == 'q':
            break
        
        if not user_input:
            continue
        
        candidates = ime.get_candidates(user_input)
        if candidates:
            print(f"候选字: {' '.join(candidates[:20])}")
            print(f"共 {len(candidates)} 个候选")
        else:
            print("没有找到候选字")


if __name__ == "__main__":
    main()
