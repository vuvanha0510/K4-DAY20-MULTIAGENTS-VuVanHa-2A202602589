"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import re
from pathlib import Path

from .model import make_model
from .tasks import ROOT, eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------


def _reply_to_text(content) -> str:
    """Chuẩn hóa `AIMessage.content` về chuỗi.

    Một số provider (ví dụ Gemini qua langchain-google-genai) trả content dạng danh sách khối
    `[{"type": "text", "text": ...}]` thay vì chuỗi; `parse_skill_blocks` cần chuỗi thuần.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    return str(content)


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    """Đọc các lần chạy của TÁC VỤ HỌC (role == "learn") trong `source_condition`, nhờ LLM viết skill, ghi file.

    Các bước: nạp run.json + trace.md -> (nếu không có check nào thất bại: in cảnh báo và trả về [] mà KHÔNG gọi LLM)
    -> dựng prompt -> model.invoke(prompt) -> parse_skill_blocks -> validate_skill(text, expected_name=name)
    -> ghi `<out_dir>/<name>/SKILL.md`. Mặc định `out_dir` = <gốc lab>/skills/auto (dùng `ROOT` từ lab.tasks).
    Giữ tối đa `max_skills` skill hợp lệ; skill không hợp lệ bị bỏ qua.
    Prompt chứa, với mỗi check thất bại, TÊN và trường `detail` (lời nhận xét của bot đánh giá: phát biểu quy tắc bị vi phạm)
    cùng phần cuối của vết (trace). Với tác vụ học, `detail` chỉ phát biểu quy tắc, không chứa đáp án.
    Tuyệt đối KHÔNG đưa dữ liệu của tác vụ đánh giá (role == "eval") vào prompt.
    model mặc định: make_model() (lab.model).
    Trả về: danh sách đường dẫn SKILL.md đã ghi.
    """
    import json
    if out_dir is None:
        out_dir = ROOT / "skills" / "auto"
    else:
        out_dir = Path(out_dir)

    results_path = Path(results_dir) / source_condition
    runs = []

    for run_json in results_path.glob("*/run.json"):
        r = json.loads(run_json.read_text(encoding="utf-8"))
        if r.get("role") != "learn":
            continue
        trace_path = run_json.parent / "trace.md"
        trace = trace_path.read_text(encoding="utf-8")[-6000:] if trace_path.exists() else ""
        failed = [(c["name"], c.get("detail", "")) for c in r.get("checks", []) if not c.get("passed", True)]
        runs.append({"task": r["task"], "failed": failed, "trace": trace})

    if not any(r["failed"] for r in runs):
        print("Cảnh báo: không có check thất bại ở tác vụ học")
        return []

    # Build prompt
    prompt = f"""You write SKILL files for an engineering agent that fixes Python packages and analyses dirty CSV/JSON/log data.
Below are the failed checks of previous runs (name + the grader's remark) and the tail of their traces.
Find the GENERAL procedural mistakes (not task-specific answers) and write at most {max_skills} short skills
that help avoid them on a NEW task of the same kind.

Rules:
- Write the whole skill in English, ASCII only. Never use Vietnamese or any non-ASCII character.
- Skills must be general: never mention a task id, a task-specific file name, an answer, or a concrete number.
- Each skill has a YAML frontmatter with `name` (lower-case, dash-separated) and `description`
  (ONE sentence starting with "Use this skill when ..."), followed by at most 40 lines of imperative
  guidance (a checklist of good practices).
- Output format, character for character:
=== SKILL: <name> ===
---
name: <name>
description: <khi nào dùng>
---
<nội dung>
=== END ===

"""

    for run in runs:
        if not run["failed"]:
            continue
        prompt += f"\n=== TASK: {run['task']} ===\n"
        for name, detail in run["failed"]:
            prompt += f"\nFailed check: {name}\nGrader remark: {detail}\n"
        if run["trace"]:
            prompt += f"\nTrace (tail):\n{run['trace']}\n"

    if model is None:
        model = make_model()

    reply = _reply_to_text(model.invoke(prompt).content)
    blocks = parse_skill_blocks(reply)

    written = []
    for name, text in blocks:
        if len(written) >= max_skills:
            break
        problems = validate_skill(text, expected_name=name)
        if problems:
            continue
        skill_dir = out_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_path = skill_dir / "SKILL.md"
        skill_path.write_text(text, encoding="utf-8")
        written.append(skill_path)

    return written


if __name__ == "__main__":
    import json
    for p in curate_skills():
        print("wrote", p)
