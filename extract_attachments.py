#!/usr/bin/env python3
"""
extract_attachments.py

Пример: python tools/extract_attachments.py --input tools/ОРВ.yaml --output tools/attachments_list.txt

Собирает все значения под ключом `attachments` в любом месте YAML-дерева
и сохраняет уникальный список значений (по одному на строке) в текстовый файл.
"""
import argparse
import json
import sys
from collections import OrderedDict

try:
    import yaml
except Exception as e:
    print("PyYAML required. Установите: pip install pyyaml", file=sys.stderr)
    raise


def collect_attachments(node, results):
    """Рекурсивно обходит node и добавляет значения ключа 'attachments' в results (list).
    Ожидается, что значения - список или одиночная строка.
    """
    if isinstance(node, dict):
        for k, v in node.items():
            if k == 'attachments':
                # может быть список или одиночное значение
                if isinstance(v, list):
                    for it in v:
                        results.append(str(it))
                elif v is None:
                    continue
                else:
                    results.append(str(v))
            else:
                collect_attachments(v, results)
    elif isinstance(node, list):
        for item in node:
            collect_attachments(item, results)


def main():
    p = argparse.ArgumentParser(description='Extract all "attachments" values from YAML')
    p.add_argument('--input', '-i', default='tools/ОРВ.yaml', help='Input YAML file')
    p.add_argument('--output', '-o', default='tools/attachments_list.txt', help='Output text file (one value per line)')
    p.add_argument('--json', action='store_true', help='Also write JSON file with the list (output + .json)')
    args = p.parse_args()

    with open(args.input, 'r', encoding='utf-8') as fh:
        # использую safe_load чтобы загрузить весь файл
        data = yaml.safe_load(fh)

    raw = []
    collect_attachments(data, raw)

    # сохранить уникальные значения, в порядке первого появления
    uniq = list(OrderedDict.fromkeys(raw))

    with open(args.output, 'w', encoding='utf-8') as out:
        for v in uniq:
            out.write(f"{v}\n")

    print(f"Wrote {len(uniq)} attachment entries to {args.output}")

    if args.json:
        jpath = args.output + '.json'
        with open(jpath, 'w', encoding='utf-8') as jh:
            json.dump(uniq, jh, ensure_ascii=False, indent=2)
        print(f"Also wrote JSON to {jpath}")


if __name__ == '__main__':
    main()
