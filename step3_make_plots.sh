#!/bin/bash

sinter plot --in out/stats.csv --group_func "f'''p={metadata['p']} b={metadata['b']} g={metadata['g']} r/d={metadata['r']/metadata['d']}'''" --x_func "metadata['d']" --xaxis "Patch Diameter" --filter_func "metadata['b'] == 'X'" --out out/plots/d_vs_lp_x.png &
sinter plot --in out/stats.csv --group_func "f'''p={metadata['p']} b={metadata['b']} g={metadata['g']} r/d={metadata['r']/metadata['d']}'''" --x_func "metadata['d']" --xaxis "Patch Diameter" --filter_func "metadata['b'] == 'Z'" --out out/plots/d_vs_lp_z.png &

sinter plot --in out/stats.csv --group_func "f'''d={metadata['d']} b={metadata['b']} g={metadata['g']} r={metadata['r']}'''" --x_func "metadata['p']" --xaxis "[log]Physical Error Rate" --filter_func "metadata['b'] == 'X'" --out out/plots/p_vs_lp_x.png &
sinter plot --in out/stats.csv --group_func "f'''d={metadata['d']} b={metadata['b']} g={metadata['g']} r={metadata['r']}'''" --x_func "metadata['p']" --xaxis "[log]Physical Error Rate" --filter_func "metadata['b'] == 'Z'" --out out/plots/p_vs_lp_z.png &

wait
