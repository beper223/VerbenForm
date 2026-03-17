from pathlib import Path
import markdown

from django.shortcuts import render


def markdown_page(request):

    file_path = Path("content/work_1c.md")
    with open(file_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    html = markdown.markdown(
        md_text,
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.toc',
        ]
    )

    return render(request, "markdown.html", {"content": html})