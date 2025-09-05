import os
import pathlib
import json
import yaml  # pip install pyyaml

def chart_html(spec_path: str, rel_root: str = '.') -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{spec_path}</title>
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
</head>
<body>
  <h2>{spec_path}</h2>
  <div id="vis"></div>
  <script type="text/javascript">
    vegaEmbed('#vis', "./{rel_root}/{spec_path}.json");
  </script>
</body>
</html>"""

def build_tree(base_dir: str):
    """扫描所有 yaml/json 配置文件"""
    tree = {}
    for root, _, files in os.walk(base_dir):
        rel_root = os.path.relpath(root, base_dir)
        for f in files:
            if f.endswith((".json", ".yaml", ".yml")):
                parts = rel_root.split(os.sep) if rel_root != "." else []
                node = tree
                for p in parts:
                    node = node.setdefault(p, {})
                name, ext = os.path.splitext(f)
                node[name] = None
    return tree

def render_tree(node, prefix="charts", path=""):
    html = "<ul>\n"
    for name, child in node.items():
        if child is None:
            html_path = os.path.join(prefix, path, f"{name}.html").replace("\\", "/")
            html += f'<li><a href="{html_path}">{name}</a></li>\n'
        else:
            html += f"<li>{name}{render_tree(child, prefix, os.path.join(path, name))}</li>\n"
    html += "</ul>\n"
    return html

def main():
    base_dir = "data"
    build_dir = pathlib.Path("build/charts")
    build_dir.mkdir(parents=True, exist_ok=True)

    for root, _, files in os.walk(base_dir):
        for f in files:
            if not f.endswith((".json", ".yaml", ".yml")):
                continue

            rel_path = os.path.relpath(root, base_dir)
            rel_dir = "" if rel_path == "." else rel_path
            name, ext = os.path.splitext(f)
            json_out = pathlib.Path("build/charts") / rel_dir / f"{name}.json"

            html_path = build_dir / rel_dir / f"{name}.html"
            html_path.parent.mkdir(parents=True, exist_ok=True)

            spec_rel = os.path.join(rel_dir, name).replace("\\", "/")
            print(spec_rel)
            root_rel = '/'.join(['..'] * (len(spec_rel.split(os.sep)) - 1))
            spec_src = pathlib.Path(root) / f

            if ext in [".yaml", ".yml"]:
                # 转换成 json 存到 build/data
                with open(spec_src, encoding="utf-8") as fp:
                    spec = yaml.safe_load(fp)
            else:
                with open(spec_src, encoding="utf-8") as fp:
                    spec = json.load(fp)

            json_out.parent.mkdir(parents=True, exist_ok=True)
            with open(json_out, "w", encoding="utf-8") as fp:
                json.dump(spec, fp, ensure_ascii=False, indent=2)

            # 写 html
            html_path.write_text(chart_html(spec_rel, root_rel), encoding="utf-8")

    # 索引页
    tree = build_tree(base_dir)
    index_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Charts</title>
</head>
<body>
  <h1>Charts</h1>
  {render_tree(tree)}
</body>
</html>"""
    pathlib.Path("build/index.html").write_text(index_html, encoding="utf-8")

if __name__ == "__main__":
    main()
