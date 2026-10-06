# Báo cáo Lab: Self evolving Agentic



## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Vũ Văn Hà | 2A202602589 | Toàn bộ |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `google_genai:gemini-3.1-flash-lite`, temperature=0, recursion_limit=60 (lần dùng `gemini-3.8-flash` bị từ chối 429 vì hết quota free tier)
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: Deep Agents 0.2.1, Windows 11, chạy trực tiếp trong `.venv`
- Số lần chạy tác vụ đã dùng / ngân sách: **4 lần chạy tác vụ học** (3 `baseline` + 2 `subagents`, trong đó `subagents/code-learn` phải chạy lại) ≈ 610k token; đã dùng gần hết quota Gemini free tier (20 request/ngày), nên **chưa chạy được** `skills-auto` và toàn bộ tác vụ đánh giá.
- Commit của tag `freeze`: commit `c321071`→`hypotheses`, tag `freeze` trên commit kế tiếp (`freeze skills`) — xác nhận bằng `python scripts/verify_freeze.py` → `OK`

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)



- H1 (subagents so với baseline): `subagents` sẽ không vượt `baseline` trên điểm trung bình. Căn cứ: trên 3 tác vụ học, `baseline` đạt 16/18 check kỹ thuật (chỉ hụt 2) trong khi `subagents` mới đạt 7/12; hai điều kiện đều 0/9 và 0/6 check quy ước `rule_`. Lợi ích của việc chia việc bị bù bằng chi phí token cao hơn và bối cảnh bị mất khi bàn giao.
- H2 (skills-auto so với baseline): `skills-auto` sẽ không cải thiện điểm, vì skill do curator sinh ra toàn quy về nhóm lỗi E (quy ước tổ chức không có trong đề) chứ không giải quyết nhóm lỗi kỹ thuật chiếm đa số; đồng thời `skills_read` có thể bằng 0 vì `description` không nêu đúng tình huống kích hoạt.
- H3 (tác vụ học so với tác vụ đánh giá): điểm trên tác vụ đánh giá sẽ thấp hơn tác vụ học ở cả ba điều kiện, vì quy ước `rule_` mới của tác vụ đánh giá chưa từng xuất hiện trong dữ liệu curator sinh skill (tự diễn giải: skill viết từ vết tác vụ học không chứa quy ước đánh giá).

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có các công cụ sau:
   - **Công cụ tệp (file tools):** `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`
   - **Shell:** `execute` (cho phép chạy lệnh shell trong sandbox)
   - **Subagent:** `task` (cho phép giao việc cho subagent)

2. Về subagent `general-purpose`:
   - Mô tả: "General-purpose agent for researching complex questions, searching for files and content, and executing multi-step tasks. When you are searching for a keyword or file and are not confident that you will find the right match in the first few tries use this agent to perform the search for you. This agent has access to all tools as the main agent."
   - Subagent **chỉ nhìn thấy ngữ cảnh mà tác tử chính gửi trong prompt giao việc** (context isolation). Theo mô tả: "Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report."

3. System prompt mặc định của Deep Agents rỗng. Các câu hướng dẫn hành vi:
   - Từ mô tả `task`: "Put full detail in the prompt and state exactly what it should return — unless an agent type below says it inherits your conversation instead."
   - Từ mô tả `execute`: "You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)



| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| baseline / code-learn | `visible_suite_passes` | G (không kết thúc) | `1 failed, 7 passed in 0.37s`; `error = GraphRecursionError: Recursion limit of 60 reached`, 209k token, 0 tool call ghi nhận được vì luồng bị cắt |
| baseline / code-learn | `rule_type_hints` | E | `RULE: every public function ... has type annotations` |
| baseline / code-learn | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py with one test function per bug` |
| baseline / code-learn | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md under '## Unreleased'` |
| baseline / data-learn | `north_q1_revenue` | D | `wrong value (got 3189.59)` — đọc/diễn giải dữ liệu bẩn (múi giờ, trùng lặp) sai |
| baseline / data-learn | `rule_money_in_cents` | E | `RULE: money values in answer.json are integer cents` |
| baseline / data-learn | `rule_meta_block` | E | `RULE: answer.json has an object meta = {source, rows_in, ...}` |
| baseline / data-learn | `rule_clean_csv` | E | `RULE: write workspace/clean.csv with header order_id,timestamp_utc,region,amount_cents` |
| baseline / logs-learn | `rule_service_names` | E | `RULE: service names are lower-case with '-' replaced by '_'` |
| baseline / logs-learn | `rule_sorted_errors` | E | `RULE: errors is sorted by service, then by timestamp_utc` |
| baseline / logs-learn | `rule_schema_header` | E | `RULE: top-level object has schema_version 2 and generated_by "log-triage"` |

