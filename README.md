# Heavy Hex Demo

The code in this repository was written as a demonstration of using stim to analyze an error correcting code, for the IBM quantum summer school.

```bash
# regenerate circuits:
./step1_make_circuits.sh

# recollect data (using pymatching)
./step2_collect_data.sh

# regenerate plots
./step3_make_plots.sh
```

Plotting logical error rate vs distance:

| X BASIS (no threshold)                | Correlated Matching                                                          | Uncorrelated Matching                                                          |
|---------------------------------------|------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| Flag measurements marked as detectors | ![imag](out/plots/correlated_diam_vs_logical_error_rate_X.png)          | ![imag](out/plots/uncorrelated_diam_vs_logical_error_rate_X.png)          |
| Flag measurements not included        | ![imag](out/plots/correlated_diam_vs_logical_error_rate_X_no_flags.png) | ![imag](out/plots/uncorrelated_diam_vs_logical_error_rate_X_no_flags.png) |


| Z BASIS                | Correlated Matching                                                          | Uncorrelated Matching                                                          |
|---------------------------------------|------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| Flag measurements marked as detectors | ![imag](out/plots/correlated_diam_vs_logical_error_rate_Z.png)          | ![imag](out/plots/uncorrelated_diam_vs_logical_error_rate_Z.png)          |
| Flag measurements not included        | ![imag](out/plots/correlated_diam_vs_logical_error_rate_Z_no_flags.png) | ![imag](out/plots/uncorrelated_diam_vs_logical_error_rate_Z_no_flags.png) |

Plotting logical error rate vs physical error rate:

| X BASIS (no threshold)                | Correlated Matching                                                     | Uncorrelated Matching                                                          |
|---------------------------------------|-------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| Flag measurements marked as detectors | ![imag](out/plots/correlated_physical_noise_vs_logical_error_rate_X.png)          | ![imag](out/plots/uncorrelated_physical_noise_vs_logical_error_rate_X.png)          |
| Flag measurements not included        | ![imag](out/plots/correlated_physical_noise_vs_logical_error_rate_X_no_flags.png) | ![imag](out/plots/uncorrelated_physical_noise_vs_logical_error_rate_X_no_flags.png) |


| Z BASIS                | Correlated Matching                                                          | Uncorrelated Matching                                                          |
|---------------------------------------|------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| Flag measurements marked as detectors | ![imag](out/plots/correlated_physical_noise_vs_logical_error_rate_Z.png)          | ![imag](out/plots/uncorrelated_physical_noise_vs_logical_error_rate_Z.png)          |
| Flag measurements not included        | ![imag](out/plots/correlated_physical_noise_vs_logical_error_rate_Z_no_flags.png) | ![imag](out/plots/uncorrelated_physical_noise_vs_logical_error_rate_Z_no_flags.png) |
