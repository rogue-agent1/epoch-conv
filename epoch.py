#!/usr/bin/env python3
"""epoch - Convert between Unix timestamps and human dates. Zero deps."""
import sys, time, datetime

def ts_to_human(ts):
    dt = datetime.datetime.fromtimestamp(float(ts))
    utc = datetime.datetime.utcfromtimestamp(float(ts))
    print(f"Timestamp: {ts}")
    print(f"Local:     {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"UTC:       {utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"ISO 8601:  {dt.isoformat()}")

def human_to_ts(s):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d"):
        try:
            dt = datetime.datetime.strptime(s, fmt)
            print(f"Date:      {s}")
            print(f"Timestamp: {int(dt.timestamp())}")
            print(f"Millis:    {int(dt.timestamp() * 1000)}")
            return
        except ValueError:
            continue
    print(f"Cannot parse: {s}"); sys.exit(1)

def main():
    if len(sys.argv) < 2:
        now = time.time()
        print(f"Now: {int(now)}")
        print(f"  => {datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')}")
        return
    arg = " ".join(sys.argv[1:])
    try:
        float(arg)
        ts_to_human(arg)
    except ValueError:
        human_to_ts(arg)

if __name__ == "__main__":
    main()
