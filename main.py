from argparse import ArgumentParser
from pathlib import Path
from lib.netkeiba import ColumnList

KEYWORD = "AI予想"


def main():
    parser = ArgumentParser()
    parser.add_argument("--keyword", type=str, default=KEYWORD)
    parser.add_argument("--output_dir", type=str, default=".")
    args = parser.parse_args()

    print("Keyword:", args.keyword)
    columns = ColumnList(keyword=args.keyword).get_all()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for column in columns:
        with open(output_dir / f"{column.cid}.txt", "w") as f:
            f.write(column.content)


if __name__ == "__main__":
    main()
