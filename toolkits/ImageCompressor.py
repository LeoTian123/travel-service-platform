import os


class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char  # 字符(字节)
        self.freq = freq  # 频率
        self.left = None  # 左子节点
        self.right = None  # 右子节点

    def __lt__(self, other):
        return self.freq < other.freq


class ImageCompressor:
    @staticmethod
    def compress_image(input_path, output_path):
        """压缩文件，使用哈夫曼编码"""
        try:
            # 读取文件内容
            with open(input_path, 'rb') as f:
                data = f.read()

            # 统计字节频率
            frequency = {}
            for byte in data:
                frequency[byte] = frequency.get(byte, 0) + 1

            # 构建哈夫曼树
            heap = []
            for byte, freq in frequency.items():
                node = HuffmanNode(byte, freq)
                heap.append(node)

            # 特殊情况处理：空文件
            if not heap:
                with open(output_path, 'wb') as f:
                    f.write(b'HCMP\x00\x00\x00\x00')  # 文件头，空数据标记
                return True

            # 构建哈夫曼树
            while len(heap) > 1:
                heap.sort(key=lambda x: x.freq)
                left = heap.pop(0)
                right = heap.pop(0)
                merged = HuffmanNode(None, left.freq + right.freq)
                merged.left = left
                merged.right = right
                heap.append(merged)

            root = heap[0]

            # 生成哈夫曼编码表
            code_table = {}

            def generate_codes(node, current_code):
                if node is None:
                    return
                if node.char is not None:
                    code_table[node.char] = current_code
                    return
                generate_codes(node.left, current_code + '0')
                generate_codes(node.right, current_code + '1')

            generate_codes(root, '')

            # 编码数据
            encoded_data = ''.join(code_table[byte] for byte in data)

            # 构建频率表字节数据 (格式: 字符数 + 每个字符的字节+频率)
            freq_table_bytes = len(frequency).to_bytes(4, 'big')
            for byte, freq in frequency.items():
                freq_table_bytes += bytes([byte]) + freq.to_bytes(4, 'big')

            # 计算需要填充的位数
            padding = 8 - (len(encoded_data) % 8)
            if padding == 8:
                padding = 0

            # 添加填充位和填充计数
            encoded_data += '0' * padding
            padding_info = padding.to_bytes(1, 'big')

            # 转换为字节
            encoded_bytes = bytearray()
            for i in range(0, len(encoded_data), 8):
                byte = int(encoded_data[i:i + 8], 2)
                encoded_bytes.append(byte)

            # 写入压缩文件
            with open(output_path, 'wb') as f:
                f.write(b'HCMP')  # 文件标识
                f.write(freq_table_bytes)  # 频率表
                f.write(padding_info)  # 填充信息
                f.write(encoded_bytes)  # 编码后的数据

            return True
        except Exception as e:
            print(f"Error compressing file: {e}")
            return False

    @staticmethod
    def decompress_image(input_path):
        """解压缩文件，使用哈夫曼编码"""
        try:
            with open(input_path, 'rb') as f:
                # 读取文件头
                file_id = f.read(4)
                if file_id != b'HCMP':
                    return None  # 不是压缩文件

                # 读取频率表
                char_count = int.from_bytes(f.read(4), 'big')

                # 特殊情况：空文件
                if char_count == 0:
                    return b'', None

                frequency = {}
                for _ in range(char_count):
                    byte = f.read(1)[0]
                    freq = int.from_bytes(f.read(4), 'big')
                    frequency[byte] = freq

                # 读取填充信息
                padding = f.read(1)[0]

                # 读取编码后的数据
                encoded_bytes = f.read()

            # 转换为位字符串
            encoded_bits = ''
            for byte in encoded_bytes:
                bits = bin(byte)[2:].rjust(8, '0')
                encoded_bits += bits

            # 移除填充位
            encoded_bits = encoded_bits[:len(encoded_bits) - padding]

            # 构建哈夫曼树
            heap = []
            for byte, freq in frequency.items():
                node = HuffmanNode(byte, freq)
                heap.append(node)

            while len(heap) > 1:
                heap.sort(key=lambda x: x.freq)
                left = heap.pop(0)
                right = heap.pop(0)
                merged = HuffmanNode(None, left.freq + right.freq)
                merged.left = left
                merged.right = right
                heap.append(merged)

            root = heap[0]

            # 解码数据
            decoded_data = bytearray()
            current_node = root
            for bit in encoded_bits:
                if bit == '0':
                    current_node = current_node.left
                else:
                    current_node = current_node.right

                if current_node.char is not None:
                    decoded_data.append(current_node.char)
                    current_node = root

            return decoded_data, None  # 返回二进制数据和None(格式不再需要)
        except Exception as e:
            print(f"Error decompressing file: {e}")
            return None, None

    @staticmethod
    def get_compressed_filename(original_filename):
        """生成压缩后的文件名"""
        return f"{original_filename}.hcmp"

    @staticmethod
    def is_compressed_file(filename):
        """检查是否为压缩文件"""
        return filename.endswith('.hcmp')

if __name__ == '__main__':
    ImageCompressor.compress_image('../Media/journals/main-data.pickle', '../Media/journals/main-data.pickle.hcmp')
    data, _ = ImageCompressor.decompress_image('main-data.pickle.hcmp')
    with open('main-data-ex.pickle', 'wb') as f:
        f.write(data)
