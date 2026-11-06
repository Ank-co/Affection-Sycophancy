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

Converted from BF16 with `convert_hf_to_gguf.py` of llama.cpp b10786, quantized to Q6_K with `llama-quantize` of the same release (2026-11-06).

| Server name | Role | Weights (revision) | File | SHA-256 |
|---|---|---|---|---|
| `qwen3-8b` | original | [Qwen/Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B) at `b968826d9c46` | `C:\llm\models\Qwen3-8B-Q6_K.gguf` | `F75C8C7395149E2C4E731BE1FA618EE069007CD50D4E51996B3F31BE73B143D8` |
| `qwen3-8b-huihui` | abliterated (Huihui v2) | [huihui-ai/Huihui-Qwen3-8B-abliterated-v2](https://huggingface.co/huihui-ai/Huihui-Qwen3-8B-abliterated-v2) at `7d89db760292` | `C:\llm\models\Huihui-Qwen3-8B-abliterated-v2-Q6_K.gguf` | `BE68E7A1B5DD27DD962867B15D61E3209325458541936E3449D0F60A85815CE4` |
| `qwen3-8b-mlabonne` | abliterated (mlabonne) | [mlabonne/Qwen3-8B-abliterated](https://huggingface.co/mlabonne/Qwen3-8B-abliterated) at `30c72fa348f3` | `C:\llm\models\Qwen3-8B-abliterated-Q6_K.gguf` | `C7555750BAB067CFA785607F477B935BA7D4F794D15B110F441BEC3EB454E5EE` |

The mlabonne weights are stored in float32 (32.8 GB), the two others in bfloat16; all three go through the same chain (BF16 GGUF, then Q6_K), so the only difference is the float32-to-bfloat16 rounding at conversion.
