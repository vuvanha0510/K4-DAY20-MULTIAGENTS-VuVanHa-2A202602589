"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": "Dùng khi cần đọc nhiều tệp, tìm hiểu cấu trúc dự án, đọc README, docstring, hoặc mẫu dữ liệu để báo cáo sự thật. Không sửa đổi tệp.",
            "system_prompt": "Bạn là một explorer. Nhiệm vụ của bạn là đọc và thu thập thông tin từ workspace. Không được sửa đổi bất kỳ tệp nào. Hãy đọc kỹ README, docstring, mã nguồn, và dữ liệu mẫu rồi báo cáo ngắn gọn những gì bạn tìm thấy."
        },
        {
            "name": "implementer",
            "description": "Dùng khi cần thực hiện thay đổi mã, sửa lỗi, chạy test hoặc script, và báo cáo kết quả.",
            "system_prompt": "Bạn là một implementer. Nhiệm vụ của bạn là thực hiện thay đổi mã nguồn, chạy test hoặc script để kiểm tra. Hãy làm theo các quy tắc được truyền trong prompt giao việc và báo cáo kết quả chạy test."
        },
        {
            "name": "reviewer",
            "description": "Dùng khi cần kiểm tra độc lập kết quả theo đề bài và các trường hợp biên, không sửa tệp.",
            "system_prompt": "Bạn là một reviewer. Nhiệm vụ của bạn là kiểm tra độc lập kết quả làm việc theo đề bài, kiểm tra các trường hợp biên (edge cases), và báo cáo xem kết quả có đạt yêu cầu không. Không được sửa đổi tệp."
        },
    ]
