#!/bin/bash

sinter plot \
    --in out/stats.csv \
    --group_func "f'''p={metadata['p']} b={metadata['b']} g={metadata['g']} r/d={metadata['r']/metadata['d']}'''" \
    --x_func "metadata['d']" \
    --xaxis "Patch Diameter" \
    --filter_func "metadata['b'] == 'X' and 'correlated' in decoder and 'noflags' in metadata['g']" \
    --out out/plots/correlated_diam_vs_logical_error_rate_X_no_flags.png &
sinter plot \
    --in out/stats.csv \
    --group_func "f'''p={metadata['p']} b={metadata['b']} g={metadata['g']} r/d={metadata['r']/metadata['d']}'''" \
    --x_func "metadata['d']" \
    --xaxis "Patch Diameter" \
    --filter_func "metadata['b'] == 'Z' and 'correlated' in decoder and 'noflags' in metadata['g']" \
    --out out/plots/correlated_diam_vs_logical_error_rate_Z_no_flags.png &
sinter plot \
    --in out/stats.csv \
    --group_func "f'''p={metadata['p']} b={metadata['b']} g={metadata['g']} r/d={metadata['r']/metadata['d']}'''" \
    --x_func "metadata['d']" \
    --xaxis "Patch Diameter" \
    --filter_func "metadata['b'] == 'X' and 'correlated' not in decoder and 'noflags' in metadata['g']" \
    --out out/plots/uncorrelated_diam_vs_logical_error_rate_X_no_flags.png &
sinter plot \
    --in out/stats.csv \
    --group_func "f'''p={metadata['p']} b={metadata['b']} g={metadata['g']} r/d={metadata['r']/metadata['d']}'''" \
    --x_func "metadata['d']" \
    --xaxis "Patch Diameter" \
    --filter_func "metadata['b'] == 'Z' and 'correlated' not in decoder and 'noflags' in metadata['g']" \
    --out out/plots/uncorrelated_diam_vs_logical_error_rate_Z_no_flags.png &

sinter plot \
    --in out/stats.csv \
    --group_func "f'''d={metadata['d']} b={metadata['b']} g={metadata['g']} r={metadata['r']}'''" \
    --x_func "metadata['p']" \
    --xaxis "[log]Physical Error Rate" \
    --filter_func "metadata['b'] == 'X' and 'correlated' in decoder and 'noflags' in metadata['g']" \
    --out out/plots/correlated_physical_noise_vs_logical_error_rate_X_no_flags.png &
sinter plot \
    --in out/stats.csv \
    --group_func "f'''d={metadata['d']} b={metadata['b']} g={metadata['g']} r={metadata['r']}'''" \
    --x_func "metadata['p']" \
    --xaxis "[log]Physical Error Rate" \
    --filter_func "metadata['b'] == 'Z' and 'correlated' in decoder and 'noflags' in metadata['g']" \
    --out out/plots/correlated_physical_noise_vs_logical_error_rate_Z_no_flags.png &
sinter plot \
    --in out/stats.csv \
    --group_func "f'''d={metadata['d']} b={metadata['b']} g={metadata['g']} r={metadata['r']}'''" \
    --x_func "metadata['p']" \
    --xaxis "[log]Physical Error Rate" \
    --filter_func "metadata['b'] == 'X' and 'correlated' not in decoder and 'noflags' in metadata['g']" \
    --out out/plots/uncorrelated_physical_noise_vs_logical_error_rate_X_no_flags.png &
sinter plot \
    --in out/stats.csv \
    --group_func "f'''d={metadata['d']} b={metadata['b']} g={metadata['g']} r={metadata['r']}'''" \
    --x_func "metadata['p']" \
    --xaxis "[log]Physical Error Rate" \
    --filter_func "metadata['b'] == 'Z' and 'correlated' not in decoder and 'noflags' in metadata['g']" \
    --out out/plots/uncorrelated_physical_noise_vs_logical_error_rate_Z_no_flags.png &