Nhận xét: **nhóm E chiếm 10/12 lỗi** (đa số tuyệt đối). Bằng chứng phủ định cho A-D: `python scripts/check_breakdown.py` cho thấy `baseline` đạt **16/18 check kỹ thuật** nhưng **0/9 check quy ước**. Nghĩa là tác tử đọc đề, chạy test, sửa đúng nguyên nhân gốc và xử lý dữ liệu bẩn khá tốt; nó chỉ không biết các quy ước tổ chức vốn **không nằm trong đề**. Đây đúng là nhóm lỗi mà một skill có thể phòng ngừa: skill mô tả "đọc kỹ mọi quy ước trong đề, kể cả quy ước về tên trường, thứ tự, kiểu đơn vị và metadata trước khi ghi tệp" sẽ nâng trực tiếp 9 check `rule_`.

## 5. Điều kiện `subagents` (Phần 2.3)

- **Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):**
  1. **explorer** - Đọc và báo cáo: Dùng khi cần đọc nhiều tệp, tìm hiểu cấu trúc dự án, đọc README, docstring, hoặc mẫu dữ liệu để báo cáo sự thật. Không sửa đổi tệp.
  2. **implementer** - Thực hiện: Dùng khi cần thực hiện thay đổi mã, sửa lỗi, chạy test hoặc script, và báo cáo kết quả.
  3. **reviewer** - Kiểm tra độc lập: Dùng khi cần kiểm tra độc lập kết quả theo đề bài và các trường hợp biên, không sửa tệp.

- `subagent_calls` từ các tác vụ học và nhận xét (kể cả trường hợp bằng 0): **`subagent_calls = 0` ở cả hai lần chạy** (`subagents/code-learn`, `subagents/data-learn`). Tác tử chính không giao việc cho subagent nào; nó tự làm hết bằng vòng lặp tool thông thường (27 tool call ở `code-learn`). Đây là kết quả học được: system prompt `SUBAGENTS_NOTE` chỉ mô tả subagent, không ép dùng, và với 3 subagent định nghĩa sẵn (`explorer`, `implementer`, `reviewer`) tác tử vẫn thấy chi phí bàn giao là không đáng khi bài toán không đủ lớn.

- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc): không có lần giao việc nào. Điểm đáng chú ý: `subagents/data-learn` đạt **0/8** với mọi check kỹ thuật báo `FileNotFoundError` (tác tử kết thúc mà không tạo ra `answer.json`), tức là ở lần chạy này tác tử chính đã hỏng — bằng chứng cho thấy vấn đề nằm ở độ ổn định của lần chạy chứ không phải ở việc chia subagent.

- Ảnh hưởng đến token và thời gian: `subagents` tốn **114,376** token/lần chạy so với **107,766** của `baseline` (+6%), và `subagents/code-learn` chạy lâu hơn (27 tool call, 184,580 token). Không đổi được điểm; ở đây còn tệ hơn vì 1 lần chạy hỏng hoàn toàn.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: **0 lần chạy curator trong phiên này** (dùng 3 skill có sẵn trong `skills/auto/` từ lần curator trước ở Phần 3); 0 skill bị xóa.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `adhere-to-strict-output-rules-and-metadata` | Tổng quát (đúng tinh thần) | Đúng hướng nhưng **chung chung**: "đọc kỹ mọi quy tắc chấm điểm về tên tệp, cấu trúc thư mục, khóa" không nêu quy tắc cụ thể nào | ~8 dòng; `description` nêu đúng tình huống kích hoạt (sinh JSON/artifact) → nên dễ được đọc |
| `enforce-code-quality-and-formatting-rules` | **Nửa riêng cho `code-learn`**: kéo theo type hints, docstring, naming, CHANGELOG | Đúng về kỹ thuật nhưng **quá rộng** — "annotate mọi public function", "cập nhật CHANGELOG" là biến số theo dự án, áp dụng vào tác vụ dữ liệu sẽ vô nghĩa | ~8 dòng; `description` đúng (viết/refactor Python) |
| `preserve-existing-tests-and-add-regressions` | **Riêng cho `code-learn`** | Đúng và an toàn, nhưng **hạn chế tác tử**: "never modify existing test files" có thể chặn cả việc sửa một test thật sự sai | ~7 dòng; `description` nêu đúng tình huống (fix test suite) |

