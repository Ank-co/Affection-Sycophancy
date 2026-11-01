# Model files

SHA-256 of every model file, recorded before its first test run (pre-registration §3). The runner also stores the
server's model path and settings in `results/campaign/<model>/meta-*.json` at every session.

## 35B family (llama.cpp, KV cache q8_0)

Server names: `qwen3.6-35b-base-i1` (original) and `qwen3.6-35b-abliterated`.

| File | SHA-256 |
|---|---|
| `C:\llm\models\Qwen3.6-35B-A3B.i1-Q3_K_M.gguf` | `05C715FABC010789BECE0BEE26F1B911CB67CB26D353F3E419C595D27538A8F7` |
| `C:\llm\models\Huihui-Qwen3.6-35B-A3B-abliterated.i1-Q3_K_M.gguf` | `A73D0D6E38BE6C72745F3A60C311C8BFC4E4AEA84A617651FB2B4D27E7FFC3A8` |

llama.cpp build `b10786-de8656bd9` (read from the server by the runner, 2026-11-01).

Command (PowerShell, from the repository folder):

```powershell
Get-FileHash -Algorithm SHA256 C:\llm\models\Qwen3.6-35B-A3B.i1-Q3_K_M.gguf, C:\llm\models\Huihui-Qwen3.6-35B-A3B-abliterated.i1-Q3_K_M.gguf | Format-List
```

## 8B family

To be added before the first 8B test run: Qwen/Qwen3-8B, huihui-ai/Huihui-Qwen3-8B-abliterated-v2,
mlabonne/Qwen3-8B-abliterated, one quantization chain and type for the three.