sinter plot \
    --in out/stats.csv \
    --group_func "f'''p={metadata['p']} b={metadata['b']} g={metadata['g']} r/d={metadata['r']/metadata['d']}'''" \
    --x_func "metadata['d']" \
    --xaxis "Patch Diameter" \
    --filter_func "metadata['b'] == 'X' and 'correlated' in decoder and 'noflags' not in metadata['g']" \
    --out out/plots/correlated_diam_vs_logical_error_rate_X.png &
sinter plot \
    --in out/stats.csv \
    --group_func "f'''p={metadata['p']} b={metadata['b']} g={metadata['g']} r/d={metadata['r']/metadata['d']}'''" \
    --x_func "metadata['d']" \
    --xaxis "Patch Diameter" \
    --filter_func "metadata['b'] == 'Z' and 'correlated' in decoder and 'noflags' not in metadata['g']" \
    --out out/plots/correlated_diam_vs_logical_error_rate_Z.png &
sinter plot \
    --in out/stats.csv \
    --group_func "f'''p={metadata['p']} b={metadata['b']} g={metadata['g']} r/d={metadata['r']/metadata['d']}'''" \
    --x_func "metadata['d']" \
    --xaxis "Patch Diameter" \
    --filter_func "metadata['b'] == 'X' and 'correlated' not in decoder and 'noflags' not in metadata['g']" \
    --out out/plots/uncorrelated_diam_vs_logical_error_rate_X.png &
sinter plot \
    --in out/stats.csv \
    --group_func "f'''p={metadata['p']} b={metadata['b']} g={metadata['g']} r/d={metadata['r']/metadata['d']}'''" \
    --x_func "metadata['d']" \
    --xaxis "Patch Diameter" \
    --filter_func "metadata['b'] == 'Z' and 'correlated' not in decoder and 'noflags' not in metadata['g']" \
    --out out/plots/uncorrelated_diam_vs_logical_error_rate_Z.png &

sinter plot \
    --in out/stats.csv \
    --group_func "f'''d={metadata['d']} b={metadata['b']} g={metadata['g']} r={metadata['r']}'''" \
    --x_func "metadata['p']" \
    --xaxis "[log]Physical Error Rate" \
    --filter_func "metadata['b'] == 'X' and 'correlated' in decoder and 'noflags' not in metadata['g']" \
    --out out/plots/correlated_physical_noise_vs_logical_error_rate_X.png &
sinter plot \
    --in out/stats.csv \
    --group_func "f'''d={metadata['d']} b={metadata['b']} g={metadata['g']} r={metadata['r']}'''" \
    --x_func "metadata['p']" \
    --xaxis "[log]Physical Error Rate" \
    --filter_func "metadata['b'] == 'Z' and 'correlated' in decoder and 'noflags' not in metadata['g']" \
    --out out/plots/correlated_physical_noise_vs_logical_error_rate_Z.png &
sinter plot \
    --in out/stats.csv \
    --group_func "f'''d={metadata['d']} b={metadata['b']} g={metadata['g']} r={metadata['r']}'''" \
    --x_func "metadata['p']" \
    --xaxis "[log]Physical Error Rate" \
    --filter_func "metadata['b'] == 'X' and 'correlated' not in decoder and 'noflags' not in metadata['g']" \
    --out out/plots/uncorrelated_physical_noise_vs_logical_error_rate_X.png &
sinter plot \
    --in out/stats.csv \
    --group_func "f'''d={metadata['d']} b={metadata['b']} g={metadata['g']} r={metadata['r']}'''" \
    --x_func "metadata['p']" \
    --xaxis "[log]Physical Error Rate" \
    --filter_func "metadata['b'] == 'Z' and 'correlated' not in decoder and 'noflags' not in metadata['g']" \
    --out out/plots/uncorrelated_physical_noise_vs_logical_error_rate_Z.png &

wait
