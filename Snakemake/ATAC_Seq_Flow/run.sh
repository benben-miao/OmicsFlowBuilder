# Run Test
snakemake --snakefile atac_seq_flow.py --dryrun

# Run Dag
snakemake --snakefile atac_seq_flow.py --dag

# Run Graph
# mamba install graphviz
snakemake --snakefile atac_seq_flow.py --dag | dot -Tpdf -o graph.pdf

# Run Jobs
snakemake --snakefile atac_seq_flow.py --printshellcmds --jobs 3 &

# Run Details
snakemake --help