# Guest programs

`issue4.py` 至 `issue8.py` 是 Device Service program execution 实际提交到
同一 running UIFlow2 guest 的最小测试程序。源码 SHA256 与运行结果见
`../evidence/summary.json`。

`summary.json` 的 `program_source_sha256` 是 Device Service 的 canonical
bundle hash。单个 `main.py` 文件 SHA256 为：

| 文件 | SHA256 |
| --- | --- |
| `issue4.py` | `8602e9b55392a3b612c94d7ad2dcc2ec130c3ef4bac4eeec83ff026846800319` |
| `issue5.py` | `8c3d6fc3733995222a27b79a826f278b6b78f9461c612a91fd2a42b8b5a619e7` |
| `issue6.py` | `c0cbc6b13b567950d3698d2231130419968e6b13bb1157b605151d72d2614894` |
| `issue7.py` | `cbc975cdb8198e6e44f86a1c28ea9789e825dc574d70c4d8bd497e7f85cfa604` |
| `issue8.py` | `952c0e7f10b18d900e6de42540a8ddfefb63220c386fb0b6abb804ab53dbf263` |

这些程序只操作公开 UIFlow2 API；没有嵌入凭据、内网端点或物理设备标识。
