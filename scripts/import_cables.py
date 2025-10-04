import argparse
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--xml-cable", required=False, default="Câble.xml")
    p.add_argument("--xml-layer", required=False, default="Couche câble.xml")
    p.add_argument("--db", required=False, default="data/celestex.db")
    args = p.parse_args()

    print("Stub importer")
    print(f" cable xml: {args.xml_cable}")
    print(f" layer xml: {args.xml_layer}")
    print(f" db path  : {args.db}")
    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    # TODO: parse XMLs and load SQLite

if __name__ == "__main__":
    main()