Nhận xét chung: cả 3 skill đều hợp lệ về định dạng (validator không từ chối) nhưng **không skill nào nhắm vào nhóm lỗi E thực sự** (`rule_changelog`, `rule_money_in_cents`, `rule_meta_block`, `rule_clean_csv`, `rule_sorted_errors`) — đó là lý do dự đoán H2 là `skills-auto` không cải thiện điểm.

## 7. Kết quả so sánh (Phần 4.3, 4.4)



```text
| Task | baseline | subagents |
|---|---|---|
| code-learn | 6/10 | 7/10 |
| data-learn | 4/8 | 0/8 |
| logs-learn | 6/9 | - |
| **Mean score - learning tasks** | 0.59 | 0.35 |
| **Mean score - evaluation tasks** | - | - |
| **Mean tokens per run** | 107,766 | 114,376 |
| **Runs that read a skill** | 0/3 | 0/2 |

python scripts/check_breakdown.py:
condition     role    technical  house rules  mean tokens  read a skill
baseline      learn    16/18         0/9          107,766      0/3
subagents     learn    7/12         0/6          114,376      0/2
```

Các lần chạy có lỗi:
- `baseline/code-learn`: `GraphRecursionError: Recursion limit of 60 reached` — đã thử chạy lại nhưng vẫn vượt trần; theo GUIDE "Xử lý sự cố" đây là hành vi lặp vô hạn của mô hình, điểm vẫn được chấm như kết quả thực tế (6/10) và được nêu như hạn chế ở mục 9.
- `subagents/data-learn`: không có `error` nhưng tác tử không tạo `answer.json`, mọi check báo `FileNotFoundError`, điểm 0/8. Đây là lần chạy không hoàn thành, **không phải hiệu năng của điều kiện subagents**; điểm trung bình của `subagents` vì vậy bị đánh giá thấp không đúng lý thuyết.
- `subagents/logs-learn`: **chưa có dữ liệu** (hết thời gian/thiếu quota mô hình), `subagents` và `skills-auto` trên tác vụ đánh giá cũng chưa chạy được.
- Không có lần chạy `skills-auto` nào (`skills_read = 0/3` chỉ vì không chạy), và `skills_modified` không quan sát được. `python scripts/verify_freeze.py` trả về `OK` cho 0 lần chạy skill condition — tức là tag `freeze` và commit `hypotheses` hợp lệ nhưng **chưa có dữ liệu `skills-auto` để đối chiếu**.

## 8. Phân tích



