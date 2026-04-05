import h5py
import numpy as np
import matplotlib.pyplot as plt

tau = 1e-11

with h5py.File("fluxanl.h5", "r") as f:
    avg_flux_expected = f["avg_flux"]["expected"][0]
    avg_flux_ci_lb = f["avg_flux"]["ci_lbound"][0]
    avg_flux_ci_ub = f["avg_flux"]["ci_ubound"][0]
    avg_flux_sterr = f["avg_flux"]["sterr"][0]

    mean_flux_index = f["target_flux/index"]["mean_flux"][0]
    mean_flux_ci_lb = f["target_flux/index"]["mean_flux_ci_lb"][0]
    mean_flux_ci_ub = f["target_flux/index"]["mean_flux_ci_ub"][0]

    raw_flux = f["target_flux/target_0/flux"][:]
    n_iter = f["target_flux/target_0/n_iter"][:]

print("From avg_flux:")
print("  mean rate =", avg_flux_expected)
print("  CI        =", (avg_flux_ci_lb, avg_flux_ci_ub))
print("  stderr    =", avg_flux_sterr)

print("\nFrom target_flux/index:")
print("  mean rate =", mean_flux_index)
print("  CI        =", (mean_flux_ci_lb, mean_flux_ci_ub))

print("\nConverted to s^-1 using tau = 1e-11:")
print("  mean rate =", avg_flux_expected / tau)
print("  CI        =", (avg_flux_ci_lb / tau, avg_flux_ci_ub / tau))
print("  stderr    =", avg_flux_sterr / tau)

print("\nRaw flux check:")
print("  arithmetic mean of raw flux =", np.mean(raw_flux))
print("  final raw flux value        =", raw_flux[-1])

# flux evolution figure
raw_rate = raw_flux / tau

plt.figure(figsize=(6, 4))
plt.plot(n_iter, raw_rate, linewidth=1)
plt.axhline(avg_flux_expected / tau, linestyle="--", linewidth=1,
            label=f"mean rate = {avg_flux_expected / tau:.2e} s$^{{-1}}$")
plt.xlabel("Iteration")
plt.ylabel("Flux / rate (s$^{-1}$)")
plt.title("Flux evolution")
plt.legend()
plt.tight_layout()

plt.savefig("flux_evolution.png", dpi=300)
plt.close()
