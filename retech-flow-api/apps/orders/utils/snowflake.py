import time


class Snowflake:
    """
    Twitter 雪花算法 (纯 Python 实现)
    生成 64 位整型数字:
    1位符号位(0) + 41位时间戳 + 10位机器/数据中心ID + 12位序列号
    """
    def __init__(self, datacenter_id=1, worker_id=1):
        # 基础参数配置
        self.twepoch = 1672531200000  # 自定义纪元时间戳 (2023-01-01) 可以用更晚的时间延长老命

        # 各部分占用的位数
        self.worker_id_bits = 5
        self.datacenter_id_bits = 5
        self.sequence_bits = 12

        # 各部分的最大值
        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)
        self.max_datacenter_id = -1 ^ (-1 << self.datacenter_id_bits)
        self.sequence_mask = -1 ^ (-1 << self.sequence_bits)

        # 各部分的偏移量 (位移操作)
        self.worker_id_shift = self.sequence_bits
        self.datacenter_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_left_shift = self.sequence_bits + self.worker_id_bits + self.datacenter_id_bits

        # 校验传入的 ID 是否合法
        if worker_id > self.max_worker_id or worker_id < 0:
            raise ValueError(f"worker_id 值必须在 0 到 {self.max_worker_id} 之间")
        if datacenter_id > self.max_datacenter_id or datacenter_id < 0:
            raise ValueError(f"datacenter_id 值必须在 0 到 {self.max_datacenter_id} 之间")

        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = 0
        self.last_timestamp = -1

    def _gen_timestamp(self):
        # 获取当前时间的毫秒数
        return int(time.time() * 1000)

    def _til_next_millis(self, last_timestamp):
        # 如果当前时间与上次相同，就自旋等待下一毫秒
        timestamp = self._gen_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._gen_timestamp()
        return timestamp

    def get_id(self):
        """生成唯一 ID 的核心方法"""
        timestamp = self._gen_timestamp()

        # 时钟回拨防御
        if timestamp < self.last_timestamp:
            raise Exception("系统时钟回拨，拒绝生成 ID")

        # 同一毫秒内并发，递增序列号
        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & self.sequence_mask
            # 毫秒内的序列号用完了，等待下一毫秒
            if self.sequence == 0:
                timestamp = self._til_next_millis(self.last_timestamp)
        else:
            # 不同毫秒，序列号重置为 0
            self.sequence = 0

        self.last_timestamp = timestamp

        # 位运算拼接成 64 位整数
        new_id = ((timestamp - self.twepoch) << self.timestamp_left_shift) | \
                 (self.datacenter_id << self.datacenter_id_shift) | \
                 (self.worker_id << self.worker_id_shift) | \
                 self.sequence

        return new_id


# 实例化一个全局的生成器器 (机器 ID 和数据中心 ID 随便配，反正你是单机)
# 你可以在别的模块直接 from .snowflake import id_worker
id_worker = Snowflake(datacenter_id=1, worker_id=1)