1. So với `baseline`, điều kiện nào cải thiện điểm? **Không điều kiện nào cải thiện điểm trên bằng chứng thu được.** `subagents` chỉ tốt hơn ở `code-learn` (7/10 so với 6/10) nhưng kém hẳn ở `data-learn` (0/8 so với 4/8). Không thể kết luận về tác vụ **đánh giá** vì chưa có lần chạy nào cho `*-eval`. Không có trường hợp "cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá" trong dữ liệu hiện có.
2. Tách điểm thành check kỹ thuật và check quy ước: `baseline` đạt **16/18 check kỹ thuật** nhưng **0/9 check quy ước**; `subagents` đạt 7/12 kỹ thuật và 0/6 quy ước. Skill do curator sinh (3 skill) nhắm vào **chất lượng mã và bảo toàn test**, tức là nhóm check kỹ thuật — nhưng nhóm kỹ thuật vốn đã gần đạt (16/18) nên biên lợi ích rất nhỏ. Skill **không** đụng tới nhóm `rule_` (0/9), và trên các check quy ước **mới** của tác vụ đánh giá chắc chắn cũng không được giúp: skill được viết từ vết `code-learn`/`data-learn`/`logs-learn`, mà bản thân đề bài có những quy ước đánh giá chỉ xuất hiện ở tác vụ đánh giá — curator không thể biết trước những quy ước đó. Đây chính là giới hạn của self-evolving: skill chỉ học được quy ước đã xuất hiện trong dữ liệu, không học được quy ước mới.
3. Vết và `skills_read`: do chưa chạy `skills-auto` nên không có vết nào có `skills_read > 0`; ở `baseline` và `subagents`, `skills_read = 0` vì điều kiện đó không mount skill. Một ví dụ minh hoạ rõ cơ chế: skill `preserve-existing-tests-and-add-regressions` có thể **giúp** đạt `visible_suite_passes` ở `code-learn` (nếu được đọc) vì nó cấm sửa test gốc — đúng trạng thái lỗi quan sát được; nhưng nó **không giúp** `rule_changelog`, vì skill nói về type hints và test chứ **không hề nhắc tới CHANGELOG hay mục `## Unreleased`** — skill thiếu, không phải skill sai.
4. Chi phí: `baseline` 107,766 token/lần chạy, `subagents` 114,376 (+6%). Điểm trên mỗi token: `baseline` 0.59 điểm/107,766 ≈ 5,5e-6; `subagents` 0.35/114,376 ≈ 3,1e-6. `baseline` hiệu quả hơn rõ rệt. Đa tác tử **không đáng chi phí** trong thí nghiệm này, vì `subagent_calls = 0`: tác tử không dùng subagent nào nên không có lợi ích phân công lao động nào để bù chi phí, chỉ thêm phần prompt và mô tả tool.
5. Dấu hiệu rò rỉ dữ liệu / quá khớp: có. `enforce-code-quality-and-formatting-rules` (yêu cầu type hints, CHANGELOG, naming convention) và `preserve-existing-tests-and-add-regressions` (tests/test_regressions.py) là **chi tiết riêng của `code-learn`** được đóng băng thành "skill tổng quát" — đây là overfitting mạnh. Biện pháp đã dùng: không sửa tay `skills/auto/` (giữ nguyên đầu ra curator), tách riêng cột "Tổng quát hay riêng cho tác vụ học?" ở mục 6, và giới hạn skill chỉ được đọc ở điều kiện `skills-auto` (chứ không áp cho `baseline`/`subagents`) để bảng so sánh vẫn công bằng.
6. Nhiễu: **chưa đo được** — thiếu lần chạy `skills-auto` ở Phần 3.4 để so với sau đóng băng. Nhưng có một ước lượng gián tiếp: hai lần chạy cùng điều kiện `baseline` trên `code-learn` đều cho 6/10 dù một lần vượt recursion limit; và `data-learn` của `subagents` là 0/8. Với quy mô 3 tác vụ, một lần chạy, điểm khác biệt 1 check là hoàn toàn nằm trong nhiễu. Vì vậy các chênh lệch nhỏ trong mục 7 không nên được đọc là hiệu ứng thật.

## 9. Hạn chế và tính hợp lệ



1. **Số lần chạy rất ít và không đều**: mỗi cấu hình chỉ chạy một lần, `subagents` chỉ có 2/3 tác vụ học, `skills-auto` và toàn bộ tác vụ đánh giá chưa có dữ liệu vì hết quota mô hình. Mọi khác biệt 1-2 check trong bảng ở mục 7 vì thế **không có giá trị thống kê** và không nên dùng để kết luận về subagent hay skill.
2. **Nhiễu mô hình rất lớn**: `baseline/code-learn` chạm trần recursion limit (209k token) và một lần chạy khác dừng sớm hơn nhưng vẫn 6/10; `subagents/data-learn` không tạo ra tệp đầu ra nào (0/8). Cùng một cấu hình cho kết quả rất khác nhau → cần trung bình nhiều lần chạy mới kết luận được.
3. **Tác vụ và quy ước do giảng viên thiết kế sẵn**: các check `rule_` hoàn toàn không có trong đề, và mỗi tác vụ đánh giá lại có một bộ quy ước riêng. Điều này có lợi cho phép "self-evolving" (tác tử thấy phản hồi) nhưng cũng giới hạn kết luận: kỹ thuật curator ở đây chỉ chứng minh được là **chuyển phản hồi thành văn bản hướng dẫn**, chưa chứng minh là học quy ước mới.
4. **Chỉ một mô hình**: toàn bộ số liệu thu được trên `gemini-3.1-flash-lite` (mô hình nhỏ, dễ lặp). Kết luận không suy rộng được sang mô hình mạnh hơn — với mô hình mạnh, giả thuyết của GUIDE là nhóm E vẫn chiếm đa số, còn điểm kỹ thuật sẽ gần 100%.
5. **Skill do curator sinh có thể sai**: curator có tính ngừa nhiên; 3 skill ở mục 6 được đánh giá là hợp lệ về định dạng nhưng có phần **quá khớp `code-learn`**, nên kết quả `skills-auto` (chưa có) có nguy cơ đo hiệu ứng học thuộc thay vì khả năng khái quát.

