# # alex_cli/libfind.py
# import subprocess
# from cyclopts import App

# app = App()

# @app.default
# def libfind(
#     keyword1: str = None,
#     keyword2: str = None,
#     directory: str = ".",
# ):
#     """Search markdown files in a given directory (non-recursive), fzf, copy result to clipboard."""

#     # Awk command: escape single quotes, wrap result in quotes, no newline
#     awk_cmd = r"""{gsub("\047","'\''"); printf "\047%s\047", $0}"""

#     if not keyword1:
#         cmd = f"ls -1 {directory} | fzf | awk '{awk_cmd}' | pbcopy"
#     elif keyword1 and not keyword2:
#         cmd = f"rg --max-depth 1 -i -l {keyword1!r} {directory} | fzf | awk '{awk_cmd}' | pbcopy"
#     else:
#         cmd = (
#             f"rg --max-depth 1 -i -l --null {keyword1!r} {directory} "
#             f"| xargs -0 rg --max-depth 1 -i -l {keyword2!r} "
#             f"| fzf | awk '{awk_cmd}' | pbcopy"
#         )

#     subprocess.run(cmd, shell=True, check=True)


# if __name__ == "__main__":
#     app()

# alex_cli/libfind.py
import subprocess
from cyclopts import App

app = App()

@app.default
def libfind(
    keyword1: str = None,
    keyword2: str = None,
    directory: str = ".",
):
    """Search markdown files in a given directory (non-recursive), fzf, copy result to clipboard."""

    # Awk command: escape single quotes, wrap result in quotes, no newline
    awk_cmd = r"""{gsub("\047","'\''"); printf "\047%s\047", $0}"""

    if not keyword1:
        # Just list files in directory
        cmd = f"ls -1 {directory} | fzf | awk '{awk_cmd}' | pbcopy"
    elif keyword1 and not keyword2:
        # Search keyword1, strip leading './'
        cmd = (
            f"rg --max-depth 1 -i -l {keyword1!r} {directory} "
            f"| sed 's|^\./||' | fzf | awk '{awk_cmd}' | pbcopy"
        )
    else:
        # Search keyword1 AND keyword2, strip leading './'
        cmd = (
            f"rg --max-depth 1 -i -l --null {keyword1!r} {directory} "
            f"| xargs -0 rg --max-depth 1 -i -l {keyword2!r} "
            f"| sed 's|^\./||' | fzf | awk '{awk_cmd}' | pbcopy"
        )

    subprocess.run(cmd, shell=True, check=True)


if __name__ == "__main__":
    app()
