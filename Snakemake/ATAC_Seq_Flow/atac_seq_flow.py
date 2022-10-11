# ---> Information
# Autho: Benben.Miao
# Date: 2022-10-11
# Conda: python3, snakemake, graphviz, cutadapt, bowtie2, samtools, macs2
# Java: java8, Picard
# <---

SAMPLES = ["sample1", "sample2", "sample3"]
HG38_BOWTIE2_INDEX = "/data/hg38_bowtie2_index"
PICARD = "/env/picard.jar"

rule all: 
    input: 
        expand("bam/ATAC_Seq_{sample}_hg38_bowtie2_sort_rmdup.bam",sample=SAMPLES),
        expand("macs2_result/ATAC_Seq_{sample}_peaks.narrowPeak",sample=SAMPLES)
        
rule cutadapt: 
    input: 
        "raw_reads/ATAC_Seq_{sample}_R1.fq.gz",
        "raw_reads/ATAC_Seq_{sample}_R2.fq.gz"
    output: 
        "clean_reads/ATAC_Seq_{sample}_R1_clean.fq.gz",
        "clean_reads/ATAC_Seq_{sample}_R2_clean.fq.gz"
    log: 
        "clean_reads/ATAC_Seq_{sample}.log"
    shell: 
        "cutadapt -j 4 --times 1 -e 0.1 -O 3 --quality-cutoff 25 -m 50 \
        -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC \
        -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTAGATCTCGGTGGTCGCCGTATCATT \
        -o {output[0]} -p {output[1]} {input[0]} {input[1]} > {log} 2>&1"

rule bowtie2_map: 
    input: 
        "clean_reads/ATAC_Seq_{sample}_R1_clean.fq.gz",
        "clean_reads/ATAC_Seq_{sample}_R2_clean.fq.gz"
    output: 
        "bam/ATAC_Seq_{sample}_hg38_bowtie2.bam"
    log: 
        "bam/ATAC_Seq_{sample}_hg38_bowtie2.log"
    shell: 
        "bowtie2 -x {HG38_BOWTIE2_INDEX} -p 4 -1 {input[0]} -2 {input[1]} > {log} 2>&1"

rule bam_sort: 
    input: 
        "bam/ATAC_Seq_{sample}_hg38_bowtie2.bam"
    output: 
        "bam/ATAC_Seq_{sample}_hg38_bowtie2_sort.bam"
    log: 
        "bam/ATAC_Seq_{sample}_hg38_bowtie2_sort.log"
    shell: 
        "samtools sort -O BAM -o {output} -T {output}.temp -@ 4 -m 2G {input}"
        
rule remove_duplication: 
    input: 
        "bam/ATAC_Seq_{sample}_hg38_bowtie2_sort.bam"
    output: 
        "bam/ATAC_Seq_{sample}_hg38_bowtie2_sort_rmdup.bam",
        "bam/ATAC_Seq_{sample}_hg38_bowtie2_sort_rmdup.matrix"
    log: 
        "bam/ATAC_Seq_{sample}_hg38_bowtie2_sort_rmdup.log"
    shell: 
        "java -Xms5g -Xmx5g -XX:ParallelGCThreads=4 \
        -jar {PICARD} MarkDuplicates \
        I={input} O={output[0]} M={output[1]} \
        ASO=coordinate REMOVE_DUPLICATES=true 2>{log}"

rule call_peak:
    input: 
        "bam/ATAC_Seq_{sample}_hg38_bowtie2_sort_rmdup.bam"
    output: 
        "macs2_result/ATAC_Seq_{sample}_peaks.narrowPeak"
    params: 
        "ATAC_Seq_{sample}",
        "macs2_result"
    log: 
        "macs2_result/ATAC_Seq_{sample}_peaks.log"
    shell: 
        "macs2 callpeak -t {input} -f BAM -g hs --outdir {params[1]} -n {params[0]} -m 2 100 > {log} 2>&1"