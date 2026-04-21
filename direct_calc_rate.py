"""
Calculate folding rate constant from w_ipa direct.h5 output.
Reads ANALYSIS/TEST/direct.h5 produced by w_ipa / w_kinavg.
"""
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

DIRECT_H5 = "ANALYSIS/TEST/direct.h5"
tau = 1e-11  # seconds per WE iteration (10 ps)

with h5py.File(DIRECT_H5, "r") as f:
    labels = f["state_labels"][:].astype(str)

    # Overall mean rates (cumulative over all iterations)
    avg_rates = f["avg_rates"][:]

    # Rate evolution over iterations
    rate_evo = f["rate_evolution"][:]  # shape (n_iter, n_states, n_states)

    # Flux evolution into folded state (state 0) from unfolded (state 1)
    flux_evo = f["target_flux_evolution"][:]  # shape (n_iter, n_states)

# Identify state indices
folded_idx   = list(labels).index("folded")
unfolded_idx = list(labels).index("unfolded")

# Mean folding rate 
r = avg_rates[unfolded_idx, folded_idx]
mean_rate   = r["expected"] / tau
ci_lb       = r["ci_lbound"] / tau
ci_ub       = r["ci_ubound"] / tau
sterr       = r["sterr"] / tau

print("=" * 55)
print("  Folding rate constant (unfolded -> folded)")
print("=" * 55)
print(f"  k_fold       = {mean_rate:.4e} s^-1")
print(f"  95% CI       = ({ci_lb:.4e}, {ci_ub:.4e}) s^-1")
print(f"  stderr       = {sterr:.4e} s^-1")
print(f"  MFPT (1/k)   = {1/mean_rate*1e6:.2f} µs" if mean_rate > 0 else "  MFPT: undefined (rate=0)")
print("=" * 55)

# Rate evolution plot 
iter_stop  = rate_evo[:, unfolded_idx, folded_idx]["iter_stop"]
rate_trace = rate_evo[:, unfolded_idx, folded_idx]["expected"] / tau
ci_lb_evo  = rate_evo[:, unfolded_idx, folded_idx]["ci_lbound"] / tau
ci_ub_evo  = rate_evo[:, unfolded_idx, folded_idx]["ci_ubound"] / tau

# Mask zeros (uninitialised early iterations)
mask = rate_trace > 0

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(iter_stop[mask], rate_trace[mask], linewidth=1, label="cumulative rate")
ax.fill_between(iter_stop[mask], ci_lb_evo[mask], ci_ub_evo[mask],
                alpha=0.3, label="95% CI")
ax.axhline(mean_rate, color="red", linestyle="--", linewidth=1,
           label=f"mean = {mean_rate:.2e} s$^{{-1}}$")
ax.set_xlabel("Iteration")
ax.set_ylabel("$k_{{fold}}$ (s$^{{-1}}$)")
ax.set_title("Folding rate evolution")
ax.legend()
plt.tight_layout()
plt.savefig("folding_rate_evolution.png", dpi=300)
plt.close()
print("Saved: folding_rate_evolution.png")

# Rate evolution plot (log scale)
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(iter_stop[mask], rate_trace[mask], linewidth=1, label="cumulative rate")
ax.fill_between(iter_stop[mask],
                np.where(ci_lb_evo[mask] > 0, ci_lb_evo[mask], np.nan),
                ci_ub_evo[mask],
                alpha=0.3, label="95% CI")
ax.axhline(mean_rate, color="red", linestyle="--", linewidth=1,
           label=f"mean = {mean_rate:.2e} s$^{{-1}}$")
ax.set_yscale("log")
ax.yaxis.set_major_formatter(
    ticker.FuncFormatter(lambda y, _: f"$10^{{{int(np.log10(y))}}}$" if y > 0 else "")
)
ax.set_xlabel("Iteration")
ax.set_ylabel("$k_{{fold}}$ (s$^{{-1}}$)")
ax.set_title("Folding rate evolution")
ax.legend()
plt.tight_layout()
plt.savefig("folding_rate_evolution_log.png", dpi=300)
plt.close()
print("Saved: folding_rate_evolution_log.png")

