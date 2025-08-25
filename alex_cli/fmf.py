# file: frontmatter_filter.py
import os
import subprocess
import frontmatter
import cyclopts

app = cyclopts.App(name="fmf")

def flatten_metadata(metadata) -> str:
    """Flatten metadata dict into a single lowercase string, recursively."""
    parts = []

    def walk(value):
        if isinstance(value, dict):
            for v in value.values():
                walk(v)
        elif isinstance(value, (list, tuple, set)):
            for v in value:
                walk(v)
        else:
            parts.append(str(value))

    walk(metadata)
    return " ".join(parts).lower()

def match_keywords(metadata: dict, keywords: list[str]) -> bool:
    """Return True if all keywords are present (case-insensitive substring)."""
    text = flatten_metadata(metadata)
    return all(kw.lower() in text for kw in keywords)

@app.default
def main(
    *keywords: str,
    directory: str = ".",
    list_mode: bool = False,  # renamed from print
):
    """
    Filter .md files in DIRECTORY by keywords in frontmatter.

    - Only searches the given directory (non-recursive).
    - Case-insensitive substring match.
    - Only files containing ALL keywords are shown.
    - Raises an error if a file has missing or invalid frontmatter.
    - By default, opens fzf to choose a file and copies it to clipboard.
    - If --list is set, prints all matching filenames instead.
    """
    matched_files = []

    for file in os.listdir(directory):
        path = os.path.join(directory, file)
        if not os.path.isfile(path) or not file.endswith(".md"):
            continue

        try:
            post = frontmatter.load(path)
        except Exception as e:
            raise RuntimeError(f"Failed to load frontmatter for {path}: {e}")

        if not post.metadata:
            continue

        if match_keywords(post.metadata, keywords):
            matched_files.append(file)  # store just filename

    if not matched_files:
        return

    if list_mode:
        for f in matched_files:
            print(f"'{f}'")
    else:
        fzf = subprocess.Popen(
            ["fzf"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        input_text = "\n".join(matched_files)
        selected, _ = fzf.communicate(input=input_text)

        if selected:
            selected_clean = "'{}'".format(selected.strip())
            subprocess.run("pbcopy", input=selected_clean, text=True)
            # print(f"Copied to clipboard: {selected_clean}")

if __name__ == "__main__":
    app()






# OLD

# # file: frontmatter_filter.py
# import os
# import subprocess
# import frontmatter
# import cyclopts

# app = cyclopts.App(name="fmf")

# def flatten_metadata(metadata) -> str:
#     """Flatten metadata dict into a single lowercase string, recursively."""
#     parts = []

#     def walk(value):
#         if isinstance(value, dict):
#             for v in value.values():
#                 walk(v)
#         elif isinstance(value, (list, tuple, set)):
#             for v in value:
#                 walk(v)
#         else:
#             parts.append(str(value))

#     walk(metadata)
#     return " ".join(parts).lower()

# def match_keywords(metadata: dict, keywords: list[str]) -> bool:
#     """Return True if all keywords are present (case-insensitive substring)."""
#     text = flatten_metadata(metadata)
#     return all(kw.lower() in text for kw in keywords)

# @app.command()
# def filter(
#     *keywords: str,
#     directory: str = ".",
#     print: bool = False,  # explicitly print instead of selecting
# ):
#     """
#     Filter .md files in DIRECTORY by keywords in frontmatter.

#     - Only searches the given directory (non-recursive).
#     - Case-insensitive substring match.
#     - Only files containing ALL keywords are shown.
#     - Raises an error if a file has missing or invalid frontmatter.
#     - By default (--select), opens fzf to choose a file and copies it to clipboard.
#     - If --print is set, prints all matching filenames instead.
#     """
#     matched_files = []

#     for file in os.listdir(directory):
#         path = os.path.join(directory, file)
#         if not os.path.isfile(path) or not file.endswith(".md"):
#             continue

#         try:
#             post = frontmatter.load(path)
#         except Exception as e:
#             raise RuntimeError(f"Failed to load frontmatter for {path}: {e}")

#         if not post.metadata:
#             continue

#         if match_keywords(post.metadata, keywords):
#             matched_files.append(file)  # store just filename

#     if not matched_files:
#         return

#     if print:
#         # Explicit print mode
#         for f in matched_files:
#             print(f"'{f}'")
#     else:
#         # Default interactive selection via fzf + copy to clipboard
#         fzf = subprocess.Popen(
#             ["fzf"],
#             stdin=subprocess.PIPE,
#             stdout=subprocess.PIPE,
#             text=True
#         )
#         input_text = "\n".join(matched_files)
#         selected, _ = fzf.communicate(input=input_text)

#         if selected:
#             # Strip trailing spaces/newlines and wrap in single quotes
#             selected_clean = "'{}'".format(selected.strip())
#             subprocess.run("pbcopy", input=selected_clean, text=True)
#             print(f"Copied to clipboard: {selected_clean}")

# if __name__ == "__main__":
#     app()
