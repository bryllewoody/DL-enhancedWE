import re
import sys
from datetime import timedelta

LOG_FILE = "west.log"

iteration_pat  = re.compile(r"^Beginning iteration (\d+)")
recycle_pat    = re.compile(
    r"^Recycled ([\d.eE+\-]+) probability \((\d+) walkers?\) from target state 'folded'"
)
wallclock_pat  = re.compile(r"^Iteration wallclock: ([\d:\.]+),")

events        = []   # list of (iteration, probability, n_walkers)
wallclocks    = []   # list of timedelta
current_iter  = None

def parse_wallclock(s):
    """Parse H:MM:SS.ffffff or H:MM:SS into total seconds."""
    parts = s.split(":")
    hours, minutes = int(parts[0]), int(parts[1])
    seconds = float(parts[2])
    return timedelta(hours=hours, minutes=minutes, seconds=seconds).total_seconds()

with open(LOG_FILE) as fh:
    for line in fh:
        line = line.strip()

        m = iteration_pat.match(line)
        if m:
            current_iter = int(m.group(1))
            continue

        m = recycle_pat.match(line)
        if m:
            prob   = float(m.group(1))
            n_walk = int(m.group(2))
            events.append((current_iter, prob, n_walk))
            continue

        m = wallclock_pat.match(line)
        if m:
            wallclocks.append(parse_wallclock(m.group(1)))

if not events:
    print("No recycling events found.")
    sys.exit(0)

print(f"{'Iteration':>10}  {'Walkers':>7}  {'Probability':>18}")
print("-" * 42)
for it, prob, nw in events:
    print(f"{it:>10}  {nw:>7}  {prob:>18.6e}")

print()
print(f"Total recycling events : {len(events)}")

best = max(events, key=lambda x: x[1])
print(f"Highest probability    : {best[1]:.6e}  (iteration {best[0]}, {best[2]} walker(s))")

if wallclocks:
    avg_s = sum(wallclocks) / len(wallclocks)
    print(f"Average time/iteration : {avg_s:.4f} s  ({len(wallclocks)} iterations timed)")