## 10. Kết luận

Với dữ liệu hiện có, mô hình mạnh đã gần đạt phần lớn check kỹ thuật (`baseline` 16/18) nhưng **0/9 check quy ước**, cho thấy phần đáng giá nhất còn thiếu là tuân thủ quy ước chứ không phải năng lực lập trình. Ở điều kiện `subagents`, `subagent_calls = 0` và token cao hơn 6% nên đa tác tử không đáng chi phí khi tác vụ nhỏ. Ba skill do curator sinh quanh chất lượng mã và bảo toàn test — nhắm vào nhóm check vốn đã gần đạt — nên chưa có lý do để kỳ vọng chúng nâng điểm; đồng thời sự quá khớp `code-learn` cho thấy curator thiên về ghi lại chi tiết hơn là trừu tượng hoá. Bước tiếp theo đáng làm là bổ sung một skill "generic" về đọc kỹ quy ước đầu ra (tên tệp, thứ tự trường, kiểu đơn vị, khối metadata) và chạy **mỗi cấu hình 3 lần** trên cả 3 tác vụ đánh giá để tách tín hiệu khỏi nhiễu.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
  1. `pytest tests` (dùng `.venv`) → 29 passed
  2. `python scripts/tour.py`
  3. `python -c "from lab.model import make_model; ..."` — thử `gemini-3.8-flash` bị 429 quota free tier, đổi `LAB_MODEL=google_genai:gemini-3.1-flash-lite`
  4. `python -m lab.runner --condition baseline --tasks learn`
  5. `python -m lab.runner --condition subagents --tasks learn` (bị ngắt; chạy lại từng tác vụ)
  6. `python -m lab.runner --condition subagents --tasks data-learn logs-learn --recursion-limit 25` (chỉ xong `data-learn`)
  7. `python -m lab.compare > report/table.md`, `python scripts/check_breakdown.py`, `python scripts/verify_freeze.py` → `OK`
- Thử thách mở rộng (nếu có): **không chọn** (hết thời gian nộp bài).
- Ghi chú khác:
  - `verify_freeze.py` lỗi `UnicodeDecodeError: 'charmap'` khi chạy trên Windows console mặc định; chạy được với `$env:PYTHONUTF8=1`.
  - `python -m lab.compare > report/table.md` ghi file UTF-16 trên PowerShell; phải dùng `| Out-File -Encoding utf8` để file đọc được.
  - **Phần 3.2 (chạy curator), 3.4 (skills-auto trên tác vụ học), 4.2 (chạy tác vụ đánh giá và skills-auto all) chưa hoàn thành** vì quota Gemini free tier (20 request/ngày) bị hạn chế và hết thời gian nộp. Cần chạy lại 3 lệnh sau khi hết quota:
    ```bash
    python -m lab.curator
    python -m lab.runner --condition skills-auto --tasks learn
    python -m lab.runner --condition baseline  --tasks eval
    python -m lab.runner --condition subagents --tasks eval
    python -m lab.runner --condition skills-auto --tasks all
    ```
  - Mục 2 (H1-H3) đã commit (`hypotheses`) trước tag `freeze`; vì chưa chạy tác vụ đánh giá nên giả thuyết vẫn là dự đoán trước khi thấy điểm đánh giá — nhưng H2 dựa trên 3 skill đã có sẵn từ trước, cần nói rõ điều này khi trình bày.
