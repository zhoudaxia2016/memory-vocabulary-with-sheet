import sys
import re
from pathlib import Path
try:
  from PyPDF2 import PdfReader
except Exception as e:
  raise SystemExit("请先用 pip 安装 PyPDF2（pip install PyPDF2）") from e

pdf_path = Path(sys.argv[1])
if not pdf_path.exists():
  raise SystemExit(f"找不到 PDF：{pdf_path}")

reader = PdfReader(str(pdf_path))
text = []
for p in reader.pages:
  t = p.extract_text()
  if t:
    text.append(t)
full = "\n".join(text)

# 找第1章到第2章之间的内容
m = re.search(r"(第\s*1章[\s\S]*?)(?:第\s*2章|第\s*2\s*章)", full)
if not m:
  raise SystemExit("无法定位第1章与第2章的边界，请确认 PDF 是否完整且为可选文本层（不是纯图片扫描）。")

section = m.group(1)

# 多种规则提取单词项
# 首先尝试抓取以 '□' 开头的条目
entries = []
for part in re.split(r"□+", section):
  part = part.strip()
  if not part:
    continue
  # 取第一段（到换行或到中文/英文短语结束）
  line = part.splitlines()[0].strip()
  # 清理后取前两个“token”作为（词语 + 读音）
  # 常见形式： "合図 あいず（する）" 或 "胃 い" 或 "コンビニ"
  # 抽出连续的日文字符（包括汉字/假名/片假名）
  m2 = re.match(r"([一-龯ぁ-ゔァ-ヴー々〆]+(?:[々〆一-龯ぁ-ゔァ-ヴー]*)?)(?:\s*([ぁ-んァ-ンー]+))?", line)
  if m2:
    kanji = m2.group(1)
    reading = m2.group(2) or ""
    entry = (kanji + ("\t" + reading if reading else "")).strip()
    entries.append(entry)

# 如果 entries 太少，退回到更宽的抓取（所有日语词串）
if len(entries) < 200:
  tokens = re.findall(r"[一-龯ぁ-ゔァ-ヴー]+(?:\s[ぁ-んァ-ンー]+)?", section)
  # 过滤短垃圾
  tokens = [t for t in tokens if len(t) >= 1]
  # 去重、保序
  seen = set(); entries = []
  for t in tokens:
    if t not in seen:
      seen.add(t); entries.append(t)

# 保存文件
out_txt = Path(pdf_path.stem + ".txt")
with out_txt.open("w", encoding="utf-8") as f:
  for w in entries:
    f.write(w + "\n")

print(f"完成：共提取 {len(entries)} 条（已写入）")
print(out_txt.resolve())

