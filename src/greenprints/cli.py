"""Command line: `python -m greenprints run`."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from greenprints import report
from greenprints.config import ConfigError, load_config
from greenprints.load import RawDataMissing
from greenprints.pipeline import build


def run(root: Path | None = None) -> int:
    try:
        cfg = load_config(root)
    except ConfigError as e:
        print(f"CONFIG ERROR: {e}", file=sys.stderr)
        return 2
    try:
        res = build(cfg)
    except RawDataMissing as e:
        print(str(e), file=sys.stderr)
        return 3

    out = cfg.output_dir
    out.mkdir(parents=True, exist_ok=True)
    report.clean_table(res.shipments, cfg).to_csv(out / "shipments_clean.csv", index=False)
    report.write_excel(res, out / "greenprints_results.xlsx")
    (out / "data_quality_report.md").write_text(report.data_quality_md(res), encoding="utf-8")
    meth = report.methodology_md(cfg, res)
    (cfg.root / "METHODOLOGY.md").write_text(meth, encoding="utf-8")
    shutil.copyfile(cfg.root / "METHODOLOGY.md", out / "METHODOLOGY.md")

    h = report.headline(res.shipments, cfg)
    print(f"Project Greenprints - WARM v{cfg.warm['warm_version']}, "
          f"{cfg.start_date} to {cfg.end_date}")
    print(f"  Shipments:          {h['shipments']}  "
          f"({h['n_estimated']} estimated weight, {h['n_missing']} missing weight)")
    print(f"  Total lbs:          {h['lbs']:,.0f}  "
          f"(recorded {h['lbs_recorded']:,.0f}, estimated {h['lbs_estimated']:,.0f})")
    print(f"  MTCO2e avoided:     {h['central']:,.1f}  (range {h['low']:,.1f} - {h['high']:,.1f})"
          f"  [{report.practice_label(cfg, cfg.headline_baseline)} baseline]")
    for b in cfg.baselines[1:]:
        hb = report.headline(res.shipments, cfg, b)
        print(f"  Sensitivity:        {hb['central']:,.1f}  "
              f"(range {hb['low']:,.1f} - {hb['high']:,.1f})  "
              f"[{report.practice_label(cfg, b)} baseline]")
    print(f"  Data-quality items: {len(res.issues)}")
    for ok, msg in res.sanity:
        print(f"  {'OK   ' if ok else 'CHECK'} {msg}")
    if not all(ok for ok, _ in res.sanity):
        print("  WARNING: results differ from the expected sanity-check totals in "
              "settings.yaml. See data_quality_report.md.")
    print(f"Outputs written to {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="greenprints", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    r = sub.add_parser("run", help="Calculate emissions and write all outputs")
    r.add_argument("--root", type=Path, default=None,
                   help="Project folder (default: the greenprints/ folder)")
    args = p.parse_args(argv)
    if args.command == "run":
        return run(args.root)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
